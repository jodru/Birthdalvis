'''
@author: jodru

Birthdalvis

Happy birthday
'''

import discord
from requests import get
from discord.ui import Button, Select, View
from discord.ext import commands, tasks
import asyncio
import logging
from collections import deque, defaultdict
from dotenv import load_dotenv
import os
import sqlite3
import math

conn = sqlite3.connect('data.db', check_same_thread = False)

def makeDatabase():
    #Init database, enable = 0 logs are disabled, enable = 1 logs are enabled (this comment is old)
    c = conn.cursor()
    try: 
        c.execute("""CREATE TABLE RegisteredGuilds (
                guildID integer UNIQUE,
                channelID integer
                )""")
        conn.commit()
        print("dbmade")
    except:
        print("dbalreadyexist");
    c.close()

load_dotenv()

# Logging section
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# The only point in this is I don't feel like removing it rn
class RegComs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def hellothere(self, ctx):
        """This is about all the "hello world" you old farts are gonna get."""
        await ctx.send("General Kenobi!")

#every birthday command you'll ever need
class BirthComs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    
    @commands.command()
    async def register(self, ctx):
        """Register guild. Guild must be registered in order to use birthday functions."""
                
        #check to see if table with guildID as name already exists
        #if so then return guild already exists
        #if not make the table
        
        guildID = str(ctx.guild.id)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO RegisteredGuilds VALUES (?, NULL)", (ctx.guild.id,))
            conn.commit()
            c.execute(f"CREATE TABLE \"{guildID}\" (nameID integer UNIQUE, birthmonth integer, birthday integer)") #IF NOT EXISTS
            conn.commit()
            await ctx.send("Guild registered.")
            #If I'm not mistaken this makes a RegisteredGuilds with a guildID.
            #If that works, it makes a new table with guildID as the name.
            #The idea is to have a table hold the names and bdays for each user in a guild, and a table hold all guildIDs and cIDs
        except:
            await ctx.send("Guild already registered.")            
        c.close()
        
    @commands.command()
    async def setAnnounceChannel(self, ctx, *, channel: discord.TextChannel):
        """Set the log channel to the id provided."""
        #Set channel for logs
        c = conn.cursor()
        try:
            c.execute("UPDATE RegisteredGuilds SET channelID = ? WHERE guildID = ?", (channel.id, ctx.guild.id))
            conn.commit()
            await ctx.send("Announcement channel set.")
        except:
            await ctx.send("Error. Did you mention a channel after the command?")
        c.close()
        
        
    @commands.command()
    async def addBirthday(self, ctx, *, userID, month, day):
        """Add a user with the id provided."""
        #set user bday
        guildID = str(ctx.guild.id)
        
        if isinstance(month, int) or isinstance(day, int):
            c = conn.cursor()
            try:
                c.execute(f"INSERT INTO \"{guildID}\" (\"{userID}\",\"{month}\",\"{day}\")")
                conn.commit()
                await ctx.send(f"User added with birthday {month}/{day}")
            except:
                await ctx.send("Error. The user may have already been added, try running !updateBirthday.")
            c.close()
        else:
            await ctx.send("Error. Did you tag a user and then follow with the month and day?")
        
    
    @commands.command()
    async def updateBirthday(self, ctx, *, user: discord.User, month, day):
        """Enable deleted message logging"""
        #update user bday if it exists
        guildID = str(ctx.guild.id)
        userID = user.id
        if isinstance(month, int) or isinstance(day, int):
            c = conn.cursor()
            try:
                c.execute(f"UPDATE {guildID} SET birthmonth = {month} WHERE nameID = {userID}")
                conn.commit()
                c.execute(f"UPDATE {guildID} SET birthday = {month} WHERE nameID = {userID}")
                conn.commit()
                await ctx.send(f"User updated with birthday {month}/{day}")
            except:
                await ctx.send("Error. Not sure what the error was.")
            c.close()
        else:
            await ctx.send("Error. Did you tag a user and then follow with the month and day?")
        
        c.close()
            
    @commands.command()
    async def removeUser(self, ctx, *, userID):
        """Remove user from database."""
        guildID = str(ctx.guild.id)
        c = conn.cursor()
        try:
            c.execute(f"DELETE FROM {guildID} WHERE nameID = {userID}")
        except:
            await ctx.send("User not found.")
        
TOKEN = ""

description = '''Testing ground for birthdalvis'''
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', activity = discord.Game(name="v0.1 - first run"), description=description, intents= intents)

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
        await bot.add_cog(RegComs(bot)) 
        
        await bot.start(TOKEN)

asyncio.run(main())

