import discord
import os
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import subprocess
import asyncio

# Configuration du bot Discord
intents = discord.Intents.default()
intents.message_content = True  # Activer pour recevoir les messages
intents.voice_states = True  # Permet de rejoindre et gérer les salons vocaux

bot = commands.Bot(command_prefix='!', intents=intents)

# Configuration de Selenium pour le contrôle du navigateur
chrome_options = Options()
chrome_options.add_argument("--headless")  # Exécuter en mode headless
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Fonction pour capturer l'audio WebSDR
async def start_audio_websdr(vc):
    # Lancer Selenium pour contrôler le navigateur et démarrer WebSDR
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get('http://websdr.78dx.ru:8901/?tune=4625usb')

    try:
        driver.implicitly_wait(10)  # Temps d'attente implicite pour charger la page
        # Cliquer sur le bouton "Audio start"
        start_button = driver.find_element(By.XPATH, '//input[@value="Audio start"]')
        start_button.click()
        print("Clicked on 'Audio start' button.")
        
        # Démarrer la capture d'audio avec FFmpeg
        ffmpeg_command = [
            'ffmpeg', '-f', 'pulse', '-i', 'default',  # Capture de l'audio via PulseAudio (pour Linux)
            '-ac', '2', '-f', 's16le', '-ar', '48000', 'pipe:1'
        ]
        process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE)
        # Utiliser Discord pour diffuser l'audio capturé
        vc.play(discord.FFmpegPCMAudio(process.stdout))
        print("Started playing audio in voice channel.")

    except Exception as e:
        print(f"Error interacting with the page: {e}")
    finally:
        await asyncio.sleep(10)  # Laisser le temps pour que l'audio démarre
        driver.quit()

# Event on_ready pour rejoindre un salon vocal et commencer l'audio WebSDR
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

    # Nom du salon vocal à rejoindre
    voice_channel_name = "3"  # Remplacez par le nom du salon vocal souhaité
    
    # Récupérer le serveur et le salon vocal
    guild = discord.utils.get(bot.guilds, id=<YOUR_GUILD_ID>)  # Remplacez par l'ID de votre serveur
    voice_channel = discord.utils.get(guild.voice_channels, name=voice_channel_name)
    
    if voice_channel is None:
        print(f"Voice channel '{voice_channel_name}' not found.")
        return

    # Connecte le bot au salon vocal
    vc = await voice_channel.connect()

    # Démarrer l'audio de WebSDR dans le salon vocal
    await start_audio_websdr(vc)

# Récupération du token depuis les secrets du repository ou une variable d'environnement
bot.run(os.getenv('DISCORD_BOT_TOKEN'))
