import asyncio
async def code(ctx, hyena): 
   await ctx.guild.create_text_channel(name=name, overwrites=overwrites, category=category,
           postition=postition, topic=topic, slowmode_delay=slowmode,
           nsfw=is_nsfw, reason=f"Channel nuke by: {ctx.author}, channel: {channel}")