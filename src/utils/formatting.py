from datetime import timedelta

def display_queue(queue, first, last, init_msg):
    if last > len(queue):
        last = len(queue)
    message = init_msg + '\n'
    num = first + 1
    for i in range(first, last):
        track = queue[i]
        message += f"{num}. "
        message += track.get("title", "Untitled") + '\n'
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

async def reply(interaction, message, eph=False):
    return await interaction.response.send_message(message, ephemeral=eph)

async def reply_with_view(interaction, message, view):
    return await interaction.response.send_message(message, view=view)
