from discord.ext import commands
from helpers.util import Pag

# Help class
class Help(commands.Cog, name="Help command"):

    # Class Initialisation
    def __init__(self, client):
        self.client = client
        self.cmds_per_page = 6 # Show 6 commands per page


    def get_command_signature(self, command: commands.Command, ctx: commands.Context):
        aliases = "|".join(command.aliases)
        cmd_invoke = f"[{command.name}|{aliases}]" if command.aliases else command.name

        full_invoke = command.qualified_name.replace(command.name, "")

        signature = f"{ctx.prefix}{full_invoke}{cmd_invoke} {command.signature}"
        return signature

    async def return_filtered_commands(self, walkable, ctx):
        filtered = []

        for c in walkable.walk_commands():
            try:
                if c.hidden:
                    continue

                elif c.parent:
                    continue

                await c.can_run(ctx)
                filtered.append(c)
            except commands.CommandError:
                continue

        return self.return_sorted_commands(filtered)

    def return_sorted_commands(self, commandList):
        return sorted(commandList, key=lambda x: x.name)

    async def setup_help_pag(self, ctx, entity=None, title=None):
        entity = entity or self.client
        title = title or self.client.description

        pages = []

        if isinstance(entity, commands.Command):
            filtered_commands = (
                list(set(entity.all_commands.values()))
                if hasattr(entity, "all_commands")
                else []
            )
            filtered_commands.insert(0, entity)

        else:
            filtered_commands = await self.return_filtered_commands(entity, ctx)

        for i in range(0, len(filtered_commands), self.cmds_per_page):
            next_commands = filtered_commands[i : i + self.cmds_per_page]
            commands_entry = "" # Declare an empty string

            for cmd in next_commands:
                desc = cmd.short_doc or cmd.description
                signature = self.get_command_signature(cmd, ctx)
                subcommand = "Has subcommands\n" if hasattr(cmd, "all_commands") else ""
                # Setup the string that need to send
                commands_entry += (
                    f"• **__{cmd.name}__**\n```\n{signature}\n```{desc}\n\n"
                    # Case Asking a Specific command, i.e. ".help roll"
                    if isinstance(entity, commands.Command)
                    # Case Asking commands list, i.e. ".help"
                    else f"• **__{cmd.name}__**\n{desc}\n    {subcommand}\n"
                )
            pages.append(commands_entry)

        await Pag(title=title, color=0xCE2029, entries=pages, length=1).start(ctx)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog has been loaded\n-----")

    # Define help command itself
    @commands.command(
        name="help", 
        aliases=["h", "commands"], 
        description="The help command!"
    )
    async def help_command(self, ctx, *, entity=None):
        if not entity:
            await self.setup_help_pag(ctx)

        else:
            cog = self.client.get_cog(entity)
            if cog:
                await self.setup_help_pag(ctx, cog, f"{cog.qualified_name}'s commands")

            else:
                command = self.client.get_command(entity)
                if command:
                    await self.setup_help_pag(ctx, command, command.name)

                else:
                    await ctx.send("Entity not found.")


def setup(client):
    client.add_cog(Help(client))