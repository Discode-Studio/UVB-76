import discord
from discord.ext import commands
import os
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import asyncio

# Configuration du bot Discord
intents = discord.Intents.default()
intents.message_content = True  # Assurez-vous que cette option est activée

bot = commands.Bot(command_prefix='!', intents=intents)

# Configuration de Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")  # Exécuter Chrome en mode headless
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Fonction pour démarrer l'audio WebSDR
async def start_audio_websdr():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get('https://www.youtube.com/live/8h_D2P0iqMk?si=lkCa7Knww42CUIF6')

    try:
        driver.implicitly_wait(10)  # Temps d'attente implicite en secondes
        start_button = driver.find_element(By.XPATH, '//input[@value="Audio start"]')
        start_button.click()
        print("Clicked on 'Audio start' button.")
    except Exception as e:
        print(f"Error interacting with the page: {e}")
    finally:
        await asyncio.sleep(5)  # Temps pour s'assurer que l'audio est démarré
        driver.quit()

# Fonction pour diffuser un fichier audio (le buzzer) sur Discord
async def play_buzzer(vc):
    if not vc.is_playing():  # Vérifie si le bot n'est pas déjà en train de jouer un audio
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('uvb_buzzer.wav'))  # Chemin vers le fichier buzzer
        vc.play(source)
    else:
        print("Already playing audio. Skipping buzzer.")

# Fonction pour diffuser l'audio PulseAudio sur Discord
async def stream_system_audio_to_discord(vc):
    # Lancer FFmpeg avec PulseAudio pour capturer l'audio du système
    ffmpeg_command = [
        'ffmpeg',
        '-f', 'pulse',          # Utilise PulseAudio
        '-i', 'default',        # Capture l'audio depuis la source par défaut de PulseAudio
        '-ac', '2',             # 2 canaux audio (stéréo)
        '-f', 's16le',          # Format de sortie en PCM 16 bits
        '-ar', '48000',         # Taux d'échantillonnage audio (Discord supporte 48kHz)
        'pipe:1'                # Envoyer la sortie via un pipe
    ]
    
    # Lancer FFmpeg en utilisant subprocess
    ffmpeg_process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE)
    
    # Transmettre l'audio capturé sur Discord
    if not vc.is_playing():  # Vérifie si le bot n'est pas déjà en train de jouer un audio
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(ffmpeg_process.stdout, pipe=True))
        vc.play(source)
    else:
        print("Already playing audio. Skipping system audio.")

# Event on_ready pour afficher que le bot est prêt et rejoindre le canal vocal automatiquement
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    
    # Rejoindre le salon vocal automatiquement
    guild = discord.utils.get(bot.guilds)
    voice_channel = discord.utils.get(guild.voice_channels, name="3")  # Nom du salon vocal
    vc = await voice_channel.connect()

    # Jouer le buzzer au démarrage
    await play_buzzer(vc)

    # Démarrer la capture et diffusion audio WebSDR
    await start_audio_websdr()
    
    # Diffuser l'audio système capturé par PulseAudio
    await stream_system_audio_to_discord(vc)

# Le token est récupéré depuis une variable d'environnement
bot.run(os.getenv('DISCORD_BOT_TOKEN'))
