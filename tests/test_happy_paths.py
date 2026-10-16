import pytest
from conftest import setup_playing_scenario, get_embedded_title, get_message, QUEUE_EXAMPLE
from unittest.mock import patch, AsyncMock


@pytest.mark.simcord(strict_sync=False)
async def test_jumpto_right_position(simcord_env):
    ctx = await setup_playing_scenario(simcord_env)

    result = await ctx.user.slash(ctx.channel, "jumpto", pos=3)

    assert result.acknowledged
    assert not result.ephemeral
    assert get_embedded_title(result) == get_message(simcord_env.bot, "SKIPPED_SONG_MESSAGE")


@pytest.mark.simcord(strict_sync=False)
async def test_qadd_right_position(simcord_env):
    ctx = await setup_playing_scenario(simcord_env)

    fake_result = {"entries": [{"title": "Fake Song", "url": "http://fake.com"}]}
    with patch("src.cogs.music.search_ytdlp_async", new=AsyncMock(return_value=fake_result)):
        result = await ctx.user.slash(ctx.channel, "qadd", pos=3, query="test")

    expected = f"{get_message(simcord_env.bot, 'QUEUE_POSITION_MESSAGE')} 3: Fake Song"
    assert result.acknowledged
    assert not result.ephemeral
    assert get_embedded_title(result) == expected


@pytest.mark.simcord(strict_sync=False)
async def test_search_and_play(simcord_env):
    ctx = await setup_playing_scenario(simcord_env)

    fake_result = {"entries": [{"title": "Fake Song", "url": "http://fake.com"}]}
    with patch("src.cogs.music.search_ytdlp_async", new=AsyncMock(return_value=fake_result)):
        result = await ctx.user.slash(ctx.channel, "play", query="test")

    assert result.acknowledged
    assert not result.ephemeral
    assert get_embedded_title(result) == get_message(simcord_env.bot, "ADDED_SONG_MESSAGE")


@pytest.mark.simcord(strict_sync=False)
async def test_skip_while_playing(simcord_env):
    ctx = await setup_playing_scenario(simcord_env)

    fake_result = {
        "webpage_url": "http://fakeplaylist.com",
        "entries": [
            {"title": "Fake Song", "url": "http://fake.com"},
            {"title": "Fake Song 2", "url": "http://fake2.com"},
        ]
    }
    with patch("src.cogs.music.search_ytdlp_async", new=AsyncMock(return_value=fake_result)):
        await ctx.user.slash(ctx.channel, "play", query="test")
        result = await ctx.user.slash(ctx.channel, "skip")

    assert result.acknowledged
    assert not result.ephemeral
    assert get_embedded_title(result) == get_message(simcord_env.bot, "SKIPPED_SONG_MESSAGE")


@pytest.mark.simcord(strict_sync=False)
async def test_show_song_being_played(simcord_env):
    ctx = await setup_playing_scenario(simcord_env)

    music_cog = simcord_env.bot.get_cog("Music")
    music_cog.guild_song_playing[ctx.user.guild.id] = {
        "title": "Fake Song",
        "thumbnail": "https://song.com/thumbnail.jpg",
        "webpage_url": "https://song.com",
        "duration": 180,
    }
    result = await ctx.user.slash(ctx.channel, "playing")

    assert result.acknowledged
    assert not result.ephemeral
    assert get_embedded_title(result) == get_message(simcord_env.bot, "NOW_PLAYING_MESSAGE")


@pytest.mark.simcord(strict_sync=False)
async def test_move_to_another_channel(simcord_env):
    guild = simcord_env.create_guild()
    channel = guild.create_text_channel("general")

    music_cog = simcord_env.bot.get_cog("Music")
    music_cog.guild_songs[guild.id] = QUEUE_EXAMPLE.copy()

    voice_channel_a = guild.create_voice_channel("General Voice A")
    voice_channel_b = guild.create_voice_channel("General Voice B")
    real_voice_channel = simcord_env.bot.get_channel(voice_channel_a.id)

    with patch("discord.VoiceClient.connect", new=AsyncMock()):
        await real_voice_channel.connect()

    real_guild = simcord_env.bot.get_guild(guild.id)
    real_guild.voice_client.is_playing = lambda: True

    user = guild.add_member(simcord_env.create_user("user"))
    await user.join_voice(voice_channel_b)

    with patch.object(real_guild.voice_client, "move_to", new=AsyncMock()):
        result = await user.slash(channel, "move")

    expected = f"{get_message(simcord_env.bot, "MOVED_MESSAGE")} General Voice B"
    assert result.acknowledged
    assert not result.ephemeral
    assert get_embedded_title(result) == expected


@pytest.mark.simcord(strict_sync=False)
async def test_leave_while_playing(simcord_env):
    ctx = await setup_playing_scenario(simcord_env)

    result = await ctx.user.slash(ctx.channel, "leave")

    assert result.acknowledged
    assert not result.ephemeral
    assert get_embedded_title(result) == get_message(simcord_env.bot, "DISCONNECTED_MESSAGE")


@pytest.mark.simcord(strict_sync=False)
async def test_two_guilds_dont_share_queue(simcord_env):
    guild_a = simcord_env.create_guild()
    guild_b = simcord_env.create_guild()

    music_cog = simcord_env.bot.get_cog("Music")
    music_cog.guild_songs[guild_a.id] = [{"title": "Song A"}]
    music_cog.guild_songs[guild_b.id] = []

    assert len(music_cog.guild_songs[guild_a.id]) == 1
    assert len(music_cog.guild_songs[guild_b.id]) == 0
