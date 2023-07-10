import discord
from discord.ext import commands
import random as rand
import asyncio

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)
member_list = []

@bot.event
async def on_ready():
    print("We have logged in as {0.user}".format(bot))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.name == "bot":
        if message.author.name not in [member[0] for member in member_list]:
            member_roles = [role.name.lower() for role in message.author.roles]

            roles_to_ignore = ["owner", "carl-bot", "role3"]

            if any(role in roles_to_ignore for role in member_roles):
                print(f"Ignored member: {message.author.name}")
                return

            member_list.append((message.author.name, message.author.id))
            print(f"Added member: {message.author.name}")

            if len(member_list) >= 1:
                winner = rand.choice(member_list)
                print(f"The winner is: {winner[0]}!")
                await message.channel.send(f"The winner is: {winner[0]}!")
                await challenge_duel(message.channel, winner)
                await reset_after_duel()

    await bot.process_commands(message)

async def challenge_duel(channel, winner):
    winner_member = channel.guild.get_member(winner[1])  # Fetch Member object instead of User object
    await channel.send(f"{winner_member.mention}, you have been challenged to a dice rolling duel by the bot!")
    await channel.send("Prepare yourself!")

    bot_roll = rand.randint(1, 6)
    player_roll = rand.randint(1, 6)

    await channel.send(f"{winner_member.mention}, roll the dice by typing '!roll'")
    await channel.send("I will also roll the dice...")

    def check(m):
        return m.author.name == winner[0] and m.content.lower() == "!roll"

    try:
        player_response = await bot.wait_for("message", check=check, timeout=30)
        player_dice_roll = rand.randint(1, 6)

        await channel.send(f"{winner_member.mention}, you rolled: {player_dice_roll}")
        await channel.send(f"I rolled: {bot_roll}")

        if player_dice_roll > bot_roll:
            await channel.send(f"{winner_member.mention}, you win the duel! Congratulations!")
        elif player_dice_roll < bot_roll:
            await channel.send("I win the duel! Better luck next time, human.")

            actions = ["kick", "timeout", "nickname"]
            weights = [0.02, 0.96, 0.02]

            action = rand.choices(actions, weights=weights, k=1)[0]
            if action == "kick":
                await channel.send(f"{winner_member.mention}, you have lost the duel. Prepare to be kicked!")
                member_to_kick = discord.utils.get(channel.guild.members, name=winner[0])
                await member_to_kick.kick(reason="Lost dice duel")
            elif action == "timeout":
                await channel.send(f"{winner_member.mention}, you have lost the duel. You will be timed out for 60 seconds.")
                await timeout(winner_member, 60)
                await channel.send(f"{winner_member.mention}, your timeout has expired. You can now participate again.")
            else:
                new_nickname = f"Loser-{winner_member.name}"
                await channel.send(f"{winner_member.mention}, you have lost the duel. Your nickname will be changed to '{new_nickname}'.")
                await winner_member.edit(nick=new_nickname)  # Change the nickname using the Member object

        else:
            await channel.send("It's a tie! The duel ends in a draw.")

    except asyncio.TimeoutError:
        await channel.send(f"{winner_member.mention}, you took too long to roll the dice. The duel is forfeited.")
        await reset_after_duel()

async def timeout(member, duration):
    timeout_role = discord.utils.get(member.guild.roles, name="Timeout")
    if timeout_role is None:
        print("Timeout role not found")
        return

    await member.add_roles(timeout_role)

    await asyncio.sleep(duration)

    await member.remove_roles(timeout_role)

async def reset_after_duel():
    global member_list
    member_list = []
    
bot.run("Key goes here")
