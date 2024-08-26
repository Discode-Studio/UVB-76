from flask import Flask, render_template, request, jsonify
import discord
from discord.ext import commands
import os
import subprocess

app = Flask(__name__)

# Configuration du bot Discord
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

vc = None  # Variable globale pour stocker l'état du canal vocal
playing_sound = None  # Variable pour indiquer si un son est joué
looping = False  # Indicateur pour la case de boucle

# Fonction pour jouer un son
async def play_sound(vc, file_path):
    global playing_sound
    if vc.is_playing():
        vc.stop()  # Arrêter tout son déjà joué
    playing_sound = discord.FFmpegPCMAudio(file_path)
    vc.play(playing_sound)

# Route pour la page d'accueil avec les boutons
@app.route('/')
def index():
    return render_template('index.html')

# API pour jouer un son
@app.route('/play', methods=['POST'])
async def play():
    global vc, looping

    # Récupération des informations de la requête
    data = request.json
    sound = data.get('sound')
    loop = data.get('loop', False)  # Valeur par défaut si 'loop' n'est pas fourni

    # Log des données reçues
    print(f'Received play request: sound={sound}, loop={loop}')

    # Définition des chemins des sons
    sound_paths = {
        'beep1': 'beep1.wav',
        'beep2': 'beep2.wav',
        'beep3': 'beep3.wav',
        'msbuzzer': 'msbuzzer.wav',
        'uvb76': 'http://websdr.78dx.ru:8901/?tune=4625usb'
    }

    # Arrêter l'audio actuel si nécessaire
    if vc and vc.is_playing():
        vc.stop()

    # Jouer le son sélectionné
    if sound in sound_paths:
        file_path = sound_paths[sound]
        if file_path.startswith('http'):
            # Pour les URL comme WebSDR, on pourrait avoir besoin d'une logique spécifique
            pass
        else:
            await play_sound(vc, file_path)
        # Gérer la boucle si activée
        if loop:
            looping = True
        else:
            looping = False
        return jsonify({'status': 'success', 'sound': sound, 'loop': loop})
    return jsonify({'status': 'error', 'message': 'Sound not found'})

# API pour arrêter le son
@app.route('/stop', methods=['POST'])
async def stop():
    global vc, looping
    if vc and vc.is_playing():
        vc.stop()
    looping = False
    return jsonify({'status': 'success', 'message': 'Stopped playing'})

# Fonction d'événement pour quand le bot est prêt
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    # Rejoindre le salon vocal automatiquement
    guild = discord.utils.get(bot.guilds)
    global vc
    voice_channel = discord.utils.get(guild.voice_channels, name="3")  # Nom du salon vocal
    if voice_channel:
        vc = await voice_channel.connect()

# Le token est récupéré depuis une variable d'environnement
bot.run(os.getenv('DISCORD_BOT_TOKEN'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
