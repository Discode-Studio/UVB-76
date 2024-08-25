import discord
from discord.ext import commands
import subprocess
import tempfile
import os

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    voice_channel = discord.utils.get(bot.guilds[0].channels, name='3')
    if voice_channel:
        vc = await voice_channel.connect()

        url = 'http://websdr.78dx.ru:8901/'

        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            temp_file_path = temp_file.name
            print(f'Temporary file created at: {temp_file_path}')

        command = [
            'ffmpeg',
            '-i', url,
            '-f', 'wav',
            temp_file_path
        ]
        subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        vc.play(discord.FFmpegPCMAudio(temp_file_path))

# Le token est maintenant récupéré depuis une variable d'environnement
bot.run(os.getenv('DISCORD_BOT_TOKEN'))
