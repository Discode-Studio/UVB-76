import discord
from discord.ext import commands
import os
import asyncio
import aiohttp

# Configuration du bot Discord
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True  # Ajouter l'intention pour les guilds (serveurs)

bot = commands.Bot(command_prefix='!', intents=intents)

# Variables globales
beep_file = 'http://streams.printf.cc:8000/buzzer.ogg'  # Le fichier beep à jouer en boucle
beep_interval_seconds = 2  # Intervalle entre chaque beep
uvb_stream_url = 'http://streams.printf.cc:8000/buzzer.ogg'  # URL du stream UVB-76
beep3_file = 'beep3.wav'  # Le fichier beep3 à jouer en cas d'erreur 404
is_beep3_playing = {}  # Dictionnaire pour suivre l'état de beep3 par serveur
is_stream_playing = {}  # Dictionnaire pour suivre si le stream est en cours de lecture par serveur
stream_tasks = {}  # Dictionnaire pour stocker les tâches de surveillance du stream par serveur

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
async def play_beep3_in_loop(vc, guild_id):
    global is_beep3_playing
    is_beep3_playing[guild_id] = True  # Indiquer que beep3 est en cours de lecture pour ce serveur
    while is_beep3_playing[guild_id]:
        if not vc.is_playing():  # Jouer le beep3 uniquement si aucun autre son n'est en cours
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(beep3_file))
            vc.play(source)
        await asyncio.sleep(2)  # Attendre 2 secondes entre chaque beep3

# Fonction pour arrêter beep3 si le flux revient
def stop_beep3(guild_id):
    global is_beep3_playing
    is_beep3_playing[guild_id] = False  # Arrêter la lecture de beep3 pour ce serveur

# Fonction pour vérifier si le stream UVB-76 est disponible et si l'erreur est 404
async def check_uvb_stream_404():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(uvb_stream_url) as response:
                # Vérifie si la réponse est exactement une 404 (Not Found)
                return response.status == 404
    except aiohttp.ClientError:
        return False

# Fonction pour jouer le stream UVB-76
async def play_uvb_stream(vc, guild_id):
    global is_stream_playing
    if not is_stream_playing.get(guild_id):  # Ne jouer le stream que s'il n'est pas déjà en lecture pour ce serveur
        is_stream_playing[guild_id] = True  # Indiquer que le stream est en cours de lecture pour ce serveur
        stream_source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(uvb_stream_url))
        vc.play(stream_source, after=lambda e: set_stream_playing(guild_id, False))
    else:
        print(f"Stream already playing for guild {guild_id}.")

# Fonction pour remettre à False quand le stream s'arrête pour un serveur
def set_stream_playing(guild_id, value):
    global is_stream_playing
    is_stream_playing[guild_id] = value

# Fonction pour vérifier les salons et se connecter
async def check_and_connect_to_voice_channels():
    for guild in bot.guilds:
        voice_channel = discord.utils.get(guild.voice_channels, name="General")
        if voice_channel:
            if not any(vc.channel == voice_channel for vc in bot.voice_clients):
                await voice_channel.connect()
        else:
            # Si aucun canal vocal "General" n'existe, le créer
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(connect=True, speak=True)
            }
            general_channel = await guild.create_voice_channel('General', overwrites=overwrites)
            await general_channel.connect()

# Fonction principale pour surveiller la disponibilité du flux pour chaque serveur
async def monitor_uvb_stream(vc, guild_id):
    global stream_tasks
    while True:
        uvb_is_404 = await check_uvb_stream_404()
        if not uvb_is_404:
            stop_beep3(guild_id)  # Arrêter beep3 si le stream n'est pas en 404
            if not vc.is_playing():  # Ne jouer le stream que s'il n'est pas déjà joué
                await play_uvb_stream(vc, guild_id)
        else:
            if not is_beep3_playing.get(guild_id):  # Ne démarrer beep3 que s'il ne joue pas déjà pour ce serveur
                bot.loop.create_task(play_beep3_in_loop(vc, guild_id))
        await asyncio.sleep(10)  # Vérifier toutes les 10 secondes

# Event on_ready pour afficher que le bot est prêt et rejoindre les salons vocaux automatiquement
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    
    # Vérifie et connecte aux salons vocaux disponibles
    await check_and_connect_to_voice_channels()

    # Pour chaque serveur, connecter au salon "General" et surveiller le stream
    for guild in bot.guilds:
        voice_channel = discord.utils.get(guild.voice_channels, name="General")
        if voice_channel:
            vc = await voice_channel.connect()

            # Jouer le long beep 5 fois au démarrage
            await play_audio_repeatedly(vc, 'long_beep.wav', repeat_count=5)

            # Démarrer la tâche de surveillance du stream UVB-76 pour chaque serveur
            global stream_tasks
            if guild.id not in stream_tasks:
                stream_tasks[guild.id] = bot.loop.create_task(monitor_uvb_stream(vc, guild.id))

# Le token est récupéré depuis une variable d'environnement
bot.run(os.getenv('DISCORD_BOT_TOKEN'))
