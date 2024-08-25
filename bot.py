import discord
import os
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import asyncio
import subprocess

# Configuration du bot Discord
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Configuration de Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")  # Exécuter Chrome en mode headless
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Fonction pour démarrer l'audio WebSDR via Selenium
async def start_websdr_audio():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get('http://websdr.78dx.ru:8901/?tune=4625usb')

    try:
        driver.implicitly_wait(10)  # Temps d'attente implicite
        start_button = driver.find_element(By.XPATH, '//input[@value="Audio start"]')
        start_button.click()
        print("Clicked on 'Audio start' button.")
    except Exception as e:
        print(f"Error interacting with the page: {e}")
    finally:
        await asyncio.sleep(5)  # Attendre que l'audio démarre
        driver.quit()

# Fonction pour capturer l'audio avec ffmpeg et le diffuser sur Discord
async def stream_websdr_to_discord(vc):
    ffmpeg_command = [
        'ffmpeg',
        '-i', 'http://websdr.78dx.ru:8901/?tune=4625usb',  # Lien WebSDR avec la fréquence
        '-f', 's16le',  # Format de sortie audio
        '-ar', '48000',  # Taux d'échantillonnage
        '-ac', '2',  # Nombre de canaux audio
        'pipe:1'  # Pipe pour rediriger l'audio vers Discord
    ]

    # Lancer ffmpeg pour capturer l'audio
    ffmpeg_process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE)

    # Créer une source audio Discord à partir du flux ffmpeg
    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(ffmpeg_process.stdout))

    # Jouer l'audio capturé dans le salon vocal
    vc.play(source)

# Event on_ready pour joindre automatiquement le salon vocal et démarrer le flux WebSDR
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

    # Récupérer le salon vocal à partir de son nom ou ID (ici "3")
    guild = discord.utils.get(bot.guilds)  # Utilisez la méthode appropriée pour obtenir la guild
    voice_channel = discord.utils.get(guild.voice_channels, name="3")  # Nom du salon vocal
    
    if voice_channel:
        vc = await voice_channel.connect()
        await start_websdr_audio()  # Démarrer l'audio WebSDR
        await stream_websdr_to_discord(vc)  # Capturer et diffuser l'audio sur Discord
    else:
        print("Le salon vocal n'a pas été trouvé.")

# Le token est récupéré depuis une variable d'environnement
bot.run(os.getenv('DISCORD_BOT_TOKEN'))
