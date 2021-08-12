import discord, random, sqlite3, ast, asyncio
from discord.ext import commands

class Todo(commands.Cog):
    def __init__(self, hyena):
        self.hyena = hyena
        self.db = self.hyena.main_db2

    @property
    def category(self):
        return ["Utils", "Fun"] # Choose from Utils, Mod, Fun, Conf ## Let it be in a list as we sometimes need to send two of these

    @commands.group(name='todo', aliases=['to-do', 'to_do'], usage="[p]todo", description="Manage your own todo list")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def todo(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(color=random.choice(self.hyena.colors),
                                timestamp=ctx.message.created_at)

            embed.set_author(name="Hyena TO-DO system", icon_url=self.hyena.user.avatar.url)
            embed.add_field(name="Commands:", value="""
`add [task]`: Add a new task to your todo list.
`remove [task position]`: Remove a task from your todo list. 
`view`: View all your current tasks.
`edit [task position] [new task]`: Edit a task
`clear`: Clear all your tasks
`info [task position]`: View a single task
""")
            embed.add_field(name="Command usage:", value="`Usage [p]todo [command] [args]`", inline=False)
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
            embed.set_thumbnail(url=ctx.author.avatar.url)
            
            await ctx.send(embed=embed)

    async def validate(self, ctx, todo: str) -> str:
        todo = todo.strip()
        if len(todo) > 500:
            self.hyena.get_command("todo add").reset_cooldown(ctx)
            return await ctx.send("Your todo cannot be more than 500 characters long")
        if todo.isnumeric():
            self.hyena.get_command("todo add").reset_cooldown(ctx)
            return await ctx.send("Your todo is a numeric value, add more to the description")

        return str(todo)

    @todo.command(name='add', aliases=['insert'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def add(self, ctx, *, todo: str):
        todo = await self.validate(ctx, todo)
        if not isinstance(todo, str):
            return
        if len(todo) > 500:
            self.hyena.get_command("todo add").reset_cooldown(ctx)
            return await ctx.send("Your todo cannot be more than 500 characters long")

        res = await self.db.fetch(f'SELECT * FROM todo WHERE user_id = $1', ctx.author.id)

        if not res or res[0]['todos'] == []:
            await self.db.execute("INSERT INTO todo(user_id, todos) VALUES ($1, $2)", ctx.author.id, [todo])
            await ctx.send(f"Successfully added `{todo}` to your todo list. I swear you're not gonna complete any of them. \n`Position: 1`")
        if res:
            lst = res[0]['todos']

            if todo in lst:
                self.hyena.get_command("todo add").reset_cooldown(ctx)
                return await ctx.send("Your todo is already in your current todos nub")
            if len(lst) == 20:
                self.hyena.get_command("todo add").reset_cooldown(ctx)
                return await ctx.send("Your todo list has reached maximum limit [20] remove some of them [clear] to add more!")

            await self.db.execute("UPDATE todo SET todos = $1 WHERE user_id = $2", [*lst, todo], ctx.author.id)

            await ctx.send(f"Successfully added `{todo}` to your todo list. I swear you're not gonna complete any of them. \n`Position: {len(lst) + 1}`")

    @todo.command(name="list", aliases=['list_todos', 'view'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def list_todos(self, ctx):
        res = await self.db.fetch(f'SELECT * FROM todo WHERE user_id = $1', ctx.author.id)

        if not res or res[0]['todos'] == []:
            self.hyena.get_command("todo list").reset_cooldown(ctx)
            return await ctx.send("You have no current todos :|")
        if res:
            lst = res[0]['todos']

            embeds = []

            home_embed = discord.Embed(color=random.choice(self.hyena.colors), timestamp=ctx.message.created_at)
            home_embed.set_author(name=f"{ctx.author}'s ToDo(s)", icon_url=ctx.author.avatar.url)
            home_embed.add_field(name="Pagination Controls:", value="""
⏮️ goes to the first page
◀️ goes to the previous page
▶️ goes to the next page
⏭️ goes to the last page
⏹️ stops the interactive pagination session
""")
            home_embed.set_footer(text="Hyena", icon_url=self.hyena.user.avatar.url)
            embeds.append(home_embed)

            for idx, x in enumerate(lst):
                embed = discord.Embed(color=random.choice(self.hyena.colors), timestamp=ctx.message.created_at)
                embed.set_author(name=f"Todo #{idx + 1}", icon_url=ctx.author.avatar.url)
                embed.add_field(name="Description:", value=x)
                embed.set_thumbnail(url=ctx.author.avatar.url)

                embeds.append(embed)

            cur_page = 0

            pagination_emojis = ["⏮️", "◀️", "⏹️", "▶️", "⏭️"]

            da_msg = await ctx.send(embed=embeds[0])

            for emoji in pagination_emojis:
                try:
                    await da_msg.add_reaction(emoji)
                except discord.errors.Forbidden:
                    await ctx.send("Bruh I don't have permissions to add reactions")

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in pagination_emojis and reaction.message.id == da_msg.id

            while True:
                try:
                    reaction, user = await self.hyena.wait_for("reaction_add", timeout=60, check=check)
                except asyncio.TimeoutError:
                    for emoji in pagination_emojis:
                        try:
                            await da_msg.clear_reaction(emoji)
                        except discord.errors.Forbidden:
                            break
                    break
                else:
                    da_reaction_he_made = str(reaction.emoji)
                    if da_reaction_he_made == "▶️":
                        cur_page += 1
                        try:
                            await da_msg.remove_reaction(da_reaction_he_made, user)
                        except:
                            pass

                        if cur_page == len(embeds):
                            cur_page -= 1; continue

                        the_current_embed = embeds[cur_page]
                        await da_msg.edit(embed=the_current_embed)

                    elif da_reaction_he_made == "◀️":
                        cur_page -= 1
                        try:
                            await da_msg.remove_reaction(da_reaction_he_made, user)
                        except:
                            pass

                        if cur_page == -1:
                            cur_page += 1; continue

                        the_current_embed = embeds[cur_page]
                        await da_msg.edit(embed=the_current_embed)

                    elif da_reaction_he_made == "⏹️":
                        await da_msg.edit(content="Stopped the todo list screen!", suppress=True)
                        for emoji in pagination_emojis:
                            try:
                                await da_msg.clear_reaction(emoji)
                            except discord.errors.Forbidden:
                                break
                        break

                    elif da_reaction_he_made == "⏮️":
                        try:
                            await da_msg.remove_reaction(da_reaction_he_made, user)
                        except:
                            pass
                        cur_page = 0
                        await da_msg.edit(embed=embeds[0])

                    elif da_reaction_he_made == "⏭️":
                        try:
                            await da_msg.remove_reaction(da_reaction_he_made, user)
                        except:
                            pass
                        cur_page = len(embeds) - 1
                        await da_msg.edit(embed=embeds[-1])

    async def validate_position(self, ctx, position: str) -> int:
        if not position.isnumeric():
            return await ctx.send(f"The todo position should be an integer")
        position = int(position)

        if position <= 0 or position > 20:
            self.hyena.get_command("todo remove").reset_cooldown(ctx)
            return await ctx.send("The todo position should be between 1 and 20")

        return position

    @todo.command(name="remove")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def remove(self, ctx, position: str):
        position = await self.validate_position(ctx, position)
        if not isinstance(position, int):
            return

        res = await self.db.fetch(f'SELECT * FROM todo WHERE user_id = $1', ctx.author.id)

        if not res or res[0]['todos'] == []:
            self.hyena.get_command("todo remove").reset_cooldown(ctx)
            return await ctx.send("You have no current todos :|")
        if res:
            lst = res[0]['todos']

            try:
                lst.pop(position - 1)
            except IndexError:
                self.hyena.get_command("todo remove").reset_cooldown(ctx)
                return await ctx.send(f"The todo position cannot be greater than your lenght of current todos: `{len(lst)}`")

            await self.db.execute("UPDATE todo SET todos = $1 WHERE user_id = $2", lst, ctx.author.id)
            await ctx.send(f"Successfully removed `#{position}` from your todo list.")

    @todo.command(name="edit")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def edit(self, ctx, position: str, *, new_task: str):
        position = await self.validate_position(ctx, position)
        if not isinstance(position, int):
            return

        new_task = await self.validate(ctx, new_task)
        if not isinstance(new_task, str):
            return

        res = await self.db.fetch(f'SELECT * FROM todo WHERE user_id = $1', ctx.author.id)

        if not res or res[0]['todos'] == []:
            self.hyena.get_command("todo edit").reset_cooldown(ctx)
            return await ctx.send("You have no current todos :|")
        if res:
            lst = res[0]['todos']

            try:
                lst[position - 1] = new_task
            except IndexError:
                self.hyena.get_command("todo remove").reset_cooldown(ctx)
                return await ctx.send(f"The todo position cannot be greater than your lenght of current todos: `{len(lst)}`")

            await self.db.execute("UPDATE todo SET todos = $1 WHERE user_id = $2", lst, ctx.author.id)
            await ctx.send(f"Successfully edited `#{position}` in your todo list.")

    @todo.command(name="clear")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def clear(self, ctx):
        res = await self.db.fetch(f'SELECT * FROM todo WHERE user_id = $1', ctx.author.id)

        if not res or res[0]['todos'] == []:
            self.hyena.get_command("todo clear").reset_cooldown(ctx)
            return await ctx.send("You have no current todos :|")
        if res:
            await self.db.execute('DELETE FROM todo WHERE user_id = $1', ctx.author.id)
            await ctx.send("Successfully cleared all your TODO(s)")

    @todo.command(name="info")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def info(self, ctx, position: str):
        position = await self.validate_position(ctx, position)
        if not isinstance(position, int):
            return

        res = await self.db.fetch(f'SELECT * FROM todo WHERE user_id = $1', ctx.author.id)

        if not res or res[0]['todos'] == []:
            self.hyena.get_command("todo info").reset_cooldown(ctx)
            return await ctx.send("You have no current todos :|")
        if res:
            lst = res[0]['todos']

            try:
                task = lst[position - 1]
            except IndexError:
                self.hyena.get_command("todo info").reset_cooldown(ctx)
                return await ctx.send(f"The todo position cannot be greater than your lenght of current todos: `{len(lst)}`")

            embed = discord.Embed(color=random.choice(self.hyena.colors), timestamp=ctx.message.created_at)
            embed.set_author(name=f"Todo #{position}", icon_url=ctx.author.avatar.url)
            embed.add_field(name="Description:", value=task)
            embed.set_thumbnail(url=ctx.author.avatar.url)

            await ctx.send(embed=embed)

def setup(hyena):
    hyena.add_cog(Todo(hyena))