import discord
from discord.activity import create_activity
from discord.ext import commands
from discord_slash import SlashCommand
import discord_slash
from discord_slash.model import SlashCommandPermissionType
from discord_slash.utils.manage_commands import create_option, create_permission
import logging
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
BOT_OWNER = int(os.environ.get("BOT_OWNER"))
HOME_GUILD = int(os.environ.get("HOME_GUILD"))

class SpoofBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        commands.Bot.__init__(self, *args, **kwargs)
        self.webhooks = {}
        self.slash = SlashCommand(self, sync_commands=True)
        self.guild_ids = [HOME_GUILD]
        self.add_commands()
        self.permissions = {}

    async def on_ready(self):
        print(f"Logged in as {self.user}")
        self.guild_ids = [guild.id for guild in self.guilds]
        # self.permissions = {guild.id: {
        #     manage_guild: [role.id for role in guild.roles if role.permissions.manage_guild],
        #     manage_guild: [role.id for role in guild.roles if role.permissions.manage_guild]
        # }}
        self.add_slash_commands()

    async def create_webhook(self, channel: discord.TextChannel, name: str = "Webhook"):
        if channel.id in self.webhooks:
            return self.webhooks[channel.id]
        w = await channel.create_webhook(name=name)
        self.webhooks[channel.id] = w
        return w

    async def delete_webhook(self, channel: discord.TextChannel):
        await self.webhooks[channel.id].delete()
        del self.webhooks[channel.id]

    def add_commands(self):
        @self.command()
        async def webhook(ctx, name: str, *, message: str):
            w = await self.create_webhook(ctx.channel, bot.user.display_name)
            await w.send(message, name=name)
            await ctx.message.delete()

        @self.command()
        @commands.has_permissions(manage_guild=True)
        async def enable_roles(ctx, command: str, *roles: discord.Role):
            permissions[ctx.guild.id] = [role.id for role in roles]

        @self.command()
        async def initslashcommands(ctx):
            self.add_slash_commands()
            await ctx.message.add_reaction(u"\uE419")

    def add_slash_commands(self):
        
        @self.slash.slash(name="ping",
                          description="Check how fast the bot responds on its network",
                          guild_ids=self.guild_ids)
        async def _ping(ctx):  # Defines a new "context" (ctx) command called "ping."
            await ctx.send(f"Pong! ({bot.latency*1000}ms)")

        @self.slash.slash(name="doc",
                        description="Check how fast the bot responds on its network",
                        guild_ids=self.guild_ids)
        async def _doc(ctx):  # Defines a new "context" (ctx) command called "ping."
            await ctx.send(f"What's up, doc?")

        @self.slash.slash(
            name="echo",
            description="Say something using the bot",
            options=[
                create_option(
                    name="message",
                    description="The text of the message you will send",
                    option_type=3,
                    required=True
                ),
                create_option(
                    name="channel",
                    description="The channel where this message will be sent. By default, the channel where the command is executed.",
                    option_type=7,
                    required=False
                )
            ],
            guild_ids=self.guild_ids)
        @self.slash.permission(
            guild_id=self.guild_ids[0],
            permissions=[
                create_permission(769407256622006343,
                                  SlashCommandPermissionType.ROLE, True),
                create_permission(BOT_OWNER, SlashCommandPermissionType.USER, True)
            ])
        async def _echo(ctx, message: str, channel: discord.TextChannel = None):
            if not channel:
                channel = ctx.channel
            await channel.send(content=message)
            await ctx.send('Done!', hidden=True)

        @self.slash.slash(
            name="spoof",
            description="Spoof a user",
            options=[
                create_option(
                    name="user",
                    description="The user to spoof",
                    option_type=6,
                    required=True
                ),
                create_option(
                    name="message",
                    description="The message content",
                    option_type=3,
                    required=True
                ),
                create_option(
                    name="channel",
                    description="The channel where the message should be sent. Current channel is default.",
                    option_type=7,
                    required=False
                )
            ],
            guild_ids=self.guild_ids)
        @self.slash.permission(
            guild_id=self.guild_ids[0],
            permissions=[
                create_permission(769407256622006343,
                                  SlashCommandPermissionType.ROLE, True),
                create_permission(BOT_OWNER, SlashCommandPermissionType.USER, True)
            ])
        async def _spoof(ctx, user: discord.User, message: str, channel: discord.TextChannel = None):
            w = await self.create_webhook(channel or ctx.channel, bot.user.name)
            await w.send(message, username=user.display_name, avatar_url=user.avatar_url)
            if channel and ctx.channel != channel:
                await ctx.send("Message sent.", hidden=False)
            else:
                await ctx.send("Message sent.", hidden=True)

        @self.slash.slash(
            name="move",
            description="Move a message",
            options=[
                create_option(
                    name="message",
                    description="The message id to move",
                    option_type=3,
                    required=True
                ),
                create_option(
                    name="to channel",
                    description="The channel where the message should be moved.",
                    option_type=7,
                    required=True
                ),
                create_option(
                    name="from channel",
                    description="The channel where the message originally was. By default the current channel.",
                    option_type=7,
                    required=False
                ),
                create_option(
                    name="delete original",
                    description="Should the original message be deleted? True by default",
                    option_type=5,
                    required=False
                )
            ],
            guild_ids=self.guild_ids)
        @self.slash.permission(
            guild_id=self.guild_ids[0],
            permissions=[
                create_permission(769407256622006343,
                                  SlashCommandPermissionType.ROLE, True),
                create_permission(BOT_OWNER, SlashCommandPermissionType.USER, True)
            ])
        async def _move(ctx, message_id: str, to_channel: discord.TextChannel, from_channel: discord.TextChannel, delete_original: bool = True):
            from_channel = from_channel or ctx.channel
            message = await from_channel.fetch_message(message_id)

            w = await self.create_webhook(to_channel, bot.user.name)
            await w.send(message.content, username=message.author.display_name, avatar_url=message.author.avatar_url)
            
            if ctx.channel != from_channel and ctx.channel != to_channel:
                await ctx.send("Message sent.", hidden=False)
            else:
                await ctx.send("Message sent.", hidden=True)

        

bot = SpoofBot(command_prefix="'")

bot.run(BOT_TOKEN)
