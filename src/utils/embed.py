from discord import Embed
from utils.formatting import display_queue, get_duration

def common_embed(title: str, description: str | None = None):
    return Embed(title=title, description=description)

def play_embed(messages, track):
    duration = get_duration(track)
    thumbnail = track["thumbnail"]
    webpage_url = track["webpage_url"]
    song_title = track.get("title", "Untitled")

    embed = Embed(title=messages["NOW_PLAYING_MESSAGE"])
    embed.add_field(name=song_title, value=f"[{messages['REDIRECTION_MESSAGE']}]({webpage_url})")
    embed.add_field(name=messages["DURATION"], value=duration)
    embed.set_image(url=thumbnail)
    return embed

def queue_embed(queue, first, last, init_msg):
    return Embed(title=init_msg, description=display_queue(queue, first, last, init_msg))
