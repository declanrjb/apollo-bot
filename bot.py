import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
import requests
import pandas as pd
import datetime
import json
import re
import apolloInterface as ai

load_dotenv('tokens.env')

description = """
"""

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or('$'),
    description=description,
    intents=intents,
)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")

@bot.event
async def on_message(message):
    channel = message.channel

    tagged = [tag.id for tag in message.mentions]
    if bot.user.id in tagged or 'direct message' in str(channel).lower():
        
        
        message_content = message.content.lower()
        if "what's showing" in message_content or 'whats showing' in message_content or 'what is showing' in message_content:

            day_specified = False
            weekdays = pd.Series(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'today', 'tonight', 'tomorrow']).apply(lambda x: x.lower())
            for weekday in weekdays:
                if weekday in message_content:
                    day_specified = True
                    target_day = weekday

            if not day_specified:
                schedule = ai.showtimes_in_range(datetime.datetime.today(), datetime.datetime.today() + datetime.timedelta(days=6))
            elif target_day == 'tonight' or target_day == 'today':
                schedule = ai.showtimes_in_range(datetime.datetime.today(), datetime.datetime.today())
            elif target_day == 'tomorrow':
                schedule = ai.showtimes_in_range(datetime.datetime.today() + datetime.timedelta(days=1), datetime.datetime.today() + datetime.timedelta(days=1))
            else:
                target_date = ai.date_for_day(target_day)
                schedule = ai.showtimes_in_range(target_date, target_date)
            
            outbound_message = ai.format_response(schedule)
            if len(outbound_message) == 0:
                await channel.send(f'There are no showtimes available on {target_date}.')
            else:
                await channel.send(outbound_message)

bot.run(os.getenv('BOT_TOKEN'))