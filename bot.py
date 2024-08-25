import os
import discord
from discord.ext import commands
import asyncio
import subprocess

TOKEN = os.getenv('DISCORD_BOT_TOKEN')  # Ton token Discord
VOICE_CHANNEL_ID = 1248150853295149191   # Remplace par l'ID de ton salon vocal
YOUTUBE_URL = 'https://www.youtube.com/live/8h_D2P0iqMk?si=UAAJO0ghOHijDBSE'  # URL du live YouTube

# Initialiser le bot Discord
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f'Bot connecté comme {bot.user}')
    voice_channel = bot.get_channel(VOICE_CHANNEL_ID)
    if voice_channel is not None:
        vc = await voice_channel.connect()

        # Commande pour utiliser yt-dlp et récupérer l'audio du live YouTube
        command = [
            'yt-dlp', '-f', 'bestaudio', '-o', '-', YOUTUBE_URL,
            '|', 'ffmpeg', '-i', 'pipe:0', '-f', 's16le', '-ar', '48000', '-ac', '2', 'pipe:1'
        ]
        
        # Démarre la commande yt-dlp avec subprocess
        process = subprocess.Popen(' '.join(command), stdout=subprocess.PIPE, shell=True)

        # Diffuser l'audio capturé en continu
        vc.play(discord.FFmpegPCMAudio(process.stdout))

        print(f"Diffusion en cours sur {voice_channel.name}")

# Commande pour arrêter le bot
@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

# Lancer le bot Discord
bot.run(TOKEN)
