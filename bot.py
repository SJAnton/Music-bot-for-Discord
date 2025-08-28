import asyncio
import discord
import json
import yt_dlp
from datetime import datetime, timedelta
from discord.ext import commands
from zoneinfo import ZoneInfo

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

CONFIG = {}
MESSAGES = {}

current_songs = {}
songs_queues = {}

try:
    with open("config.json", "r", encoding="UTF-8") as config_file:
        CONFIG = json.load(config_file)
except Exception as e:
    print(f"Could not load config.json: {e}")
try:
    with open("messages.json", "r", encoding="UTF-8") as messages_file:
        all_messages = json.load(messages_file)
        MESSAGES = all_messages[CONFIG["LANGUAGE"]]
except Exception as e:
    print(f"Could not load messages.json: {e}")

ffmpeg_options = {
    "before_options" : "-nostdin -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options" : "-vn -ar 48000 -ac 2 -f s16le",
    "executable" : "ffmpeg"
}

yt_dlp_options = {
    "format" : "bestaudio/best",
    "skip_download" : True,
    "extract_flat" : True,
    "preferredcodec" : "opus",
    "youtube_include_dash_manifest" : False,
    "youtube_include_hls_manifest" : False,
}

async def reply(interaction, message, eph=False):
    return await interaction.response.send_message(message, ephemeral=eph)

def get_duration(track):
    secs = track.get("duration", -1)
    duration = str(timedelta(seconds=secs))
    if secs == -1:
        return "??:??"
    elif secs >= 3600:
        return duration
    _, m, s = duration.split(":")
    return f"{m}:{s}"

async def get_current_song(interaction):
    guild_id = interaction.guild_id
    track = current_songs.get(guild_id, None)
    voice_client = interaction.guild.voice_client
    if not voice_client or not track:
        return False
    return track

# Searches for the video and extracts its audio information.
# Uses download=False as we want this information to be streamed instead of downloaded.
def _extract(query, yt_dlp_opts):
    with yt_dlp.YoutubeDL(yt_dlp_opts) as ydl:
        return ydl.extract_info(query, download=False)

# Runs the search function on a separate thread from the current loop.
async def search_ytdlp_async(query, yt_dlp_opts):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda : _extract(query, yt_dlp_opts))

# Handles the playing of the next song in the queue.
async def play_next(voice_client, guild_id, channel):
    if guild_id not in songs_queues or not songs_queues[guild_id]:
        current_songs[guild_id] = None
        return
    flat_track = songs_queues[guild_id].pop(0)
    try:
        track = await search_ytdlp_async(flat_track["url"], yt_dlp_options)
        audio_url = track["url"]
        song_title = track.get("title", "Untitled")
        duration = get_duration(track)

        def play_after(error):
            if error:
                print(f"{MESSAGES['SKIP_ERROR']} {song_title}.")
            asyncio.run_coroutine_threadsafe(play_next(voice_client, guild_id, channel), bot.loop)

        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(audio_url, **ffmpeg_options), volume=CONFIG["VOLUME"])
        await asyncio.sleep(0.3) # fixes the speed up at the start
        voice_client.play(source, after=play_after)
        current_songs[guild_id] = track
        asyncio.create_task(channel.send(f"{MESSAGES['NOW_PLAYING_MESSAGE']} {song_title} [{duration}]"))
    except Exception as e:
        print(f"{MESSAGES['PLAY_ERROR']} {e}")
        asyncio.create_task(play_next(voice_client, guild_id, channel))

@bot.event
async def on_ready():
    #await bot.tree.sync()
    print(MESSAGES["BOT_LOGGED_IN_MESSAGE"] + f" {bot.user}.")

@bot.tree.command(name="play", description=MESSAGES["PLAY_DESCRIPTION"])
async def play(interaction: discord.Interaction, query: str):
    await interaction.response.defer()

    fwup = interaction.followup
    user_voice = interaction.user.voice
    voice_client = interaction.guild.voice_client
    if not user_voice:
        return await fwup.send(MESSAGES["DISCONNECTED_WARNING"])
    elif voice_client and user_voice.channel != voice_client.channel:
        return await fwup.send(MESSAGES["NOT_IN_SAME_CHANNEL_WARNING"])
    elif not voice_client:
        voice_client = await user_voice.channel.connect()
    
    search_query = query if "youtube.com" in query else CONFIG["SEARCH_RESULT"] + ' ' + query
    try:
        results = await search_ytdlp_async(search_query, yt_dlp_options)
    except yt_dlp.DownloadError as e:
        return await fwup.send(f"{MESSAGES['DOWNLOAD_ERROR']} {e}")

    flat_tracks = results.get("entries", [])
    guild_id = interaction.guild.id
    if not flat_tracks:
        return await fwup.send(MESSAGES["NO_RESULTS_WARNING"])
    elif len(flat_tracks) == 1:
        songs_queues.setdefault(guild_id, []).append(flat_tracks[0])
        await fwup.send(f"{MESSAGES['ADDED_SONG_MESSAGE']} {flat_tracks[0].get('title', 'Untitled')}")
    else:
        songs_queues.setdefault(guild_id, []).extend(flat_tracks)
        await fwup.send(
            f"{MESSAGES['ADDED_PLAYLIST_MESSAGE']} {results.get('title', 'Untitled')}. "
            f"{MESSAGES['SONGS_NUMBER_MESSAGE']} {len(flat_tracks)}."
        )

    if not voice_client.is_playing() and not voice_client.is_paused():
        return await play_next(voice_client, guild_id, interaction.channel)

@bot.tree.command(name="playing", description=MESSAGES["PLAYING_DESCRIPTION"])
async def playing(interaction: discord.Interaction):
    track = await get_current_song(interaction)
    if not track:
        await reply(interaction, MESSAGES["NOT_PLAYING_WARNING"], True)
    duration = get_duration(track)
    song_title = track.get("title", "Untitled")
    return await reply(interaction, f"{MESSAGES['NOW_PLAYING_MESSAGE']} {song_title} [{duration}]")

@bot.tree.command(name="skip", description=MESSAGES["SKIP_DESCRIPTION"])
async def skip(interaction: discord.Interaction):
    user_channel = interaction.user.voice.channel
    voice_client = interaction.guild.voice_client
    if not voice_client:
        return await reply(interaction, MESSAGES["DISCONNECTED_WARNING"], True)
    elif user_channel != voice_client.channel:
        return await reply(interaction, MESSAGES["NOT_IN_SAME_CHANNEL_WARNING"], True)
    elif not voice_client.is_playing():
        return await reply(interaction, MESSAGES["NOT_PLAYING_WARNING"], True)
    skipped_song = await get_current_song(interaction)
    voice_client.stop()
    await reply(interaction, f"{MESSAGES['SKIPPED_SONG_MESSAGE']} {skipped_song.get('title', 'Untitled')}.")

@bot.tree.command(name="pause", description=MESSAGES["PAUSE_DESCRIPTION"])
async def pause(interaction: discord.Interaction):
    user_channel = interaction.user.voice.channel
    voice_client = interaction.guild.voice_client
    if not voice_client or not voice_client.is_playing():
        return await reply(interaction, MESSAGES["NOT_PLAYING_WARNING"], True)
    elif user_channel != voice_client.channel:
        return await reply(interaction, MESSAGES["NOT_IN_SAME_CHANNEL_WARNING"], True)
    elif voice_client.is_paused():
        return await reply(interaction, MESSAGES["ALREADY_PAUSED_WARNING"], True)
    voice_client.pause()
    await reply(interaction, MESSAGES["PAUSED_SONG_MESSAGE"])

@bot.tree.command(name="resume", description=MESSAGES["RESUME_DESCRIPTION"])
async def resume(interaction: discord.Interaction):
    user_channel = interaction.user.voice.channel
    voice_client = interaction.guild.voice_client
    if not voice_client:
        return await reply(interaction, MESSAGES["NOT_PLAYING_WARNING"], True)
    elif user_channel != voice_client.channel:
        return await reply(interaction, MESSAGES["NOT_IN_SAME_CHANNEL_WARNING"], True)
    elif voice_client.is_playing() and not voice_client.is_paused():
        return await reply(interaction, MESSAGES["NOT_PAUSED_WARNING"], True)
    voice_client.resume()
    await reply(interaction, MESSAGES["RESUMED_SONG_MESSAGE"])

@bot.tree.command(name="queue", description=MESSAGES["QUEUE_DESCRIPTION"])
async def queue(interaction: discord.Interaction):
    guild_id = interaction.guild_id
    if guild_id not in songs_queues or not songs_queues[guild_id]:
        return await reply(interaction, MESSAGES["EMPTY_QUEUE_WARNING"], True)
    message = MESSAGES["SONGS_IN_QUEUE_MESSAGE"] + '\n'
    for track in songs_queues.get(guild_id, []):
        message += track.get("title", "Untitled") + '\n'
    await reply(interaction, message)

@bot.tree.command(name="clear", description=MESSAGES["CLEAR_DESCRIPTION"])
async def clear(interaction: discord.Interaction):
    guild_id = interaction.guild.id
    songs_queues.get(guild_id, []).clear()
    await reply(interaction, MESSAGES["EMPTY_QUEUE_MESSAGE"])

@bot.tree.command(name="volume", description=MESSAGES["VOLUME_DESCRIPTION"])
async def volume(interaction: discord.Interaction, vol : int):
    if vol < 0 or vol > 100:
        return await reply(interaction, MESSAGES["VOLUME_NUMBER_WARNING"], True)
    voice_client = interaction.guild.voice_client
    if not voice_client or not voice_client.is_playing():
        return await reply(interaction, MESSAGES["NOT_PLAYING_WARNING"], True)
    elif isinstance(voice_client.source, discord.PCMVolumeTransformer):
        voice_client.source.volume = vol/100
        await reply(interaction, f"{MESSAGES['VOLUME_CHANGE_MESSAGE']} {vol}.")

@bot.tree.command(name="move", description=MESSAGES["MOVE_DESCRIPTION"])
async def move(interaction: discord.Interaction):
    user_channel = interaction.user.voice.channel
    voice_client = interaction.guild.voice_client
    if not voice_client:
        return await reply(interaction, MESSAGES["NOT_PLAYING_WARNING"], True)
    elif user_channel == voice_client.channel:
        return await reply(interaction, MESSAGES["SAME_VOICE_CHANNEL_WARNING"], True)
    await voice_client.move_to(user_channel)
    await reply(interaction, f"{MESSAGES['MOVED_MESSAGE']} {user_channel.name}.")

@bot.tree.command(name="leave", description=MESSAGES["LEAVE_DESCRIPTION"])
async def leave(interaction: discord.Interaction):
    user_voice = interaction.user.voice
    voice_client = interaction.guild.voice_client
    if not voice_client:
        return await reply(interaction, MESSAGES["DISCONNECTED_WARNING"], True)
    elif user_voice and user_voice.channel != voice_client.channel:
        return await reply(interaction, MESSAGES["NOT_IN_SAME_CHANNEL_WARNING"], True)
    elif voice_client.is_playing():
        voice_client.stop()
    current_songs[interaction.guild_id] = None
    songs_queues.get(interaction.guild_id, []).clear()
    await voice_client.disconnect()
    await reply(interaction, MESSAGES["DISCONNECTED_MESSAGE"])

@bot.tree.command(name="time", description=MESSAGES["TIME_DESCRIPTION"])
async def time(interaction: discord.Interaction):
    data = datetime.now(tz=ZoneInfo(CONFIG["TIMEZONE"]))
    hour = data.strftime(CONFIG["TIME_FORMAT"])
    await reply(
        interaction, f"{MESSAGES['CURRENT_DATE_MESSAGE']} {data.day}/{data.month}/{data.year}. {MESSAGES['CURRENT_HOUR_MESSAGE']} {hour}."
    )

try:
    bot.run(CONFIG["TOKEN"])
finally:
    print(MESSAGES["BOT_DISCONNECTED_MESSAGE"])
