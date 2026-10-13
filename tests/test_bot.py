async def test_ready_without_discord(simcord_env):
    guild = simcord_env.create_guild()

    assert simcord_env.bot.is_ready()
    assert simcord_env.bot.get_guild(guild.id) is not None


async def test_bot_initializes(simcord_env):
    assert simcord_env.bot.is_ready()
    assert simcord_env.bot.user is not None
