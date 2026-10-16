from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from conftest import get_embedded_description, get_embedded_title, get_message


@pytest.mark.simcord(strict_sync=False)
async def test_time_command(simcord_env):
    guild = simcord_env.create_guild()
    channel = guild.create_text_channel("general")
    user = guild.add_member(simcord_env.create_user("user"))

    result = await user.slash(channel, "time")

    config = simcord_env.bot.config
    now = datetime.now(tz=ZoneInfo(config["TIMEZONE"]))

    expected_hour = now.strftime(config["TIME_FORMAT"])
    expected_title = f"{get_message(simcord_env.bot, 'CURRENT_DATE_MESSAGE')} {now.day}/{now.month}/{now.year}"
    expected_description = (
        f"{get_message(simcord_env.bot, 'CURRENT_HOUR_MESSAGE')} {expected_hour}"
    )

    assert result.acknowledged
    assert not result.ephemeral
    assert get_embedded_title(result) == expected_title
    assert get_embedded_description(result) == expected_description
