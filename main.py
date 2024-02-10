import disnake
from disnake.ext import commands

from dotenv import load_dotenv
import os

from NWS_Weather import current_weather

intents = disnake.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

@bot.slash_command(name="weather", description="Get weather from either a nws station or a zipcode")
async def weather(ctx, station: str = None, zipcode: int = None):
    try:
        if station is None and zipcode is not None: # If using the zipcode
            weather = current_weather(zipcode=zipcode)[0]
        elif station is not None and zipcode is None: # If using the station 
            # if station does not start with K, add K to the beginning    
            if not station.startswith("K"): station = f"K{station}"
            
            station = station.upper()
            weather = current_weather(station=station)[0]
        else:
            await ctx.send("You must provide either a station or a zipcode")
            return

        # Create an embed
        embed = disnake.Embed(
            title="Current Weather",
            description=f"Weather at { station if station is not None else zipcode }",
            color=0x00ff00,
            timestamp=weather.timestamp
        )
        
        embed.set_thumbnail(url=weather.icon)
        
        # Add fields to the embed
        # fields are time, temp, wind speed, wind direction, relative humidity, and cloud ceiling
        
        embed.add_field(name="Temperature",         value=f"{round((weather.temperature * 1.8) + 32)}°F",      inline=True)
        embed.add_field(name="Wind Speed",          value=f"{round(weather.wind_speed * 0.6213711922)} MPH",   inline=True)
        embed.add_field(name="Wind Direction",      value=f"{round(weather.wind_direction)}°",                 inline=True)
        embed.add_field(name="Relative Humidity",   value=f"{round(weather.relative_humidity)}%",              inline=True)
        
        clouds = weather.cloud_layers.layers[0]
        if clouds["amount"] == "CLR": embed.add_field(name="Cloud Ceiling", value="Clear", inline=True)
        else: embed.add_field(name="Cloud Ceiling", value=f"{weather.cloud_layers.layers[0]['amount']} {round(weather.cloud_layers.layers[0]['base']['value'] * 3.2808)} ft",                inline=True)
        
        
        # Send the embed
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send("Not a valid airport (or something else went wrong)")
        print(e)

load_dotenv()
bot.run(os.getenv("TOKEN"))
