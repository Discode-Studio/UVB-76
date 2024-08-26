from flask import Flask, render_template, request, jsonify
import discord
from discord.ext import commands
import os
import subprocess
import asyncio

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

# Fonction pour capturer et diffuser le son du WebSDR
async def stream_websdr(vc):
    # Assurer que ffmpeg est installé et configuré correctement
    command = [
        'ffmpeg',
        '-i', 'http://websdr.78dx.ru:8901/?tune=4625usb',
        '-f', 'wav',
        'pipe:1'
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    source = discord.FFmpegPCMAudio(process.stdout, pipe=True)
    vc.play(source)

# Route pour la page d'accueil avec les boutons
@app.route('/')
def index():
    return render_template('index.html')

# API pour jouer un son
@app.route('/play', methods=['POST'])
def play():
    global vc, looping

    # Récupération des informations de la requête
    sound = request.json.get('sound')
    loop = request.json.get('loop')

    # Log des données reçues
    print(f'Received play request: sound={sound}, loop={loop}')

    # Définition des chemins des sons
    sound_paths = {
        'beep1': 'beep1.wav',
        'beep2': 'beep2.wav',
        'beep3': 'beep3.wav',
        'msbuzzer': 'msbuzzer.wav',
        'uvb76': 'websdr'  # Utilise le flux WebSDR pour UVB-76
    }

    if sound in sound_paths:
        file_path = sound_paths[sound]
        if file_path == 'websdr':
            asyncio.run(stream_websdr(vc))
        else:
            asyncio.run(play_sound(vc, file_path))
        
        looping = loop
        return jsonify({"status": "success", "message": f"Playing {sound}"})
    else:
        return jsonify({"status": "error", "message": "Invalid sound"}), 400

# API pour arrêter la lecture
@app.route('/stop', methods=['POST'])
def stop():
    global vc
    if vc.is_playing():
        vc.stop()
    return jsonify({"status": "success", "message": "Playback stopped"})

# Démarrer le bot Discord
@bot.event
async def on_ready():
    global vc
    print(f'Logged in as {bot.user.name}')
    
    # Rejoindre le salon vocal automatiquement
    guild = discord.utils.get(bot.guilds)
    voice_channel = discord.utils.get(guild.voice_channels, name="3")  # Nom du salon vocal
    vc = await voice_channel.connect()

# Le token est récupéré depuis une variable d'environnement
bot.run(os.getenv('DISCORD_BOT_TOKEN'))

# Lancer le serveur Flask
if __name__ == '__main__':
    app.run(debug=True, port=5000)
