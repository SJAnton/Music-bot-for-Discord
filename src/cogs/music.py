import discord
import yt_dlp
from audio.player import is_playable, play_next, search_ytdlp_async, yt_dlp_options
from discord.ext import commands
from utils.embed import *
from utils.formatting import *
from utils.view import *

PLAY_DESCRIPTION = "Plays a song or adds it to the queue."
PLAYING_DESCRIPTION = "Returns the name of the song that is being played."
SKIP_DESCRIPTION = "Skips to the next song of the queue."
PAUSE_DESCRIPTION = "Pauses the player."
RESUME_DESCRIPTION = "Resumes the player."
QUEUE_DESCRIPTION = "Displays the contents of the queue."
CLEAR_DESCRIPTION = "Clears the queue."
VOLUME_DESCRIPTION = "Changes the volume of the player (between 0 and 100)."
MOVE_DESCRIPTION = "Moves the player to the requester's current voice channel."
LEAVE_DESCRIPTION = "Clears the queue and leaves the voice channel."

class Music(commands.Cog):
    def __init__(self, bot, config, messages):
        self.bot = bot
        self.config = config
        self.messages = messages

        self.guild_songs = {}
        self.guild_song_playing = {}
        
    @commands.hybrid_command(name="play", description=PLAY_DESCRIPTION)
    async def play(self, ctx: commands.Context, *, query: str):
        user_voice = ctx.interaction.user.voice
        voice_client = ctx.interaction.guild.voice_client
        if not user_voice:
            return await reply(
                interaction=ctx.interaction,
                embed=common_embed(title=self.messages["DISCONNECTED_WARNING"]),
                eph=True
            )
        elif voice_client and user_voice.channel != voice_client.channel:
            return await reply(
                interaction=ctx.interaction,
                embed=common_embed(title=self.messages["NOT_IN_SAME_CHANNEL_WARNING"]),
                eph=True
            )
        elif not voice_client:
            voice_client = await user_voice.channel.connect()    
    
        await ctx.interaction.response.defer()
        fwup = ctx.interaction.followup
        search_query = query if "youtube.com" in query else self.config["SEARCH_RESULT"] + ' ' + query
        try:
            results = await search_ytdlp_async(search_query, yt_dlp_options)
        except yt_dlp.DownloadError as e:
            return await fwup.send(embed=common_embed(title=f"{self.messages['DOWNLOAD_ERROR']}\n {e}"))

        flat_tracks = results.get("entries", [])
        guild_id = ctx.interaction.guild.id
        if not flat_tracks:
            return await fwup.send(embed=common_embed(title=self.messages["NO_RESULTS_WARNING"]))
        elif len(flat_tracks) == 1:
            self.guild_songs.setdefault(guild_id, []).append(flat_tracks[0])
            await fwup.send(
                embed=common_embed(
                    title=self.messages['ADDED_SONG_MESSAGE'],
                    description=flat_tracks[0].get('title', 'Untitled')
                )
            )
        else:
            playable_tracks = [t for t in flat_tracks if is_playable(t)]
            self.guild_songs.setdefault(guild_id, []).extend(playable_tracks)
            await fwup.send(
                embed=common_embed(
                    title=f"{self.messages['ADDED_PLAYLIST_MESSAGE']} {results.get('title', 'Untitled')}",
                    description=f"{self.messages['SONGS_NUMBER_MESSAGE']} {len(playable_tracks)}"
                )
            )

        if not voice_client.is_playing() and not voice_client.is_paused():
            return await play_next(
                voice_client,
                guild_id,
                ctx.interaction.channel,
                self.guild_songs,
                self.guild_song_playing,
                self.messages,
                self.config["VOLUME"],
                self.bot.loop
            )

    @commands.hybrid_command(name="playing", description=PLAYING_DESCRIPTION)
    async def playing(self, ctx: commands.Context):
        track = self.guild_song_playing.get(ctx.interaction.guild_id, None)
        if not track:
            return await reply(
                interaction=ctx.interaction,
                embed=common_embed(title=self.messages["NOT_PLAYING_WARNING"]),
                eph=True
            )
        await reply(interaction=ctx.interaction, embed=play_embed(self.messages, track))

    @commands.hybrid_command(name="skip", description=SKIP_DESCRIPTION)
    async def skip(self, ctx: commands.Context):
        user_voice = ctx.interaction.user.voice
        voice_client = ctx.interaction.guild.voice_client
        if not voice_client or not voice_client.is_playing():
            return await reply(
                interaction=ctx.interaction,
                embed=common_embed(title=self.messages["NOT_PLAYING_WARNING"]),
                eph=True
            )
        elif not await is_right_channel(ctx.interaction, self.messages, user_voice, voice_client):
            return
        voice_client.stop()
        await reply(
            interaction=ctx.interaction,
            embed=common_embed(
                title=self.messages["SKIPPED_SONG_MESSAGE"],
                description=get_song_title(ctx.interaction, self.guild_song_playing)
            )
        )

    @commands.hybrid_command(name="pause", description=PAUSE_DESCRIPTION)
    async def pause(self, ctx: commands.Context):
        user_voice = ctx.interaction.user.voice
        voice_client = ctx.interaction.guild.voice_client
        if not voice_client or not voice_client.is_playing():
            return await reply(
                interaction=ctx.interaction,
                embed=common_embed(title=self.messages["NOT_PLAYING_WARNING"]),
                eph=True
            )
        elif voice_client.is_paused():
            return await reply(
                interaction=ctx.interaction,
                embed=common_embed(title=self.messages["ALREADY_PAUSED_WARNING"]),
                eph=True
            )
        elif not await is_right_channel(ctx.interaction, self.messages, user_voice, voice_client):
            return
        voice_client.pause()
        await reply(
            interaction=ctx.interaction,
            embed=common_embed(
                title=self.messages["PAUSED_SONG_MESSAGE"],
                description=get_song_title(ctx.interaction, self.guild_song_playing)
            )
        )

    @commands.hybrid_command(name="resume", description=RESUME_DESCRIPTION)
    async def resume(self, ctx: commands.Context):
        user_voice = ctx.interaction.user.voice
        voice_client = ctx.interaction.guild.voice_client
        if not voice_client:
            return await reply(
                interaction=ctx.interaction,
                embed=common_embed(title=self.messages["NOT_PLAYING_WARNING"]),
                eph=True
            )
        elif voice_client.is_playing() and not voice_client.is_paused():
            return await reply(
                interaction=ctx.interaction,
                embed=common_embed(title=self.messages["NOT_PAUSED_WARNING"]),
                eph=True
            )
        elif not await is_right_channel(ctx.interaction, self.messages, user_voice, voice_client):
            return
        voice_client.resume()
        await reply(
            interaction=ctx.interaction,
            embed=common_embed(
                title=self.messages["RESUMED_SONG_MESSAGE"],
                description=get_song_title(ctx.interaction, self.guild_song_playing)
            )
        )

    @commands.hybrid_command(name="queue", description=QUEUE_DESCRIPTION)
    async def queue(self, ctx: commands.Context):
        guild_id = ctx.interaction.guild_id
        if guild_id not in self.guild_songs or not self.guild_songs[guild_id]:
            return await reply(
                interaction=ctx.interaction,
                embed=common_embed(title=self.messages["EMPTY_QUEUE_WARNING"]),
                eph=True
            )
        init_msg = self.messages["SONGS_IN_QUEUE_MESSAGE"]
        jump = self.config["QUEUE_DISPLAY_SIZE"]
        queue = self.guild_songs.get(guild_id, [])
        await reply(
            interaction=ctx.interaction,
            embed=queue_embed(queue, 0, jump, init_msg),
            view=QueueView(queue, jump, init_msg)
        )

    @commands.hybrid_command(name="clear", description=CLEAR_DESCRIPTION)
    async def clear(self, ctx: commands.Context):
        queue = self.guild_songs.get(ctx.interaction.guild_id, [])
        n_items = len(queue)
        queue.clear()
        await reply(
            interaction=ctx.interaction,
            embed=common_embed(
                title=self.messages["EMPTIED_QUEUE_MESSAGE"],
                description=f"{self.messages['CLEARED_ITEMS_MESSAGE']} {n_items}"
            )
        )

    @commands.hybrid_command(name="volume", description=VOLUME_DESCRIPTION)
    async def volume(self, ctx: commands.Context, *, vol: int):
        if vol < 0 or vol > 100:
            return await reply(
                interaction=ctx.interaction,
                embed=common_embed(title=self.messages["VOLUME_NUMBER_WARNING"]),
                eph=True
            )
        user_voice = ctx.interaction.user.voice
        voice_client = ctx.interaction.guild.voice_client
        if not voice_client or not voice_client.is_playing():
            return await reply(
                interaction=ctx.interaction,
                embed=common_embed(title=self.messages["NOT_PLAYING_WARNING"]),
                eph=True
            )
        elif not await is_right_channel(ctx.interaction, self.messages, user_voice, voice_client):
            return
        elif isinstance(voice_client.source, discord.PCMVolumeTransformer):
            voice_client.source.volume = vol / 100
            await reply(
                interaction=ctx.interaction,
                embed=common_embed(title=f"{self.messages['VOLUME_CHANGE_MESSAGE']} {vol}")
            )

    @commands.hybrid_command(name="move", description=MOVE_DESCRIPTION)
    async def move(self, ctx: commands.Context):
        user_voice = ctx.interaction.user.voice
        voice_client = ctx.interaction.guild.voice_client
        if not voice_client:
            return await reply(
                interaction=ctx.interaction,
                embed=common_embed(title=self.messages["NOT_PLAYING_WARNING"]),
                eph=True
            )
        elif not await is_right_channel(ctx.interaction, self.messages, user_voice, voice_client):
            return
        await voice_client.move_to(user_voice.channel)
        await reply(
            interaction=ctx.interaction,
            embed=common_embed(title=f"{self.messages['MOVED_MESSAGE']} {user_voice.channel.name}")
        )

    @commands.hybrid_command(name="leave", description=LEAVE_DESCRIPTION)
    async def leave(self, ctx: commands.Context):
        guild_id = ctx.interaction.guild_id
        user_voice = ctx.interaction.user.voice
        voice_client = ctx.interaction.guild.voice_client
        if not voice_client:
            return await reply(
                interaction=ctx.interaction,
                embed=common_embed(title=self.messages["NOT_PLAYING_WARNING"]),
                eph=True
            )
        elif not await is_right_channel(ctx.interaction, self.messages, user_voice, voice_client):
            return
        elif voice_client.is_playing():
            voice_client.stop()
        self.guild_song_playing[guild_id] = None
        self.guild_songs.get(guild_id, []).clear()
        await voice_client.disconnect()
        await reply(interaction=ctx.interaction, embed=common_embed(title=self.messages["DISCONNECTED_MESSAGE"]))
