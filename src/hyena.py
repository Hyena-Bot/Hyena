import ast
import asyncio
import datetime
import math
import os
import random
import sqlite3
import sys
import traceback

import asyncpg
import discord
import inputimeout
import topgg
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()
hyena_intents = discord.Intents.all()
hyena_intents.presences = False


class Hyena(commands.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(
            command_prefix=self._get_hyena_prefix,
            owner_ids=[711444754080071714, 699543638765731892],
            intents=hyena_intents,
            allowed_mentions=discord.AllowedMentions(
                everyone=False, roles=False, users=True, replied_user=False
            ),
            description="The main purpose of this bot is to help you manage your discord server in a pretty good way, hyena offers you with a lot of stuff such as AutoModeration, General Moderations, and a lot more.",
            *args,
            **kwargs,
        )

        self.help_command = None
        self.secrets = {
            x: y
            for x, y in os.environ.items()
            if x in ["TOKEN", "POSTGRES", "TOPGG", "API_KEY"]
        }
        self.applying = []
        self.prefix_caches = {}
        self.get_version = self.get_hyena_version
        self.get_commands = self.get_total_commands
        self.hyena_cogs = [
            f"cogs.{cog[:-3]}"
            for cog in os.listdir("cogs")
            if cog.endswith(".py") and not cog.startswith("_")
        ]
        self.colors = [0xFFFDFC, 0x3A4047]
        from utilities.data import action_logs
        from utilities.data import automod as am
        from utilities.data import tools

        self.tools = tools
        self.action_logs_pkg = action_logs
        self.automod_handler = am.Detections
        self.launch_time = datetime.datetime.utcnow()
        self.topgg = topgg.DBLClient(self, self.secrets["TOPGG"])

    async def on_error(self, event_method: str, *args, **kwargs) -> None:
        console = self.get_channel(794467788332728365)
        embeds = self.tools.error_to_embed()
        context_embed = discord.Embed(
            title="Context",
            description=f"**Event**: {event_method}",
            color=discord.Color.red(),
        )
        await console.send(embeds=[*embeds, context_embed])

    def run(self):

        prompt = """
Which mode do you wanna boot to?

Available Modes: 
Secure [Only dev Commands]
Normal [Regular usage]
CDev [All commands but only devs can run commands]

After 5 seconds hyena will default to normal boot     
"""
        try:
            current_mode_type = (
                inputimeout.inputimeout(prompt=prompt + "\n", timeout=5).lower().strip()
            )
        except:
            current_mode_type = "normal"

        if current_mode_type in ["", " ", "normal", "production", "prod"]:
            self.current_mode_type = "normal"
        elif current_mode_type in ["dev", "development", "prodnt", "prodn't"]:
            self.current_mode_type = "dev"
        elif current_mode_type in ["cdev", "devcommands"]:
            self.current_mode_type = "cdev"
        else:
            self.current_mode_type = "normal"

        print(f"--- Continuing with {self.current_mode_type.title()} mode ---")
        if self.current_mode_type != "dev":
            try:
                for cog in self.hyena_cogs:
                    try:
                        self.load_extension(cog)
                    except Exception as e:
                        raise e
            except Exception as e:
                raise e
        super().run(self.secrets["TOKEN"])

    async def _get_hyena_prefix(self, hyena, message):
        base = [f"<@!{hyena.user.id}> ", f"<@{hyena.user.id}> "]
        prefixes = None
        try:
            caches = self.prefix_caches[message.guild.id]
            prefixes = [*caches, *base]
        except KeyError:
            pass

        if prefixes is None:
            result = await hyena.main_db.fetch(
                f"SELECT prefix FROM prefixes WHERE guild_id = $1", message.guild.id
            )

            if result:
                lst = result[0]["prefix"]
                prefixes = [*lst, *base]
                hyena.prefix_caches[message.guild.id] = lst
            if not result:
                prefixes = ["-", *base]

        return prefixes

    async def connect_database(self):
        self.main_db = await asyncpg.create_pool(
            database="hyena",
            user="postgres",
            password=self.secrets["POSTGRES"],
            host="127.0.0.1",
        )
        self.main_db2 = await asyncpg.create_pool(
            database="hyena2",
            user="postgres",
            password=self.secrets["POSTGRES"],
            host="127.0.0.1",
        )
        self.automod_db = await asyncpg.create_pool(
            database="hyena_automod",
            user="postgres",
            password=self.secrets["POSTGRES"],
            host="127.0.0.1",
        )
        self.welcome_goodbye_db = await asyncpg.create_pool(
            database="hyena_welcome_goodbye",
            user="postgres",
            password=self.secrets["POSTGRES"],
            host="localhost",
        )
        self.toggle_db = await asyncpg.create_pool(
            database="hyena_toggle",
            user="postgres",
            password=self.secrets["POSTGRES"],
            host="localhost",
        )

    def get_hyena_version(self):
        with open("./assets/version.txt", "r") as f:
            return f.read()

    def get_total_commands(self, hyena):
        total = 0
        for command in hyena.commands:
            if type(command).__name__ == "Group":
                total += len(command.commands) + 1
                continue
            total += 1

        return total

    clear = lambda self: os.system("cls" if os.name == "nt" else "clear")

    async def on_ready(self):
        await self.wait_until_ready()
        channel = self.get_channel(794467787988008973)
        embed = discord.Embed(
            title="Hyena has been booted up!",
            colour=random.choice(self.colors),
            description=f"Logged in as {self.user}.",
        )
        try:
            await channel.send(embed=embed)
        except:
            pass
        self.change_status.start()

        message = "Booting up hyena..."
        for i in range(2):
            for i in range(len(message), len(message) - 4, -1):
                self.clear()
                print(message[:i])
                await asyncio.sleep(1)
        self.clear()
        print(len(message) * "\b")
        sys.stdout.write("\033[F")
        print(f"Logged in as {self.user}.")

    def get_blacklisted_users(self):
        db = sqlite3.connect("./data/dev.sqlite")
        cursor = db.cursor()
        cursor.execute("SELECT * FROM blacklists")
        r = cursor.fetchall()

        try:
            users = r[0][0]
        except:
            return []

        users = users.strip("][").split(", ")
        if users == [""]:
            return users
        users = [int(i) for i in users]
        return users

    async def process_commands(self, message):
        if message.guild is None or message.author.bot:
            return

        await super().process_commands(message)

    async def on_message(self, message):
        if self.current_mode_type == "cdev":
            if message.author.id not in self.owner_ids:
                return
        if message.author.id in self.get_blacklisted_users():
            return

        await self.process_commands(message)

    def get_cog_aliases(self, term: str):
        # aliases = {
        #     ("afk",) : "afk",
        #     ("application", "applications", "apply") : "application",
        #     ("automod", "automoderation", "am") : "automod",
        #     ("command-logs", "cmd_logs", "cmd-logs") : "command-logs",
        #     ("dev", "developer", "development") : "dev",
        #     ("fun-cmds", "fun", "fun_commands", "fun_commands") : "fun-cmds",
        #     ("giveaway", "giveaways", "gws", "gw") : "giveaways",
        #     ("goodbye-welcome", "leave-join", "welcome", "goodbye") : "goodbye-welcome",
        #     ("help", "helpcmd") : "help",
        #     ("hyena-mail", "mail", "hyena_mail") : "hyena-mail",
        #     ("invites", "invite", "inv") : "invites",
        #     ("logging", "logs", "log") : "logging",
        #     ("mod_actions", "actions", "moderation_actions") : "mod_actions",
        #     ("moderation", "mod") : "moderation",
        #     ("mute-system", "mute", "mutes") : "mute-system",
        #     ("prefix", "prefixes", "pre") : "prefix",
        #     ("roles", "role", "ar", "role-sys") : "roles",
        #     ("starboard", "sb") : "starboard",
        #     ("suggestions", "suggestion", "suggest") : "suggestions",
        #     ("support-server", "hyena-development", "hyena-dev", "ss") : "support-server",
        #     ("tickets", "ticket") : "tickets",
        #     ("todo", "todo_list") : "todo",
        #     ("toggle", "toggles", "enable", "disable") : "toggle",
        #     ("utils", "utilities", "util") : "utils",
        #     ("warns", "warn") : "warns",
        #     ("core-handlers", "handlers", "core") : "core-handlers"
        # }
        aliases = {
            ("core-handlers", "handlers", "core"): "core-handlers",
            ("afk",): "afk",
            ("chatbot", "chat", "ai", "ai-chatbot"): "chatbot",
            (
                "mod_actions",
                "actions",
                "moderation_actions",
                "action-logs",
            ): "action-logs",
            ("moderation", "mod"): "moderation",
            ("utils", "utilities", "util"): "utils",
            ("serverconf", "conf", "server"): "serverconf",
            ("fun", "fun-cmds"): "fun",
            ("apps", "applications", "app", "applications"): "applications",
            ("dev", "developer", "development"): "dev",
            ("prefix", "prefixes", "pre"): "prefix",
            ("tickets", "ticket"): "tickets",
            (
                "goodbye-welcome",
                "leave-join",
                "welcome",
                "goodbye",
                "welcome-goodbye",
            ): "welcome-goodbye",
            ("todo", "todos", "to-do"): "todo",
            ("logging", "logs", "log"): "logging",
            ("giveaway", "giveaways", "gws", "gw"): "giveaways",
            ("mute-system", "mute", "mutes"): "mute-system",
        }

        for alias, cog in aliases.items():
            if term.lower() in alias:
                return cog
        return term

    async def handle_load(self, ctx, cog: str):
        if cog in ["*", "all"]:
            errored_out = []
            for cog in self.hyena_cogs:
                try:
                    self.load_extension(cog)
                except commands.errors.ExtensionAlreadyLoaded:
                    errored_out.append((cog[5:], "This extension is already loaded"))
                except commands.errors.ExtensionNotFound:
                    errored_out.append((cog[5:], "This extension was not found"))
                except Exception as e:
                    errored_out.append((cog[5:], str(e)))
            if errored_out == []:
                return await ctx.send("Successfully completed the operation.")

            newline = "\n"

            await ctx.send(
                f"""
Successfully completed the operation. 
```
Errored out : {newline.join([f"{x[0]} : {x[1]}" for x in errored_out])}
```
"""
            )
            return

        if cog.endswith(".py"):
            cog = cog[:-3]

        cog = self.get_cog_aliases(cog)

        try:
            self.load_extension(f"cogs.{cog}")
            await ctx.message.add_reaction("<:OP_Verified:815589801586851840>")
        except commands.errors.ExtensionAlreadyLoaded:
            await ctx.send(f"The cog `{cog}` is already loaded")
        except commands.errors.ExtensionNotFound:
            await ctx.send(f"The cog `{cog}` is Not found...")
        except:
            embed = discord.Embed(
                title=f"Error while loading ext: {cog}", color=discord.Colour.red()
            )
            embed.description = f"""
    ```py
    {traceback.format_exc()}
    ```
    """
            await ctx.send(embed=embed)

    async def handle_unload(self, ctx, cog: str):
        if cog in ["*", "all"]:
            errored_out = []
            for cog in self.hyena_cogs:
                try:
                    self.unload_extension(cog)
                except commands.errors.ExtensionNotLoaded:
                    errored_out.append((cog[5:], "This extension was not loaded"))
                except commands.errors.ExtensionNotFound:
                    errored_out.append((cog[5:], "This extension was not found"))
                except Exception as e:
                    errored_out.append((cog[5:], str(e)))
            if errored_out == []:
                return await ctx.send("Successfully completed the operation.")

            newline = "\n"

            await ctx.send(
                f"""
Successfully completed the operation.
```
Errored out : {newline.join([f"{x[0]} : {x[1]}" for x in errored_out])}
```
"""
            )
            return

        if cog.endswith(".py"):
            cog = cog[:-3]

        cog = self.get_cog_aliases(cog)

        try:
            self.unload_extension(f"cogs.{cog}")
            await ctx.message.add_reaction("<:OP_Verified:815589801586851840>")
        except commands.errors.ExtensionNotLoaded:
            await ctx.send(f"The cog `{cog}` isn't even loaded.")
        except commands.errors.ExtensionNotFound:
            await ctx.send(f"The cog `{cog}` is Not found...")
        except:
            embed = discord.Embed(
                title=f"Error while loading ext: {cog}", color=discord.Colour.red()
            )
            embed.description = f"""
    ```py
    {traceback.format_exc()}
    ```
    """
            await ctx.send(embed=embed)

    async def handle_reload(self, ctx, cog: str):
        if cog in ["*", "all"]:
            errored_out = []
            for cog in self.hyena_cogs:
                try:
                    self.reload_extension(cog)
                except commands.errors.ExtensionNotLoaded:
                    errored_out.append((cog[5:], "This extension was not loaded"))
                except commands.errors.ExtensionNotFound:
                    errored_out.append((cog[5:], "This extension was not found"))
                except Exception as e:
                    errored_out.append((cog[5:], str(e)))
            if errored_out == []:
                return await ctx.send("Successfully completed the operation.")

            newline = "\n"
            return await ctx.send(
                f"""
    Successfully completed the operation. 
    ```
    Errored out : {newline.join([f"{x[0]} : {x[1]}" for x in errored_out])}
    ```
    """
            )

        if cog.endswith(".py"):
            cog = cog[:-3]

        cog = self.get_cog_aliases(cog)

        try:
            self.reload_extension(f"cogs.{cog}")
            await ctx.message.add_reaction("<:OP_Verified:815589801586851840>")
        except commands.errors.ExtensionNotLoaded:
            await ctx.send(f"The cog `{cog}` isn't even loaded.")
        except commands.errors.ExtensionNotFound:
            await ctx.send(f"The cog `{cog}` is Not found...")
        except:
            embed = discord.Embed(
                title=f"Error while loading ext: {cog}", color=discord.Colour.red()
            )
            embed.description = f"""
    ```py
    {traceback.format_exc()}
    ```
    """
            await ctx.send(embed=embed)

    @tasks.loop(seconds=20)
    async def change_status(self):
        status = [
            discord.Streaming(name="On -help", url="https://bit.ly/hyena-bot"),
            discord.Game(name="With the BAN HAMMER! | -help"),
            discord.Activity(
                type=discord.ActivityType.watching, name="The Chat! | -help"
            ),
            discord.Game(
                name=f"On {len(self.guilds)} Guilds With {len(self.users)} Users | -help"
            ),
            discord.Activity(
                type=discord.ActivityType.listening,
                name="the mods While eating Donuts | -help",
            ),
            discord.Activity(
                type=discord.ActivityType.competing, name="With Other Bots! | -help"
            ),
            discord.Game(name="Got a new upgrade im v3.0 | -help"),
        ]
        await self.change_presence(
            activity=random.choice(status), status=discord.Status.dnd
        )
