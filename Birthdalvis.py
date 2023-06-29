'''
@author: jodru

Birthdalvis

Happy birthday
'''

import discord
import datetime
from datetime import date
from requests import get
from discord.ext import commands, tasks
import asyncio
import logging
from dotenv import load_dotenv
import os
import sqlite3
import math

utc = datetime.timezone.utc
time = datetime.time(hour=7, minute=0, second=0, tzinfo=utc)

conn = sqlite3.connect('data.db', check_same_thread = False)

def makeDatabase():
    #Init database, enable = 0 logs are disabled, enable = 1 logs are enabled
    c = conn.cursor()
    try: 
        c.execute("""CREATE TABLE RegisteredGuilds (
                guildID integer UNIQUE,
                channelID integer
                )""")
        conn.commit()
        print("dbmade")
    except:
        print("dbexist");
    c.close()

load_dotenv()

# Logging section
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

#every birthday command you'll ever need
class BirthComs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.my_task.start()
    
    @commands.command()
    async def register(self, ctx):
        """Register guild. Guild must be registered in order to use birthday functions."""
                
        #check to see if table with guildID as name already exists
        #if so then return guild already exists
        #if not make the table
        #should be no reason to deregister a guild
        
        guildID = str(ctx.guild.id)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO RegisteredGuilds VALUES (?, NULL)", (ctx.guild.id,))
            conn.commit()
            c.execute(f"CREATE TABLE \"{guildID}\" (nameID integer UNIQUE, birthmonth integer, birthday integer)") #IF NOT EXISTS
            conn.commit()
            await ctx.send("Guild registered.")
        except:
            await ctx.send("Guild already registered.")            
        c.close()
        
    @commands.command()
    async def setAnnounceChannel(self, ctx, *, channel: discord.TextChannel):
        """Set the log channel to the id provided."""
        #Set channel for logs, or really the birthday announcement channel
        c = conn.cursor()
        try:
            c.execute("UPDATE RegisteredGuilds SET channelID = ? WHERE guildID = ?", (channel.id, ctx.guild.id))
            conn.commit()
            await ctx.send("Announcement channel set.")
        except:
            await ctx.send("Error. Did you mention a channel after the command?")
        c.close()
        
        
    @commands.command()
    async def addBirthday(self, ctx, user: discord.User, monthstr, daystr):
        """Add a user with the id provided."""
        #set user bday
        guildID = str(ctx.guild.id)
        month = int(monthstr)
        day = int(daystr)
        userID = user.id
        print(userID)
        if isinstance(month, int) and isinstance(day, int):
            c = conn.cursor()
            try:
                c.execute(f"INSERT INTO \"{guildID}\" (nameID, birthmonth, birthday) VALUES (\"{userID}\",\"{month}\",\"{day}\")")
                conn.commit()
                await ctx.send(f"User added with birthday {month}/{day}")
            except:
                await ctx.send("Error. The user may have already been added, try running !updateBirthday.")
            c.close()
        else:
            print(type(month))
            await ctx.send("Error. Did you tag a user and then follow with the month and day?")
        
    
    @commands.command()
    async def updateBirthday(self, ctx, user: discord.User, monthstr, daystr):
        """Update a user's birthday."""
        #update user bday if it exists
        guildID = str(ctx.guild.id)
        month = int(monthstr)
        day = int(daystr)
        userID = user.id
        if isinstance(month, int) or isinstance(day, int):
            c = conn.cursor()
            try:
                c.execute(f"UPDATE \"{guildID}\" SET birthmonth = \"{month}\" WHERE nameID = \"{userID}\"")
                conn.commit()
                c.execute(f"UPDATE \"{guildID}\" SET birthday = \"{day}\" WHERE nameID = \"{userID}\"")
                conn.commit()
                await ctx.send(f"User updated with birthday {month}/{day}")
            except:
                await ctx.send("Error. Not sure what the error was, but there was one.")
            c.close()
        else:
            await ctx.send("Error. Did you tag a user and then follow with the month and day?")
        
        c.close()
            
    @commands.command()
    async def removeUser(self, ctx, *, userIDstr):
        """Remove user from database."""
        guildID = str(ctx.guild.id)
        c = conn.cursor()
        userID = int(userIDstr)
        try:
            c.execute(f"DELETE FROM \"{guildID}\" WHERE nameID = \"{userID}\"")
            await ctx.send("User removed.")
            
        except:
            await ctx.send("User not found.")
        c.close()
            
    @tasks.loop(time=time)
    async def my_task(self):


        #runs at 7am UTC every day and tags everyone if there is a birthday
        c = conn.cursor()
        regGuilds = [registered[0] for registered in c.execute("SELECT guildID FROM RegisteredGuilds")]
        for x in regGuilds:
            currGuildID = x
            c.execute(f"SELECT * from \"{currGuildID}\"")
            records = c.fetchall()
            today = date.today()
            for row in records:
                if row[1] == today.month and row[2] == today.day:
                    c.execute(f"SELECT channelID FROM RegisteredGuilds WHERE guildID = \"{currGuildID}\"")
                    cID = c.fetchone()[0]
                    channel = bot.get_channel(cID)
                    await channel.send(f"@everyone Today is <@{row[0]}>'s birthday! Everyone wish them a happy birthday!!")
       

        
TOKEN = ""

description = '''Testing ground for birthdalvis'''
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', activity = discord.Game(name="v0.4 - IT'S ALIVE"), description=description, intents= intents)

@bot.event
async def on_ready():
    makeDatabase()             
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


async def main():
    async with bot:
        await bot.add_cog(BirthComs(bot))     
        await bot.start(TOKEN)

asyncio.run(main())

