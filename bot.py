import discord
from discord.ext import commands
import os
import asyncio
import aiohttp  # Nouvelle bibliothèque pour vérifier le stream asynchrone

# Configuration du bot Discord
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Variables globales
beep_file = 'http://streams.printf.cc:8000/buzzer.ogg'  # Le fichier beep à jouer en boucle
beep_interval_seconds = 2  # Intervalle entre chaque beep
uvb_stream_url = 'http://streams.printf.cc:8000/buzzer.ogg'  # URL du stream UVB-76
beep3_file = 'beep3.wav'  # Le fichier beep3 à jouer en cas d'erreur 404
is_beep3_playing = False  # Variable pour suivre si beep3 est en cours de lecture
is_stream_playing = False  # Variable pour suivre si le stream UVB-76 est en cours de lecture
stream_task = None  # Stocker la tâche de surveillance du stream

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
    global is_beep3_playing
    is_beep3_playing = True  # Indiquer que beep3 est en cours de lecture
    while is_beep3_playing:
        if not vc.is_playing():  # Jouer le beep3 uniquement si aucun autre son n'est en cours
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(beep3_file))
            vc.play(source)
        await asyncio.sleep(2)  # Attendre 2 secondes entre chaque beep3

# Fonction pour arrêter beep3 si le flux revient
def stop_beep3():
    global is_beep3_playing
    is_beep3_playing = False  # Arrêter la lecture de beep3

# Fonction pour vérifier si le stream UVB-76 est disponible avec aiohttp
async def check_uvb_stream_available():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(uvb_stream_url) as response:
                # Vérifie si la réponse est un code de succès HTTP
                return response.status == 200
    except aiohttp.ClientError:
        return False

# Fonction pour jouer le stream UVB-76
async def play_uvb_stream(vc):
    global is_stream_playing
    if not is_stream_playing:  # Ne jouer le stream que s'il n'est pas déjà en lecture
        is_stream_playing = True  # Indiquer que le stream est en cours de lecture
        stream_source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(uvb_stream_url))
        vc.play(stream_source, after=lambda e: set_stream_playing(False))
    else:
        print("Stream already playing.")

# Fonction pour remettre à False quand le stream s'arrête
def set_stream_playing(value):
    global is_stream_playing
    is_stream_playing = value

# Fonction pour vérifier les salons et se connecter
async def check_and_connect_to_voice_channels():
    for guild in bot.guilds:
        voice_channel = discord.utils.get(guild.voice_channels, name="General")
        if voice_channel:
            if not any(vc.channel == voice_channel for vc in bot.voice_clients):
                await voice_channel.connect()

# Fonction principale pour surveiller la disponibilité du flux
async def monitor_uvb_stream(vc):
    global stream_task
    while True:
        stream_available = await check_uvb_stream_available()
        if stream_available:
            stop_beep3()  # Arrêter beep3 si le stream est disponible
            if not vc.is_playing():  # Ne jouer le stream que s'il n'est pas déjà joué
                await play_uvb_stream(vc)
        else:
            if not is_beep3_playing:  # Ne démarrer beep3 que s'il ne joue pas déjà
                bot.loop.create_task(play_beep3_in_loop(vc))
        await asyncio.sleep(10)  # Vérifier toutes les 10 secondes

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

        # Démarrer la tâche de surveillance du stream UVB-76
        global stream_task
        if not stream_task:
            stream_task = bot.loop.create_task(monitor_uvb_stream(vc))

# Le token est récupéré depuis une variable d'environnement
bot.run(os.getenv('DISCORD_BOT_TOKEN'))
