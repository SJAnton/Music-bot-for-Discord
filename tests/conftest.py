import discord
import pytest
from src.bot import Bot
from src.utils.json_loader import load_config_file, load_messages_file
from simcord import ChannelHandle, MemberActor
from typing import NamedTuple
from unittest.mock import patch, AsyncMock

CONFIG = load_config_file()
MESSAGES = load_messages_file(CONFIG["LANGUAGE"])

QUEUE_EXAMPLE = [
    {"title": "song_1"},
    {"title": "song_2"},
    {"title": "song_3"},
    {"title": "song_4"},
    {"title": "song_5"},
]


class VoiceTestContext(NamedTuple):
    channel: ChannelHandle
    user: MemberActor


@pytest.fixture
def simcord_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    return Bot(CONFIG, MESSAGES, command_prefix='!', intents=intents)


def get_message(bot, message):
    return bot.messages[message]


def get_embedded_title(result):
    if result.response:
        return result.response.embeds[0].title
    return result.followups[0].embeds[0].title


def get_embedded_description(result):
    if result.response:
        return result.response.embeds[0].description
    return result.followups[0].embeds[0].description


async def assert_function_and_response(env, command, message, **kwargs):
    guild = env.create_guild()
    channel = guild.create_text_channel("general")
    user = guild.add_member(env.create_user("user"))

    result = await user.slash(channel, command, **kwargs)
    
    assert result.acknowledged
    assert result.ephemeral
    assert get_embedded_title(result) == get_message(env.bot, message)


async def assert_function_from_voice_channel_and_response(
    env, command, message, is_playing, is_paused, **kwargs
):
    guild = env.create_guild()
    channel = guild.create_text_channel("general")
    voice_channel = guild.create_voice_channel("General Voice")

    real_voice_channel = env.bot.get_channel(voice_channel.id)

    with patch("discord.VoiceClient.connect", new=AsyncMock()):
        await real_voice_channel.connect()

    real_guild = env.bot.get_guild(guild.id)
    real_guild.voice_client.is_playing = lambda: is_playing
    real_guild.voice_client.is_paused = lambda: is_paused

    user = guild.add_member(env.create_user("user"))
    await user.join_voice(voice_channel)

    result = await user.slash(channel, command, **kwargs)

    assert result.acknowledged
    assert result.ephemeral
    assert get_embedded_title(result) == get_message(env.bot, message)


async def assert_function_from_another_voice_channel_and_response(env, command, message, **kwargs):
    guild = env.create_guild()
    channel = guild.create_text_channel("general")
    voice_channel_a = guild.create_voice_channel("General Voice A")
    voice_channel_b = guild.create_voice_channel("General Voice B")

    real_voice_channel_a = env.bot.get_channel(voice_channel_a.id)

    with patch("discord.VoiceClient.connect", new=AsyncMock()):
        await real_voice_channel_a.connect()

    real_guild = env.bot.get_guild(guild.id)
    real_guild.voice_client.is_playing = lambda: True

    user = guild.add_member(env.create_user("user"))
    await user.join_voice(voice_channel_b)

    result = await user.slash(channel, command, **kwargs)

    assert result.acknowledged
    assert result.ephemeral
    assert get_embedded_title(result) == get_message(env.bot, message)


async def assert_function_with_queue_and_response(env, command, message, queue, **kwargs):
    guild = env.create_guild()
    channel = guild.create_text_channel("general")

    music_cog = env.bot.get_cog("Music")
    music_cog.guild_songs[guild.id] = queue.copy()

    user = guild.add_member(env.create_user("user"))

    result = await user.slash(channel, command, **kwargs)

    assert result.acknowledged
    assert result.ephemeral
    assert get_embedded_title(result) == get_message(env.bot, message)


async def setup_playing_scenario(simcord_env) -> VoiceTestContext:
    guild = simcord_env.create_guild()
    channel = guild.create_text_channel("general")

    music_cog = simcord_env.bot.get_cog("Music")
    music_cog.guild_songs[guild.id] = QUEUE_EXAMPLE.copy()

    voice_channel = guild.create_voice_channel("General Voice")
    real_voice_channel = simcord_env.bot.get_channel(voice_channel.id)

    with patch("discord.VoiceClient.connect", new=AsyncMock()):
        await real_voice_channel.connect()

    real_guild = simcord_env.bot.get_guild(guild.id)
    real_guild.voice_client.is_playing = lambda: True

    user = guild.add_member(simcord_env.create_user("user"))
    await user.join_voice(voice_channel)

    return VoiceTestContext(channel, user)
