import discord
from discord.ext import commands
import botconfig
from database_code import db_logic

db = db_logic.db_commands()


class KeepingCommands:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hello(self, ctx):
        '''Greeting.\n- Zoe, hello'''
        if(str(ctx.author.top_role) == "Tennō"):
            msg = "Hello there, server owner {0.author.mention}.".format(ctx)
            "Have a nice day!"
        elif(str(ctx.author.top_role) == "Developer"):
            msg = "*Beep* *Boop* 🤖 Hello creator,  {0.author.mention}." \
                .format(ctx)
        elif(botconfig.easter_egg_names[0] in str(ctx.author) or
             botconfig.easter_egg_names[1] in str(ctx.author)):
            msg = botconfig.easter_egg_msgs[0]
        else:
            msg = "Hiya, I'm Zoe! {0.author.top_role} {0.author.mention}" \
                .format(ctx)
        await ctx.send(msg)

    @commands.command()
    async def love(self, ctx, member: discord.Member = None):
        '''Tells you what Zoe loves.\n- Zoe, love (Member)'''
        if not member:
            await ctx.send("I love video games.")
        else:
            await ctx.send(f"Oh I totes love {member} but Ezreal has my"
                           "heart.")

    @commands.command()
    async def rank(self, ctx, roles=botconfig.roles):
        '''Shows your rank.\n- Zoe, rank'''
        rank = roles[db.read_xp(ctx)[0]]
        embed = discord.Embed(title='Rank:', description="{0}, your rank is {1}!"
        .format(ctx.author.mention, rank), colour=ctx.author.colour)
        embed.set_author(icon_url=ctx.author.avatar_url,
                         name=str(ctx.author))
        await ctx.channel.send(content=None, embed=embed)

    @commands.command()
    async def give(self, ctx, role=None):
        '''Give yourself a game rank.\n- Zoe, give (role)'''
        role_keys = list(botconfig.game_roles.keys())
        if role is not None:
            if role in botconfig.game_roles:
                await ctx.author.add_roles(discord.utils.get(ctx.author.guild.roles, name=botconfig.game_roles[role]))
                await ctx.channel.send("Added role!")
        else:
            embed = discord.Embed(title='Game Roles:', description="*Note: Use the plain text above the role, don't mention!", colour=0x2ecc71)
            i = 0
            for role in botconfig.game_roles:
                embed.add_field(name=role_keys[i], value=discord.utils.get(ctx.author.guild.roles, name=botconfig.game_roles[role]).mention)
                i+=1
            embed.add_field(name="\uFEFF", value="\uFEFF")
            await ctx.channel.send(content= None,embed=embed)

    @commands.command() # remove a role
    async def remove(self, ctx, role):
        '''Removes a color role or game role.\n- Zoe, remove Role'''
        if role in botconfig.game_roles and discord.utils.get(ctx.author.guild.roles, name=botconfig.game_roles[role]) in ctx.author.roles:
            await ctx.author.remove_roles(discord.utils.get(ctx.author.guild.roles, name=botconfig.game_roles[role]))
            await ctx.send("Role removed!")
        else:
            if role in botconfig.game_roles:
                await ctx.send("You don't even have that role.")
            else:
                await ctx.send("Huh? I can only remove your game roles.")

    @commands.command()
    async def leaderboards(self, ctx):
        '''Displays the richest members.\n- Zoe, leaderboards'''
        leaders = db.leaderboards()
        embed = discord.Embed(title="Leaderboards: ", colour=0x2ecc71)
        embed.add_field(name="\uFEFF", value="\uFEFF")
        embed.add_field(name=" 1. " + leaders[0][0].replace("_", "#"), value=str(leaders[0][1]) + "\U0001F4B8")
        embed.add_field(name="\uFEFF", value="\uFEFF") # two extra fields to center the number one spot
        for i in range(1, 10):
           embed.add_field(name=str(i+1) + ". " + leaders[i][0].replace("_","#"), value=str(leaders[i][1]))
        await ctx.send(content=None, embed=embed)

    @commands.command()
    async def help(self, ctx, category=None):
        '''Displays this message\n- Zoe, help'''
        if category == None:
            embed = discord.Embed(description="Use help `Category`" ,colour=0x2ecc71)
            embed.set_author(name="Categories:")
            embed.add_field(name="House Keeping Commands", value="Zoe, help house", inline=False)
            embed.add_field(name="Admin Commands", value="Zoe, help admin", inline=False)
            embed.add_field(name="Economy Commands", value="Zoe, help economy", inline=False)
            await ctx.send(content=None, embed=embed)

        elif category == "house":
            embed = discord.Embed(description="General commands\n*Arguements in brackets are optional." ,colour=0x2ecc71)
            embed.set_author(name="House Keeping")

            for command in list(self.bot.get_cog_commands("KeepingCommands")):
                embed.add_field(name=str(command).capitalize(), value=command.help, inline=False)

            await ctx.send(content=None, embed=embed)

        elif category == "admin":
            embed = discord.Embed(description="Admin/Moderator commands" ,colour=0x2ecc71)
            embed.set_author(name="Admin")

            for command in list(self.bot.get_cog_commands("AdminCommands")):
                embed.add_field(name=str(command).capitalize(), value=command.help, inline=False)

            await ctx.send(content=None, embed=embed)

        elif category == "economy":
            embed = discord.Embed(description="Currency commands\n*Arguements in brackets are optional." ,colour=0x2ecc71)
            embed.set_author(name="Economy")

            for command in list(self.bot.get_cog_commands("EconomyCommands")):
                embed.add_field(name=str(command).capitalize(), value=command.help, inline=False)

            await ctx.send(content=None, embed=embed)
        else:
            await ctx.send("That's not a category.")


def setup(bot):
    bot.add_cog(KeepingCommands(bot))
