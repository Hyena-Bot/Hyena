class GuildConfig:
    def __init__(self, guild, hyena):
        self.guild = guild
        self.hyena = hyena
        self.db = self.hyena.main_db2

    async def get_channel(self):
        res = await self.db.fetch(
            "SELECT channel_id FROM modlogs WHERE guild_id = $1", self.guild.id
        )
        if not res:
            return None
        try:
            ch = await self.hyena.fetch_channel(res[0]["channel_id"])
        except:
            ch = None
        return ch


class CommandLogs:
    def __init__(self, hyena, *args, **kwargs):
        self.hyena = hyena

    async def send(self, ctx, embed):
        channel = await GuildConfig(ctx.guild, self.hyena).get_channel()
        if channel:
            try:
                await channel.send(embed=embed)
            except:
                pass

    async def send_2(self, guild, embed):
        channel = await GuildConfig(guild, self.hyena).get_channel()
        if channel:
            try:
                await channel.send(embed=embed)
            except:
                pass
