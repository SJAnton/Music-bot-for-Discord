import pytest
from conftest import (
    QUEUE_EXAMPLE,
    assert_function_with_queue_and_response,
    get_embedded_title,
    get_message,
)


@pytest.mark.simcord(strict_sync=False)
async def test_jumpto_zero(simcord_env):
    await assert_function_with_queue_and_response(
        simcord_env, "jumpto", "INVALID_POSITION_ERROR", QUEUE_EXAMPLE, pos=0
    )


@pytest.mark.simcord(strict_sync=False)
async def test_jumpto_negative(simcord_env):
    await assert_function_with_queue_and_response(
        simcord_env, "jumpto", "INVALID_POSITION_ERROR", QUEUE_EXAMPLE, pos=-1
    )


@pytest.mark.simcord(strict_sync=False)
async def test_jumpto_over_queue_length(simcord_env):
    await assert_function_with_queue_and_response(
        simcord_env,
        "jumpto",
        "INVALID_POSITION_ERROR",
        QUEUE_EXAMPLE,
        pos=len(QUEUE_EXAMPLE) + 1,
    )


@pytest.mark.simcord(strict_sync=False)
async def test_qadd_zero(simcord_env):
    await assert_function_with_queue_and_response(
        simcord_env,
        "qadd",
        "INVALID_POSITION_ERROR",
        QUEUE_EXAMPLE,
        query="test",
        pos=0,
    )


@pytest.mark.simcord(strict_sync=False)
async def test_qadd_negative(simcord_env):
    await assert_function_with_queue_and_response(
        simcord_env,
        "qadd",
        "INVALID_POSITION_ERROR",
        QUEUE_EXAMPLE,
        query="test",
        pos=-1,
    )


@pytest.mark.simcord(strict_sync=False)
async def test_qadd_over_queue_length(simcord_env):
    await assert_function_with_queue_and_response(
        simcord_env,
        "qadd",
        "INVALID_POSITION_ERROR",
        QUEUE_EXAMPLE,
        query="test",
        pos=len(QUEUE_EXAMPLE) + 1,
    )


@pytest.mark.simcord(strict_sync=False)
async def test_clear_queue(simcord_env):
    guild = simcord_env.create_guild()
    channel = guild.create_text_channel("general")

    music_cog = simcord_env.bot.get_cog("Music")
    music_cog.guild_songs[guild.id] = QUEUE_EXAMPLE.copy()

    user = guild.add_member(simcord_env.create_user("user"))

    result = await user.slash(channel, "clear")

    assert result.acknowledged
    assert not result.ephemeral
    assert get_embedded_title(result) == get_message(
        simcord_env.bot, "EMPTIED_QUEUE_MESSAGE"
    )
