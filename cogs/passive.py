import discord
from discord import DMChannel
from discord.embeds import Embed
from discord.ext import commands
import random
import datetime


# Passive Class include all the events, listeners and passive actions
# 
class Passive(commands.Cog):
    # Initialisation 
    def __init__(self, client):
        self.client = client

    # When Bot is ready
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")
    


    # ---------------------------------------------

    @commands.Cog.listener()
    async def on_message(self, message):
        def _check(m):
            return (
                m.author == message.author
                and len(m.mentions)
                and (datetime.datetime.utcnow() - m.created_at).seconds < 60
            )

        if not message.author.bot:
            if len(message.mentions):
                t = list(filter(lambda m: _check(m), self.client.cached_messages))
                if len(t) >= 3:
                    embed = Embed(
                        title = "Don't spam mentions!",
                    )
                    embed.set_footer(text = "Casted by Whitemane.")
                    embed.set_author(name = "Silence", icon_url = "https://cdn.discordapp.com/attachments/816542649707790348/842185223349075998/spell_shadow_impphaseshift.jpg")
                    #await message.channel.purge(limit = 3)
                    await message.channel.send(embed = embed, delete_after = 15)
                    # warn!

            # ban words!

            if isinstance(message.channel, DMChannel):
                if len(message.content) < 10:
                    await message.channel.send("Your message should be at least 10 characters.", delete_after = 30)
                else:
                    member = self.client.guild.get_member(message.author.id)
                    embed = Embed(
                        title = "Modmail",
                        color = member.color,
                        timestamp = datetime.datetime.utcnow()
                    )
                    field = [("Member", member.display_name, False), ("Message", message.content, False)]
                    for name, value, inline in field:
                        embed.add_field(
                            name = name,
                            value = value,
                            inline = inline
                        )
                    channel = discord.utils.get(member.guild.channels, name = "modmail")
                    if not channel:
                        await message.channel.send("Can not found a channel challed modmail. Please contact moderator.")
                    else:
                        await channel.send(embed = embed, delete_after = 30)
                        #await message.channel.send("Message relayed to moderators.")
        
        # Whenever the bot is tagged, respond with its prefix and her photo
        if message.content.startswith(f"<@!{self.client.user.id}>") and len(message.content) == len(
            f"<@!{self.client.user.id}>"
        ):
            prefix = self.client.DEFAULTPREFIX

            portrait = discord.Embed(
                title = f"My prefix here is `{prefix}`",
                color = self.client.colors["RED"]
            )
            portrait.set_image(url = "https://cdn.discordapp.com/attachments/816542649707790348/844084152151441418/portrait.png")
            await message.channel.send(embed = portrait, delete_after = 30)
            await message.delete(delay = 30)
            # await message.channel.send(f"My prefix here is `{prefix}`", delete_after=15)
        
        

    # When someone joined the server
    # Muted them if they are in the muted list
    # Give them a 'New' role
    @commands.Cog.listener() # @commands.Cog.event 这个？
    async def on_member_join(self, member): 
        # Do not apply this command on bots
        if member.bot:
            return

        # On member joins we find a channel called 'all-members-ann' and if it exists,
        # send an embed welcoming them to our guild
        channel = discord.utils.get(member.guild.text_channels, name='all-members-ann')
        if channel:
            embed = discord.Embed(description='Welcome to our guild!', color=random.choice(self.client.color_list))
            embed.set_thumbnail(url=member.avatar_url)
            embed.set_author(name=member.name, icon_url=member.avatar_url)
            embed.set_footer(text=member.guild, icon_url=member.guild.icon_url)
            embed.timestamp = datetime.datetime.utcnow()

            await channel.send(embed=embed)

    # when someone left the server
    #@commands.Cog.event 这个？
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        # On member remove we find a channel called general and if it exists,
        # send an embed saying goodbye from our guild-
        channel = discord.utils.get(member.guild.text_channels, name='all-members-ann')
        if channel:
            embed = discord.Embed(description='Goodbye from all of us..', color=random.choice(self.client.color_list))
            embed.set_thumbnail(url=member.avatar_url)
            embed.set_author(name=member.name, icon_url=member.avatar_url)
            embed.set_footer(text=member.guild, icon_url=member.guild.icon_url)
            embed.timestamp = datetime.datetime.utcnow()

            await channel.send(embed=embed)


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # Ignore these errors
        ignored = (commands.CommandNotFound, commands.UserInputError)
        if isinstance(error, ignored):
            return

        if isinstance(error, commands.CommandOnCooldown):
            # If the command is currently on cooldown trip this
            m, s = divmod(error.retry_after, 60)
            h, m = divmod(m, 60)
            if int(h) == 0 and int(m) == 0:
                await ctx.send(f" You must wait {int(s)} seconds to use this command!")
            elif int(h) == 0 and int(m) != 0:
                await ctx.send(
                    f" You must wait {int(m)} minutes and {int(s)} seconds to use this command!"
                )
            else:
                await ctx.send(
                    f" You must wait {int(h)} hours, {int(m)} minutes and {int(s)} seconds to use this command!"
                )
            return # Avoid raising error
        elif isinstance(error, commands.CheckFailure):
            # If the command has failed a check, trip this
            await ctx.send("Hey! You lack permission to use this command.")
        elif isinstance(error, commands.BadArgument):
            print("error\n")
        # Implement further custom checks for errors here...
        raise error


def setup(client):
    client.add_cog(Passive(client))