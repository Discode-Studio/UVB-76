import discord
from discord.ext import commands
import os
import asyncio

# Configuration du bot Discord
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Variables globales
uvb_stream_url = 'http://streams.printf.cc:8000/buzzer.ogg'  # URL du stream UVB-76

# Fonction pour jouer le stream UVB-76
async def play_uvb_stream(vc):
    if not vc.is_playing():
        stream_source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(uvb_stream_url))
        vc.play(stream_source)
    else:
        print("Stream already playing.")

# Event on_ready pour afficher que le bot est prêt et rejoindre le canal vocal automatiquement
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

    # Parcourir tous les serveurs auxquels le bot est connecté
    for guild in bot.guilds:
        # Vérifier si un salon vocal "UVB-76" existe
        voice_channel = discord.utils.get(guild.voice_channels, name="UVB-76")
        
        if voice_channel:
            # Si déjà connecté, déconnecter d'abord
            if guild.voice_client and guild.voice_client.is_connected():
                await guild.voice_client.disconnect()

            # Connecter le bot au salon vocal
            vc = await voice_channel.connect()

            # Attendre 10 secondes avant de diffuser
            await asyncio.sleep(10)
            await play_uvb_stream(vc)
        else:
            # Créer le canal "UVB-76" s'il n'existe pas
            voice_channel = await guild.create_voice_channel("UVB-76")
            vc = await voice_channel.connect()

            # Attendre 10 secondes avant de diffuser
            await asyncio.sleep(10)
            await play_uvb_stream(vc)

    # Vérifier toutes les 10 secondes si de nouveaux serveurs ont un canal "UVB-76"
    while True:
        await asyncio.sleep(10)
        for guild in bot.guilds:
            voice_channel = discord.utils.get(guild.voice_channels, name="UVB-76")

            if not voice_channel:
                # Si un canal vocal "UVB-76" n'existe pas, le créer
                voice_channel = await guild.create_voice_channel("UVB-76")
                vc = await voice_channel.connect()
                
                # Attendre 10 secondes avant de diffuser
                await asyncio.sleep(10)
                await play_uvb_stream(vc)
            else:
                # Se reconnecter si déconnecté
                if not guild.voice_client or not guild.voice_client.is_connected():
                    vc = await voice_channel.connect()

                    # Attendre 10 secondes avant de diffuser
                    await asyncio.sleep(10)
                    await play_uvb_stream(vc)

# Le token est récupéré depuis une variable d'environnement
bot.run(os.getenv('DISCORD_BOT_TOKEN'))
