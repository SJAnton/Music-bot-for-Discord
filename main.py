import asyncio
import discord
import os
import signal
from src.bot import Bot
from src.utils.json_loader import load_config_file, load_messages_file

CONFIG = load_config_file()
MESSAGES = load_messages_file(CONFIG["LANGUAGE"])
DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
SIGNALS = (signal.SIGTERM, signal.SIGINT)

async def main(discord_token, bot):
    async with bot:
        loop = asyncio.get_running_loop()
        for sig in SIGNALS:
            loop.add_signal_handler(sig, lambda: asyncio.create_task(bot.close()))
        await bot.start(discord_token)

if DISCORD_TOKEN:
    intents = discord.Intents.default()
    intents.message_content = True
    bot = Bot(CONFIG, MESSAGES, command_prefix='!', intents=intents)
    try:
        asyncio.run(main(DISCORD_TOKEN, bot))
    finally:
        print(MESSAGES["BOT_DISCONNECTED_MESSAGE"])
else:
    print(MESSAGES["NO_TOKEN_ERROR"])
