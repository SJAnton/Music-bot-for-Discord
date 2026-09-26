import asyncio
import discord
import yt_dlp

DEFAULT_TITLE = "Untitled"
DELETED_TITLE = "[Deleted video]"
PRIVATE_TITLE = "[Private video]"

ffmpeg_options = {
    "before_options" : "-nostdin -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options" : "-vn -ar 48000 -ac 2 -f s16le",
    "executable" : "ffmpeg"
}

# Checks if a song is private or has been deleted.
def is_playable(track):
    title = track.get("title", DEFAULT_TITLE)
    return title not in (DELETED_TITLE, PRIVATE_TITLE)

# Searches for the video and extracts its audio information.
# Uses download=False as we want this information to be streamed instead of downloaded.
def _extract(query, yt_dlp_opts):
    with yt_dlp.YoutubeDL(yt_dlp_opts) as ydl:
        return ydl.extract_info(query, download=False)

# Runs the search function on a separate thread from the current loop.
async def search_ytdlp_async(query, yt_dlp_opts):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda : _extract(query, yt_dlp_opts))

# Makes the bot leave the voice channel automatically after a specific time has passed.
async def automatic_leave(voice_client, time_limit):
    try:
        counter = 0
        while counter < time_limit and not voice_client.is_playing() and not voice_client.is_paused():
            counter += 1
            await asyncio.sleep(1)
        if not voice_client.is_playing() and not voice_client.is_paused():
            await voice_client.disconnect()
    except asyncio.CancelledError:
        return

# Returns the audio source of the track.
async def get_source(track, volume):
    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(track["url"], **ffmpeg_options), volume=volume)
    source.read() # Fixes the fast playing at the beginning
    return source
