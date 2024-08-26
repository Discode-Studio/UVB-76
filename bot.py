import discord
from discord.ext import commands
import os
import asyncio
import aiohttp

# Configuration du bot Discord
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True  # Ajouter l'intention pour les guilds (serveurs)

bot = commands.Bot(command_prefix='!', intents=intents)

# Variables globales
beep_file = 'http://streams.printf.cc:8000/buzzer.ogg'
beep_interval_seconds = 2
uvb_stream_url = 'http://streams.printf.cc:8000/buzzer.ogg'
beep3_file = 'beep3.wav'
is_beep3_playing = {}
is_stream_playing = {}
stream_tasks = {}

async def play_audio_repeatedly(vc, file, repeat_count, interval_seconds=2):
    for _ in range(repeat_count):
        if not vc.is_playing():
            print(f"Playing audio file: {file}")
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(file))
            vc.play(source)
            while vc.is_playing():
                await asyncio.sleep(1)
        await asyncio.sleep(interval_seconds)

async def play_beep_in_loop(vc):
    while True:
        if not vc.is_playing():
            print(f"Playing beep in loop from: {beep_file}")
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(beep_file))
            vc.play(source)
        await asyncio.sleep(beep_interval_seconds)

async def play_beep3_in_loop(vc, guild_id):
    global is_beep3_playing
    is_beep3_playing[guild_id] = True
    while is_beep3_playing[guild_id]:
        if not vc.is_playing():
            print(f"Playing beep3 in loop for guild: {guild_id}")
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(beep3_file))
            vc.play(source)
        await asyncio.sleep(2)

def stop_beep3(guild_id):
    global is_beep3_playing
    is_beep3_playing[guild_id] = False

async def check_uvb_stream_404():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(uvb_stream_url) as response:
                return response.status == 404
    except aiohttp.ClientError:
        return False

async def play_uvb_stream(vc, guild_id):
    global is_stream_playing
    if not is_stream_playing.get(guild_id):
        is_stream_playing[guild_id] = True
        print(f"Playing UVB stream for guild: {guild_id}")
        stream_source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(uvb_stream_url))
        vc.play(stream_source, after=lambda e: set_stream_playing(guild_id, False))
    else:
        print(f"Stream already playing for guild {guild_id}.")

def set_stream_playing(guild_id, value):
    global is_stream_playing
    is_stream_playing[guild_id] = value

async def check_and_connect_to_voice_channels():
    for guild in bot.guilds:
        voice_channel = discord.utils.get(guild.voice_channels, name="General")
        vc = discord.utils.get(bot.voice_clients, guild=guild)
        
        if voice_channel and vc is None:
            print(f"Connecting to voice channel in guild: {guild.name}")
            vc = await voice_channel.connect()
        elif voice_channel is None:
            print(f"Creating and connecting to voice channel in guild: {guild.name}")
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(connect=True, speak=True)
            }
            general_channel = await guild.create_voice_channel('General', overwrites=overwrites)
            vc = await general_channel.connect()

async def monitor_uvb_stream(vc, guild_id):
    global stream_tasks
    while True:
        uvb_is_404 = await check_uvb_stream_404()
        if not uvb_is_404:
            stop_beep3(guild_id)
            if not vc.is_playing():
                await play_uvb_stream(vc, guild_id)
        else:
            if not is_beep3_playing.get(guild_id):
                bot.loop.create_task(play_beep3_in_loop(vc, guild_id))
        await asyncio.sleep(10)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    
    await check_and_connect_to_voice_channels()

    for guild in bot.guilds:
        voice_channel = discord.utils.get(guild.voice_channels, name="General")
        vc = discord.utils.get(bot.voice_clients, guild=guild)
        
        if voice_channel and vc is None:
            vc = await voice_channel.connect()

            await play_audio_repeatedly(vc, 'long_beep.wav', repeat_count=5)

            global stream_tasks
            if guild.id not in stream_tasks:
                stream_tasks[guild.id] = bot.loop.create_task(monitor_uvb_stream(vc, guild.id))

bot.run(os.getenv('DISCORD_BOT_TOKEN'))
