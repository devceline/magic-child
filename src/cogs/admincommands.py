import discord
import datetime
from discord.ext import commands
from database_code import db_logic
import botconfig as b
import random


random.seed()
db = db_logic.db_commands()

class AdminCommands:

    def command_allowed(self, member1, member2):
        if member1.top_role > member2.top_role:
            return True
        else:
            return False

    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=''):
        '''Kicks member from the server\n- Zoe, kick Member'''
        if self.command_allowed(ctx.author, member):
            msg = "{0} {1}".format("Run you fluffy cutie thing!", member.mention)
            await ctx.send(msg)
            await ctx.guild.kick(member, reason=reason)
        else:
            await ctx.send("{0.mention}, you don't have permission to do that!".format(ctx.author))

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=''):
        '''Bans member from the server.\n- Zoe, ban Member'''
        if self.command_allowed(ctx.author, member):
            msg = "{0} {1}".format(b.ban_messages[random.randrange(0, 2, 1)],
                                member.mention)
            await ctx.send(msg)
            await ctx.guild.ban(member, reason=reason, delete_message_days=1)
        else:
            await ctx.send("{0.mention}, you don't have permission to do that!".format(ctx.author))

    @commands.command(name="mute")
    @commands.has_permissions(manage_messages=True)
    async def mute(self, ctx, member: discord.Member):
        '''Voice mutes member.\n- Zoe, mute Member'''
        if self.command_allowed(ctx.author, member):
            await member.edit(mute=True)

    @commands.command(name="unmute")
    @commands.has_permissions(manage_messages=True)
    async def unmute(self, ctx, member: discord.Member):
        '''Voice unmutes member.\n- Zoe, unmute Member'''
        if self.command_allowed(ctx.author, member):
            await member.edit(mute=False)
        else:
            await ctx.send("{0.mention}, you don't have permission to do that!".format(ctx.author))

    @commands.command(name="bye")
    async def bye(self, ctx):
        '''Shuts the bot down.\n- Zoe, bye'''
        if(str(ctx.author.top_role) == "Tennō"):
            msg = "Good bye, server owner {0.author.mention}. see ya!". \
                format(ctx)
        elif(str(ctx.author.top_role) == "Developer"):
            msg = "*Beep* *Boop* 🤖 Byebye creator,  {0.author.mention}."\
                .format(ctx)
        else:
            await ctx.send("Bye bye {0}".format(ctx.author.mention))
            return
        await ctx.send(msg)
        print("\nMagic Child exited normally, no errors.\n-------")
        await self.bot.logout()

    @commands.command(name="mutec")
    @commands.has_permissions(manage_messages=True)
    async def mutec(self, ctx, member: discord.Member, minutes):
        '''Chat mutes member.\n Zoe, mutec Member'''
        if self.command_allowed(ctx.author, member):
            db.chat_mute(member, minutes )
            await ctx.send("{0.mention} has been muted".format(member))
            role = "Muted"
            await member.add_roles(discord.utils.get(member.guild.roles, name=role))
        else:
            await ctx.send("{0.mention}, you don't have permission to do that!".format(ctx.author))

    @commands.command(name="unmutec")
    @commands.has_permissions(manage_messages=True)
    async def unmutec(self, ctx, member: discord.Member):
        '''Chat unmutes member.\n- Zoe, unmutec Member'''
        if self.command_allowed(ctx.author, member):
            role = discord.utils.get(member.guild.roles, name="Muted")
            await member.remove_roles(role)
            await ctx.send("{0.mention} has been unmuted".format(member))
        else:
            await ctx.send("{0.mention}, you don't have permission to do that!".format(ctx.author))

    @commands.command(name="say")
    async def say(self, ctx, channel, message):
        '''Send a message to a channel.\n- Zoe, say channel message'''
        channel = discord.utils.get(ctx.guild.channels, name=channel)
        self.developer = discord.utils.get(ctx.guild.roles, name='Developer')
        if self.developer in ctx.author.roles and b.easter_egg_names[2] in str(ctx.author):
            await channel.send(message)

    @commands.command(name="game")
    async def game(self, ctx, game):
        '''Change game presence of Zoe.\n- Zoe, game GameName'''
        self.developer = discord.utils.get(ctx.guild.roles, name='Developer')
        self.tenno = discord.utils.get(ctx.guild.roles, name='Tennō')
        if self.developer or self.tenno in ctx.author.roles:
            game = discord.Game(str(game))
            await self.bot.change_presence(status=discord.Status.online, activity=game)
            await ctx.send("Presence changed!")

    @commands.command(name="embed")
    async def embed(self, ctx, title, channel, embedMessage):
        '''Embed a string.\n- Zoe, embed embedTitle Channel\n"\nEmbed Message here,\n you can use ENTER for new lines\n"'''
        self.developer = discord.utils.get(ctx.guild.roles, name='Developer')
        self.tenno = discord.utils.get(ctx.guild.roles, name='Tennō')
        if self.developer or self.tenno in ctx.author.roles:
            if "-t" in embedMessage:
                time_period = " AM"
                now = datetime.datetime.now()
                hour = now.hour
                minute = now.minute

                if(minute) < 10:
                    minute = "0" + str(minute)

                if (now.hour) > 12:
                    hour= now.hour - 12
                    time_period=" PM"

                now_string = "___***" +  str(now.day) + "/" + str(now.month) + "/" + str(now.year) + \
                             " " +str(hour) + ":" + str(minute) + time_period + " GMT" + "***___"

                embedMessage = embedMessage.replace("-t", now_string)

            embeded = discord.Embed(description=" ", color=0x2ecc71)
            embeded.add_field(name=title, value=embedMessage)
            channel = discord.utils.get(ctx.guild.channels, name=channel)
            await channel.send(content=None, embed=embeded)
def setup(bot):
    bot.add_cog(AdminCommands(bot))
