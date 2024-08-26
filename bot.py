import discord
from discord.ext import commands, tasks
import os
import random
import asyncio

# Configuration du bot Discord
intents = discord.Intents.default()
intents.message_content = True  # Activer l'intention pour les messages

bot = commands.Bot(command_prefix='!', intents=intents)

vc = None  # Variable pour stocker le canal vocal
current_beep = None  # Garder la trace du son actuel joué

# Liste des fichiers de beep
beeps = ['beep1.wav', 'beep2.wav', 'beep3.wav']

# Fonction pour jouer un beep aléatoire
async def play_random_beep():
    global vc, current_beep
    if vc and not vc.is_playing():
        beep_file = random.choice(beeps)
        current_beep = beep_file
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(beep_file))
        vc.play(source)
        print(f"Playing {beep_file}")
    elif vc and vc.is_playing():
        print("Audio is still playing, waiting for it to finish.")

# Tâche pour changer de beep toutes les 5 minutes
@tasks.loop(minutes=5)
async def change_beep():
    await play_random_beep()

# Event on_ready pour afficher que le bot est prêt et rejoindre le canal vocal automatiquement
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    
    # Rejoindre le salon vocal automatiquement
    guild = discord.utils.get(bot.guilds)
    global vc
    voice_channel = discord.utils.get(guild.voice_channels, name="3")  # Remplacez par le nom correct du salon vocal
    if voice_channel:
        vc = await voice_channel.connect()

    # Jouer un premier beep aléatoire et démarrer la tâche de changement
    await play_random_beep()
    change_beep.start()

# Le token est récupéré depuis une variable d'environnement
bot.run(os.getenv('DISCORD_BOT_TOKEN'))
