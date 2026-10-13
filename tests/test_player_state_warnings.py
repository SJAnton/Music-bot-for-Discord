import pytest
from conftest import assert_function_from_voice_channel_and_response


@pytest.mark.simcord(strict_sync=False)
async def test_pause_when_already_paused(simcord_env):
    await assert_function_from_voice_channel_and_response(
        simcord_env, "pause", "ALREADY_PAUSED_WARNING", is_playing=True, is_paused=True
    )


@pytest.mark.simcord(strict_sync=False)
async def test_resume_when_playing(simcord_env):
    await assert_function_from_voice_channel_and_response(
        simcord_env, "resume", "NOT_PAUSED_WARNING", is_playing=True, is_paused=False
    )


@pytest.mark.simcord(strict_sync=False)
async def test_volume_less_than_zero(simcord_env):
    await assert_function_from_voice_channel_and_response(
        simcord_env, "volume", "VOLUME_NUMBER_WARNING", is_playing=True, is_paused=False, vol=-100
    )


@pytest.mark.simcord(strict_sync=False)
async def test_volume_over_a_hundred(simcord_env):
    await assert_function_from_voice_channel_and_response(
        simcord_env, "volume", "VOLUME_NUMBER_WARNING", is_playing=True, is_paused=False, vol=200
    )


@pytest.mark.simcord(strict_sync=False)
async def test_move_to_same_channel(simcord_env):
    await assert_function_from_voice_channel_and_response(
        simcord_env, "move", "SAME_VOICE_CHANNEL_WARNING", is_playing=True, is_paused=False
    )
