import discord
import os
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import asyncio

# Configuration du bot Discord
intents = discord.Intents.default()
intents.message_content = True  # Assurez-vous que cette option est activée
intents.voice_states = True  # Nécessaire pour gérer les connexions vocales

bot = commands.Bot(command_prefix='!', intents=intents)

# Configuration de Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")  # Exécuter Chrome en mode headless
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Fonction pour démarrer l'audio WebSDR
async def start_audio_websdr(vc):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get('http://websdr.78dx.ru:8901/?tune=4625usb')

    try:
        driver.implicitly_wait(10)  # Temps d'attente implicite en secondes
        start_button = driver.find_element(By.XPATH, '//input[@value="Audio start"]')
        start_button.click()
        print("Clicked on 'Audio start' button.")
        
        # Attendre que l'audio commence
        await asyncio.sleep(5)
        
        # Lire l'audio depuis la sortie de Selenium et le jouer dans le salon vocal
        # Utilisation d'une URL de stream comme exemple, il peut être nécessaire de capturer le flux correctement
        audio_source_url = 'http://websdr.78dx.ru:8901/stream'
        vc.play(discord.FFmpegPCMAudio(audio_source_url))
        print("Started playing audio in voice channel.")
    except Exception as e:
        print(f"Error interacting with the page: {e}")
    finally:
        driver.quit()

# Event on_ready pour rejoindre un salon vocal et commencer l'audio WebSDR
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

    # Nom du salon vocal à rejoindre
    voice_channel_name = "3"  # Remplacez par le nom du salon vocal voulu
    
    # Recherche du salon vocal avec le nom spécifié
    guild = discord.utils.get(bot.guilds, id=1248150852368072804)  # Remplacez par l'ID de votre serveur
    voice_channel = discord.utils.get(guild.voice_channels, name=voice_channel_name)
    
    if voice_channel is None:
        print(f"Voice channel '{voice_channel_name}' not found.")
        return

    # Connecte le bot au salon vocal
    vc = await voice_channel.connect()

    await start_audio_websdr(vc)

# Le token est récupéré depuis une variable d'environnement
bot.run(os.getenv('DISCORD_BOT_TOKEN'))
