from datetime import datetime
from discord.ext import commands
from utils.formatting import reply
from zoneinfo import ZoneInfo

TIME_DESCRIPTION = "Returns the current date and hour."

class Misc(commands.Cog):
    def __init__(self, bot, config, messages):
        self.bot = bot
        self.config = config
        self.messages = messages

    @commands.hybrid_command(name="time", description=TIME_DESCRIPTION)
    async def time(self, ctx: commands.Context):
        data = datetime.now(tz=ZoneInfo(self.config["TIMEZONE"]))
        hour = data.strftime(self.config["TIME_FORMAT"])
        await reply(
            ctx.interaction,
            f"{self.messages['CURRENT_DATE_MESSAGE']} {data.day}/{data.month}/{data.year}. {self.messages['CURRENT_HOUR_MESSAGE']} {hour}."
        )
