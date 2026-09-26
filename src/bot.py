from discord.ext import commands
from .cogs.misc import Misc
from .cogs.music import Music

class Bot(commands.Bot):
    def __init__(self, config, messages, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.messages = messages

    async def setup_hook(self):
        await self.add_cog(Misc(self, self.config, self.messages))
        await self.add_cog(Music(self, self.config, self.messages))

    async def on_ready(self):
        #await bot.tree.sync()
        print(f"{self.messages['BOT_LOGGED_IN_MESSAGE']} {self.user}.")
