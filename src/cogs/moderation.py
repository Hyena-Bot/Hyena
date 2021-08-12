import asyncio
import datetime
import random
from typing import Optional

import discord
from discord.ext import commands
from utilities.data import moderation_actions


class Moderation(commands.Cog):
    def __init__(self, hyena):
        self.hyena = hyena
        self.logging = self.hyena.action_logs_pkg.CommandLogs(self.hyena)

    @commands.command(
        name="ban",
        usage="[p]ban [member] [delete_days] [reason : optional]",
        description="Yeet someone out of the server forever",
    )
    @commands.has_permissions(ban_members=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(
        self,
        ctx,
        member: discord.Member,
        delete_days: Optional[int] = 0,
        *,
        reason="No reason provided",
    ):
        if not delete_days in [0, 1, 7]:
            reason = f"{delete_days} " + reason
        try:
            if (
                ctx.author.top_role > member.top_role
                or ctx.guild.owner == ctx.author
                and not member == ctx.author
            ):
                try:
                    await member.send(
                        f"**{ctx.guild.name}:** You have been 🔨 Banned \n**Reason:** {reason}"
                    )
                except:
                    pass

                await member.ban(
                    delete_message_days=delete_days,
                    reason=f"Banned by: {ctx.author}, Reason: {reason}.",
                )

                await ctx.send(f"🔨 Banned `{member}` \n**Reason:** {reason}")

                embed = discord.Embed(color=random.choice(self.hyena.colors))
                embed.set_author(name=f"BAN | {member}", icon_url=member.avatar.url)
                embed.add_field(name="User", value=f"{member.name}")
                embed.add_field(name="Moderator", value=f"{ctx.author.name}")
                embed.add_field(name="Reason", value=f"{reason}")
                embed.set_footer(
                    text=f"Moderator: {ctx.author}", icon_url=ctx.author.avatar.url
                )

                await self.logging.send(ctx, embed)
                await moderation_actions.log(self.db, self.hyena, {"user_id": member.id, "data": {"action": "Ban", "reason": reason, "delete_days": delete_days}}, ctx)
            else:
                if member == ctx.author:
                    return await ctx.send("You can't ban yourself. 🤦🏻‍")
                else:
                    return await ctx.send(
                        "Error, this person has a higher or equal role to you"
                    )

        except discord.errors.Forbidden:
            return await ctx.send(f"Hmmm, I do not have permission to ban {member}.")

    @commands.command(
        usage="[p]kick [member] [reason : optional]",
        description="Kick someone out of this server :)",
    )
    @commands.has_permissions(kick_members=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):
        try:
            if (
                ctx.author.top_role > member.top_role
                or ctx.guild.owner == ctx.author
                and not member == ctx.author
            ):
                try:
                    await member.send(
                        f"**{ctx.guild.name}:** You have been 🦿 Kicked \n**Reason:** {reason}"
                    )
                except:
                    pass

                await member.kick(reason=f"Kicked by: {ctx.author}, Reason: {reason}.")
                await ctx.send(f"🦿 Kicked `{member}` \n**Reason:** {reason}")

                embed = discord.Embed(color=random.choice(self.hyena.colors))
                embed.set_author(name=f"KICK | {member}", icon_url=member.avatar.url)
                embed.add_field(name="User", value=f"{member.name}")
                embed.add_field(name="Moderator", value=f"{ctx.author.name}")
                embed.add_field(name="Reason", value=f"{reason or 'None'}")
                embed.set_footer(
                    text=f"Moderator: {ctx.author}", icon_url=ctx.author.avatar.url
                )

                await self.logging.send(ctx, embed)
                await moderation_actions.log(self.db, self.hyena, {"user_id": member.id, "data": {"action": "Kick", "reason": reason}}, ctx)
            else:
                if member == ctx.author:
                    return await ctx.send("You can't kick yourself. 🤦🏻‍")
                else:
                    return await ctx.send(
                        "Error, this person has a higher or equal role to you"
                    )
        except discord.errors.Forbidden:
            return await ctx.send(f"Hmmm, I do not have permission to kick {member}.")

    @commands.command(
        aliases=["revoke_ban", "revoke-ban"],
        usage="[p]unban [member]",
        description="Revoke someone's ban",
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx, member, *, reason="No reason provided"):
        member = str(member).strip()
        bans = await ctx.message.guild.bans()
        unbanned_user = None
        success = False

        if member.isnumeric():
            for ban_entry in bans:
                if ban_entry.user.id == int(member):
                    message = await ctx.send("Found ban entry :)")
                    await ctx.guild.unban(ban_entry.user)
                    await message.edit(
                        f"🔓 Unbanned `{ban_entry.user}` \n**Reason:** {reason}"
                    )
                    success = True
                    unbanned_user = ban_entry.user
        else:
            for ban_entry in bans:
                if str(ban_entry.user).lower() == member.lower():
                    message = await ctx.send("Found ban entry :)")
                    await ctx.guild.unban(ban_entry.user)
                    await message.edit(
                        f"🔓 Unbanned `{ban_entry.user}` \n**Reason:** {reason}"
                    )
                    success = True
                    unbanned_user = ban_entry.user

        if success:
            try:
                await unbanned_user.send(
                    f"**{ctx.guild.name}:** You have been 🔓 unbanned \n**Reason:** {reason}"
                )
            except:
                pass

            embed = discord.Embed(color=random.choice(self.hyena.colors))
            embed.set_author(
                name=f"UNBAN | {unbanned_user}", icon_url=unbanned_user.avatar.url
            )
            embed.add_field(name="User", value=f"{unbanned_user.name}")
            embed.add_field(name="Moderator", value=f"{ctx.author.name}")
            embed.set_footer(
                text=f"Moderator: {ctx.author}", icon_url=ctx.author.avatar.url
            )
            await self.logging.send(ctx, embed)
        if not success:
            await ctx.send(
                f"Cannot Find {member}, \nNOTE: You can send both IDs and their proper names whichever you like the most :)"
            )

    @commands.command(
        aliases=["clear"],
        usage="[p]purge [amount]",
        description="Clear messages from a channel",
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(
        commands.has_permissions(manage_channels=True), commands.is_owner()
    )
    @commands.bot_has_permissions(manage_messages=True)
    async def purge(self, ctx, amount, member: discord.Member = None):
        await ctx.message.delete()
        hist = await ctx.channel.history(limit=2).flatten()
        created_at = (datetime.datetime.utcnow() - hist[1].created_at).days
        back = datetime.datetime.utcnow() - datetime.timedelta(days=14)

        if int(created_at) >= 14:
            return await ctx.send(
                "Message is more than 2 weeks old! No messages were deleted :|"
            )

        if amount == "all" or amount == "nuke":
            amount = 1000

        if not amount.isnumeric():
            return await ctx.send(
                "Only `Integers (Numbers), all, nuke` will be accepted"
            )
        amount = int(amount)

        if amount > 100000:
            return await ctx.send(
                "Smh so many messages :| Delete the channel instead dumb"
            )

        if member is not None:
            purged_messages = await ctx.channel.purge(
                limit=amount,
                after=back,
                check=lambda x: not x.pinned and x.author.id == member.id,
            )
            p = len(purged_messages)
            message = await ctx.send(
                f"Successfully purged `{p}` messages from `{member.name}` in the last `{amount}` messages!"
            )
        else:
            purged_messages = await ctx.channel.purge(
                limit=amount,
                after=back,
                check=lambda message_to_check: not message_to_check.pinned,
            )
            p = len(purged_messages)
            message = await ctx.send(f"Purged `{p}` messages!")
        await asyncio.sleep(2)
        await message.delete()

    @commands.command(
        name="lockchannel",
        aliases=["lock"],
        usage="[p]lock [channel : optional]",
        description="Lock a channel so that people can't talk in it",
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(
        commands.has_permissions(manage_channels=True), commands.is_owner()
    )
    @commands.bot_has_permissions(manage_channels=True)
    async def lock_channel(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel

        try:
            await channel.set_permissions(ctx.guild.roles[0], send_messages=False)
            await ctx.send(f"🔒 The channel {channel.mention} has been locked")
        except:
            return await ctx.send("I dont seem to have the permissions")

        embed = discord.Embed(colour=random.choice(self.hyena.colors))
        embed.set_author(name=f"LOCK | {channel.name}", icon_url=ctx.author.avatar.url)
        embed.add_field(name="Channel", value=f"{channel.name}")
        embed.add_field(name="Moderator", value=f"{ctx.author.name}")
        embed.set_footer(
            text=f"Moderator: {ctx.author}", icon_url=ctx.author.avatar.url
        )

        await self.logging.send(ctx, embed)

    @commands.command(
        name="unlockchannel",
        aliases=["unlock"],
        usage="[p]unlock [channel : optional]",
        description="Unlock channel to give access to the people to talk in the channel",
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(
        commands.has_permissions(manage_channels=True), commands.is_owner()
    )
    @commands.bot_has_permissions(manage_channels=True)
    async def unlock_channel(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel

        try:
            await channel.set_permissions(ctx.guild.roles[0], send_messages=True)
            await ctx.send(f"🔓 The channel {channel.mention} has been unlocked")
        except:
            return await ctx.send("I dont seem to have the permissions")

        embed = discord.Embed(colour=random.choice(self.hyena.colors))
        embed.set_author(
            name=f"UNLOCK | {channel.name}", icon_url=ctx.author.avatar.url
        )
        embed.add_field(name="Channel", value=f"{channel.name}")
        embed.add_field(name="Moderator", value=f"{ctx.author.name}")
        embed.set_footer(
            text=f"Moderator: {ctx.author}", icon_url=ctx.author.avatar.url
        )

        await self.logging.send(ctx, embed)

    @commands.command(
        name="nuke",
        aliases=["clone"],
        usage="[p]nuke [channel : optional]",
        description="Delete and clone a channel to clear all of the messages",
    )
    @commands.cooldown(1, 20, commands.BucketType.user)
    @commands.bot_has_permissions(manage_channels=True)
    async def nuke(self, ctx, channel: discord.TextChannel = None):
        if ctx.author != ctx.guild.owner:
            return await ctx.send("Owner only command for now!")
        blacklisted_guilds = [
            829590074831667230,
            794467787690344508,
            757823432875442226,
        ]

        if (
            ctx.guild.id in blacklisted_guilds
            and not ctx.author.id in self.hyena.owner_ids
        ):
            return await ctx.send(
                "This command is disabled for this guild. This is managed directly by bot owners Donut#4427 and Div_100#5748. \n\nWhat can you do? Try and appeal this case in the support server: `https://discord.gg/cHYWdK5GNt` if the owner accepts it, it's good else you're done for. <:kek:826293846689185842>"
            )
        if channel is None:
            channel = ctx.channel

        msg = await ctx.send(
            "Are you sure you want to nuke (delete and clone a new one) this channel?"
        )
        await ctx.send("https://tenor.com/view/nuke-press-button-gif-14853646")

        try:
            await msg.add_reaction("✅")
            await msg.add_reaction("❌")
            await asyncio.sleep(0.5)
        except:
            return await ctx.send("Uh oh! I cant add reactions || gib perms nub ||")

        try:
            reaction, user = await self.hyena.wait_for(
                "reaction_add",
                timeout=30,
                check=lambda reaction, user: user == ctx.author
                and str(reaction.emoji) == "✅"
                or "❌",
            )
        except asyncio.TimeoutError:
            try:
                msg.remove_reaction("✅", ctx.guild.me)
                msg.remove_reaction("❌", ctx.guild.me)
            except:
                pass
        else:
            del user
            if str(reaction.emoji) == "✅":
                position = channel.position
                category = channel.category
                name = channel.name
                overwrites = channel.overwrites
                topic = channel.topic
                is_nsfw = channel.is_nsfw()
                slowmode = channel.slowmode_delay

                try:
                    await channel.delete(
                        reason=f"Channel nuke by: {ctx.author}, channel: {channel}"
                    )
                    channel2 = await ctx.guild.create_text_channel(
                        name=name,
                        overwrites=overwrites,
                        category=category,
                        position=position,
                        topic=topic,
                        slowmode_delay=slowmode,
                        nsfw=is_nsfw,
                        reason=f"Channel nuke by: {ctx.author}, channel: {channel}",
                    )
                except discord.errors.Forbidden:
                    return await ctx.send("I cant do that action")
                except:
                    pass

                await channel2.send(
                    "Nuked this channel <a:NukeExplosion:799910729435316234>"
                )
                await channel2.send(
                    "https://tenor.com/view/nuclear-explosion-nuke-bomb-boom-gif-16286228"
                )

                em = discord.Embed(colour=random.choice(self.hyena.colors))
                em.set_author(
                    name=f"NUKE | {channel.mention}", icon_url=ctx.author.avatar.url
                )
                em.add_field(name="Channel", value=channel.name)
                em.add_field(name="Moderator", value=ctx.author)
                em.set_footer(
                    text=f"Moderator: {ctx.author}", icon_url=self.hyena.user.avatar.url
                )

                self.logging.send(ctx, em)
            else:
                await ctx.send("K! I will not nuke this channel!")

    @commands.command(
        name="softban",
        description="Bans and immediately unbans a member to act as a purging kick.",
        usage="[p]softban [member] [delete_days : optional] [reason : optional]",
    )
    @commands.check_any(commands.has_permissions(ban_members=True), commands.is_owner())
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.bot_has_permissions(ban_members=True)
    async def softban(
        self,
        ctx,
        member: discord.Member,
        delete_days: Optional[int] = 1,
        *,
        reason="No reason provided",
    ):
        if not delete_days in [0, 1, 7]:
            reason = f"{delete_days} " + reason

        if ctx.author == member:
            return await ctx.send("Imagine banning yourself. 🤦🏻‍")

        if (
            ctx.author.top_role <= member.top_role
            and not ctx.author.id == ctx.guild.owner.id
        ):
            return await ctx.send(
                f"Your top role `{ctx.author.top_role}` is smaller or equal to {member}'s top role `{member.top_role}"
            )

        await ctx.guild.ban(
            member,
            reason="Softbanned by " + str(ctx.author),
            delete_message_days=delete_days,
        )
        await ctx.guild.unban(member, reason="Softbanned by " + str(ctx.author))

        try:
            await member.send(
                f"**{ctx.guild.name}:** You have been 🔨 Softbanned \n**Reason:** {reason}"
            )
        except:
            pass

        await ctx.send(f"🔨 Softbanned `{member}` \n**Reason:** {reason}")

        embed = discord.Embed(color=random.choice(self.hyena.colors))
        embed.set_author(name=f"SOFTBAN | {member}", icon_url=member.avatar.url)
        embed.add_field(name="User", value=f"{member.name}")
        embed.add_field(name="Moderator", value=f"{ctx.author.name}")
        embed.add_field(name="Reason", value=f"{reason}")
        embed.add_field(name="Delete Days", value=delete_days)
        embed.set_footer(
            text=f"Moderator: {ctx.author}", icon_url=ctx.author.avatar.url
        )

        await self.logging.send(ctx, embed)
        await moderation_actions.log(self.db, self.hyena, {"user_id": member.id, "data": {"action": "SotBan", "reason": reason, "delete_days": delete_days}}, ctx)

    @commands.command(
        name="nickname",
        aliases=["nick"],
        usage="[p]nickname [member] [nickname : optional]",
        description="Change the nickname of a member",
    )
    @commands.bot_has_permissions(manage_nicknames=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def nickname(self, ctx, member: discord.Member, *, nickname=None):
        if nickname == None:
            nickname = member.name
        if ctx.author == member:
            try:
                await member.edit(nick=nickname)
            except:
                return await ctx.send(
                    "Uh oh! Something went wrong, seems like the bot doesn't have the permissions"
                )

        if ctx.author.guild_permissions.manage_nicknames:
            return await ctx.send(
                "> <:NO:800323400449916939> You are missing the `manage_nicknames` permission(s)!"
            )

        if member.top_role >= ctx.author.top_role:
            return await ctx.send("You cannot do this action due to the role hierarchy")

        try:
            await member.edit(nick=nickname)
        except:
            return await ctx.send(
                "Uh oh! Something went wrong, seems like the bot doesn't have the permissions"
            )
        await ctx.send(f"Changed {member.name}'s nickname to `{nickname}`")


def setup(hyena):
    hyena.add_cog(Moderation(hyena))
