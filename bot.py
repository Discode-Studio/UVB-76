import time
import discord
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

async def start_audio_websdr():
    # Configuration de ChromeOptions pour Selenium
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--headless")  # Exécution en mode headless
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--disable-software-rasterizer")
    
    # Démarrer WebDriver avec ces options
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # Aller sur le site WebSDR
    driver.get('http://websdr.78dx.ru:8901/?tune=4625usb')
    print(driver.title)

    # Optionnel: Attendre quelques secondes pour que la page soit bien chargée
    time.sleep(5)

    # Ferme le navigateur après une certaine durée (ou selon vos besoins)
    # driver.quit()  # Décommentez si vous voulez fermer le navigateur après exécution

async def stream_system_audio_to_discord(vc):
    # Exemple de configuration pour diffuser l'audio via FFmpeg (assurez-vous d'avoir les fichiers requis)
    ffmpeg_process = discord.FFmpegPCMAudio('uvb_buzzer.wav')
    source = discord.PCMVolumeTransformer(ffmpeg_process)
    vc.play(source)

@bot.event
async def on_ready():
    print(f'Connecté en tant que {bot.user}')
    
    # Connexion à un canal vocal Discord
    guild = discord.utils.get(bot.guilds, name='Nom de votre serveur')  # Mettez le nom de votre serveur ici
    voice_channel = discord.utils.get(guild.voice_channels, name='Nom du canal vocal')  # Mettez le nom du canal vocal ici
    
    vc = await voice_channel.connect()

    # Démarre la diffusion de l'audio WebSDR
    await start_audio_websdr()

    # Diffuse un fichier audio local (par exemple, uvb_buzzer.wav) dans Discord
    await stream_system_audio_to_discord(vc)

# Lancement du bot Discord
bot.run('YOUR_DISCORD_BOT_TOKEN')
