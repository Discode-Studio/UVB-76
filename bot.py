import discord
from discord.ext import commands
import os
import asyncio
import requests

# Configuration du bot Discord
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Variables globales
beep_file = 'http://streams.printf.cc:8000/buzzer.ogg'  # Le fichier beep à jouer en boucle
beep_interval_seconds = 2  # Intervalle entre chaque beep
uvb_stream_url = 'http://streams.printf.cc:8000/buzzer.ogg'  # URL du stream UVB-76
beep3_file = 'beep3.wav'  # Le fichier beep3 à jouer en cas d'erreur 404

# Fonction pour jouer un fichier audio un certain nombre de fois
async def play_audio_repeatedly(vc, file, repeat_count, interval_seconds=2):
    for _ in range(repeat_count):
        if not vc.is_playing():  # Vérifie si aucun autre son n'est joué
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(file))
            vc.play(source)
            while vc.is_playing():
                await asyncio.sleep(1)  # Attendre que le son soit joué en entier
        await asyncio.sleep(interval_seconds)  # Attendre entre chaque répétition

# Fonction pour jouer le beep en boucle
async def play_beep_in_loop(vc):
    while True:
        if not vc.is_playing():  # Jouer le beep uniquement si aucun autre son n'est en cours
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(beep_file))
            vc.play(source)
        await asyncio.sleep(beep_interval_seconds)  # Attendre 2 secondes entre chaque beep

# Fonction pour jouer le beep3 en boucle
async def play_beep3_in_loop(vc):
    while True:
        if not vc.is_playing():  # Jouer le beep3 uniquement si aucun autre son n'est en cours
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(beep3_file))
            vc.play(source)
        await asyncio.sleep(2)  # Attendre 2 secondes entre chaque beep3

# Fonction pour vérifier si le stream UVB-76 est disponible
async def check_uvb_stream_available():
    try:
        response = requests.head(uvb_stream_url)
        # Vérifie si la réponse est un code de succès HTTP
        return response.status_code == 200
    except requests.RequestException:
        return False

# Fonction pour jouer le stream UVB-76
async def play_uvb_stream(vc):
    if not vc.is_playing():
        # Lecture du flux audio en direct à partir du lien
        stream_source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(uvb_stream_url))
        vc.play(stream_source)
    else:
        print("Stream already playing.")

# Fonction pour vérifier les salons et se connecter
async def check_and_connect_to_voice_channels():
    for guild in bot.guilds:
        voice_channel = discord.utils.get(guild.voice_channels, name="General")
        if voice_channel:
            if not any(vc.channel == voice_channel for vc in bot.voice_clients):
                await voice_channel.connect()

# Event on_ready pour afficher que le bot est prêt et rejoindre le canal vocal automatiquement
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    
    # Vérifie et connecte aux salons vocaux disponibles
    await check_and_connect_to_voice_channels()

    # Obtenir le premier canal vocal disponible
    if bot.voice_clients:
        vc = bot.voice_clients[0]

        # Jouer le long beep 5 fois au démarrage
        await play_audio_repeatedly(vc, 'long_beep.wav', repeat_count=5)

        # Vérifier la disponibilité du stream UVB-76 et jouer le beep3 si 404
        while True:
            stream_available = await check_uvb_stream_available()
            if stream_available:
                # Démarrer la diffusion UVB-76 en continu
                await play_uvb_stream(vc)
            else:
                # Démarrer la boucle pour jouer beep3.wav toutes les 2 secondes
                bot.loop.create_task(play_beep3_in_loop(vc))
            await asyncio.sleep(10)  # Vérifie toutes les 10 secondes

# Le token est récupéré depuis une variable d'environnement
bot.run(os.getenv('DISCORD_BOT_TOKEN'))
