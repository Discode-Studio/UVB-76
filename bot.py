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

    for guild in bot.guilds:
        # Vérifier les permissions du bot dans le serveur
        me = guild.me
        guild_perms = guild.me.guild_permissions

        # Vérifier si le bot peut gérer les salons et se connecter
        if not (guild_perms.manage_channels and guild_perms.connect and guild_perms.speak):
            print(f"Skipping {guild.name}: missing permissions.")
            continue

        voice_channel = discord.utils.get(guild.voice_channels, name="UVB-76")
        
        if voice_channel:
            perms = voice_channel.permissions_for(me)
            if not (perms.connect and perms.speak):
                print(f"Skipping {guild.name}: missing connect/speak in {voice_channel.name}.")
                continue

            if guild.voice_client and guild.voice_client.is_connected():
                await guild.voice_client.disconnect()

            vc = await voice_channel.connect()
            await asyncio.sleep(10)
            await play_uvb_stream(vc)
        else:
            # Vérifier si le bot peut créer un salon
            if not guild_perms.manage_channels:
                print(f"Skipping {guild.name}: cannot create channels.")
                continue
            voice_channel = await guild.create_voice_channel("UVB-76")
            vc = await voice_channel.connect()
            await asyncio.sleep(10)
            await play_uvb_stream(vc)

    while True:
        await asyncio.sleep(10)
        for guild in bot.guilds:
            me = guild.me
            guild_perms = guild.me.guild_permissions
            if not (guild_perms.manage_channels and guild_perms.connect and guild_perms.speak):
                continue

            voice_channel = discord.utils.get(guild.voice_channels, name="UVB-76")
            if not voice_channel:
                if not guild_perms.manage_channels:
                    continue
                voice_channel = await guild.create_voice_channel("UVB-76")
                vc = await voice_channel.connect()
                await asyncio.sleep(10)
                await play_uvb_stream(vc)
            else:
                perms = voice_channel.permissions_for(me)
                if not (perms.connect and perms.speak):
                    continue
                if not guild.voice_client or not guild.voice_client.is_connected():
                    vc = await voice_channel.connect()
                    await asyncio.sleep(10)
                    await play_uvb_stream(vc)

# Le token est récupéré depuis une variable d'environnement
bot.run(os.getenv('DISCORD_BOT_TOKEN'))
