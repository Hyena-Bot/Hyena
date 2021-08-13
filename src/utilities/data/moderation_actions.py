import datetime
import json

import discord


async def log(db, hyena, data, ctx):
    """
    For Donut:

    I added these docstrings for you to figure it out


    `db`: asyncpg.Connection
    Description: The db object

    `hyena`: SubClass Hyena ( Inherits from commands.Bot )
    Description: The hyena lmao

    `data`: dict
    Description: Now this is where stuff get complicated
    You have to do it in a specific manner
    ```python
    {
        "user_id": 69696969696, # Id of the user against which the moderation action was take
        "data": {
            "action": "The moderation action" # e.g. "Warn",
            "reason": "wutever"
            # You can add as many keys as you want.
            # These two are mandoratory you could add any others
        }
    }
    ```
    `ctx`: commands.Context
    Description: ctx ;-;
    """
    data["data"]["moderator"] = f"{ctx.author} ( {ctx.author.id} )"
    data["data"]["time"] = datetime.datetime.utcnow().strftime("%a %d-%m-%Y %H:%M UTC")
    _data = await db.fetchrow(
        "SELECT * FROM moderation_actions WHERE user_id = $1 AND guild_id = $2",
        data["user_id"],
        ctx.guild.id,
    )
    if _data is None:
        dumped_data = json.dumps([data["data"]])
        await db.execute(
            "INSERT INTO moderation_actions(guild_id, user_id, moderation_data) VALUES ($1, $2, $3)",
            ctx.guild.id,
            data["user_id"],
            dumped_data,
        )
    else:
        loaded_data = json.loads(_data[2])
        loaded_data.append(data["data"])
        dumped_data = json.dumps(loaded_data)
        await db.execute(
            "UPDATE moderation_actions SET moderation_data = $1 WHERE user_id = $2 AND guild_id = $3",
            dumped_data,
            data["user_id"],
            ctx.guild.id,
        )
