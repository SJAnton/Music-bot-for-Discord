import pytest
from conftest import assert_function_from_another_voice_channel_and_response


@pytest.mark.simcord(strict_sync=False)
async def test_play_from_another_voice_channel(simcord_env):
    await assert_function_from_another_voice_channel_and_response(
        simcord_env, "play", "NOT_IN_SAME_CHANNEL_WARNING", query="test"
    )


@pytest.mark.simcord(strict_sync=False)
async def test_skip_from_another_voice_channel(simcord_env):
    await assert_function_from_another_voice_channel_and_response(
        simcord_env, "skip", "NOT_IN_SAME_CHANNEL_WARNING"
    )


@pytest.mark.simcord(strict_sync=False)
async def test_pause_from_another_voice_channel(simcord_env):
    await assert_function_from_another_voice_channel_and_response(
        simcord_env, "pause", "NOT_IN_SAME_CHANNEL_WARNING"
    )


@pytest.mark.simcord(strict_sync=False)
async def test_resume_from_another_voice_channel(simcord_env):
    await assert_function_from_another_voice_channel_and_response(
        simcord_env, "resume", "NOT_IN_SAME_CHANNEL_WARNING"
    )


@pytest.mark.simcord(strict_sync=False)
async def test_volume_from_another_voice_channel(simcord_env):
    await assert_function_from_another_voice_channel_and_response(
        simcord_env, "volume", "NOT_IN_SAME_CHANNEL_WARNING", vol=100
    )
