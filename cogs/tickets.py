import discord, sqlite3, random
from discord.ext import commands

class Tickets(commands.Cog):
    def __init__(self, hyena, colours):
        self.hyena = hyena
        self.colours = colours

    @commands.group(name="ticket", aliases=['tickets'])
    async def ticket(self, ctx):

        if ctx.invoked_subcommand is None:
            embed = discord.Embed(color=random.choice(self.colours))
            embed.set_author(name="Hyena Ticket System")
            embed.add_field(name="Ticket Options", value="`create`, `enable`, `disable`, `close`")

            await ctx.send(embed=embed)


    @ticket.command(name="create")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def create(self, ctx):

        try:
            db = sqlite3.connect("./data/ticket.sqlite")
            cursor = db.cursor()
            cursor.execute(f"SELECT yesno FROM ticket WHERE guild_id = {ctx.guild.id}")
            result = cursor.fetchone()

            yn = result[0]

        except:
            yn = 'disabled'

        if yn == 'enabled':

            var = f'{ctx.author.name}-{ctx.author.discriminator}'
            channel_name = var.lower()
            category = discord.utils.get(ctx.guild.categories, name='HYENA-TICKETS')
            channel = discord.utils.get(ctx.guild.text_channels, name=f'{channel_name}')

            if category is None:
                category = await ctx.guild.create_category_channel("HYENA-TICKETS")

            if channel is not None:
                await ctx.send("You already have a ticket in use!")
                return
            if channel is None:
                channel = await ctx.guild.create_text_channel(f'{channel_name}', category=category)
                await channel.set_permissions(ctx.guild.default_role, read_messages=False)
                await channel.set_permissions(ctx.author, read_messages=True)
                embed = discord.Embed(title="New Ticket.", description="Please be patient support will here shortly :)",
                                    colour=random.choice(self.colours))
                embed.set_author(name=ctx.author)
                await channel.edit(topic=f"{ctx.author.id}")
                await channel.send(embed=embed)
                msg = await channel.send(ctx.author.mention)
                await msg.delete()
                await ctx.send(f"{ctx.author.mention}, New ticket has been made for you at {channel.mention}, Support will be with you soon!")
                return

        else:
            await ctx.send("Tickets are disabled in this server! Please ask a Mod to enable it!")


    @ticket.command(name="enable")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(commands.has_permissions(manage_guild=True), commands.is_owner())
    async def enable(self, ctx):
        sql, val = "", ""
        db = sqlite3.connect('./data/ticket.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT yesno FROM ticket WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()

        if result is None:
            sql = "INSERT INTO ticket(guild_id, yesno) VALUES(?,?)"
            val = (ctx.guild.id, "enabled")
            await ctx.send(f"Ticket system is `enabled`")
        if result is not None:
            sql = "UPDATE ticket SET yesno = ? where guild_id = ?"
            val = ("enabled", ctx.guild.id)
            await ctx.send(f"Ticket system is `enabled`")

        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

        category = discord.utils.get(ctx.guild.categories, name='HYENA-TICKETS')

        if category is None:
            category = await ctx.guild.create_category_channel("HYENA-TICKETS")


    @ticket.command(name="disable")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(commands.has_permissions(manage_guild=True), commands.is_owner())
    async def disable_command(self, ctx):
        sql, val = "", ""
        db = sqlite3.connect('./data/ticket.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT yesno FROM ticket WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()

        if result is None:
            sql = "INSERT INTO ticket(guild_id, yesno) VALUES(?,?)"
            val = (ctx.guild.id, "disabled")
            await ctx.send(f"Ticket system is `disabled`")
        if result is not None:
            sql = "UPDATE ticket SET yesno = ? where guild_id = ?"
            val = ("disabled", ctx.guild.id)
            await ctx.send(f"Ticket system is `disabled`")

        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

        category = discord.utils.get(ctx.guild.categories, name='HYENA-TICKETS')

        if category is not None:
            await category.delete()


    @ticket.command(name="close")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(commands.has_permissions(manage_channels=True), commands.is_owner())
    async def close(self, ctx, channel: discord.TextChannel = None, *, reason='None'):
        if channel is None:
            channel = ctx.channel

        category = discord.utils.get(ctx.guild.categories, name='HYENA-TICKETS')
        if channel.category == category:
            try:
                member_id = channel.topic
                member = ctx.guild.get_member(int(member_id))
                await channel.delete(reason=f"Ticket closed by {ctx.author}, for reason {reason}")
                await member.send(f"Your ticket in **{ctx.guild.name}** has been closed by **{ctx.author}**.")
            except discord.errors.Forbidden:
                pass
            try:
                await ctx.author.send("Ticket closed")
            except discord.errors.Forbidden:
                pass


def setup(hyena):
    hyena.add_cog(Tickets(hyena, [0xFFED1B, 0xF1EFE3, 0x00A8FE, 0x1FEDF9, 0x7CF91F, 0xF91F43]))
    