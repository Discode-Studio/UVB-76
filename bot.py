import discord
from discord.ext import commands
import subprocess
import os

TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # Utilisation du secret GitHub pour le token

# Configurer le bot Discord
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} est connecté à Discord!')
    
    # Connexion au salon vocal
    voice_channel = discord.utils.get(bot.get_all_channels(), name='Général')  # Remplace par le nom de ton salon vocal
    if voice_channel is None:
        print("Salon vocal non trouvé.")
        return
    
    vc = await voice_channel.connect()
    
    # URL du flux audio WebSDR
    stream_url = "http://websdr.78dx.ru:8901/"  # Remplace par l'URL correcte du flux audio si nécessaire

    # Utiliser FFmpeg pour lire le flux audio dans Discord
    process = subprocess.Popen(
        ["ffmpeg", "-i", stream_url, "-f", "s16le", "-ar", "48000", "-ac", "2", "pipe:1"],
        stdout=subprocess.PIPE
    )
    
    # Jouer l'audio dans Discord
    vc.play(discord.FFmpegPCMAudio(process.stdout))
    
    # Optionnel : ajouter un message pour confirmer que l'audio est joué
    await voice_channel.send("Je joue maintenant le flux audio du WebSDR.")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
    else:
        await ctx.send("Je ne suis pas connecté à un salon vocal.")

bot.run(TOKEN)
