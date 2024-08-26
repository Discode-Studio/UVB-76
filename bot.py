import discord
from discord.ext import commands
import os
import asyncio
import aiohttp

# Configuration du bot Discord
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Variables globales
long_beep_file = 'long_beep.wav'  # Fichier long beep à jouer au démarrage
uvb_stream_url = 'http://streams.printf.cc:8000/buzzer.ogg'  # URL du stream UVB-76
check_interval_seconds = 10  # Intervalle entre chaque vérification des salons vocaux

# Fonction pour jouer un fichier audio un certain nombre de fois
async def play_audio_repeatedly(vc, file, repeat_count, interval_seconds=2):
    for _ in range(repeat_count):
        if not vc.is_playing():
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(file))
            vc.play(source)
            while vc.is_playing():
                await asyncio.sleep(1)
        await asyncio.sleep(interval_seconds)

# Fonction pour vérifier si le stream UVB-76 est disponible
async def check_uvb_stream_available():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(uvb_stream_url) as response:
                return response.status == 200
    except aiohttp.ClientError:
        return False

# Fonction pour jouer le stream UVB-76
async def play_uvb_stream(vc):
    if not vc.is_playing():
        stream_source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(uvb_stream_url))
        vc.play(stream_source)
    else:
        print("Stream already playing.")

# Fonction pour vérifier et se connecter aux salons vocaux
async def check_and_connect_to_voice_channels():
    for guild in bot.guilds:
        voice_channel = discord.utils.get(guild.voice_channels, name="General")
        vc = discord.utils.get(bot.voice_clients, guild=guild)

        if voice_channel:
            if vc is None or not vc.is_connected():
                try:
                    vc = await voice_channel.connect()
                    print(f"Connected to voice channel in guild: {guild.name}")

                    # Jouer le long beep 5 fois au démarrage
                    await play_audio_repeatedly(vc, long_beep_file, repeat_count=5)

                    # Vérifier la disponibilité du stream UVB-76
                    stream_available = await check_uvb_stream_available()

                    if stream_available:
                        await play_uvb_stream(vc)

                    # Attendre avant de passer au prochain serveur
                    await asyncio.sleep(check_interval_seconds)
                except Exception as e:
                    print(f"Failed to connect to voice channel in guild: {guild.name}, error: {e}")
        else:
            # Créer un salon vocal nommé "General" s'il n'existe pas
            try:
                await guild.create_voice_channel(name="General")
                print(f"Created voice channel 'General' in guild: {guild.name}")
            except Exception as e:
                print(f"Failed to create voice channel in guild: {guild.name}, error: {e}")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

    await check_and_connect_to_voice_channels()

    while True:
        await asyncio.sleep(check_interval_seconds)  # Vérifie toutes les 10 secondes

        for guild in bot.guilds:
            voice_channel = discord.utils.get(guild.voice_channels, name="General")
            vc = discord.utils.get(bot.voice_clients, guild=guild)

            if voice_channel:
                if vc is None or not vc.is_connected():
                    try:
                        vc = await voice_channel.connect()
                        print(f"Connected to voice channel in guild: {guild.name}")

                        await play_audio_repeatedly(vc, long_beep_file, repeat_count=5)

                        stream_available = await check_uvb_stream_available()

                        if stream_available:
                            await play_uvb_stream(vc)

                        await asyncio.sleep(check_interval_seconds)
                    except Exception as e:
                        print(f"Failed to connect to voice channel in guild: {guild.name}, error: {e}")
                else:
                    # Si le bot est déjà connecté, assurez-vous que le stream UVB-76 est joué
                    stream_available = await check_uvb_stream_available()
                    if stream_available:
                        if not vc.is_playing():
                            await play_uvb_stream(vc)
            else:
                # Créer un salon vocal nommé "General" s'il n'existe pas
                try:
                    await guild.create_voice_channel(name="General")
                    print(f"Created voice channel 'General' in guild: {guild.name}")
                except Exception as e:
                    print(f"Failed to create voice channel in guild: {guild.name}, error: {e}")

# Le token est récupéré depuis une variable d'environnement
bot.run(os.getenv('DISCORD_BOT_TOKEN'))
