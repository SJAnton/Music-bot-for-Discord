from discord import Embed
from .formatting import display_queue, get_duration

def common_embed(title: str, description: str | None = None):
    return Embed(title=title, description=description)

def play_embed(messages, track):
    duration = get_duration(track)
    thumbnail = track["thumbnail"]
    webpage_url = track["webpage_url"]
    song_title = track.get("title", "Untitled")

    embed = Embed(title=messages["NOW_PLAYING_MESSAGE"])
    embed.add_field(name=song_title, value=f"[{messages['REDIRECTION_MESSAGE']}]({webpage_url})")
    embed.add_field(name=messages["DURATION_MESSAGE"], value=duration)
    embed.set_image(url=thumbnail)
    return embed

def playlist_embed(messages, results, amount_playable):
    title = results.get("title", "Untitled")
    webpage_url = results["webpage_url"]
    embed = Embed(
        title=f"{messages['ADDED_PLAYLIST_MESSAGE']}",
        description=title
    )
    embed.add_field(
        name=f"{messages['SONGS_NUMBER_MESSAGE']} {amount_playable}",
        value=f"[{messages['REDIRECTION_MESSAGE']}]({webpage_url})"
    )
    return embed

def queue_embed(queue, first, last, init_msg):
    return Embed(title=init_msg, description=display_queue(queue, first, last))
