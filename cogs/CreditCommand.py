import datetime

from discord import ApplicationCommandInteraction
from discord.ext import commands

from opengpt import get_user_data


class CreditCommand(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.slash_command(name="credits", description="Check your credits")
    async def credits(self, ctx: ApplicationCommandInteraction):
        user_id = str(ctx.author.id)
        sky_credits, model, last_used = await get_user_data(user_id)
        print(sky_credits, last_used)

        renew_at = last_used + datetime.timedelta(days=1)

        await ctx.respond(f"You have {sky_credits} credits left.\n"
                          f"They renew at <t:{round(renew_at.timestamp())}:R>\n\n"
                          f"Your current model is `{model}`", hidden=True)


def setup(bot):
    bot.add_cog(CreditCommand(bot))
