import random
import time

import discord
from discord.ext import commands


class Afk(commands.Cog):
    def __init__(self, hyena, colours):
        self.hyena = hyena
        self.colours = colours
        self._afk = {}

    @property
    def category(self):
        return ["Utils"]

    @commands.command(
        name="afk",
        description="Set an AFK status to display when you are mentioned",
        usage="[p]afk [reason : optional]",
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def afk(self, ctx, *, reason="AFK"):
        data = self._afk.get(ctx.guild.id)
        if data is None:
            self._afk[ctx.guild.id] = []
        data = []
        ids = [e[0] for e in data]
        if ctx.author.id in ids:
            return
        data.append((ctx.author.id, reason, time.time()))
        self._afk[ctx.guild.id] = data

        await ctx.reply(f"{ctx.author.mention} I set your AFK: {reason}")
        nick = ctx.author.display_name
        nick = nick[:24] + ".." if len(str(nick)) > 26 else nick

        try:
            await ctx.author.edit(nick=f"[AFK] {nick}")
        except:
            pass

    async def remove_afk(self, message, guild_data):
        ctx = await self.hyena.get_context(message)
        if str(ctx.command) == "afk":
            return
        if (
            not list(
                filter(
                    message.content.lower().startswith,
                    [
                        "hyena no unafk",
                        "no unafk",
                        "hyena don't unafk",
                        "do not unafk",
                        "don't unafk",
                    ],
                )
            )
            == []
        ):
            return
        for data_block in guild_data:
            if message.author.id in data_block:
                if time.time() - data_block[2] < 10:
                    await message.channel.send(
                        f"{message.author.mention}, A little too quick there!"
                    )
                    return
                guild_data.remove(data_block)
        self._afk[message.guild.id] = guild_data
        await message.reply(f"Welcome back {message.author}")
        if message.author.display_name.startswith("[AFK]"):
            try:
                await message.author.edit(nick=message.author.display_name[6:])
            except:
                pass

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None or message.author.bot:
            return
        mentions = message.mentions
        guild_data = self._afk.get(message.guild.id)
        if guild_data is None or guild_data == []:
            return
        ids = [e[0] for e in guild_data]
        if message.author.id in ids:
            return await self.remove_afk(message, guild_data)

        if len(mentions) == 0:
            return
        for men in mentions:
            if men.id in ids:
                reason = "AFK"
                timestamp = None
                for data_block in guild_data:
                    if men.id in data_block:
                        reason = data_block[1]
                        timestamp = data_block[2]
                await message.reply(f"{men} is AFK: {reason} - <t:{int(timestamp)}:R>")
                break


def setup(hyena):
    hyena.add_cog(
        Afk(hyena, [0xFFED1B, 0xF1EFE3, 0x00A8FE, 0x1FEDF9, 0x7CF91F, 0xF91F43])
    )
