import discord
from discord.ext import commands
import os
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import asyncio

# Configuration du bot Discord
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Configuration de Selenium
chrome_options = Options()
# Désactiver le mode headless pour voir l'interaction
# chrome_options.add_argument("--headless")  # Désactiver pour voir l'interface
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Fonction pour démarrer l'audio WebSDR
async def start_audio_websdr():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get('http://websdr.78dx.ru:8901/?tune=4625usb')

    try:
        driver.implicitly_wait(10)  # Temps d'attente implicite en secondes

        # Attendre que le bouton soit cliquable et cliquer dessus
        start_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@value="Audio start"]'))
        )
        start_button.click()
        print("Clicked on 'Audio start' button.")

        # Afficher les logs du navigateur
        for log in driver.get_log('browser'):
            print(log)

    except Exception as e:
        print(f"Error interacting with the page: {e}")
    finally:
        await asyncio.sleep(5)  # Temps pour s'assurer que l'audio est démarré
        driver.quit()

# Fonction pour diffuser un fichier audio (le buzzer) sur Discord
async def play_buzzer(vc):
    if not vc.is_playing():
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('uvb_buzzer.wav'))
        vc.play(source)
    else:
        print("Already playing audio. Skipping buzzer.")

# Fonction pour diffuser l'audio PulseAudio sur Discord
async def stream_system_audio_to_discord(vc):
    ffmpeg_command = [
        'ffmpeg',
        '-f', 'pulse',
        '-i', 'default',
        '-ac', '2',
        '-f', 's16le',
        '-ar', '48000',
        'pipe:1'
    ]
    
    ffmpeg_process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE)
    
    if not vc.is_playing():
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(ffmpeg_process.stdout, pipe=True))
        vc.play(source)
    else:
        print("Already playing audio. Skipping system audio.")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    
    guild = discord.utils.get(bot.guilds)
    voice_channel = discord.utils.get(guild.voice_channels, name="3")
    vc = await voice_channel.connect()

    await play_buzzer(vc)
    await start_audio_websdr()
    await stream_system_audio_to_discord(vc)

bot.run(os.getenv('DISCORD_BOT_TOKEN'))
