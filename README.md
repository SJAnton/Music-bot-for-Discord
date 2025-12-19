# Music bot for Discord
Simple bot that plays audio from YouTube videos and playlists. Supports English and Spanish.

## Dependencies

[discord.py](https://pypi.org/project/discord.py/): API wrapper for Discord.

[Deno](https://docs.deno.com/runtime/getting_started/installation/): JavaScript runtime required by yt-dlp.

[FFmpeg](https://www.ffmpeg.org/download.html): required for audio processing.

[PyNaCl](https://pypi.org/project/PyNaCl/): Python binding to the Networking and Cryptography (NaCl) library.

[tzdata](https://pypi.org/project/tzdata/): package required to display the current date and time.

[yt-dlp](https://pypi.org/project/yt-dlp/): YouTube audio/video downloader.

## Setup

The token needed for the bot to work can be obtained following [this guide](https://www.writebots.com/discord-bot-token/), then it has to be inserted in the config.json file.

FFmpeg needs to be added to the server's PATH variable, which can be done following [this guide](https://phoenixnap.com/kb/ffmpeg-windows).

The config.json file also allows the user to change between English (EN) and Spanish (ES), as well as setting the time zone, time format, which result from the search is to be loaded, and the volume.

### New commands

Any new commands written for the bot need to be synchronized by executing the bot.tree.sync() line inside the on_ready() function. Otherwise the slash command will not show up when typing it.

### Custom messages

Every message can be customized via the messages.json file, as well as adding another language, which needs to have the same messages as the English and Spanish versions.

## Commands
| Command | Description |
|---------|-------------|
|/play | Plays the audio from a video, by searching or directly from a link. |
|/playing | Displays the song that is playing. |
|/skip | Skips to the next song in the queue. |
|/pause | Pauses the player. |
|/resume | Resumes the player. |
|/queue | Displays the contents of the queue. |
|/clear | Empties the queue. |
|/volume | Changes the volume of the player. |
|/move | Moves the bot to the current voice channel. |
|/leave | Disconnects the bot from the voice channel. |
|/time | Displays the current date and time. |