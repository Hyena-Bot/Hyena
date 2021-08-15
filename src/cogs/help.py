import random

import discord
from discord.ext import commands as comms


class HelpSelect(discord.ui.Select):
    def __init__(self, view):
        self._view = view
        options = [
            discord.SelectOption(label="Home", value="1", emoji="🏘️"),
            discord.SelectOption(
                label="Utility", value="2", emoji="<:tools:844508570813071400>"
            ),
            discord.SelectOption(
                label="Utility ( Second Page )",
                value="3",
                emoji="<:tools:844508570813071400>",
            ),
            discord.SelectOption(
                label="Moderation", value="4", emoji="<:banthonk:832104988046000178>"
            ),
            discord.SelectOption(
                label="Fun", value="5", emoji="<:fun:844509126095929354>"
            ),
            discord.SelectOption(label="Setup", value="6", emoji="⚙️"),
            discord.SelectOption(label="Setup ( Second Page )", value="7", emoji="⚙️"),
        ]
        super().__init__(
            custom_id="skip-to-page", placeholder="Skip to page", options=options, row=0
        )

    async def callback(self, interaction):
        self._view.action = f"skip-{self.values[0]}"
        self._view.stop()


class HelpView(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=60)
        self.user = user
        self.action = None
        self.add_item(HelpSelect(self))

    async def interaction_check(self, interaction) -> bool:
        return interaction.user.id == self.user.id

    @discord.ui.button(
        emoji="<:double_left:875244843452989490>",
        custom_id="first-page",
        row=1,
        style=discord.ButtonStyle.blurple,
    )
    async def double_left(self, button, interaction):
        self.action = "first-page"
        self.stop()

    @discord.ui.button(
        emoji="<:left:875244882799771699>",
        custom_id="page-1",
        row=1,
        style=discord.ButtonStyle.blurple,
    )
    async def left(self, button, interaction):
        self.action = "page-1"
        self.stop()

    @discord.ui.button(
        emoji="🔒", custom_id="stop", row=1, style=discord.ButtonStyle.red
    )
    async def _stop(self, button, interaction):
        self.action = "stop"
        self.stop()

    @discord.ui.button(
        emoji="<:right:875244926688960533>",
        custom_id="page+1",
        row=1,
        style=discord.ButtonStyle.blurple,
    )
    async def right(self, button, interaction):
        self.action = "page+1"
        self.stop()

    @discord.ui.button(
        emoji="<:double_right:875244972318810133>",
        custom_id="last-page",
        row=1,
        style=discord.ButtonStyle.blurple,
    )
    async def double_right(self, button, interaction):
        self.action = "last-page"
        self.stop()


class HelpCommand(comms.Cog):
    def __init__(self, hyena, colors):
        self.hyena = hyena
        self.colors = colors

    @property
    def category(self):
        return [
            None
        ]  # Choose from Utils, Mod, Fun, Conf ## Let it be in a list as we sometimes need to send two of these

    async def command_disabled(self, command, guild):
        command = str(command.name)
        db = self.hyena.toggle_db
        data = await db.fetchrow("SELECT * FROM commands WHERE guild_id = $1", guild.id)
        if data is None:
            return False

        if command in data[1]:
            return True
        else:
            return False

    async def get_prefix(self, ctx):
        result = await self.hyena.main_db.fetch(
            f"SELECT * FROM prefixes WHERE guild_id = $1", ctx.guild.id
        )

        if result:
            lst = result[0]["prefix"]
            lst = [n.strip() for n in lst]

            try:
                prefix = lst[0]
            except:
                prefix = self.hyena.user.mention
        else:
            prefix = "-"

        return prefix

    @comms.command(
        name="help",
        aliases=["h", "commands"],
        description="Oh you want help for help? Help is the command you can use to get familiar with hyena",
        usage="[p]help [command/page]",
    )
    @comms.cooldown(1, 10, comms.BucketType.user)
    async def help(self, ctx, command_name=None):
        color = random.choice(self.colors)
        cogs = [self.hyena.get_cog(e) for e in self.hyena.cogs]
        prefix = await self.get_prefix(ctx)
        prefix = prefix.strip()[0:5] + ".." if len(prefix) > 7 else prefix
        util_cogs = [e for e in cogs if "Utils" in e.category]
        fun_cogs = [e for e in cogs if "Fun" in e.category]
        mod_cogs = [e for e in cogs if "Mod" in e.category]

        """-----------------------------------------------------------------------------------------------------------------------------------------------------------------"""
        embed_1 = discord.Embed(color=color, timestamp=ctx.message.created_at)
        embed_1.set_thumbnail(url=self.hyena.user.avatar.url)
        embed_1.set_author(name="Hyena Help", icon_url=self.hyena.user.avatar.url)
        embed_1.add_field(
            name="Navigating the pages:",
            value="""
<:double_left:875244843452989490> Go to first page
<:left:875244882799771699> Go back one page
🔒 Lock the help screen.
<:right:875244926688960533> Go Forward one page
<:double_right:875244972318810133> Go to the last page
""",
        )
        embed_1.add_field(
            name="❓ | New To Hyena?",
            value="`Hyena is an easy to use multi-purpose bot with all sorts of moderation commands you will ever need! Use this help page to get familiar with the bot!`",
            inline=False,
        )
        embed_1.add_field(
            name="Contents:",
            value="**Page 1.** This Screen \n**Page 2.** Utilities \n**Page 3.** Utilites ( Second Page ) \n**Page 4.** Moderation \n**Page 5.** Fun \n**Page 6.** Setups \n**Page 7.** Setups (Second Page)",
        )
        embed_1.add_field(
            name="Useful Links",
            value=f"[Invite Me](https://bit.ly/hyena-bot) | [Support Server](https://discord.gg/cHYWdK5GNt)",
        )
        embed_1.set_footer(
            text=f"Requested by {ctx.author} | Prefix: Use {prefix} before each command",
            icon_url=ctx.author.avatar.url,
        )
        """-----------------------------------------------------------------------------------------------------------------------------------------------------------------"""

        """-----------------------------------------------------------------------------------------------------------------------------------------------------------------"""
        embed_2 = discord.Embed(color=color, timestamp=ctx.message.created_at)
        embed_2.set_thumbnail(url=self.hyena.user.avatar.url)
        embed_2.set_author(
            name="Tools and Utilities",
            icon_url="https://cdn.discordapp.com/emojis/844508570813071400.png?v=1",
        )
        commands = ""
        command_block = []
        group_block = []
        for cog in util_cogs:
            for command in cog.get_commands():
                if type(command).__name__ == "Group":
                    if not len(group_block) > 14:
                        group_block.append(
                            f"`{prefix}{command.name}` : {command.description.capitalize()[:31] + '..' if len(command.description) > 30 else command.description.capitalize()}"
                        )
                if type(command).__name__ == "Command":
                    if not len(command_block) > 14:
                        command_block.append(command.name)

        command_block = f"```{', '.join(command_block)}```"
        group_block = "\n".join(group_block)

        embed_2.add_field(name="Settings:", value=group_block, inline=False)
        embed_2.add_field(
            name="Commands:", value=command_block + "\n**P.T.O**", inline=False
        )
        embed_2.description = "Hyena loves to help you. Utilities go brr"  # commands
        embed_2.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url
        )
        """-----------------------------------------------------------------------------------------------------------------------------------------------------------------"""

        """-----------------------------------------------------------------------------------------------------------------------------------------------------------------"""
        embed_7 = discord.Embed(color=color, timestamp=ctx.message.created_at)
        embed_7.set_thumbnail(url=self.hyena.user.avatar.url)
        embed_7.set_author(
            name="Tools and Utilities",
            icon_url="https://cdn.discordapp.com/emojis/844508570813071400.png?v=1",
        )
        commands = ""
        _command_block = []
        _group_block = []
        for cog in util_cogs:
            for command in cog.get_commands():
                if type(command).__name__ == "Group":
                    if (
                        f"`{prefix}{command.name}` : {command.description.capitalize()[:31] + '..' if len(command.description) > 30 else command.description.capitalize()}"
                    ) not in group_block:
                        _group_block.append(
                            f"`{prefix}{command.name}` : {command.description.capitalize()[:31] + '..' if len(command.description) > 30 else command.description.capitalize()}"
                        )
                if type(command).__name__ == "Command":
                    if command.name not in command_block:
                        _command_block.append(command.name)

        command_block = f"```{', '.join(_command_block)}```"
        group_block = "\n".join(_group_block)

        if len(group_block) >= 1:
            embed_7.add_field(name="Settings:", value=group_block, inline=False)

        embed_7.add_field(name="Commands:", value=command_block, inline=False)
        embed_7.description = "Second page because hyena is way too helpful"  # commands
        embed_7.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url
        )
        """-----------------------------------------------------------------------------------------------------------------------------------------------------------------"""

        """-----------------------------------------------------------------------------------------------------------------------------------------------------------------"""

        embed_3 = discord.Embed(color=color, timestamp=ctx.message.created_at)
        embed_3.set_thumbnail(url=self.hyena.user.avatar.url)
        embed_3.set_author(
            name="Moderation",
            icon_url="https://cdn.discordapp.com/emojis/832104988046000178.png?v=1",
        )
        commands = ""
        command_block = []
        group_block = []
        for cog in mod_cogs:
            for command in cog.get_commands():
                if type(command).__name__ == "Group":
                    group_block.append(
                        f"`{prefix}{command.name}` : {command.description.capitalize()}"
                    )
                if type(command).__name__ == "Command":
                    command_block.append(command.name)

            # embed_3.add_field(name=type(re).__name__, value="```" + ("\n".join([f"[p]{e.name}" for e in re.get_commands()]).replace('[p]', prefix) + "```"))
            # commands += ('\n'.join([f"`[p]{e.name}` - {e.description}" for e in re.get_commands()]) + '\n')

        command_block = f"```{', '.join(command_block)}```"
        group_block = "\n".join(group_block)

        embed_3.add_field(name="Settings:", value=group_block, inline=False)
        embed_3.add_field(name="Commands:", value=command_block, inline=False)

        embed_3.description = (
            "BanThonk, *Goes ahead and bans all the rule breakers*"  # commands
        )
        embed_3.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url
        )
        """-----------------------------------------------------------------------------------------------------------------------------------------------------------------"""

        """-----------------------------------------------------------------------------------------------------------------------------------------------------------------"""
        embed_4 = discord.Embed(color=color, timestamp=ctx.message.created_at)
        embed_4.set_thumbnail(url=self.hyena.user.avatar.url)
        embed_4.set_author(
            name="Fun",
            icon_url="https://cdn.discordapp.com/emojis/844509126095929354.png?v=1",
        )
        commands = ""
        image_block = []
        text_block = []
        other_block = []

        for cog in fun_cogs:
            if str(type(cog).__name__) == "TextFun":
                for command in cog.get_commands():
                    text_block.append(command.name)
            if str(type(cog).__name__) == "ImageFun":
                for command in cog.get_commands():
                    image_block.append(command.name)
            if str(type(cog).__name__) == "OtherFun":
                for command in cog.get_commands():
                    other_block.append(command.name)
            # embed_4.add_field(name=type(re).__name__, value="```" + ("\n".join([f"[p]{e.name}" for e in re.get_commands()]).replace('[p]', prefix) + "```"))
            # commands += (', '.join([f"`[p]{e.name}`" for e in re.get_commands()]) + ', ')

        image_block = f"```{', '.join(image_block)}```"
        text_block = f"```{', '.join(text_block)}```"
        other_block = f"```{', '.join(other_block)}```"

        embed_4.add_field(name="Text Fun:", value=text_block, inline=False)
        embed_4.add_field(name="Image Fun:", value=image_block, inline=False)
        embed_4.add_field(name="Other Fun:", value=other_block, inline=False)

        embed_4.description = (
            "Wanna have some fun? Hyena heard you."  # commands.strip(',')
        )
        embed_4.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url
        )
        """-----------------------------------------------------------------------------------------------------------------------------------------------------------------"""

        """-----------------------------------------------------------------------------------------------------------------------------------------------------------------"""
        embed_5 = discord.Embed(color=color, timestamp=ctx.message.created_at)
        embed_5.set_thumbnail(url=self.hyena.user.avatar.url)

        embed_5.set_author(
            name="Setup",
            icon_url="https://cdn.discordapp.com/emojis/844509389154811915.png?v=1",
        )
        commands = ""
        r__group_block = []

        for command in self.hyena.commands:
            if type(command).__name__ == "Group":
                if len(r__group_block) > 10:
                    break
                description = command.description.capitalize()
                # description = (description[:50] + '...') if len(description) > 50 else description
                r__group_block.append(f"`{prefix}{command.name}` : {description}")

        r__group_block_str = "\n".join(r__group_block) + "\n**P.T.O**"

        embed_5.add_field(name="Commands:", value=r__group_block_str, inline=False)
        embed_5.description = (
            "Configure Hyena according to your needs."  # commands.strip(',')
        )
        embed_5.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url
        )
        """-----------------------------------------------------------------------------------------------------------------------------------------------------------------"""

        """-----------------------------------------------------------------------------------------------------------------------------------------------------------------"""
        embed_6 = discord.Embed(color=color, timestamp=ctx.message.created_at)
        embed_6.set_thumbnail(url=self.hyena.user.avatar.url)

        embed_6.set_author(
            name="Setup",
            icon_url="https://cdn.discordapp.com/emojis/844509389154811915.png?v=1",
        )
        commands = ""
        group_block = []

        for command in self.hyena.commands:
            if type(command).__name__ == "Group":
                if len(group_block) > 10:
                    break
                description = command.description.capitalize()
                description = f"`{prefix}{command.name}` : {description}"
                if description not in r__group_block:
                    group_block.append(description)

        group_block = "\n".join(group_block)

        embed_6.add_field(name="Commands:", value=group_block, inline=False)
        embed_6.description = "Too many things you can do with Hyena, We will need another page"  # commands.strip(',')
        embed_6.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url
        )
        """-----------------------------------------------------------------------------------------------------------------------------------------------------------------"""

        helps = {
            "1": embed_1,
            "2": embed_2,
            "3": embed_7,
            "4": embed_3,
            "5": embed_4,
            "6": embed_5,
            "7": embed_6,
            "home": embed_1,
            "utils": embed_2,
            "utils2": embed_7,
            "moderation": embed_3,
            "fun": embed_4,
            "setup": embed_5,
            "setup2": embed_6,
        }
        if command_name is None:

            cur_page = 1
            view = HelpView(ctx.author)
            view.children[0].disabled = True
            view.children[1].disabled = True
            message = await ctx.send(embed=helps["1"], view=view)
            while True:
                wait = await view.wait()
                if wait is True:
                    for child in view.children:
                        child.disabled = True
                    view.timeout = 1
                    await message.edit(view=view)
                    return

                action = view.action
                new_view = HelpView(ctx.author)

                if action == "stop":
                    for child in view.children:
                        child.disabled = True
                    view.timeout = 1
                    await message.edit(view=view)
                    return

                if action.startswith("skip-"):
                    page = action.split("-")[1]
                    embed = helps.get(page)
                    cur_page = int(page)
                    if cur_page == 7:
                        new_view.children[4].disabled = True
                        new_view.children[3].disabled = True
                            
                    if cur_page == 1:
                        new_view.children[0].disabled = True
                        new_view.children[1].disabled = True
                    await message.edit(embed=embed, view=new_view)
                    view = new_view


                if action.startswith("page"):
                    add_or_sub = True if action[4] in ["+", "+"] else False
                    if add_or_sub:
                        skip_by = int(action[4:])
                        new_page = cur_page + skip_by
                        if new_page > 7:
                            new_page -= 7
                        embed = helps.get(str(new_page))
                        cur_page = new_page
                        if cur_page == 7:
                            new_view.children[4].disabled = True
                            new_view.children[3].disabled = True

                        if cur_page == 1:
                            new_view.children[0].disabled = True
                            new_view.children[1].disabled = True

                        await message.edit(embed=embed, view=new_view)
                        view = new_view

                    else:
                        skip_by = int(action[4:])
                        new_page = cur_page + skip_by
                        if new_page < 1:
                            new_page += 7
                        embed = helps.get(str(new_page))
                        cur_page = new_page
                        if cur_page == 7:
                            new_view.children[4].disabled = True
                            new_view.children[3].disabled = True

                        if cur_page == 1:
                            new_view.children[0].disabled = True
                            new_view.children[1].disabled = True
                        await message.edit(embed=embed, view=new_view)
                        view = new_view

                if action == "last-page":
                    embed = helps.get("7")
                    new_view.children[4].disabled = True
                    new_view.children[3].disabled = True
                    await message.edit(embed=embed, view=new_view)
                    view = new_view
                    cur_page = 7

                if action == "first-page":
                    embed = helps.get("1")
                    new_view.children[0].disabled = True
                    new_view.children[1].disabled = True
                    await message.edit(embed=embed, view=new_view)
                    view = new_view
                    cur_page = 1

        else:
            if command_name in helps.keys():
                await ctx.send(embed=helps.get(str(command_name)))
            else:
                command = self.hyena.get_command(command_name)
                if command is None:
                    return await ctx.send(
                        f"Cannot find any such command named `{command_name}`. Did you make a typo?"
                    )

                description = command.description
                if description is None:
                    description = "Not set"

                aliases = command.aliases
                if aliases == []:
                    aliases = "None"
                if aliases != [] and aliases != "None":
                    aliases = ", ".join(aliases)

                is_disabled = await self.command_disabled(command, ctx.guild)
                is_disabled = "Yes" if is_disabled else "No"

                embed = discord.Embed(color=color, timestamp=ctx.message.created_at)
                embed.set_author(name="Hyena", icon_url=self.hyena.user.avatar.url)
                embed.add_field(
                    name="Name:", value=f"```{command.name}```", inline=False
                )
                embed.add_field(
                    name="Description:", value=f"```{description}```", inline=False
                )
                embed.add_field(
                    name="Usage:",
                    value=f"```{command.usage}```".replace("[p]", prefix),
                )
                embed.add_field(name="Aliases:", value=f"```{aliases}```", inline=False)
                embed.add_field(
                    name="Disabled:", value=f"```{is_disabled}```", inline=False
                )
                embed.set_footer(
                    text=f"Requested by: {ctx.author}", icon_url=ctx.author.avatar.url
                )
                if command.__class__.__name__ == "Group":
                    commands = [c.name for c in command.commands]
                    commands = f'```{", ".join(commands)}```'
                    embed.add_field(name="Sub-Commands", value=commands, inline=False)

                embed.set_thumbnail(url=ctx.guild.icon.url)

                return await ctx.send(embed=embed)


def setup(hyena):
    hyena.add_cog(HelpCommand(hyena, hyena.colors))
