  
import discord
from discord.ext import commands
import action_scraper

bot = commands.Bot(command_prefix="!", description="Bot d'Altarax")


# When the bot starts
@bot.event
async def on_ready():
    print("Je suis prêt !")


# Basic commands to know the bot (bourso :D)
@bot.command()
async def bourso(ctx, word="info"):
    if word == "info":
        await ctx.send("Hello, je m'appelle Bourso ! \n"
                       "Pour connaître de moi fait !bourso help")
    elif word == "help":
        await ctx.send("Voici les commandes utilisables : \n"
                       "!info ACTION \n"
                       "!analyses ACTION \n"
                       "!var ACTION \n"
                       "!graph ACTION DATE")
    else:
        await ctx.send("As-t choisi un paramètre existant ? Ré-essaie.")


#Load any extension (like action_scraper)
@bot.command()
async def load(ctx, name=None):
    if name:
        bot.load_extension(name)
        await ctx.send("Extension chargée")


#Unload any extension (like action_scraper)
@bot.command()
async def unload(ctx, name=None):
    if name:
        bot.unload_extension(name)
        await ctx.send("Extension déchargée")


#Reload any extension (like action_scraper)
@bot.command()
async def reload(ctx, name=None):
    if name:
        try:
            bot.reload_extension(name)
            await ctx.send("Extension rechargée")
        except:
            bot.load_extension(name)


bot.run("")
