import discord
from discord.ext import commands
import subprocess
import tempfile
import os

# Définir les intents requis
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    voice_channel = discord.utils.get(bot.guilds[0].channels, name='3')
    if voice_channel:
        vc = await voice_channel.connect()

        # URL pour la fréquence spécifique
        url = 'http://websdr.78dx.ru:8901/?tune=4625usb'

        # Création d'un fichier temporaire pour stocker le flux audio
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            temp_file_path = temp_file.name
            print(f'Temporary file created at: {temp_file_path}')

        # Commande ffmpeg pour récupérer le flux audio
        command = [
            'ffmpeg',
            '-i', url,
            '-f', 'wav',
            '-ar', '44100',  # Taux d'échantillonnage
            '-ac', '2',      # Nombre de canaux audio
            temp_file_path
        ]
        
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process.communicate()  # Attendre que le processus ffmpeg se termine
        except Exception as e:
            print(f"Error running ffmpeg: {e}")

        if os.path.getsize(temp_file_path) > 0:  # Vérifier que le fichier n'est pas vide
            vc.play(discord.FFmpegPCMAudio(temp_file_path))
        else:
            print("Le fichier temporaire est vide. Vérifie l'URL du flux audio.")

# Le token est récupéré depuis une variable d'environnement
bot.run(os.getenv('DISCORD_BOT_TOKEN'))
