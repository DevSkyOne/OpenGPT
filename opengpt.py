import asyncio
import datetime
import logging
import os
import re
from pathlib import Path

import aiofiles
import aiomysql
import discord
import dotenv
import openai
import tiktoken
from aiomysql import Pool
from discord.ext import commands

from database.connection import get_pool
from database.models import UserData

log = logging.getLogger('BOT-MAIN')

dotenv.load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    strip_after_prefix=True,
    intents=intents,
    sync_commands=True,
    delete_not_existing_commands=True,
    activity=discord.Activity(name='Ask me anything', type=discord.ActivityType.listening),
    auto_check_for_updates=True
)
openai.api_key = os.getenv("OPENAI_API_KEY")

tokenizer_cache = {"gpt-4": tiktoken.encoding_for_model("gpt-4"),
                   "gpt-3.5-turbo": tiktoken.encoding_for_model("gpt-3.5-turbo")}

model_pricing = {
    "gpt-4": {
        "max_tokens": 8100,
        "prompt": 0.03,
        "response": 0.06,
    },
    "gpt-3.5-turbo": {
        "max_tokens": 4000,
        "prompt": 0.002,
        "response": 0.002,
    },
}


def calculate_credit_price(model, prompt_tokens, response_tokens):
    prompt_price = round((prompt_tokens * model_pricing[model]["prompt"]))
    response_price = round((response_tokens * model_pricing[model]["response"]))
    return prompt_price + response_price + 1


def calculate_credits_to_response_tokens(model, credits):
    return round(credits / model_pricing[model]["response"])


async def set_user_model(user_id, model):
    user = await UserData(user_id).load()
    user.model = model
    await user.save()


async def get_user_data(user_id) -> UserData:
    return await UserData(user_id).load()


async def generate_text(context=None, thinking_message: discord.Message = None, user: UserData = None) -> (str, int):
    conversation = [
        {"role": "system", "content": f"You are a funny Discord bot assistant, named 'OpenGPT'. For human"
                                      f" support, refer to DevSky Coding Support "
                                      f"(https://discord.gg/devsky). The User"
                                      f" '{user}' started this conversation with you. The current datetime is "
                                      f"{datetime.datetime.now(datetime.timezone.utc)}."
                                      f"""Consider the following in your responses:
- Be conversational
- Add unicode emoji to be more playful in your responses
- Write spoilers using spoiler tags. For example ||At the end of The Sixth Sense it is revealed that he is dead||.
- You can mention people by including their user_id in <@user_id>, for example if you wanted to mention yourself
 you should say <@{bot.user.id}>.

Format text using markdown:
- **bold** to make it clear something is important. For example: **This is important.**
- [title](url) to add links to text. For example: [Google](https://www.google.com/)

Users can interact with you by mentioning you or replying to one of your messages.
Note that you will respond using informal language (e.g., 'Du'-form in German, never ever use 'Sie').
"""}]

    if context:
        conversation.extend(context)

    if tokenizer_cache.get(user.model):
        enc = tokenizer_cache[user.model]
    else:
        enc = tiktoken.encoding_for_model(user.model)
        tokenizer_cache[user.model] = enc

    conversation_content = "\n".join([f"{message['content']}" for message in conversation])
    prompt_tokens = enc.encode(conversation_content)

    prompt_credits = calculate_credit_price(user.model, len(prompt_tokens), 0)
    if prompt_credits > user.credits:
        return "I'm sorry, but you don't have enough credits to answer this question.", 0

    available_credits = user.credits - prompt_credits
    max_response_tokens = calculate_credits_to_response_tokens(user.model, available_credits)

    pricing = model_pricing.get(user.model)
    max_tokens = pricing["max_tokens"]

    response = openai.ChatCompletion.create(
        model=user.model,
        messages=conversation,
        max_tokens=(min(max_tokens - len(prompt_tokens), max_response_tokens)),
        temperature=0.9,
        stream=True,
    )

    full_response = ""
    sent_parts = 1
    for chunk in response:
        if chunk['choices']:
            chunk_message = chunk['choices'][0]['delta']
            if chunk_message.get('content'):
                received_message = chunk_message['content']
                full_response += received_message
                if len(full_response) / 250 > sent_parts:
                    sent_parts += 1
                    if thinking_message:
                        thinking_message_content = f"Generating response... (this may take a while)" \
                                                   f" ({sent_parts * 100} characters received)"

                        if len(full_response) < 1600:
                            thinking_message_content += f"\n\n{full_response}"
                        else:
                            thinking_message_content += f"\n\n{full_response[:1600]}...\n\n" \
                                                        f"*...truncated* (Please wait for the full response.)"

                        await thinking_message.edit(content=thinking_message_content, allowed_mentions=discord.AllowedMentions.none())

    response_tokens = enc.encode(full_response)
    sky_credits = calculate_credit_price(user.model, len(prompt_tokens), len(response_tokens))
    user.credits -= sky_credits
    await user.save()

    return full_response, sky_credits


async def send_thinking_message(message):
    return await message.channel.send("Let me think for a moment... (this may take a while)", reference=message)


async def delete_thinking_message(wait_message):
    await wait_message.delete()


async def send_response(message, response):
    def adjust_chunks(responses_chunks):
        for i in range(len(responses_chunks) - 1):
            # Check for code blocks
            if responses_chunks[i].count("```") % 2 != 0:
                closing_index = responses_chunks[i].rfind("")
                reopened_chunk = responses_chunks[i + 1][:closing_index + 1].strip()
                responses_chunks[i] = f"{responses_chunks[i]}{'' * (3 - closing_index % 3)}"
                responses_chunks[
                    i + 1] = f"{'```'[closing_index % 3:]}{reopened_chunk}{responses_chunks[i + 1][closing_index + 1:].strip()}"

            # Check for split words
            if not (responses_chunks[i][-1].isspace() or responses_chunks[i + 1][0].isspace()):
                split_index = responses_chunks[i].rfind(" ")
                if split_index != -1:
                    responses_chunks[i + 1] = responses_chunks[i][split_index + 1:] + responses_chunks[i + 1]
                    responses_chunks[i] = responses_chunks[i][:split_index + 1]

    if len(response) > 1850:
        responses = [response[i:i + 1850] for i in range(0, len(response), 1850)]

        adjust_chunks(responses)

        reference = message
        for response in responses:
            reference = await message.channel.send(response, reference=reference, allowed_mentions=discord.AllowedMentions.none())
    else:
        await message.channel.send(response, reference=message, allowed_mentions=discord.AllowedMentions.none())


async def get_conversation_history(message, conversation=None):
    if conversation is None:
        conversation = []

    if message.author == bot.user:
        conversation.insert(0, {"role": "system", "content": message.content})
    else:
        conversation.insert(0, {"role": "user", "content": message.content})

    if message.reference:
        reply_message = await message.channel.fetch_message(message.reference.message_id)
        return await get_conversation_history(reply_message, conversation)

    return conversation


@bot.event
async def on_message(message):
    if message.author == bot.user:
        await bot.process_commands(message)
        return

    direct_mentioned = f"<@{bot.user.id}>" in message.content  # Make sure you add ! for direct mentions
    referenced_message_by_bot = (message.reference and message.reference.resolved.author == bot.user)

    if not direct_mentioned and not referenced_message_by_bot:
        return

    thinking_message = await send_thinking_message(message)

    context = await get_conversation_history(message)

    await thinking_message.edit(content="Context found. Generating response... (this may take a while)")

    try:
        asyncio.create_task(generate_answer(context, message, thinking_message))
    except Exception as e:
        await thinking_message.edit(content=f"An error occurred: {e}")


async def generate_answer(context, message, thinking_message):
    user = await get_user_data(message.author.id)
    response_text, sky_credits = await generate_text(context=context,
                                                     thinking_message=thinking_message,
                                                     user=user)
    if not response_text:
        response_text = "I don't know what to say."

    # Replace @gif(search term) with a random gif from giphy with the search term
    response_text = re.sub(r"@gif\((.+?)\)", lambda m: f"{m.group(1)}", response_text)

    await send_response(message, response_text)
    await delete_thinking_message(thinking_message)


@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")


async def init_db() -> None:
    pool: Pool = await get_pool()
    async with aiofiles.open("database/db_structure.sql", "r") as fp:
        struct = await fp.read()

    async with pool.acquire() as connection:
        connection: aiomysql.Connection
        cursor: aiomysql.Cursor = await connection.cursor()
        for query in struct.split(";"):
            try:
                await cursor.execute(query)
            except Exception as e:
                log.error(e)
                continue
    pool.close()
    await pool.wait_closed()


if __name__ == '__main__':
    try:
        log.info("Starting bot...")
        bot.loop.run_until_complete(init_db())
        cogs = [p.stem for p in Path('./cogs').glob('**/*.py') if not p.name.startswith('__')]
        log.info('Loading \x1b[31m%d\x1b[0m extensions...' % len(cogs))

        for cog in cogs:
            bot.load_extension(f'cogs.{cog}')
            log.info('Loaded \x1b[31m%s\x1b[0m' % cog)

        bot.run(os.getenv("BOT_TOKEN"))
    except KeyboardInterrupt:
        log.info("Shutting down...")
        log.info("Goodbye!")
        exit(0)
