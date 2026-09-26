# Music bot for Discord
Simple bot that plays audio from YouTube videos and playlists. Supports English and Spanish.

## Requirements

The only requirement to run this bot is [Docker](https://www.docker.com/get-started/). All dependencies are bundled inside the container.

## Setup

1. Obtain a Discord bot token by following [this guide](https://www.writebots.com/discord-bot-token/).
2. Create a `token.env` file in the project's root folder with `DISCORD_TOKEN=your_token_here`
3. Run `docker compose up --build` command to build the container's image.

### New commands

Any new commands written for the bot need to be synchronized by executing the bot.tree.sync() line inside the on_ready() function in the bot.py module. Otherwise the slash command will not show up when typing it.

### Configuration

The config.json file allows the user to switch between English (EN) and Spanish (ES), as well as setting the time zone, time format, which result from the search is to be loaded, and the volume.

### Custom messages

Every message can be customized via the messages.json file, as well as adding another language, which needs to have the same messages as the English and Spanish versions.

## Commands
| Command | Description |
|---------|-------------|
|/play | Plays the audio from a video, by searching or directly from a link. |
|/playing | Displays the song that is playing. |
|/skip | Skips to the next song in the queue. |
|/jumpto | Skips the song that is playing and jumps to a specific position of the queue. |
|/pause | Pauses the player. |
|/resume | Resumes the player. |
|/queue | Displays the contents of the queue. |
|/qadd | Inserts a video or playlist to a specific position of the queue. |
|/clear | Empties the queue. |
|/volume | Changes the volume of the player. |
|/move | Moves the bot to the current voice channel. |
|/leave | Disconnects the bot from the voice channel. |
|/time | Displays the current date and time. |