import asyncio
import datetime
import os
import re
import sqlite3
from pathlib import Path

import discord
import dotenv
import openai
import tiktoken
from discord.ext import commands

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

# Connect to the database (creates a new file if it doesn't exist)
connection = sqlite3.connect("./users.db")

# Create a cursor object to execute SQL commands
cursor = connection.cursor()

# Create a table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS users
                  (clientid VARCHAR(45) PRIMARY KEY, credits INTEGER DEFAULT 100,
                   last_used DATETIME DEFAULT CURRENT_TIMESTAMP)''')
connection.commit()

tokenizer_cache = {"gpt-4": tiktoken.encoding_for_model("gpt-4"),
                   "gpt-3.5-turbo": tiktoken.encoding_for_model("gpt-3.5-turbo")}

model_pricing = {
    "gpt-4": {
        "prompt": 0.03,
        "response": 0.06,
    },
    "gpt-3.5-turbo": {
        "prompt": 0.002,
        "response": 0.002,
    },
}


def calculate_credit_price(model, prompt_tokens, response_tokens):
    prompt_price = round((prompt_tokens * model_pricing[model]["prompt"]))
    response_price = round((response_tokens * model_pricing[model]["response"]))
    return prompt_price + response_price


def calculate_credits_to_response_tokens(model, credits):
    return round(credits / model_pricing[model]["response"])


async def get_user_credits(user_id) -> (int, datetime.datetime):
    cursor.execute("SELECT credits, last_used FROM users WHERE clientid = ?", (user_id,))
    user_credits = cursor.fetchone()
    if user_credits:
        last_used = user_credits[1]
        if last_used:
            last_used = datetime.datetime.strptime(last_used, "%Y-%m-%d %H:%M:%S").replace(tzinfo=datetime.timezone.utc)
            if last_used < datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1):
                cursor.execute("UPDATE users SET credits = 100 WHERE clientid = ?", (user_id,))
                connection.commit()
                return 100, last_used
            else:
                return user_credits[0], last_used
    else:
        cursor.execute("INSERT INTO users (clientid) VALUES (?)", (user_id,))
        return 100, datetime.datetime.now(datetime.timezone.utc)


async def generate_text(context=None, thinking_message: discord.Message = None, user_id=-1, max_credits=100) -> (
str, int):
    model = os.getenv("OPENAI_MODEL")
    conversation = [
        {"role": "system", "content": f"You are my personal assistant, especially for code reviews or other "
                                      f"technic stuff, named 'OpenGPT'. For more in depth help and real"
                                      f" support, refer me to DevSky Coding Support "
                                      f"(https://discord.gg/devsky). I am using the OpenAI model"
                                      f" '{model}'. The datetime is "
                                      f"{datetime.datetime.now(datetime.timezone.utc)}."
                                      f"I can interact with you by mentioning you or replying to your "
                                      f"messages. I have {max_credits} credits left. Please use informal"
                                      f" language."}]

    if context:
        conversation.extend(context)

    if tokenizer_cache.get(model):
        enc = tokenizer_cache[model]
    else:
        enc = tiktoken.encoding_for_model(model)
        tokenizer_cache[model] = enc

    conversation_content = "\n".join([f"{message['content']}" for message in conversation])
    prompt_tokens = enc.encode(conversation_content)

    prompt_credits = calculate_credit_price(model, len(prompt_tokens), 0)
    if prompt_credits > max_credits:
        return "I'm sorry, but you don't have enough credits to answer this question.", 0

    available_credits = max_credits - prompt_credits
    max_response_tokens = calculate_credits_to_response_tokens(model, available_credits)

    response = openai.ChatCompletion.create(
        model=model,
        messages=conversation,
        max_tokens=(min(8100 - len(prompt_tokens), max_response_tokens)),
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
                if len(full_response) / 100 > sent_parts:
                    sent_parts += 1
                    if thinking_message:
                        thinking_message_content = f"Generating response... (this may take a while)" \
                                                   f" ({sent_parts * 100} characters received)"

                        if len(full_response) < 1600:
                            thinking_message_content += f"\n\n{full_response}"
                        else:
                            thinking_message_content += f"\n\n{full_response[:1600]}...\n\n" \
                                                        f"*...truncated* (Please wait for the full response.)"

                        # Filter out mentions
                        thinking_message_content = thinking_message_content.replace(f"@everyone", "@ everyone")
                        thinking_message_content = thinking_message_content.replace(f"@here", "@ here")
                        ping_regex = re.compile(r"<@!?[0-9]+>")

                        # Find all user mentions and replace them with obfuscated text
                        def replace_mention(match):
                            mention = match.group(0)
                            if mention.startswith("<"):
                                return "**@**user"
                            else:
                                return mention

                        thinking_message_content = ping_regex.sub(replace_mention, thinking_message_content)

                        await thinking_message.edit(content=thinking_message_content)

    response_tokens = enc.encode(full_response)
    sky_credits = 0
    pricing = model_pricing.get(model)
    if pricing:
        sky_credits = calculate_credit_price(model, len(prompt_tokens), len(response_tokens))
        cursor.execute("UPDATE users SET credits = credits - ? WHERE clientid = ?", (sky_credits, user_id))
        connection.commit()

    return full_response, sky_credits


async def send_thinking_message(message):
    return await message.channel.send("Let me think for a moment... (this may take a while)", reference=message)


async def delete_thinking_message(wait_message):
    await wait_message.delete()


async def send_response(message, response):

    # Filter out mentions
    response = response.replace(f"@everyone", "@ everyone")
    response = response.replace(f"@here", "@ here")
    ping_regex = re.compile(r"<@!?[0-9]+>")

    # Find all user mentions and replace them with obfuscated text
    def replace_mention(match):
        mention = match.group(0)
        if mention.startswith("<"):
            return "**@**user"
        else:
            return mention

    response = ping_regex.sub(replace_mention, response)

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
            reference = await message.channel.send(response, reference=reference)
    else:
        await message.channel.send(response, reference=message)


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

    direct_mentioned = "<@646411900267135004>" in message.content  # Make sure you add ! for direct mentions
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
    sky_credits, _ = await get_user_credits(message.author.id)
    response_text, sky_credits = await generate_text(context=context,
                                                     thinking_message=thinking_message,
                                                     user_id=message.author.id,
                                                     max_credits=sky_credits)
    if not response_text:
        response_text = "I don't know what to say."
    await send_response(message, response_text)
    await delete_thinking_message(thinking_message)


@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")


if __name__ == '__main__':
    try:
        cogs = [p.stem for p in Path('./cogs').glob('**/*.py') if not p.name.startswith('__')]
        print('Loading \x1b[31m%d\x1b[0m extensions...' % len(cogs))

        for cog in cogs:
            bot.load_extension(f'cogs.{cog}')
            print('Loaded \x1b[31m%s\x1b[0m' % cog)

        bot.run(os.getenv("BOT_TOKEN"))
    except KeyboardInterrupt:
        print("Shutting down...")
        connection.commit()
        connection.close()
        print("Goodbye!")
        exit(0)
