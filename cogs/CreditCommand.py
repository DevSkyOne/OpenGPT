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
        user = await get_user_data(user_id)
        print(user)

        renew_at = user.last_used + datetime.timedelta(days=1)

        await ctx.respond(f"You have {user.credits} credits left for today.\n"
                          f"They renew at <t:{round(renew_at.timestamp())}:R>\n\n"
                          f"Your current model is `{user.model}`", hidden=True)


def setup(bot):
    bot.add_cog(CreditCommand(bot))
