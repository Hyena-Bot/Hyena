import discord
import aiohttp
import io
import random
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType




class ImageFun(commands.Cog):
    def __init__(self, hyena, colors):
        self.hyena = hyena
        self.hyena.colors = colors
        
    
    @property
    def data(self):
        return ["Image Fun"]

# commands:
 
 # Triggered

    @commands.command()
    @commands.cooldown(1, 3, BucketType.user)
    async def triggered(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author

        async with aiohttp.ClientSession() as trigSession:
            async with trigSession.get(f'https://some-random-api.ml/canvas/triggered?avatar={member.avatar.url}') as trigImg: # get users avatar as png with 1024 size
                triggerData = io.BytesIO(await trigImg.read()) 
                file = discord.File(triggerData, 'triggered.gif')

                embed = discord.Embed(color = random.choice(self.hyena.colors))
                embed.set_author(name = f"{member.name} is triggered", icon_url= member.avatar.url)
                embed.set_image(url = 'attachment://triggered.gif')

                await trigSession.close()


                await ctx.send(file = file, embed = embed) 
# wasted 

    @commands.command()
    @commands.cooldown(1, 3, BucketType.user)
    async def wasted(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author

        async with aiohttp.ClientSession() as wastedSession:
            async with wastedSession.get(f'https://some-random-api.ml/canvas/wasted?avatar={member.avatar.url}') as wasteImg: # get users avatar as png with 1024 size
                wastedData = io.BytesIO(await wasteImg.read()) 
                file = discord.File(wastedData, 'wasted.png')

                embed = discord.Embed(color = random.choice(self.hyena.colors))
                embed.set_author(name = f"{member.name} has been wasted :|", icon_url= member.avatar.url)
                embed.set_image(url = 'attachment://wasted.png')

                await wastedSession.close()
                
                await ctx.send(file = file, embed = embed)
# mission passed

    @commands.command()
    @commands.cooldown(1, 3, BucketType.user)
    async def passed(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author

        async with aiohttp.ClientSession() as passedSession:
            async with passedSession.get(f'https://some-random-api.ml/canvas/passed?avatar={member.avatar.url}') as passImg: # get users avatar as png with 1024 size
                passedData = io.BytesIO(await passImg.read()) 
                file = discord.File(passedData, 'passed.png')

                embed = discord.Embed(color = random.choice(self.hyena.colors))
                embed.set_author(name = f"{member.name} has passed the mission :)", icon_url= member.avatar.url)
                embed.set_image(url = 'attachment://passed.png')

                await passedSession.close()
 
                await ctx.send(file = file, embed = embed)

# jail 

    @commands.command()
    @commands.cooldown(1, 3, BucketType.user)
    async def jail(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author

        async with aiohttp.ClientSession() as jailSession:
            async with jailSession.get(f'https://some-random-api.ml/canvas/jail?avatar={member.avatar.url}') as jailedImg: # get users avatar as png with 1024 size
                jailData = io.BytesIO(await jailedImg.read()) 
                file = discord.File(jailData, 'jailed.png')

                embed = discord.Embed(color = random.choice(self.hyena.colors))
                embed.set_author(name = f"{member.name} was just sent to jail ;-;", icon_url= member.avatar.url)
                embed.set_image(url = 'attachment://jailed.png')

                await jailSession.close()
                
                await ctx.send(file = file, embed = embed)

# comrade

    @commands.command()
    @commands.cooldown(1, 3, BucketType.user)
    async def comrade(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author

        async with aiohttp.ClientSession() as comradeSession:
            async with comradeSession.get(f'https://some-random-api.ml/canvas/comrade?avatar={member.avatar.url}') as comradeImg: # get users avatar as png with 1024 size
                comradeData = io.BytesIO(await comradeImg.read()) 
                file = discord.File(comradeData, 'comrade.png')

                embed = discord.Embed(color = random.choice(self.hyena.colors))
                embed.set_author(name = f"{member.name} was forced to become a comrade ???", icon_url= member.avatar.url)
                embed.set_image(url = 'attachment://comrade.png')

                await comradeSession.close()
                
                await ctx.send(file = file, embed = embed)

# pixelssssssssss

    @commands.command()
    @commands.cooldown(1, 3, BucketType.user)
    async def pixelate(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author

        async with aiohttp.ClientSession() as pixelSession:
            async with pixelSession.get(f'https://some-random-api.ml/canvas/pixelate?avatar={member.avatar.url}') as pixelImg: # get users avatar as png with 1024 size
                pixelData = io.BytesIO(await pixelImg.read()) 
                file = discord.File(pixelData, 'pixelated.png')

                embed = discord.Embed(color = random.choice(self.hyena.colors))
                embed.set_author(name = f"{member.name} why did u even do this ?", icon_url= member.avatar.url)
                embed.set_image(url = 'attachment://pixelated.png')

                await pixelSession.close()
                

                await ctx.send(file = file, embed = embed)
# hmmmm
    
    @commands.command()
    @commands.cooldown(1, 3, BucketType.user)
    async def comment(self, ctx, member: discord.Member = None, *,comment = "Next time provide a comment nub."):
        if not member:
            member = ctx.author

        async with aiohttp.ClientSession() as ytSession:
            async with ytSession.get(f'https://some-random-api.ml/canvas/youtube-comment?avatar={member.avatar.url}&username={member.name}&comment={comment}') as commnt: # get users avatar as png with 1024 size
                commentData = io.BytesIO(await commnt.read()) 
                file = discord.File(commentData, 'pixelated.png')

                embed = discord.Embed(color = random.choice(self.hyena.colors))
                embed.set_author(name = f"{member.name} Just commented", icon_url= member.avatar.url)
                embed.set_image(url = 'attachment://pixelated.png')

                await ytSession.close()
                
                await ctx.send(file = file, embed = embed)


                 
        
        

# ---------------------------- End of Image Fun ---------------------------------

# The text fun commands go below

class TextFun(commands.Cog):
    def __init__(self, hyena, colors):
        self.hyena = hyena
        self.colors = colors

    @property
    def data(self):
        return ["Text Fun"]

# commands:

    @commands.command()
    async def sus(self, ctx):
        await ctx.send("SUSU")



    

# ---------------------------- End of Text Fun ---------------------------------
  

# setup stuff

def setup(hyena):
    hyena.add_cog(TextFun(hyena, hyena.colors))
    hyena.add_cog(ImageFun(hyena, hyena.colors))
