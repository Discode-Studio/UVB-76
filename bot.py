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
def play():
    global vc, looping

    # Récupération des informations de la requête
    sound = request.json.get('sound')
    loop = request.json.get('loop')

    # Définition des chemins des sons
    sound_paths = {
        'beep1': 'beep1.wav',
        'beep2': 'beep2.wav',
        'beep3': 'beep3.wav',
        'msbuzzer': 'msbuzzer.wav',
        'uvb76': 'http://websdr.78dx.ru:8901/?tune=4625usb'  # Lien WebSDR pour UVB-76
    }

    file_path = sound_paths.get(sound)

    # Si la case boucle est cochée
    looping = loop

    if file_path:
        # Lancer la tâche de jouer le son
        bot.loop.create_task(play_sound(vc, file_path))
        return jsonify({'status': 'playing', 'sound': sound})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid sound'}), 400

# API pour arrêter le son
@app.route('/stop', methods=['POST'])
def stop():
    global vc
    if vc and vc.is_playing():
        vc.stop()
    return jsonify({'status': 'stopped'})

# Tâche Discord pour se connecter à un canal vocal
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    guild = discord.utils.get(bot.guilds)
    voice_channel = discord.utils.get(guild.voice_channels, name="3")  # Nom du salon vocal
    global vc
    vc = await voice_channel.connect()

# Démarrer le bot Discord dans un thread séparé
def run_discord_bot():
    bot.run(os.getenv('DISCORD_BOT_TOKEN'))

# Exécution du serveur Flask
if __name__ == '__main__':
    # Lancer Discord dans une tâche asynchrone
    import threading
    threading.Thread(target=run_discord_bot).start()
    # Lancer le serveur Flask
    app.run(host='0.0.0.0', port=5000)
