import os
import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import tempfile
import subprocess

TOKEN = os.getenv('DISCORD_BOT_TOKEN')  # Ton token Discord
VOICE_CHANNEL_ID = 123456789012345678   # ID du salon vocal
YOUTUBE_URL = 'https://www.youtube.com/live/8h_D2P0iqMk?si=UAAJO0ghOHijDBSE'  # URL du live YouTube
COOKIES_FILE = 'cookies.txt'  # Chemin vers le fichier cookies

# Initialiser le bot Discord
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f'Bot connecté comme {bot.user}')
    voice_channel = bot.get_channel(VOICE_CHANNEL_ID)
    if voice_channel is not None:
        vc = await voice_channel.connect()

        # Télécharger le flux audio en utilisant yt-dlp avec cookies
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'outtmpl': '-',
            'cookies': COOKIES_FILE,  # Utiliser les cookies pour l'authentification
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(YOUTUBE_URL, download=False)
            url = info['formats'][0]['url']

        # Créer un fichier temporaire pour stocker l'audio
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            tmp_file.close()
            # Télécharger l'audio depuis l'URL
            ffmpeg_command = [
                'ffmpeg', '-i', url, '-f', 'wav', tmp_file.name
            ]
            subprocess.run(ffmpeg_command, check=True)

            # Lire l'audio du fichier temporaire
            vc.play(discord.FFmpegPCMAudio(tmp_file.name))

        print(f"Diffusion en cours sur {voice_channel.name}")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

bot.run(TOKEN)
