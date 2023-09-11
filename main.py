import os
import dotenv
import discord
import asyncio
from discord.ext import commands
# from services.help_cog import help_cog
from services.music_cog import music_cog

dotenv.load_dotenv()


async def load_commands(bot):
    # await bot.add_cog(help_cog(bot))
    await bot.add_cog(music_cog(bot))

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)

asyncio.run(load_commands(bot))

bot.run(os.getenv("DISCORD_BOT_TOKEN"))
