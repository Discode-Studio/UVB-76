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
intents.voice_states = True  # Pour rejoindre les salons vocaux

bot = commands.Bot(command_prefix='!', intents=intents)

# Configuration de Selenium pour contrôler le navigateur WebSDR
chrome_options = Options()
chrome_options.add_argument("--headless")  # Exécuter en mode headless
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Fonction pour jouer le buzzer UVB-76 en rejoignant le salon vocal
async def play_buzzer(vc):
    source = discord.FFmpegPCMAudio('uvb_buzzer.wav')  # Chemin vers le fichier buzzer
    vc.play(source)
    while vc.is_playing():
        await asyncio.sleep(1)

# Fonction pour démarrer et capturer l'audio WebSDR via Selenium et FFmpeg
async def start_audio_websdr(vc):
    # Lancer Selenium pour démarrer WebSDR
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get('http://websdr.78dx.ru:8901/?tune=4625usb')

    try:
        driver.implicitly_wait(10)  # Attendre que la page se charge
        # Cliquer sur le bouton "Audio start"
        start_button = driver.find_element(By.XPATH, '//input[@value="Audio start"]')
        start_button.click()
        print("Clicked on 'Audio start' button.")

        # Utilisation de FFmpeg pour capturer l'audio de WebSDR
        ffmpeg_command = [
            'ffmpeg', '-f', 'pulse', '-i', 'default',  # Capture audio avec PulseAudio (Linux)
            '-ac', '2', '-f', 's16le', '-ar', '48000', 'pipe:1'
        ]
        process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE)
        vc.play(discord.FFmpegPCMAudio(process.stdout))
        print("Started streaming WebSDR audio in the voice channel.")

    except Exception as e:
        print(f"Error starting WebSDR audio: {e}")
    finally:
        await asyncio.sleep(10)  # Laisser le temps pour que l'audio démarre
        driver.quit()

# Event on_ready pour rejoindre un salon vocal et démarrer l'audio
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

    # Nom du salon vocal à rejoindre
    voice_channel_name = "3"  # Remplacez par le nom du salon vocal

    # Récupérer le serveur et le salon vocal
    guild = discord.utils.get(bot.guilds, id=1248150852368072804)  # Remplacez par l'ID de votre serveur
    voice_channel = discord.utils.get(guild.voice_channels, name=voice_channel_name)

    if voice_channel is None:
        print(f"Voice channel '{voice_channel_name}' not found.")
        return

    # Connexion au salon vocal
    vc = await voice_channel.connect()

    # Jouer le son de buzzer UVB-76 à la connexion
    await play_buzzer(vc)

    # Démarrer la capture audio WebSDR
    await start_audio_websdr(vc)

# Lancer le bot Discord avec le token
bot.run(os.getenv('DISCORD_BOT_TOKEN'))
