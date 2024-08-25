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

bot = commands.Bot(command_prefix='!', intents=intents)

# Configuration de Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")  # Exécuter Chrome en mode headless
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Fonction pour démarrer l'audio WebSDR
async def start_audio_websdr():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get('http://websdr.78dx.ru:8901/?tune=4625usb')

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

# Commande pour démarrer le WebSDR
@bot.command()
async def start(ctx):
    await ctx.send("Starting WebSDR...")
    await start_audio_websdr()
    await ctx.send("WebSDR audio should now be playing.")

# Event on_ready pour afficher que le bot est prêt
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

# Le token est récupéré depuis une variable d'environnement
bot.run(os.getenv('DISCORD_BOT_TOKEN'))
