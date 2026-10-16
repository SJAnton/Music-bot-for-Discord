import pytest
from conftest import assert_function_and_response


@pytest.mark.simcord(strict_sync=False)
async def test_play_not_in_voice_channel(simcord_env):
    await assert_function_and_response(
        simcord_env, "play", "DISCONNECTED_WARNING", query="test"
    )


@pytest.mark.simcord(strict_sync=False)
async def test_playing_while_not_playing(simcord_env):
    await assert_function_and_response(simcord_env, "playing", "NOT_PLAYING_WARNING")


@pytest.mark.simcord(strict_sync=False)
async def test_skip_while_not_playing(simcord_env):
    await assert_function_and_response(simcord_env, "skip", "NOT_PLAYING_WARNING")


@pytest.mark.simcord(strict_sync=False)
async def test_pause_while_not_playing(simcord_env):
    await assert_function_and_response(simcord_env, "pause", "NOT_PLAYING_WARNING")


@pytest.mark.simcord(strict_sync=False)
async def test_resume_while_not_playing(simcord_env):
    await assert_function_and_response(simcord_env, "resume", "NOT_PLAYING_WARNING")


@pytest.mark.simcord(strict_sync=False)
async def test_volume_while_not_playing(simcord_env):
    await assert_function_and_response(
        simcord_env, "volume", "NOT_PLAYING_WARNING", vol=100
    )


@pytest.mark.simcord(strict_sync=False)
async def test_leave_while_not_playing(simcord_env):
    await assert_function_and_response(simcord_env, "leave", "NOT_PLAYING_WARNING")


@pytest.mark.simcord(strict_sync=False)
async def test_empty_queue(simcord_env):
    await assert_function_and_response(simcord_env, "queue", "EMPTY_QUEUE_WARNING")
