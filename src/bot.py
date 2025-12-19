import discord
from discord.ext import commands
from cogs.misc import Misc
from cogs.music import Music
from utils.json_loader import load_config_file, load_messages_file

intents = discord.Intents.default()
intents.message_content = True

CONFIG = load_config_file()
MESSAGES = load_messages_file(CONFIG["LANGUAGE"])

class Bot(commands.Bot):
    async def setup_hook(self):
        await self.add_cog(Misc(bot, CONFIG, MESSAGES))
        await self.add_cog(Music(bot, CONFIG, MESSAGES))

bot = Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    #await bot.tree.sync()
    print(f"{MESSAGES['BOT_LOGGED_IN_MESSAGE']} {bot.user}.")
   
if CONFIG["TOKEN"]:
    try:
        bot.run(CONFIG["TOKEN"])
    finally:
        print(MESSAGES["BOT_DISCONNECTED_MESSAGE"])
else:
    print(MESSAGES["NO_TOKEN_ERROR"])
