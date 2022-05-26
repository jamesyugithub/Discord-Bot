from typing import Optional
import discord
from discord.ext import commands
import random


# This class defines bot's normal abilities for general purpose.
# Public Commands: say, poke, roll, ask
# Restrict Commands: displayf, purge

# Convert a string to a command dictionary.
# PARAM:
#   @argument the whloe string of user input
# RETURN:
#   cmds A map if the convertion was successful.
#   Otherwise return None.
class ArgumentConverter(commands.Converter): # Make this class a sub-class of commands.Converter
    async def convert(self, ctx, argument):
        if not argument:
            await ctx.send("Empty argument.", delete_after=15)
            return None
        # descSubst = desc.replace('\\n', '\n')
        keys = []
        values = []
        args = argument.split()
        print(args)
        cmds = {}
        content = ""
        for i, segment in enumerate(args):
            if segment.startswith('-'):
                keys.append(segment)
                if content != "":
                    values.append(str(content)[:-1])
                    content=""
                    print(content)
            elif i == len(args)-1:
                content += f"{segment}"
                values.append(content)
            else:
                content += f"{segment} "
        print(keys, values)
        if len(keys) != len(values):
            await ctx.send("The format of arguments are wrong.", delete_after = 15)
            return None
       
        cmds = dict(zip(keys, values))
        
        if "-a" in cmds and "-ai" not in cmds or "-ai" in cmds and "-a" not in cmds:
            await ctx.send("Must provide both author name and author icon.", delete_after=15)
            return None
        elif "-t" not in cmds and "-d" not in cmds and "-i" not in cmds:
            await ctx.send("Must have a tile or description.", delete_after=15)
            return None
        elif not cmds:
            await ctx.send("Command Dict is None.", delete_after=15)
            return None

        return cmds

# Convert the dict to build an embed
async def EmbedConverter(self, ctx, cmds):
    embed = discord.Embed(
            title="",
            description="",
            colour = self.client.colors["RED"]
        )
    for key, value in cmds.items():
        if key == "-t":
            embed.title = value
        elif key=="-d":
            embed.description = value
        elif key=="-a":
            embed.set_author(
            name=value,
            url=cmds["-ai"]
            )
        elif key=="-ai":
            continue
        elif key=="-i":
            embed.set_image(url=value)
            
        elif key=="-f":
            embed.set_footer=value
        else:
            await ctx.send("Unexpected argument.", delete_after=15)
            return None
    return embed


class Ability(commands.Cog): 
    
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    # --------- General abilities for everyone ---------

    # Roll the dice (1-100)
    @commands.command(
        aliases = ['ssz', 'random'],
        name='roll',
        description="Roll a dice from 1-100.",
    ) 
    async def roll(self, ctx):
        await ctx.send(f'{ctx.author.mention}掷出{random.randint(1, 100)}点（1-100）')

    # User ask a question, bot repeat it and give a random answer
    @commands.command(
        aliases = ['foresee', 'luck'],
        name='ask',
        description="Ask bot a question, try your luck!",
        usage='<question>'
    ) 
    async def ask(self, ctx, *, question): 
        question = question or "Ask me a question." # ?
        responses = ['It is certain.', 
                     'It is decidedly so.', 
                     'Yes.', 
                     'Out look not so good.', 
                     'Very doubtful.']
        #await ctx.send(f'Question: {question}\nAnswer: {random.choice(responses)}')
        await ctx.reply(f'Answer: {random.choice(responses)}')

    # --------- Abilities for bot's owner or server manager ---------

    # Send a embeded message in a specific channel (Blue)
    # Format:
    #   Title
    #   contant
    # What's left: User can input colour and channel

    @commands.group(
        aliases=['df', 'embed'],
        description="Main command that send embeded message.\n.<Main-cmd> <Sub-cmd> <Sub-cmd's argument>",
        invoke_without_command=True
    )
    @commands.guild_only()
    async def displayf(self, ctx):
        await ctx.invoke(self.client.get_command("help"), entity="displayf")

    # SUB-COMMAND: .df new
    #
    @displayf.command(
        name="new",
        description="Make a new embeded! -h channel, -t title, -d description, -a author, -ai author image, -i image, -f footer. No field addtion"
    )
    async def df_new(self, ctx, *, content:ArgumentConverter=None):
        if not content:
            return

        channel = None
        cmds = content

        if "-h" in cmds:
            channel = cmds["-h"]

        embeds = await EmbedConverter(self, ctx, cmds)
        if embeds.title == None and embeds.description == None  and embeds.image == None:
            await ctx.send("Error on converting embed.", delete_after=15)
            return

        await ctx.message.delete(delay=30)
        if (channel == None): # 在当前频道发布
            await ctx.send(embed = embeds) 
        else:
            if (channel.startswith("<#")):
                ch = self.client.get_channel(int(channel[2:-1])) # 
            else:
                ch = self.client.get_channel(int(channel))
            await ch.send(embed = embeds)
    
    @displayf.command(
        name="edit",
        description="Edit an embeded message.\nRequired argument: <-m> message ID and at least one of [-t] title, or [-d] description, or [-i] image link\nOptional argument: [-h] channel ID, [-f] footer, [-a] author, [-ai] author icon\n If you want to add author, you must have both [-a] and [-ai].\n"
    )
    @commands.guild_only()
    async def df_edit(self, ctx, *, argument:ArgumentConverter=None):
        if not argument:
            return
        cmds = argument
        if "-m" in cmds:
            message = await ctx.channel.fetch_message(cmds["-m"])
        else:
            await ctx.send("Must give me a message ID,", delete_after=15)
            return

        channel = None
        
        if "-h" in cmds:
            channel = cmds["-h"]
        
        embeds = await EmbedConverter(self, ctx, cmds)
        if not embeds:
            return

        await ctx.message.delete(delay=30)
        if (channel == None): # 在当前频道发布
            await message.edit(embed = embeds)
        else:
            if (channel.startswith("<#")):
                ch = self.client.get_channel(int(channel[2:-1])) # 
            else:
                ch = self.client.get_channel(int(channel))
            await message.edit(embed = embeds)

        
    # This command make bot send message in a specific channel
    # If channel parameter is not provided, it will send in current channel
    # Format: .say <内容> [频道]
    @commands.command(
        pass_context = True,
        name="say",
        description="Make bot post a message in a certain channel.If [channel] is not provided it will post the message in the current channel.",
        usage="<message> [channel]"
    )    
    @commands.cooldown(1, 3, commands.BucketType.user) # Can be .role or channel or guild to share the cooldown
    async def say(self, ctx, contant, ch=None):        # In this case 1 time in 3 seconds and every user has their own cooldown
        if (contant == None):
            return
        if (ch == None):
            await ctx.message.delete() # Delete command message
            await ctx.send(contant)
        else:
            if (ch.startswith("<#")):
                channel = self.client.get_channel(int(ch[2:-1])) # 
            else:
                channel = self.client.get_channel(int(ch))
            await channel.send(contant)
  

    # COMMAND: .purge
    # DISCRIPTION: Clear current channel including the command message itself
    # PARAM: 
    #   @amount The amount of message need to be deleted. Default = 5 If argument is none.
    @commands.command(
        aliases = ["clear", "massdispel"],
        name="purge",
        description="Delete message in current channel. Default amount is 5.",
        usage='[amount]'
    ) 
    async def purge(self, ctx, amount:Optional[int] = 5): # 5 messages
        def not_pinned(message):
            return not message.pinned
        if 0 < amount <= 100:
            await ctx.message.delete()
            deleted = await ctx.channel.purge(limit = amount, check = not_pinned) # Also delete the command
            embed = discord.Embed(
                title = "This channel must be purged!",
                #title = f"{ctx.author.name} purged: {ctx.channel.name}", 
                description = f"{len(deleted)} messages were cleared.",
            )
            embed.set_footer(text = f"Casted by {ctx.author.name}.")
            embed.set_author(name = "Mass Dispel", icon_url = "https://cdn.discordapp.com/attachments/816542649707790348/842186920398028831/spell_arcane_massdispel.jpg")
            
            await ctx.send(embed=embed, delete_after = 15) # Delete after 15 seconds
        else:
            await ctx.message.delete(delay = 15)
            await ctx.send("Amount must be greater than 0 and less than 100.", delete_after=15)
    
    
    # COMMAND: .poke
    # DISCRIPTIN: Show Whitemane's quotes in game. 
    # AUTHORITY: All members
    @commands.command(
        aliases = ["click", "quote"],
        name="poke",
        description="Show Whitemane's quotes and its reference for 1 minute.",
    )
    async def poke(self, ctx):
        choice = random.choice(quote_list)
        embed = discord.Embed(
            title = choice,
            description = quote[choice],
            color = random.choice(self.client.color_list)
        )
        await ctx.send(embed=embed, delete_after=60)
        await ctx.message.delete(delay=63)
        
    
       
    
def setup(client):
    client.add_cog(Ability(client))
    
quote = {
        "Greetings. What do you seek?":"The on-click quotes spoken by the death knight version of Whitemane in World of Warcraft: Legion",
        "I've found that without proper guidance, Crusades quickly become Onslaughts.":"At the start of the Wrath of the Lich King expansion, Scarlet Crusade forces led by High General Brigitte Abbendis left Lordaeron behind and instead journeyed to the arctic continent of Northrend to battle the undead Scourge, with Abbendis declaring that the Scarlet Crusade was no more and that they would now be called the Scarlet Onslaught. However, despite this, the Scarlet Crusade and its members (including Whitemane) remained active in Lordaeron as a separate entity from the Onslaught.",
        "I know we're supposed to call everyone heroes these days, but Renault will always remain my champion.":"Possibly a joke about how some players incorrectly refer to heroes in HotS as \"champions\", as that is what playable characters are called in League of Legends. Renault Mograine was the son of the famed paladin Alexandros \"the Ashbringer\" Mograine. He was manipulated by the dreadlord Balnazzar to murder his father with his namesake sword the Ashbringer, and later joined the newly-formed Scarlet Crusade as the commander of Scarlet Monastery, which he oversaw alongside High Inquisitor Whitemane. In classic WoW, Scarlet Commander Mograine served as the final boss of the Scarlet Monastery dungeon alongside Whitemane. Players would first face Mograine, and upon killing him, Whitemane would emerge from her chamber, resurrect Renault with the words \"Arise, my champion\", and resume the fight at his side. Canonically, however, Renault was eventually killed by his father's vengeful spirit due to the actions of his younger brother Darion. Years later, when the in-game Scarlet Monastery was revamped in the Mists of Pandaria expansion, Renault was replaced as Whitemane's companion and Scarlet Monastery's military commander by a man named Commander Durand. Even so, when Whitemane is killed by players a final time in the revamped Monastery, her last words are \"Mograine...\"",
        "Oh, you noticed the new chapeau? It's not on my loot table, so don't try anything.":"Whitemane is widely known for her iconic hat, which she wears in her boss encounter in Scarlet Monastery and which is among the loot that can drop from her after death (in the form of \"Whitemane\'s Chapeau\" in the original Scarlet Monastery and \"Whitemane\'s Embroidered Chapeau\" in the updated version). Many Scarlet Monastery dungeon runs have taken place simply because a player desires to get their hands on the chapeau due to its distinctive appearance. As with many characters who make the transition into the Nexus, Whitemane's HotS appearance and clothing — including her hat — are slightly different from her WoW model, hence the comment about having a new chapeau.",
        "I'm not bad. I'm just rendered that way.":"Reference to a quote by Jessica Rabbit from the 1988 hybrid live-action/computer-animated film Who Framed Roger Rabbit: \"I'm not bad. I'm just drawn that way.\" Both Sally and Jessica wear distinctive red clothing, and both of them are also quite heavily sexualized characters.",
        "Why does everyone who comes to the Scarlet Monastery want to kill me? Am I out of touch? ...No, it is the heathens who are wrong.":"While the Scarlet Crusade believed that they were righteous in their quest to eliminate undead, pretty much everyone else saw them as dangerous lunatics. This quote is a reference to a line by Seymour Skinner from a 1994 episode of The Simpsons: \"Am I so out of touch? No, it's the children who are wrong.\"",
        "We Whitemanes have never approved of the Greymanes' rule. They're too neutral. With Blackmanes you know where they stand, but with Greymanes, who knows? It sickens me.":"The Greymanes are the royal family of the human kingdom of Gilneas, represented in Heroes of the Storm by King Genn Greymane. This quote is purely poking fun at the similarities between the names \"Greymane\" and \"Whitemane\", as Whitemane has absolutely no connection to the Greymane family lore-wise; specifically, this quote is a reference to a line spoken by Zapp Brannigan in a 1999 episode of Futurama: \"I hate these filthy neutrals, Kif. With enemies you know where they stand, but with neutrals, who knows? It sickens me.\" As for Blackmane, there aren't any known human families by that name, and the only thing called \"Blackmane\" in Warcraft is a group of gnoll mercenaries briefly encountered in Mists of Pandaria.",
        "I always ensure my champions keep on fighting until the end.":"Refers to Whitemane's ability to resurrect her allies after death, which she uses during her boss encounter in WoW to bring Renault/Durand and numerous lesser Scarlet Crusaders back to life to fight for her. This quote is likely also a reference to the lyrics of the 1977 Queen song \"We Are the Champions\". (Thanks to /u/CommandThrower for pointing the latter part out.)",
        "Well, Renault always got a 'rise' out of that one.":"A pun on the phrase \"getting a rise out of\" along with Sally's resurrections of Renault and the famous quote accompanying it.",
        "My Scarlet Diviners examined every Scarlet letter of every Scarlet book in Scarlet Monastery's Scarlet Library, yet none was a Scarlet thesaurus, so I burnt it down.":"Seems to just be a joke about how most things associated with the Scarlet Crusade have \"Scarlet\" in the name, though it could also partially be a reference to the 1850 Nathaniel Hawthorne novel The Scarlet Letter. The Library is a wing of Scarlet Monastery, later made part of the separate Scarlet Halls dungeon in the Mists of Pandaria revamp. Scarlet Diviners were mobs that could be found in the Library prior to the revamp. The comment about burning the library down is possibly a nod to Flameweaver Koegler, the final boss of the revamped Scarlet Halls, who is a fire mage attempting to burn away all records of the Scarlet Crusade's past failures.",
        "Me? A Horseman of the Ebon Blade? I would never serve the undead! Besides, do I look like I'd be caught dead in black?":"In World of Warcraft: Legion, years after Sally's canonical final death in Scarlet Monastery, the death knights of the Knights of the Ebon Blade raised her into undeath to become a member of the recreated Four Horsemen, a group of four powerful death knights, despite the hatred she had had for the undead in life. Aside from being freed from her insanity, the reanimated Whitemane also abandoned her old red robes in favor of black plate armor befitting a death knight.",
        "No one expects the Scarlet inquisition!":"An obvious reference to the Spanish Inquisition from Monty Python's Flying Circus. Amongst the similarities between the Spanish Inquisition and the Scarlet Crusade are such diverse elements as ruthless efficiency, torture, and an almost fanatical devotion to their religion. And nice red uniforms.",
        "Arise, my champion!":"This is perhaps Whitemane's most iconic line, spoken upon resurrecting Scarlet Commander Mograine and later Commander Durand in WoW's Scarlet Monastery dungeon.",
        "I have arisen. An interesting reversal.":"A nod to the above line and the fact that while Whitemane is usually the one doing the resurrections, in HotS she is the one who can be brought back to life by her allies. However, interestingly, it's implied in WoW that Whitemane was even able to resurrect herself after death, which is why players had to use the swords known as the Blades of the Anointed to kill her permanently in the revamped Mists of Pandaria version of Scarlet Monastery.",
        "The Light has spoken! You will pay for this treachery!":"Lines spoken by Whitemane in both the original and revamped Scarlet Monastery. The first one is spoken when she kills a player, the latter when she first emerges from her chamber to engage the players after Mograine/Durand is killed (in the original Scarlet Monastery, she said \"Mograine has fallen? You shall pay for this treachery!\", while in the revamped version she leaves out the first part and just says \"You shall pay for this treachery!\").",
        "We attack as one! We are victorious!":"These are also Whitemane quotes from WoW, but not from Scarlet Monastery. Instead, they are references to Old Hillsbrad Foothills (AKA Escape from Durnholde Keep), a dungeon in which players travel back in time to a past version of the Hillsbrad Foothills region of Lordaeron to free Thrall from captivity in the fortress of Durnholde and prevent the evil infinite dragonflight from interfering with the timeline. If players travel off the beaten path they can visit the town of Southshore and see past versions of many famous characters, such as Alexandros Mograine and Kel'Thuzad. They can also find a little girl by the name of Sally Whitemane, playing at slaying monsters (i.e., harmless frogs) with her friends Renault Mograine and Little Jimmy Vishas (who would go on to become the Scarlet torturer Interrogator Vishas). \"We attack as one!\" and \"We are victorious!\" are lines spoken by this child version of Whitemane when the children attack and kill the frog.",

}
quote_list = [q for q in quote.keys()] 
    
