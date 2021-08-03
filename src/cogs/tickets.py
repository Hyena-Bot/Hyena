import asyncio
import random
from fileinput import close

import discord
from discord.ext import commands


async def close_ticket(channel, hyena):
    if not channel.name.startswith("ticket-"):
        return await channel.send(
            "Channel is not a valid ticket, did you accidentally run the command in the wrong channel."
        )

    topic = channel.topic.split("-")
    id = topic[0].strip()
    if not id.isnumeric():
        return await channel.send(
            "Channel's topic does not start with the User ID, Please make sure that the channel topic starts with the ID of the user who opened the ticket."
        )

    id = int(id)
    try:
        member = await channel.guild.fetch_member(id)
    except:
        member = None
    data = await hyena.main_db2.fetchrow(
        "SELECT * FROM tickets WHERE guild_id = $1", channel.guild.id
    )
    transcript = f'Hyena Ticket Logging -{channel.guild.name} Transcript for member {str(member) or "Member left the server"}\n\n'

    try:
        history = channel.history(limit=256)
        _history = ""
        async for message in history:
            _history += f"{message.author}: {message.content} {('Files: ' + ', '.join(file.url for file in message.attcahments)) if len(message.attachments) > 0 else ''}"

        history = _history
    except Exception as e:

        history = "Unable to fetch messages"

    transcript += history
    with open(f"./assets/tickets/{channel.name}.txt", "w") as f:
        f.writelines(transcript)

    _channel = data[1]
    try:
        _channel = await hyena.fetch_channel(_channel)
    except Exception as e:
        _channel = None

    if _channel is not None:
        try:
            m = await _channel.send(
                f"Transcript for {member} -{channel.guild.name}",
                file=discord.File(f"./assets/tickets/{channel.name}.txt"),
            )
        except Exception as e:
            m = None

    if data[4] in ["yes", None]:
        try:
            await member.send(
                f"Here is your transcript for the ticket you opened in `{channel.guild.name}`",
                file=discord.File(f"./assets/tickets/{channel.name}.txt"),
            )
        except Exception as e:
            try:
                await m.reply("Unable to DM the user.")
            except:
                pass

    try:
        await channel.delete()
    except:
        await channel.send(
            "Unable to close the ticket, Please make sure I have manage channel permissisons."
        )


class View(discord.ui.View):
    def __init__(self, hyena):
        self.hyena = hyena
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Close Ticket",
        custom_id="close-ticket-tickets",
        style=discord.ButtonStyle.red,
        emoji="🔒",
    )
    async def test_callback(self, button, interaction):
        await interaction.response.send_message(
            "Closing Ticket, Please allow upto 3 seconds.", ephemeral=True
        )
        self.stop()
        await close_ticket(interaction.message.channel, self.hyena)


class Tickets(commands.Cog):
    def __init__(self, hyena, colours) -> None:
        self.hyena = hyena
        self.colours = colours
        self.db = hyena.main_db2
        self.loaded_ui = False

    @commands.Cog.listener()
    async def on_ready(self):
        self.hyena.add_view(View(self.hyena))

    @property
    def category(self):
        return ["Utils"]

    @commands.group(
        name="tickets",
        aliases=["ticket", "hyena-tickets", "hyena-ticket"],
        usage="[p]tickets",
        description="Wanna let users get help right from the server staff? Without having to go through th ahssle of a modmail? That too highly customizale? Hyena gotcha. Run [p]ticket for further help",
    )
    async def tickets(self, ctx):
        embed = discord.Embed(color=random.choice(self.hyena.colors))
        embed.set_author(name="Hyena Tickets", icon_url=self.hyena.user.avatar.url)
        embed.description = """
<:info:846642194052153374> Setup hyena for a super helpful and hassle-free tickets system.

**Commands:**
`setup` : Run an interactive setup
`transcript`: Change the transcript channel without having to run the setup process again.
`role`: Change the role ping without having to run the setup process again.
`dm`: Change whether to DM users after their tickets have been closed without having to run the setup process again.
`create`: Create a new ticket.
`close`: Close the current ticket - Can only be used in tickets
`disable`: Disable the ticket system.

**Privacy stuff:**
Data we store:
`Guild ID` 
`Category ID`
`Transcript Channel ID`
`Ping Role ID`
`Whether to DM users or not`

NOTE: All of the data mentioned above will be deleted from our database when you run the `disable` command.
"""
        embed.set_image(
            url="https://media.discordapp.net/attachments/849164318344085514/872107087092674560/unknown.png"
        )
        embed.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url
        )

        await ctx.send(embed=embed)

    @tickets.command(name="setup", aliases=["enable"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, type=commands.BucketType.guild)
    async def ticket_enable(self, ctx):
        if not ctx.guild.me.guild_permissions.manage_channels:
            return await ctx.send(
                "I do not have the Manage Server permission please check and try again."
            )

        overwrites = {
            ctx.guild.me: discord.PermissionOverwrite(
                manage_messages=True,
                manage_channels=True,
                add_reactions=True,
                use_external_emojis=True,
                send_messages=True,
                embed_links=True,
                attach_files=True,
                read_messages=True,
                read_message_history=True,
            ),
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        }
        for role in ctx.guild.roles:
            if role.permissions.manage_channels:
                overwrites[role] = discord.PermissionOverwrite(
                    send_messages=True,
                    embed_links=True,
                    read_messages=True,
                    read_message_history=True,
                    attach_files=True,
                )
        embed = discord.Embed(
            title="Hyena Ticket Setup",
            description="Alright, Let's get this started! \nYou will get **30** seconds to answer each question.\nType **Abort** at any time to cancel this.",
            color=random.choice(self.hyena.colors),
        )
        embed.set_footer(text="Hyena Tickets!", icon_url=self.hyena.user.avatar.url)
        await ctx.send(embed=embed)

        class View(discord.ui.View):
            def __init__(self, user):
                self.forced = False
                self.user = user
                self.activated = ""
                super().__init__(timeout=30)

            async def respond(self):
                if self.activated == "yes":
                    return "continue"
                else:
                    return "skip-1"

            async def interaction_check(self, interaction) -> bool:
                return interaction.user.id == self.user.id

            @discord.ui.button(
                custom_id="yes", label="Yes", style=discord.ButtonStyle.green
            )
            async def yes_callback(self, button, interaction):
                self.activated = button.custom_id
                self.interaction = interaction
                await self.interaction.response.send_message(
                    "Alright, I will setup the ticket transcripts."
                )
                self.stop()

            @discord.ui.button(
                custom_id="cancel", label="Cancel", style=discord.ButtonStyle.gray
            )
            async def cancel_callback(self, button, interaction):
                self.forced = True
                self.activated = button.custom_id
                self.interaction = interaction
                embed.description = (
                    "Alright I have **cancelled** the ticket system setup."
                )
                await interaction.response.send_message(embed=embed)
                return self.stop()

            @discord.ui.button(
                custom_id="no", label="No", style=discord.ButtonStyle.red
            )
            async def no_callback(self, button, interaction):
                self.activated = button.custom_id
                self.interaction = interaction
                await self.interaction.response.send_message(
                    "Alright, I will not setup the ticket trancripts."
                )
                self.stop()

        class DMView(discord.ui.View):
            def __init__(self, user):
                self.forced = False
                self.user = user
                self.activated = ""
                super().__init__(timeout=30)

            async def respond(self):
                if self.activated == "yes":
                    return "continue"
                else:
                    return "continue"

            async def interaction_check(self, interaction) -> bool:
                return interaction.user.id == self.user.id

            @discord.ui.button(
                custom_id="yes", label="Yes", style=discord.ButtonStyle.green
            )
            async def yes_callback(self, button, interaction):
                self.activated = button.custom_id
                self.interaction = interaction
                await self.interaction.response.send_message(
                    "Alright, I will DM the users once their tickets are closed."
                )
                self.stop()

            @discord.ui.button(
                custom_id="cancel", label="Cancel", style=discord.ButtonStyle.gray
            )
            async def cancel_callback(self, button, interaction):
                self.forced = True
                self.activated = button.custom_id
                self.interaction = interaction
                embed.description = (
                    "Alright I have **cancelled** the ticket system setup."
                )
                await interaction.response.send_message(embed=embed)
                return self.stop()

            @discord.ui.button(
                custom_id="no", label="No", style=discord.ButtonStyle.red
            )
            async def no_callback(self, button, interaction):
                self.activated = button.custom_id
                self.interaction = interaction
                await self.interaction.response.send_message(
                    "Alright, I will not DM users once their tickets are closed."
                )
                self.stop()

        view = View(user=ctx.author)
        questions = [
            (
                "What would you like the name of the tickets category to be?",
                None,
                "category",
            ),
            ("Do you want me to send transcripts to a channel?", view, "transcript"),
            (
                "Which channel do you want me to send the transcripts to?",
                None,
                "transcript_channel",
            ),
            (
                "What role would you like to be pinged when creating tickets? \nNote: You can send `none | nil | null` to not have one.",
                None,
                "ping",
            ),
            (
                "Do you want me to DM users with their transcripts once their tickets have been closed?",
                DMView(ctx.author),
                "dm",
            ),
        ]
        answers = {}
        skip = 0
        for index, value in enumerate(questions):
            if skip != 0:
                skip -= 1
                continue
            embed.description = value[0]
            await ctx.send(embed=embed, view=value[1])
            if value[1] is not None:
                response = await value[1].wait()
                if response:
                    embed.description = "Uh oh! It seems like you didn't answer within **30 seconds**. You can try again later."
                    return await ctx.send(embed=embed)

                if value[1].forced:
                    return

                answers[value[2]] = value[1].activated
                response = await value[1].respond()
                if "skip" in response:
                    _skip = response.split("-")
                    skip = int(_skip[1])
            else:
                try:
                    m = await self.hyena.wait_for(
                        "message",
                        check=lambda m: m.author.id == ctx.author.id
                        and m.channel.id == ctx.channel.id,
                        timeout=30,
                    )
                except:
                    embed.description = "Uh oh! It seems like you didn't answer within **30 seconds**. You can try again later."
                    return await ctx.send(embed=embed)

                if m.content.lower() in ["cancel", "abort"]:
                    embed.description = (
                        "Alright I have **cancelled** the ticket system setup."
                    )
                    return await ctx.send(embed=embed)

                answers[value[2]] = m.content

        view = discord.ui.View(timeout=30)

        embed.set_footer(text="Hyena Tickets!", icon_url=self.hyena.user.avatar.url)
        if answers.get("transcript_channel"):
            try:
                transcript_channel = await commands.TextChannelConverter().convert(
                    ctx, answers.get("transcript_channel")
                )
            except:
                return await ctx.send("Unknown channel, Did you make a typo?")
        else:
            transcript_channel = None

        if answers.get("ping") not in ["none", "null", "nope", "no", "nil"]:
            try:
                ping_role = await commands.RoleConverter().convert(
                    ctx, answers.get("ping")
                )
            except:
                return await ctx.send("Unknown role, Did you make a typo?")
        else:
            ping_role = None

        if transcript_channel is not None:
            _transcript = transcript_channel.mention
        else:
            _transcript = "N/A"

        if ping_role is not None:
            _ping = ping_role.mention
        else:
            _ping = "N/A"

        embed = discord.Embed(
            title="Hyena ticket system setup",
            color=random.choice(self.hyena.colors),
            description=f"""
Is the following information correct?

**Category name**: {answers['category']}
**Transcript Enabled**: {answers['transcript'].title()} 
**Transcript channel**: {_transcript}
**Role ping**: {_ping}
**DM users**: {answers['dm']}

Note: After 30 seconds it will default to `Yes`
""",
        )

        class ConfirmationView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=30)
                self.forced = False

            async def interaction_check(self, interaction: discord.Interaction) -> bool:
                return interaction.user.id == ctx.author.id

            @discord.ui.button(
                label="Yes", custom_id="yes", style=discord.ButtonStyle.green
            )
            async def yes_callback(self, button, interaction):
                self.interaction = interaction
                self.id = button.custom_id
                self.m = await view.interaction.response.send_message(
                    "Enabling Ticket system, just a second."
                )
                self.stop()

            @discord.ui.button(
                label="No", custom_id="No", style=discord.ButtonStyle.red
            )
            async def no_callback(self, button, interaction):
                self.interaction = interaction
                self.id = button.custom_id
                self.forced = True
                await interaction.response.send_message(
                    "Alright, I will not enable ticket system."
                )
                self.stop()

        view = ConfirmationView()
        await ctx.send(embed=embed, view=view)
        response = await view.wait()
        if view.forced:
            return
        await asyncio.sleep(1)
        if transcript_channel is not None:
            _transcript = transcript_channel.id
        else:
            _transcript = None

        if ping_role is not None:
            _ping = ping_role.id
        else:
            _ping = None
        category = await ctx.guild.create_category(
            name=answers["category"],
            reason=f"Enabled ticket system. User: {ctx.author}",
            overwrites=overwrites,
        )
        data = await self.db.fetchrow(
            "SELECT * FROM tickets WHERE guild_id = $1", ctx.guild.id
        )

        if data:
            _og_category = ctx.guild.get_channel(data[2])
            if _og_category is not None:
                try:
                    await _og_category.delete()
                except:
                    pass

            await self.db.execute(
                "DELETE FROM tickets WHERE guild_id = $1", ctx.guild.id
            )

        sql = "INSERT INTO tickets (guild_id, transcript_channel, tickets_category, role_ping, dm) VALUES ($1, $2, $3, $4, $5)"
        val = (ctx.guild.id, _transcript, category.id, _ping, answers["dm"])

        await self.db.execute(sql, *val)
        await view.m.edit("Successfully set up tickets for this server.")

    @tickets.command(name="transcript")
    @commands.has_permissions(manage_guild=True)
    async def ticket_transcript(self, ctx):
        data = await self.db.fetchrow(
            "SELECT * FROM tickets WHERE guild_id = $1", ctx.guild.id
        )
        if data is None:
            return await ctx.send(
                "Please set up the ticket system first in order to change the ticket transcript."
            )
        m = await ctx.send(
            "Which **channel** would you like me to send the ticket transcripts to?\n*Respond with `no` | `none` | `disable` in order to disable the ticket transcripts.*"
        )
        try:
            message = await self.hyena.wait_for(
                "message",
                check=lambda m: m.author.id == ctx.author.id
                and m.channel.id == ctx.channel.id,
                timeout=30,
            )
        except:
            return await m.reply(
                "You did not respond in enough time, transcript settings remain as they were."
            )

        if message.content.lower() not in ["no", "none", "null", "nil", "disable"]:
            try:
                channel = await commands.TextChannelConverter().convert(
                    ctx, message.content
                )
                channel = channel.id
            except:
                return await message.reply("Invalid channel did you make a typo?")
        else:
            channel = None

        await self.db.execute(
            "UPDATE tickets SET transcript_channel = $1 WHERE guild_id = $2",
            channel,
            ctx.guild.id,
        )
        await message.reply(
            f"Successfully updated the ticket transcript channel to <#{channel}>"
            if channel is not None
            else "Successfully disabled ticket transcripts."
        )

    @tickets.command(name="role")
    @commands.has_permissions(manage_guild=True)
    async def ticket_role(self, ctx):
        data = await self.db.fetchrow(
            "SELECT * FROM tickets WHERE guild_id = $1", ctx.guild.id
        )
        if data is None:
            return await ctx.send(
                "Please set up the ticket system first in order to change the ticket transcript."
            )
        m = await ctx.send(
            "Which **role** do you want me to ping when a ticket is created?\n*Respond with `no` | `none` | `disable` in order to disable the role ping.*"
        )
        try:
            message = await self.hyena.wait_for(
                "message",
                check=lambda m: m.author.id == ctx.author.id
                and m.channel.id == ctx.channel.id,
                timeout=30,
            )
        except:
            return await m.reply(
                "You did not respond in enough time, transcript settings remain as they were."
            )

        if message.content.lower() not in ["no", "none", "null", "nil", "disable"]:
            try:
                channel = await commands.RoleConverter().convert(ctx, message.content)
                channel = channel.id
            except:
                return await message.reply("Invalid channel did you make a typo?")
        else:
            channel = None

        await self.db.execute(
            "UPDATE tickets SET role_ping = $1 WHERE guild_id = $2",
            channel,
            ctx.guild.id,
        )
        await message.reply(
            f"Successfully updated the role ping role to <@&{channel}>"
            if channel is not None
            else "Successfully disabled role pings."
        )

    @tickets.command(name="dm")
    @commands.has_permissions(manage_guild=True)
    async def tickets_dm(self, ctx):
        data = await self.db.fetchrow(
            "SELECT * FROM tickets WHERE guild_id = $1", ctx.guild.id
        )
        if data is None:
            return await ctx.send(
                "Please set up the ticket system first in order to change the ticket transcript."
            )

        m = await ctx.message.reply(
            "Do you want me to DM users once their tickets are closed? (**Y**es/**N**o)"
        )
        try:
            message = await self.hyena.wait_for(
                "message",
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                timeout=30,
            )
        except:
            return await m.reply(
                "You did not respond in enough time, process cancelled."
            )

        if message.content.lower() in ["n", "no"]:
            val = ("no", ctx.guild.id)
            await m.reply(
                "Alright, I will not DM users once their tickets have been closed."
            )
        else:
            val = ("yes", ctx.guild.id)
            await m.reply(
                "Alright, I will DM users once their tickets have been closed."
            )

        await self.db.execute("UPDATE tickets SET dm = $1 WHERE guild_id = $2", *val)

    @tickets.command(name="create", aliases=["new"])
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def ticket_create(self, ctx):
        if ctx.invoked_subcommand is not None:
            return
        data = await self.db.fetchrow(
            "SELECT * FROM tickets WHERE guild_id = $1", ctx.guild.id
        )
        if data is None:
            return await ctx.messsage.reply(
                "Tickets system is diabled for this server. Please ask an Admin/Mod to enable it."
            )
        try:
            category = await ctx.guild.fetch_channel(data[2])
        except:
            category = None
        if not isinstance(category, discord.CategoryChannel):
            return await ctx.message.reply(
                "Tickets system appears to be not setup properly. Please ask an Admin/Mod to run the `[p]tickets setup command again.`"
            )

        overwrites = category.overwrites
        overwrites[ctx.author] = discord.PermissionOverwrite(
            send_messages=True,
            attach_files=True,
            read_messages=True,
            read_message_history=True,
            manage_messages=False,
            embed_links=True,
        )
        overwrites[ctx.guild.me] = discord.PermissionOverwrite(
            send_messages=True,
            attach_files=True,
            read_messages=True,
            read_message_history=True,
            manage_messages=False,
            embed_links=True,
            manage_channels=True,
        )

        channel = await category.create_text_channel(
            name=f"ticket-{''.join(c for c in str(ctx.author) if c.isalpha() or c.isnumeric())}",
            topic=f"{ctx.author.id} - User ID, Do not Change",
            reason=f"Ticket created by {ctx.author}",
            overwrites=overwrites,
        )
        embed = discord.Embed(
            title="Hyena Tickets",
            description=f"Hello there, Your ticket has been opened successfully, support will be here soon. \n*Please note that Hyena does not reserve any rights over the support members.*",
            color=random.choice(self.hyena.colors),
        )
        await channel.send(
            f"<@&{data[3]}> {ctx.author.mention}"
            if data[3] is not None
            else ctx.author.mention,
            embed=embed,
            view=View(self.hyena),
        )

    @tickets.command(name="close", aliases=["delete", "del"])
    @commands.has_permissions(manage_channels=True)
    async def ticket_close(self, ctx):
        await close_ticket(ctx.channel, self.hyena)

    @tickets.command(name="disable")
    @commands.has_permissions(manage_guild=True)
    async def tickets_disable(self, ctx):
        await self.db.execute("DELETE FROM tickets WHERE guild_id = $1", ctx.guild.id)
        await ctx.send("Successfully disabled ticket system for this server.")


def setup(hyena):
    hyena.add_cog(Tickets(hyena, hyena.colors))
