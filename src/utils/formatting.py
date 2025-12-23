import discord
from datetime import timedelta
from utils.embed import common_embed

def display_queue(queue, first, last, init_msg):
    if last > len(queue):
        last = len(queue)
    message = ""
    num = first + 1
    for i in range(first, last):
        track = queue[i]
        message += f"{num}. {track.get("title", "Untitled")}" + '\n'
        num += 1
    return message

def get_duration(track):
    if not track:
        return "??:??"
    secs = track.get("duration", -1)
    duration = str(timedelta(seconds=secs))
    if secs == -1:
        return "??:??"
    elif secs >= 3600:
        return duration
    _, m, s = duration.split(":")
    return f"{m}:{s}"

def get_song_title(interaction, guild_song_playing):
    track = guild_song_playing.get(interaction.guild_id, None)
    return track.get("title", "Untitled") if track else None

async def is_right_channel(interaction, messages, user_voice, voice_client):
    if not user_voice:
        await reply(
            interaction=interaction,
            embed=common_embed(title=messages["DISCONNECTED_WARNING"]),
            eph=True
        )
        return False
    elif user_voice.channel != voice_client.channel:
        await reply(
            interaction=interaction,
            embed=common_embed(title=messages["NOT_IN_SAME_CHANNEL_WARNING"]),
            eph=True
        )
        return False
    return True

async def reply(
        interaction,
        *,
        content: str | None = None,
        embed: discord.Embed | None = None,
        view: discord.ui.View = discord.utils.MISSING,
        eph = False
    ):
    return await interaction.response.send_message(
        content=content,
        embed=embed,
        view=view, 
        ephemeral=eph
    )
