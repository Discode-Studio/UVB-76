import discord
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import subprocess
import tempfile
import os
from webdriver_manager.chrome import ChromeDriverManager

# Définir les intents requis
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    voice_channel = discord.utils.get(bot.guilds[0].channels, name='general')
    if voice_channel:
        vc = await voice_channel.connect()

        # Configuration de Selenium
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Exécuter Chrome en mode headless (sans interface graphique)
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get('http://websdr.78dx.ru:8901/?tune=4625usb')

        # Attendre que la page se charge et cliquer sur le bouton "Audio start"
        try:
            start_button = driver.find_element(By.XPATH, '//*[@id="button_id"]')  # Remplace avec le bon XPATH
            start_button.click()
            print("Clicked on 'Audio start' button.")
        except Exception as e:
            print(f"Error clicking 'Audio start' button: {e}")

        # Attendre que le bouton soit cliqué
        import time
        time.sleep(5)  # Ajuste ce délai si nécessaire pour garantir que l'audio démarre correctement

        # Création d'un fichier temporaire pour stocker le flux audio
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            temp_file_path = temp_file.name
            print(f'Temporary file created at: {temp_file_path}')

        # Commande ffmpeg pour récupérer le flux audio
        command = [
            'ffmpeg',
            '-i', 'http://websdr.78dx.ru:8901/?tune=4625usb',
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

        driver.quit()  # Fermer le navigateur

# Le token est récupéré depuis une variable d'environnement
bot.run(os.getenv('DISCORD_BOT_TOKEN'))
