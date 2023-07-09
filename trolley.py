import discord
from discord.ext import commands
import random as rand
import asyncio  # Import asyncio module

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=".", intents=intents)
member_list = []


@bot.event
async def on_ready():
    print("We have logged in as {0.user}".format(bot))


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.name == "buds":  # Check if the channel name is "buds"
        if message.author.name not in [member[0] for member in member_list]:
            member_list.append((message.author.name, message.author.id))
            print(f"Added member: {message.author.name}")

            if len(member_list) >= 2:
                winner = rand.choice(member_list)
                print(f"The winner is: {winner[0]}!")
                await message.channel.send(f"The winner is: {winner[0]}!")
                await challenge_duel(message.channel, winner)
                await reset_after_duel()

    await bot.process_commands(message)


async def challenge_duel(channel, winner):
    winner_member = await bot.fetch_user(winner[1])
    await channel.send(f"{winner_member.mention}, you have been challenged to a dice rolling duel by the bot!")
    await channel.send("Prepare yourself!")

    bot_roll = rand.randint(1, 6)
    player_roll = rand.randint(1, 6)

    await channel.send(f"{winner_member.mention}, roll the dice by typing '.roll'")
    await channel.send("I will also roll the dice...")

    def check(m):
        return m.author.name == winner[0] and m.content.lower() == ".roll"

    try:
        player_response = await bot.wait_for("message", check=check, timeout=30)
        player_dice_roll = rand.randint(1, 6)

        await channel.send(f"{winner_member.mention}, you rolled: {player_dice_roll}")
        await channel.send(f"I rolled: {bot_roll}")

        if player_dice_roll > bot_roll:
            await channel.send(f"{winner_member.mention}, you win the duel! Congratulations!")
        elif player_dice_roll < bot_roll:
            await channel.send("I win the duel! Better luck next time, human.")
        else:
            await channel.send("It's a tie! The duel ends in a draw.")

    except asyncio.TimeoutError:
        await channel.send(f"{winner_member.mention}, you took too long to roll the dice. The duel is forfeited.")
        await reset_after_duel()


async def reset_after_duel():
    global member_list
    member_list = []


@bot.command()
async def random(ctx):
    members = [member for member in ctx.guild.members if not member.bot]
    if not members:
        await ctx.send("There are no non-bot members in this server.")
        return

    random_member = rand.choice(members)
    await ctx.send(f"Random member name: {random_member.name}")
    await challenge_duel(ctx.channel, (random_member.name, random_member.id))
    await reset_after_duel()


bot.run("Key goes here")
