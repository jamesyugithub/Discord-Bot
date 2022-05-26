import discord
from discord.ext import commands
import platform
import helpers.json_loader

class Setting(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    # COMMAND: ".stats"
    # DESCRIPTION: that show bot's information
    @commands.command(
        name='stats',
        description="Show the bot' information.",
        usage=''
    )
    async def stats(self, ctx):
        pythonVersion = platform.python_version()
        dpyVersion = discord.__version__
        serverCount = len(self.client.guilds)
        memberCount = len(set(self.client.get_all_members()))
        # 注意timestamp
        embed = discord.Embed(title=f'{self.client.user.name} Stats', description='\uFEFF', colour=ctx.author.colour, timestamp=ctx.message.created_at)

        embed.add_field(name='Bot Version:', value=self.client.version)
        embed.add_field(name='Python Version:', value=pythonVersion)
        embed.add_field(name='Discord.Py Version', value=dpyVersion)
        embed.add_field(name='Total Guilds:', value=serverCount)
        embed.add_field(name='Total Users:', value=memberCount)
        embed.add_field(name='Bot Developers:', value="<@597569645456785425>")

        embed.set_footer(text=f"Carpe Noctem | {self.client.user.name}")
        embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url) # 可以不要

        await ctx.send(embed=embed)
        


    # COMMAND: ".load"
    # DESCRIPTION: Load the cog files
    @commands.command(
        name='load',
        description='Load cog files.',
        hidden = True # Hide this command from the embeded command list, but can use ".help act"
    )
    async def load(self, ctx, extension):
        self.client.load_extension(f'cogs.{extension}')


    # COMMAND: ".unload"
    @commands.command(
        name='unload',
        description='Unload cog files.',
        hidden = True
    )
    async def unload(self, ctx, extension):
        self.client.unload_extension(f'cogs.{extension}')
    

    # COMMAND: ".reload"
    @commands.command(
        name='reload',
        description='Reload cog files.',
        hidden = True
    )
    async def reload(self, ctx, extension):
        self.client.unload_extension(f'cogs.{extension}')
        self.client.load_extension(f'cogs.{extension}')
        await ctx.message.delete(delay=15)


    # COMMAND: ".blacklist" and ".unblacklist"
    # DESCRIPTION: Blacklist system. The file is local.
    @commands.command(
        name="blacklist",
        description="Set who cannot use this bot. (Owner)",
        usage="<user>"
    )
    @commands.is_owner()
    async def blacklist(self, ctx, user: discord.Member):
        if ctx.message.author.id == user.id:
            await ctx.send("Hey, you cannot blacklist yourself!")
            return

        self.client.blacklisted_users.append(user.id)
        data = utils.json_loader.read_json("blacklist")
        data["blacklistedUsers"].append(user.id)
        utils.json_loader.write_json(data, "blacklist")
        await ctx.send(f"Hey, I have blacklisted {user.name} for you.")

    @commands.command(
        name="unblacklist",
        description="Remove a user from the blacklist. (Owner)",
        usage="<user>"
    )
    @commands.is_owner()
    async def unblacklist(self, ctx, user: discord.Member):
        self.client.blacklisted_users.remove(user.id)
        data = utils.json_loader.read_json("blacklist")
        data["blacklistedUsers"].remove(user.id)
        utils.json_loader.write_json(data, "blacklist")
        await ctx.send(f"Hey, I have unblacklisted {user.name} for you.")


    
    @commands.command(
        name="addrole",
        description="Upsert a role to the list.",
        usage="<role code> <role name>"
    )
    @commands.is_owner()
    async def addrole(self, ctx, code, name):
        if not code or not name:
            await ctx.send("You must give me both role's code and role's name!", delete_after = 15)
            return
        
        role = discord.utils.get(ctx.guild.roles, name = name)
        if not role:
            await ctx.send("Role was not found! Please contact the admin.")
            return
        
        data = self.client.roles[code]

        if code in data:
            data[code] = name
            utils.json_loader.write_json(data, "roles")
            await ctx.send("The code is already in the list, I will update it.", delete_after = 15)
        else:  
            data[code] = name
            utils.json_loader.write_json(data, "roles")
            await ctx.send(f"I have added {code} for role {name} into the list.", delete_after = 15)


    @commands.command(
        name="removerole",
        description="Remove a role from the list.",
        usage="<role code>"
    )
    @commands.is_owner()
    async def removerole(self, ctx, code):
        if not code:
            await ctx.send("You must tell me what role you want to remove code", delete_after = 15)
            return
        
        inDictionary = self.client.roles.pop(code, None)
        data = self.client.roles
        
        if not inDictionary:
            await ctx.send("No such role in the list.", delete_after = 15)
            return

        utils.json_loader.write_json(data, "roles")
        await ctx.send(f"The role {code} has been removed.", delete_after = 15)

    
    

def setup(client):
    client.add_cog(Setting(client))