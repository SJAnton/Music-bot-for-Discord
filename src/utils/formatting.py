import discord
from datetime import timedelta

def display_queue(queue, first, last):
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
