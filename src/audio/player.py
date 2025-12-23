import asyncio
import discord
import yt_dlp
from utils.embed import play_embed

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

# Checks if a song is private or has been deleted.
def is_playable(track):
    title = track.get("title", "Untitled")
    return title != "[Private video]" and title != "[Deleted video]"

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
async def play_next(
        voice_client,
        guild_id,
        channel,
        guild_songs,
        guild_song_playing,
        messages,
        volume,
        bot_loop
    ):
    if guild_id not in guild_songs or not guild_songs[guild_id]:
        # All the songs in the queue have been played.
        guild_song_playing[guild_id] = None
        return
    try:
        flat_track = guild_songs[guild_id].pop(0)
        track = await search_ytdlp_async(flat_track["url"], yt_dlp_options)

        def play_after(error):
            if error:
                print(f"{messages['SKIP_ERROR']}\n {track.get("title", "Untitled")}.")
            asyncio.run_coroutine_threadsafe(
                play_next(
                    voice_client,
                    guild_id,
                    channel,
                    guild_songs,
                    guild_song_playing,
                    messages,
                    volume,
                    bot_loop
                ),
                bot_loop
            )

        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(track["url"], **ffmpeg_options), volume=volume)
        source.read() # Fixes the fast playing at the beginning
        voice_client.play(source, after=play_after)
        guild_song_playing[guild_id] = track
        asyncio.create_task(channel.send(embed=play_embed(messages, track)))
    except Exception as e:
        print(f"{messages['PLAY_ERROR']}\n {e}")
        asyncio.create_task(
            play_next(
                voice_client,
                guild_id,
                channel,
                guild_songs,
                guild_song_playing,
                messages,
                volume,
                bot_loop
            ))
