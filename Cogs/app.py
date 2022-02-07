import discord
import json
import random
import os
from discord.ext import commands, tasks
from discord.utils import get
import asyncio
from datetime import datetime, timedelta
from discord.ext.commands import bot
import Email.db as db
import Email.fetchmail as fetch
import Cogs.Json.jshelper as jshelper
from discord.ext.commands.cooldowns import BucketType
import Utils.helper
import requests
from datetime import datetime
t = BucketType.user
rate = 1
per = 2
BOT_CHANNEL_ID = 939751240374558780
BOT_TEST_CHANNEL_ID = 939753678959693855
data = jshelper.openf("/config/config.json")
async def checkmail(money, codeid):
    endTime = datetime.now() + timedelta(minutes=30)
    while True:
        if datetime.now() >= endTime:
            return False
        all = db.read_useremail()
        for codes in all:
            try:
                code = int(codes[1])
            except:
                continue
            try:
                cash = float(codes[2])
            except:
                continue
            if cash == money and code == codeid:
                return True
        await asyncio.sleep(30)

def gencode():
    number = random.randint(1000, 9999)
    all = db.read_useremail()
    if len(all) == 0:
        return number
    for code in all:
        if number == code:
            return gencode()
        else:
            return number
    

class app(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
    @commands.Cog.listener()
    async def on_ready(self):
        self.log_channel = self.bot.get_channel(938204586777378847)
        data = jshelper.openf("/config/config.json")
        self.price = data["Price"]
        self.ca = f'Cashapp: ${data["cashapp"]}'
        self.vm = f'Venmo: @{data["venmo"]}'
        self.note = data["note"]
        self.role = data["role"] 
        self.fetch_email.start()
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def listprice(self, ctx):
        embed1 = discord.Embed(title="Pay using Cashapp or Venmo",
                               description=f"Cost: ${self.price}.", color=0xf50000)
        await ctx.channel.send(embed=embed1)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setprice(self, ctx, price):
        if price.isnumeric():
            data = jshelper.openf("/config/config.json")
            data["Price"] = int(price)
            self.price = int(price)
            jshelper.savef("/config/config.json", data)
            embed = discord.Embed(title=f"${price} has been set as the price.", color=0xf50000)
            await ctx.send(embed=embed)
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setrole(self, ctx, role: discord.Role):
        data = jshelper.openf("/config/config.json")
        data["role"] = str(role.name)
        self.role = str(role.name)
        jshelper.savef("/config/config.json", data)
        embed = discord.Embed(title=f"{role} has been set as the role.", color=0xf50000)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setpayment(self, ctx, type, addy):
        type = str.lower(type)
        if type == "cashapp":
            data = jshelper.openf("/config/config.json")
            data["cashapp"] = str(addy)
            self.ca = f'Cashapp: ${str(addy)}'
            jshelper.savef("/config/config.json", data)
            embed = discord.Embed(title=f"${addy} has been set as the cashapp address.", color=0xf50000)
            await ctx.send(embed=embed)
        elif type == "venmo":
            data = jshelper.openf("/config/config.json")
            data["venmo"] = str(addy)
            self.vm = f'Venmo: ${str(addy)}'
            jshelper.savef("/config/config.json", data)
            embed = discord.Embed(title=f"@{addy} has been set as the Venmo address.", color=0xf50000)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title=f'Error, Please use ".setpayment (cashapp/venmo) address"', color=0xf50000)
            await ctx.send(embed=embed)

    async def assignrole(self, ctx, role):
        role = get(ctx.guild.roles, name=role)
        await ctx.message.author.add_roles(role, reason="Donated.")

    @commands.command()
    async def cancel(self, ctx):
        if jshelper.checkopen(int(ctx.author.id)):
            await ctx.author.send("Your Previous order has been canceled.")
            jshelper.makeclose(ctx.author.id)
        else:
            await ctx.author.send("Your don't have any orders open.")
    @commands.command()
    async def redeem(self, ctx, *args):
        try:
            steamID = Utils.helper.checkMessageForID(args)
        except Exception as e:
            await ctx.channel.send(f"I could not verify your SteamID")
            return
        params = {
            "steam_id": steamID,
            "discord_id": ctx.author.id,
            "public_key": data['public_key'],
            "public_hash": data['public_hash'],
        }
        ret = requests.get('http://goregaming.net/api/redeem', params=params)
        if (ret.ok):
            try:
                ret = ret.json()
                if (ret['error'] and ret['error_message'] == "user_exists"):
                    await ctx.channel.send(f"Sorry! You have already redeemed your free credits!")
                elif(ret['error'] and ret['error-message'] == "user_does_not_exist"):
                    await ctx.channel.send(f"It looks like you aren't in our store system. Please join the server at least once before trying again!") 
                elif(ret['error']):
                    await ctx.channel.send(f"There was an error! Sending message to an admin.")
                    await self.log_channel.send(f"There was an error! {ret['error_message']}")
                else:
                   await ctx.channel.send(f"Success! 500 credits have been added to your account! You may have to rejoin or wait for a map change before the credits appear.") 
            except Exception as e:
                await self.log_channel.send(f"There was an error with the redeem API return object. Error: {e}")
        else:
            await ctx.channel.send(f"There was an error! Sending message to an admin.")
            await self.log_channel.send(f"There was an error communicating with the redeem API. Server Error: {ret.text}")
        """
        embed = discord.Embed(color=0xf50000, title="VIP Success!", type="rich", description="Name: Limbo\nSteamID: kdjfsdlkjfasidfj\nExpires 27 Dec, 2015")
        embed.set_thumbnail(url='https://cdn.akamai.steamstatic.com/steamcommunity/public/images/avatars/8b/8bcdaf46679de0d4130530318f25abba86d92f17_full.jpg')
        await ctx.channel.send(embed=embed)
        """
    @commands.command()
    async def test(self,ctx, *args):
        if ctx.channel.id != BOT_TEST_CHANNEL_ID:
            return
        try:
            steamID = Utils.helper.checkMessageForID(args)
        except Exception as e:
            print(e)
        else:
            #await ctx.channel.send(f'Found steam account with ID {x}!')
            arguments = {
                "public_key": data['public_key'],
                "public_hash": data['public_hash'],
            }
            res = requests.get(f"https://www.goregaming.net/api/donor/{steamID}", params=arguments)
            if (res.ok):
                print(res.text)
                res = res.json()
                if res['error'] is False:
                    print(res)
                    username = res["username"]
                    expiration = res['expiration_date']
                    profileURL = res['profile_url']
                    embed = discord.Embed(color=0xf50000, title="New VIP User!", type="rich", description=f"Name: {username}\nSteamID: {steamID}\nExpires: {datetime.utcfromtimestamp(expiration).strftime('%d %B, %Y')}")
                    embed.set_thumbnail(url=profileURL)
                    await ctx.channel.send(embed=embed)
                else:
                    error = res["error_message"]
                    await ctx.channel.send(f"There was an Exception from the API Error: {error}");
            else:
                await ctx.channel.send(f"Could not communicate with the API")

    @commands.cooldown(rate, per, t)
    @commands.command(ignore_extra=False)
    async def donate(self, ctx):
        if ctx.channel.id != BOT_TEST_CHANNEL_ID:
            return
        await ctx.channel.send(f'{ctx.author.mention} Please check dms!')
        one  = '1️⃣'
        two = '2️⃣'
        nay = '❌'
        tick = '✅'
        recs = [one,two,nay,tick]
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in recs
        price = self.price
        if jshelper.checkopen(int(ctx.author.id)):
            embed = discord.Embed(color=0xf50000)
            embed.add_field(name=f"ERROR",
                            value=f"Please Finish your existing order before opening a new one. \nOr press {nay} button to cancel your previous order.")
            msg = await ctx.author.send(embed=embed)
            await msg.add_reaction(nay)
            try:
                reaction, ctx.author = await self.bot.wait_for('reaction_add', timeout=120.0, check=check)
            except asyncio.TimeoutError:
                await ctx.author.send("Timed out.")
            else:
                await self.cancel(ctx)
        embed = discord.Embed(title="Choose Payment Method",description=f'Click {one} to donate with Cashapp.\nClick {two} to donate with Venmo.\nThis menu will time out in 2 minutes.',color=0x800080)
        msg = await ctx.author.send(embed=embed)
        await msg.add_reaction(one)
        await msg.add_reaction(two)
        try:
            reaction, ctx.author = await self.bot.wait_for('reaction_add', timeout=120.0, check=check)
        except asyncio.TimeoutError:
            await ctx.author.send("Timed out.")
        else:
            if str(reaction.emoji) == one:
                payment = self.ca
            elif str(reaction.emoji) == two: 
                payment = self.vm
            else:
                ctx.author.send("Incorrect reaction please start over again.")
                return
            number = gencode()
            note = self.note + str(number)
            jshelper.userexsist(ctx.author.id)  
            jshelper.makeopen(ctx.author.id)
            
            embed = discord.Embed(title=f'Payment via {payment}',color=0xf50000)
            embed.add_field(name=f"Price: ${price} \n{payment}\nNote: {note}\nMake sure you send the exact amount with the NOTE.",
                            value=f"This page will timeout in 30 mins.\nClick {tick} once you have sent the payment.")
            msg = await ctx.author.send(embed=embed)
            await ctx.author.send(note)
            await msg.add_reaction(tick)
            try:
                reaction, ctx.author = await self.bot.wait_for('reaction_add', timeout=1800.0, check=check)
            except asyncio.TimeoutError:
                await ctx.author.send("Timed out.")
            else:
                embed = discord.Embed(color=0xf50000)
                embed.add_field(name=f"Please wait while we process your payment!",
                                value=f"Usually takes upto 5 mins.")
                msg = await ctx.author.send(embed=embed)
                checkifright = await checkmail(price, number)
                if checkifright:
                    await msg.delete()
                    embed = discord.Embed(title= "Payment recieved. Thank you!", color=0x00ff00)
                    await ctx.author.send(embed=embed)
                    await self.assignrole(ctx,self.role)
                else:
                    await ctx.author.send(
                        f"Timed out. Payment not Received. Contact server admin if you have paid.")
                jshelper.makeclose(ctx.author.id)
            
    @tasks.loop(seconds=60)
    async def fetch_email(self):
        fetch.fetchmail()


def setup(bot):
    bot.add_cog(app(bot))
