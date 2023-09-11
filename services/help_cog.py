from discord.ext import commands

CHANEL_NAME = 'music-bot'


class help_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.help_message = """
            ```
            General commands:
            /play <song name / url> - searches and plays a song
            /queue - Displays the current music queue
            /skip - Skips the current song being played
            /clear - Stops the music and clears the queue
            /leave - Disconnects the bot from the voice channel
            /pause - Pauses the current song being played
            /resume - Resumes playing the current song
            /help - Displays all the available commands
            ```
            """
        self.text_channel_list = []

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                self.text_channel_list.append(channel)

        await self.send_to_specific_channel(self.help_message, CHANEL_NAME)

    @commands.command(name="help", help="Displays all the available commands")
    async def help(self, ctx):
        await ctx.send(self.help_message)

    async def send_to_all(self, msg):
        for text_channel in self.text_channel_list:
            await text_channel.send(msg)

    async def send_to_specific_channel(self, msg, channel_name):
        for text_channel in self.text_channel_list:
            if text_channel.name == channel_name:
                await text_channel.send(msg)
