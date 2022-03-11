import discord
from discord.ext import commands
import botconfig as b
import datetime
from database_code import db_logic
import random

db = db_logic.db_commands()

class EconomyCommands:

    daily_users = {}
    gamble_users = {}

    def __init__(self, bot):
        self.bot = bot

    async def has_funds(self, member, amount):
        if(amount < db.get_balance(member)):
            return True
        else:
            return False

    async def send_new_balance(self, member, target=None):
        if target is not None:
            embed = discord.Embed(title="Balance", description="{0}".format(db.get_balance(target)))
            embed.set_author(icon_url=target.avatar_url, name=str(target))
        else:
            embed = discord.Embed(title="Balance", description="{0}".format(db.get_balance(member)))
            embed.set_author(icon_url=member.avatar_url, name=str(member))
        await member.send(content=None, embed= embed)

    @commands.command()
    async def daily(self, ctx):
        '''Gives you your daily Bubbles\n- Zoe, daily'''
        if str(ctx.author) not in self.daily_users or (datetime.datetime.now() - self.daily_users[str(ctx.author)]).total_seconds() > 86400:
            # 86400 seconds in a day.
            number = random.randrange(50,251,5) # fill a value here
            db.add_currency(ctx.author, number)
            await ctx.channel.send(str(number) + " added to your account!")
            self.daily_users[str(ctx.author)] = datetime.datetime.now()
            #await self.send_new_balance(ctx.author)
        else:
            await ctx.channel.send("Come back in about {0} hours, {1} minutes."
                                    .format(
                                    23 - int((datetime.datetime.now()- self.daily_users[str(ctx.author)]).total_seconds()/3600),
                                    60 - int((datetime.datetime.now() - self.daily_users[str(ctx.author)]).total_seconds()%3600/60)
                                    )
                                    )

    @commands.command()
    async def gamble(self, ctx, amount):
        '''Gamble an amount twice per day\n- Zoe, gamble Amount'''
        amount = int(amount)
        if str(ctx.author) not in self.gamble_users or (datetime.datetime.now() - self.gamble_users[str(ctx.author)]).total_seconds() > 43200:
            if(await self.has_funds(ctx.author, amount)):
                db.deduct_currency(ctx.author, amount)
                new_amount = amount * b.gamble_multipliers[random.randrange(len(b.gamble_multipliers))]
                db.add_currency(ctx.author, new_amount)
                return_amount = new_amount-amount
                if return_amount < 0:
                    await ctx.send("Unlucky! \U0001F912. You lost " + str(return_amount) + " bubbles.")
                elif return_amount > 0:
                    await ctx.send("Congratulations! \U0001F911. You gained " + str(return_amount) + " bubbles!")
                else:
                    await ctx.send("You gained nothing... \U0001F605")
                #await self.send_new_balance(ctx.author)
                self.gamble_users[str(ctx.author)] = datetime.datetime.now()
            else:
                await ctx.send("Not enough funds. \U0001F915")
        else:
            await ctx.channel.send("Come back in about {0} hours, {1} minutes."
                                    .format(
                                    int((23 - int((datetime.datetime.now()- self.daily_users[str(ctx.author)]).total_seconds()/3600))/2),
                                    (60 - int((datetime.datetime.now() - self.daily_users[str(ctx.author)]).total_seconds()%3600/60))/2
                                    )
                                    )


    @commands.command()
    async def trade(self, ctx, member: discord.Member, amount):
        '''Give some of your Bubbles to another member.\n- Zoe, trade Member Amount'''
        amount = int(amount)
        if(await self.has_funds(ctx.author, amount)):
            db.deduct_currency(ctx.author, amount)
            db.add_currency(member, amount)
            await ctx.send(f"Gave {member} {amount}")
            await self.send_new_balance(ctx.author)
            await self.send_new_balance(member)
        else:
            await ctx.send("Not enough funds. \U0001F915")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def fund(self, ctx, member: discord.Member, amount):
        '''(Admin Only)Gives a user's Bubbles.\n- Zoe, fund Member Amount'''
        db.add_currency(member, amount)
        await ctx.send(f"Gave {member} {amount} ")
        await self.send_new_balance(member)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def deduct(self, ctx, member: discord.Member, amount):
        '''(Admin Only)Deduces a user's Bubbles.\n- Zoe, deduct Member Amount'''
        amount = int(amount)
        db.add_currency(member, amount*-1)
        await ctx.send(f"Deduced {amount} from {member}")
        await self.send_new_balance(member)


    @commands.command()
    async def buy(self, ctx, role=None):
        '''Buys a role.\n- Zoe, buy (Role)'''
        if role in b.bought_roles:
            if(await self.has_funds(ctx.author, b.bought_roles[role])):
                db.deduct_currency(ctx.author, b.bought_roles[role])
                await ctx.author.add_roles(discord.utils.get(ctx.author.guild.roles, name=role))
                await ctx.channel.send("Added role!")
                await self.send_new_balance(ctx.author)
            else:
                await ctx.send("Not enough funds!")
        else:
            embed = discord.Embed(title='Roles:\n*Color roles cost 1000 Bubbles each.\n*Event roles costs vary', description="", colour=0x2ecc71)
            for roles in b.bought_roles:
                embed.add_field(name=b.bought_roles[roles], value=discord.utils.get(ctx.author.guild.roles, name=roles).mention)
            await ctx.channel.send(content= None,embed=embed)

    @commands.command()
    async def balance(self, ctx, member: discord.Member = None):
        '''Check your balance, or someone elses.\n Zoe, balance (Member)'''
        if not member:
            await self.send_new_balance(ctx.author)
        else:
            await self.send_new_balance(ctx.author, member)


def setup(bot):
    bot.add_cog(EconomyCommands(bot))
