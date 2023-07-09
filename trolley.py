import discord
from discord.ext import commands
import random as rand
import requests

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=".", intents=intents)


@bot.event
async def on_ready():
    print("We have logged in as {0.user}".format(bot))


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith("hi"):
        print(f"Received 'hi' from {message.author.name} ({message.author.id}) in {message.guild.name} ({message.guild.id})")
        await message.channel.send("FACKYOU!")

    await bot.process_commands(message)  # Process commands


@bot.command()
async def random(ctx):
    # Get the list of members in the server
    members = [member for member in ctx.guild.members if not member.bot]
    if not members:
        await ctx.send("There are no non-bot members in this server.")
        return

    # Select a random member from the list
    random_member = rand.choice(members)
    # Send the random member's name to the channel
    await ctx.send(f"Random member name: {random_member.name}")


@bot.command()
async def fact(ctx):
    # Fetch the random fact from a website
    url = "https://uselessfacts.jsph.pl/random.json?language=en"
    response = requests.get(url)
    if response.status_code == 200:
        fact = response.json()["text"]
        await ctx.send(f"Random fact: {fact}")
    else:
        await ctx.send("Failed to fetch a random fact.")


bot.run("Key goes here")
