import discord
import json
import os
from datetime import datetime
from discord.ext import commands

with open('config.json') as config:
    prefix, token, reddit_oauth = json.load(config).values()

reddit_oauth = None

bot = commands.Bot(command_prefix=prefix)


@bot.event
async def on_message(message):
    if message.content.startswith(prefix):
        print(f'[{datetime.now()}] {message.author.name}: {message.content}')
        await bot.process_commands(message)


@bot.event
async def on_ready():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')
    game = discord.Game('r/help')
    await bot.change_presence(activity=game)
    print(f'[{datetime.now()}] Logged in as {bot.user.name}')

    # TODO create profile command

bot.run(token)
