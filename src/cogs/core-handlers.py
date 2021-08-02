import ast
import random
import sqlite3

import discord
from discord.ext import commands, tasks


class Handlers(commands.Cog):
    def __init__(self, hyena):
        self.hyena = hyena
        self.update_stats.start()
        self.hyena.add_check(self.toggle)

    @property
    def category(self):
        return ["None"]

    @tasks.loop(minutes=30)
    async def update_stats(self):
        """This function runs every 30 minutes to automatically update your server count."""
        try:
            await self.hyena.topgg.post_guild_count()
            print(f"Posted server count ({self.hyena.topgg.guild_count})")
        except Exception as e:
            print("Failed to post server count\n{}: {}".format(type(e).__name__, e))

    async def toggle(self, ctx):
        command = str(ctx.command.name)
        db = sqlite3.connect("./data/toggle.sqlite")
        cursor = db.cursor()
        cursor.execute("SELECT command FROM main WHERE guild_id = ?", (ctx.guild.id,))
        data = cursor.fetchall()
        if data is None:
            return True
        if command.lower() in [huh[0] for huh in data]:
            db = sqlite3.connect("./data/toggleconf.sqlite")
            cursor = db.cursor()
            cursor.execute("SELECT * FROM main WHERE guild_id = ?", (ctx.guild.id,))
            data = cursor.fetchone()
            if data is None:
                pass
            else:
                await ctx.send(
                    f"Uh-oh, it seems that the `{command}` command is disabled."
                )
            del data
            return False
        else:
            del data
            return True

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild or message.author.bot:
            return

        prefix = await self.hyena._get_hyena_prefix(self.hyena, message)
        prefix = prefix[0]

        if message.content in [f"<@!{self.hyena.user.id}>", f"<@{self.hyena.user.id}>"]:
            embed = discord.Embed(
                color=random.choice(self.hyena.colours), timestamp=message.created_at
            )
            embed.set_thumbnail(url=message.guild.icon_url)
            embed.set_author(name="Hyena", icon_url=self.hyena.user.avatar.url)
            embed.add_field(
                name="Information",
                value=f"Hey there! 👋🏻 I am Hyena a custom bot made by `Donut#4427` and `Div_100#5748`! Thanks for adding me to your server! I appreciate your support! My prefix for this server is `{prefix}`. Thanks for using me!",
            )
            embed.set_footer(
                icon_url=message.author.avatar.url,
                text=f"Requested by {message.author}",
            )

            await message.reply(embed=embed)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        found = False
        for channel in guild.text_channels:
            try:
                invite = await channel.create_invite(
                    max_age=0, max_uses=0, unique=False
                )
                found = True
                break
            except:
                continue
        if not found:
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).create_instant_invite:
                    try:
                        invite = await channel.create_invite(
                            max_age=0, max_uses=0, unique=False
                        )
                        found = True
                        break
                    except:
                        continue
                else:
                    invite = "Cant generate invite :("
        msg_channel = await self.hyena.fetch_channel(795176316671885332)
        await msg_channel.send(
            f"""
Hyena was added to new guild! Total guilds = {len(self.hyena.guilds)}, Guild Info:
```css
Guild ID: {guild.id}
Guild Name: {guild.name}
Guild Icon: {guild.icon}
Guild Membercount: {guild.member_count}
Guild Invite: {invite}
```
"""
        )
        for channel in guild.text_channels:
            value = random.choice(self.hyena.colours)

            join_embed = discord.Embed(
                title="Hyena Info",
                description=f"Heya! 👋🏻 Thanks For adding me to your server! The default prefix is `-`, hope you enjoy using me!",
                color=value,
            )
            join_embed.set_thumbnail(url=self.hyena.user.avatar_url)
            join_embed.add_field(
                name="Useful Links",
                value=f"[Invite Me](https://discord.com/api/oauth2/authorize?client_id=790892810243932160&permissions=8&scope=bot) | [Support Server](https://discord.gg/cHYWdK5GNt)",
                inline=False,
            )

            try:
                await channel.send(embed=join_embed)
            except:
                pass
            else:
                break

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        msg_channel = await self.hyena.fetch_channel(795176316671885332)
        await msg_channel.send(
            f"""
Hyena was removed from a guild! Total guilds = {len(self.hyena.guilds)}, Guild Info:
```css
Guild ID: {guild.id}
Guild Name: {guild.name}
Guild Icon: {guild.icon}
Guild Membercount: {guild.member_count}
```
"""
        )


def setup(hyena):
    hyena.add_cog(Handlers(hyena))
