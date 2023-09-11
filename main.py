import os
import discord
from discord.ext import commands
import youtube_dl
import asyncio
from dotenv import load_dotenv, find_dotenv


MUSIC_CHANEL = 'music-bot'
HELP_MESSAGE = """
    ```
    General commands:
    /play <song name / url> - searches and plays a song
    /join - Joins the bot to the chanel
    /leave - Disconnects the bot from the voice channel
    /pause - Pauses the current song being played
    /resume - Resumes playing the current song
    /queue - Displays the current music queue
    /skip - Skips the current song being played
    /clear - Stops the music and clears the queue
    /help - Displays all the available commands
    ```
    """

# env config
load_dotenv(find_dotenv())

# bot config
intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='/', intents=intents)

# ytdl config
ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'extractor_retries': 'auto',
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
music_queue = []
is_playing = False


# object to manage songs fetching
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        filename = None
        try:
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
            if 'entries' in data:
                data = data['entries'][0]
            filename = data['title'] if stream else ytdl.prepare_filename(data)
        except Exception as e:
            print(e)
        return filename


# commands
@bot.command(name='play', help='To play song')
async def play(ctx, url):
    try:
        print('Song request: ' + url)
        voice_channel = ctx.author.voice.channel
        connection = await voice_channel.connect()
        async with ctx.typing():
            filename = await YTDLSource.from_url(url, loop=bot.loop)
            connection.play(discord.FFmpegPCMAudio(
                executable="ffmpeg", source=filename))
    except Exception as e:
        print(e)


@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()


@bot.command(name='pause', help='This command pauses the song')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.pause()
    else:
        await ctx.send("The bot is not playing anything at the moment.")


@bot.command(name='resume', help='Resumes the song')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        await voice_client.resume()
    else:
        await ctx.send("The bot was not playing anything before this. Use play_song command")


@bot.command(name='leave', help='To make the bot leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")


@bot.command(name='stop', help='Stops the song')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        await ctx.send("The bot is not playing anything at the moment.")


@bot.command(name='HELP', help='Help commands')
async def help(ctx):
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if str(channel) == MUSIC_CHANEL:
                await channel.send(HELP_MESSAGE)


# bot initiation
@bot.event
async def on_ready():
    print('Running!')
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if str(channel) == MUSIC_CHANEL:
                await channel.send('Bot Activated - Type /HELP for all commands.')
        print('Active in {}\n Member Count : {}'.format(
            guild.name, guild.member_count))

if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_BOT_TOKEN"))
