'''
    Magic Child is a discord bot aimed at bringing Zoe's Character(from
    League of Legends™) to life
    Copyright (C) 2018  Shaheen Sarafa

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''


import discord
from discord.ext import commands
import botconfig as b
import asyncio
from database_code import db_logic
import sys
import traceback
import datetime


def get_prefix(bot, message):
    """A callable Prefix for our bot. This could be edited to allow per
     server prefixes."""

    prefixes = ['Zoe, ', '!']

    if not message.guild:
        return 'Zoe, '

    return commands.when_mentioned_or(*prefixes)(bot, message)


initial_extensions = ['cogs.admincommands', 'cogs.keepingcommands',
                      'cogs.economycommands']

db = db_logic.db_commands()

child = commands.Bot(command_prefix=get_prefix,
                     description=b.description)
child.remove_command('help')

xp_time = {}
user_message_time = {}

if __name__ == '__main__':
    for extension in initial_extensions:
        try:
            child.load_extension(extension)
        except:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            traceback.print_exc()


async def embed_send():
    # this is the pinned message in #self-roles
    embed = discord.Embed(title='How to get roles', description="Simply use the following command:"
                          "\n Zoe, give `roleName`\nThe roles are listed here:", colour=0x2ecc71)
    channel = child.get_channel(b.channels["self-roles"])
    for role in b.game_roles:
        embed.add_field(name="\uFEFF", value=role + "\n")
    embed.add_field(name="\uFEFF", value="\uFEFF")
    embed.add_field(
        name="\uFEFF", value="\n*Note: The Event role is for being pinged to game events like League customs")

    await channel.send(content=None, embed=embed)


@child.event
async def on_ready():
    print("\n" + '-------' * 6)
    print('| Logged in as: ' + str(datetime.datetime.now()), end="\n|\n")
    print("| " + child.user.name, end=" | ID: ")
    print(child.user.id)
    game = discord.Game("video games")
    await child.change_presence(status=discord.Status.online, activity=game)
    print('-------' * 6)
    # await embed_send()


async def warn(member):
    db.add_warning(member)
    if db.read_warnings(member) > 2:
        role = "Muted"
        db.chat_mute(member, 10)
        await member.add_roles(discord.utils.get(member.guild.roles, name=role))


async def log_hate(message):
    embed = discord.Embed(title='Misbehaving report:', description="{0} said the following:\n{1}"
                          .format(message.author.mention, message.content), colour=message.author.colour)
    embed.set_author(icon_url=message.author.avatar_url,
                     name=str(message.author))
    channel = child.get_channel(b.channels["mod-logs"])
    await channel.send(content=None, embed=embed)


def add_experience(message):
    try:
        if (datetime.datetime.utcnow() - xp_time[str(message.author.id)]).total_seconds() >= 60:
            db.add_xp(message)
            xp_time[str(message.author.id)] = message.created_at
    except KeyError:
        db.add_xp(message)
        xp_time[str(message.author.id)] = message.created_at


async def user_level_up(message):
    if(db.read_xp(message.author)[0] < db.read_xp(message.author)[1]):
        db.level_up(message.author)
        # debug:
        # print(int(db.read_xp(message)[0]))
        role = b.roles[db.read_xp(message.author)[1]]
        db.add_currency(message.author, b.level_up_prize[role])
        await message.author.add_roles(discord.utils.get(message.author.guild.roles, name=role))
        embed = discord.Embed(title='Rank up!', description="Congratulations {0}, you have gained rank of {1}!"
                              .format(message.author.mention, role), colour=message.author.colour)
        embed.set_author(icon_url=message.author.avatar_url,
                         name=str(message.author))
        await message.channel.send(content=None, embed=embed)


async def add_members(message):
    ''' function to add all members of a server into the database '''
    for member in message.guild.members:
        # db.initialize(member)
        await member.add_roles(discord.utils.get(message.author.guild.roles, name=b.roles[1]))


async def chat_unmute(message):
    for member in discord.utils.get(message.author.guild.roles, name="Muted").members:
        db.decrease_mute(member)
        if(db.read_chat_mute(member) < 1):
            role = discord.utils.get(member.guild.roles, name="Muted")
            await member.remove_roles(role)
        user_message_time.clear()
    asyncio.sleep(300)


async def antispam(message):
    if str(message.content) in user_message_time:
        if (message.created_at - user_message_time[str(message.content)][1]).total_seconds() < 10:
            user_message_time[str(message.content)][0] = user_message_time[str(
                message.content)][0] + 1
            if user_message_time[str(message.content)][0] > 2:
                # print(user_message_time[str(message.content)]) # debug
                await message.delete()
                embed = discord.Embed(title='Spam report:',
                                      description="{0} has been spamming the following:\n{1}"
                                      .format(message.author.mention, message.content),
                                      colour=message.author.colour)
                embed.set_author(icon_url=message.author.avatar_url,
                                 name=str(message.author))
                channel = child.get_channel(b.channels["mod-logs"])
                await channel.send(content=None, embed=embed)
                await warn(message.author)
        else:
            del user_message_time[str(message.content)]
    else:
        user_message_time[str(message.content)] = [
            0, datetime.datetime.utcnow()]


@child.event
async def on_member_join(member: discord.Member):
    embed = discord.Embed(title='Welcome member', description="Welcome {0} to Blink's Gaming Hub!\nTake a look at <#475069544625602560> and <#464716218411253760>."
                          .format(member.mention), colour=member.colour)
    embed.set_author(icon_url=member.avatar_url,
                     name=str(member))
    channel = child.get_channel(b.channels["general"])

    await member.add_roles(discord.utils.get(member.guild.roles, name=b.roles[1]))

    await channel.send(content="\U0000FEFF", embed=embed)

    # to get back their roles if they rejoined
    for i in range(1, db.read_xp(member)[0]):
        await member.add_roles(discord.utils.get(member.guild.roles, name=b.roles[i]))

async def messageCheck(message):
        if (len(message.raw_mentions)>2) and (message.author.top_roles > discord.utils.get(message.author.guild.roles, name="Marquis")):
            await log_hate(message)
            await warn(message.author)
            await message.channel.send("No more than 2 pings!")
            await message.delete()

        message.content.lower()

        for word in b.forbidden_words:
            if str(word) in str(message.content).lower():
                msg = "No, that's not nice!"
                await message.channel.send(msg)
                await log_hate(message)
                await warn(message.author)
                try:
                    # this is put in a try block just to not display unnecessary error message
                    await message.delete()
                    # Because sometimes antispam() deletes messages before this command.
                except:
                    return  # If they're spammers, they don't get xp.
                break



@child.event
async def on_message(message):

    # Only ran the function below to add all members to the database, but keeping it here for future refrence.
    # await add_members(message)
    db.leaderboards()
    if((isinstance(message.channel, discord.abc.PrivateChannel)) or (str(message.author.top_role) == "Jarls") or (message.author == child.user)):
        if "\U0000FEFF" in str(message.content):
            # to add a wave to the welcoming message
            await message.add_reaction('🖐')
        return

    await antispam(message)

    if(message.author.top_role <= discord.utils.get(message.author.guild.roles, name="Marquis")):
        await messageCheck(message)

    add_experience(message)
    await user_level_up(message)

    # this function reduces mute time by 5, not outright unmute.
    await chat_unmute(message)

    await child.process_commands(message)


child.run(b.token, bot=True, reconnect=True)
