import discord
from discord.ext import tasks, commands
import os
import random
import asyncio

# Configuration du bot Discord
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Variables globales
beeps = ['beep1.wav', 'beep2.wav', 'beep3.wav']  # Les fichiers audio des différents beeps
current_beep = None
beep_interval_seconds = 2  # Intervalle entre chaque beep

# Fonction pour jouer un fichier audio un certain nombre de fois
async def play_audio_repeatedly(vc, file, repeat_count, interval_seconds=2):
    for _ in range(repeat_count):
        if not vc.is_playing():  # Vérifie si aucun autre son n'est joué
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(file))
            vc.play(source)
            while vc.is_playing():
                await asyncio.sleep(1)  # Attendre que le son soit joué en entier
        await asyncio.sleep(interval_seconds)  # Attendre entre chaque répétition

# Fonction pour changer de beep toutes les 10 minutes
async def change_beep(vc):
    global current_beep
    while True:
        new_beep = random.choice(beeps)  # Choisir un beep aléatoire
        while new_beep == current_beep:  # S'assurer que le nouveau beep est différent
            new_beep = random.choice(beeps)

        current_beep = new_beep
        print(f"Changing beep to {current_beep}")

        # Jouer le long beep 3 fois avant de changer de tonalité
        await play_audio_repeatedly(vc, 'long_beep.wav', repeat_count=3)

        # Jouer le nouveau beep 3 fois
        await play_audio_repeatedly(vc, current_beep, repeat_count=3)

        # Attendre 10 minutes avant de changer de beep
        await asyncio.sleep(10 * 60)

# Event on_ready pour afficher que le bot est prêt et rejoindre le canal vocal automatiquement
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    
    # Rejoindre le salon vocal automatiquement
    guild = discord.utils.get(bot.guilds)
    voice_channel = discord.utils.get(guild.voice_channels, name="3")  # Nom du salon vocal
    vc = await voice_channel.connect()

    # Jouer le long beep 15 fois au démarrage
    await play_audio_repeatedly(vc, 'long_beep.wav', repeat_count=15)

    # Démarrer la boucle de changement de beep
    bot.loop.create_task(change_beep(vc))

# Le token est récupéré depuis une variable d'environnement
bot.run(os.getenv('DISCORD_BOT_TOKEN'))
