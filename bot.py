import os
import discord
from discord.ext import commands
from pathlib import Path
# For read json file
import helpers.json_loader
# In util.py and it's for eval(), but I didn't add this funciton yet.

# Use current working path and print it in terminal (估计也能用./的方式)
cwd = Path(__file__).parents[0]
cwd = str(cwd)
print(f"{cwd}\n\n")

# Help command requires member intents
intents = discord.Intents.all()  



# 定义Token位置
secret_file = helpers.json_loader.read_json("secrets")
# 命令前缀 不分大小写 使用client为变量名
client = commands.Bot( 
    command_prefix = ".",
    case_insensitive = True,
    owner_id = 597569645456785425,
    help_command = None,
    intents = intents,
)

# 声明client里的变量
client.config_token = secret_file["token"] 
client.DEFAULTPREFIX = "."
client.blacklisted_users = []
client.cwd = cwd 
client.guild = None
client.version = "0.4.0" 

client.colors = {
  'WHITE': 0xFFFFFF,
  'AQUA': 0x1ABC9C,
  'GREEN': 0x2ECC71,
  'BLUE': 0x3498DB,
  'PURPLE': 0x9B59B6,
  'LUMINOUS_VIVID_PINK': 0xE91E63,
  'GOLD': 0xF1C40F,
  'ORANGE': 0xE67E22,
  'RED': 0xFF2400,
  'NAVY': 0x34495E,
  'DARK_AQUA': 0x11806A,
  'DARK_GREEN': 0x1F8B4C,
  'DARK_BLUE': 0x206694,
  'DARK_PURPLE': 0x71368A,
  'DARK_VIVID_PINK': 0xAD1457,
  'DARK_GOLD': 0xC27C0E,
  'DARK_ORANGE': 0xA84300,
  'DARK_RED': 0x992D22,
  'DARK_NAVY': 0x2C3E50
}
client.color_list = [c for c in client.colors.values()]

# 载入Bot
@client.event
async def on_ready():
    # On ready, print some details to standard out
    print(
        f"-----\nLogged in as: {client.user.name} : {client.user.id}\n-----\nMy current prefix is: {client.DEFAULTPREFIX}\n-----"
    )
    # 更改Bot的状态与Play，也可以: ... discord.Game.(name=f”内容“)
    await client.change_presence(status = discord.Status.online, activity = discord.Game("World of Warcraft"))

    print(f"Current Roles:\n{client.roles}\n")
    print(f"Current Reaction Roles:\n{client.reaction_roles}\n")
    client.guild = client.get_guild(700578122067738635)
    print("Initialized Database\n-----")

@client.event
async def on_message(message):
    # Ignore messages sent by yourself
    if message.author.bot:
        return

    # A way to blacklist users from the bot by not processing commands
    # if the author is in the blacklisted_users list
    if message.author.id in client.blacklisted_users:
        return
    

    await client.process_commands(message)
    


#---------------- Load Cogs ------------------

if __name__ == "__main__":
    # When running this file, if it is the 'main' file
    # I.E its not being imported from another python file run this
    
    client.roles = helpers.json_loader.read_json("roles")
    client.reaction_roles = helpers.json_loader.read_json("reaction_roles")

    for file in os.listdir(cwd + "/cogs"):
        if file.endswith(".py") and not file.startswith("_"):
            client.load_extension(f"cogs.{file[:-3]}")

client.run(client.config_token)
