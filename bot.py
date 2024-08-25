import os
import discord
from discord.ext import commands
import asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import subprocess

TOKEN = os.getenv('DISCORD_BOT_TOKEN')  # Récupérer le token depuis les secrets
VOICE_CHANNEL_ID = 1248150853295149191   # ID du salon vocal
AUDIO_OUTPUT = 'output_audio.wav'       # Nom du fichier de sortie audio

# Initialiser le bot Discord avec le préfixe '!'
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# Fonction pour régler la fréquence sur 4625 kHz via Selenium
def set_frequency_4625():
    # Options pour que Chrome fonctionne en mode headless (sans interface graphique)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Chemin vers chromedriver (assurez-vous que ChromeDriver est bien configuré)
    service = Service('/path/to/chromedriver')  # Remplace par le bon chemin

    # Initialiser le navigateur
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Accéder à l'URL WebSDR
        driver.get('http://websdr.78dx.ru:8901/')

        # Attendre que l'élément de fréquence soit disponible, puis régler la fréquence sur 4625 kHz
        frequency_input = driver.find_element(By.ID, "tunedfreq")
        frequency_input.clear()
        frequency_input.send_keys('4625')
        frequency_input.send_keys('\n')
        print("Fréquence réglée sur 4625 kHz.")

        # Attendre un moment pour laisser le flux se stabiliser
        asyncio.sleep(2)

    finally:
        # Fermer le navigateur
        driver.quit()

# Commande pour que le bot se connecte à un salon vocal
@bot.event
async def on_ready():
    print(f'Bot connecté comme {bot.user}')
    voice_channel = bot.get_channel(VOICE_CHANNEL_ID)
    if voice_channel is not None:
        vc = await voice_channel.connect()

        # Commence à diffuser l'audio capturé
        set_frequency_4625()  # Régler la fréquence via Selenium

        # Exécuter la capture audio avec FFmpeg
        command = [
            'ffmpeg', '-y', '-i', 'http://websdr.78dx.ru:8901/m.wav',
            '-t', '3600',  # Capturer 1 heure d'audio
            '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '2',
            AUDIO_OUTPUT
        ]
        process = subprocess.Popen(command)
        await asyncio.sleep(10)  # Laisser FFmpeg fonctionner un peu

        # Jouer l'audio capturé en boucle
        vc.play(discord.FFmpegPCMAudio(AUDIO_OUTPUT))

        print(f"Diffusion en cours sur {voice_channel.name}")

# Commande pour arrêter le bot et déconnecter du salon vocal
@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

# Lancer le bot Discord
bot.run(TOKEN)
