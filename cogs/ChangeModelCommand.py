from discord import ApplicationCommandInteraction, SlashCommandOption, SlashCommandOptionChoice
from discord.ext import commands

from opengpt import get_user_data, set_user_model


class CreditCommand(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.slash_command(
        name="changemodel",
        description="Change your openai model",
        options=[
            SlashCommandOption(
                name='model',
                description='The openai model you want to use',
                option_type=str,
                required=True,
                choices=[
                    SlashCommandOptionChoice(
                        name='ChatGPT 3.5 Turbo',
                        value='gpt-3.5-turbo'
                    ),
                    SlashCommandOptionChoice(
                        name='ChatGPT 4 (beta)',
                        value='gpt-4'
                    )
                ]
            )
        ]

    )
    async def changemodel(self, ctx: ApplicationCommandInteraction, model: str):
        await set_user_model(str(ctx.author.id), model)
        await ctx.respond(f"Your model has been changed to `{model}`", hidden=True)


def setup(bot):
    bot.add_cog(CreditCommand(bot))
