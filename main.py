# -----------------------------------------------------------------------_---------------------------------------
import os
import discord
from discord.ext import commands

intents = discord.Intents.default()

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def setup_hook():
    await bot.tree.sync()


@bot.tree.command(name="replacerole", description="Give a role to everyone who has another role")
@app_commands.describe(target="Role to look for", new_role="Role to give its members")
@app_commands.checks.has_permissions(manage_roles=True)
async def replacerole(interaction: discord.Interaction, target: discord.Role, new_role: discord.Role):
    if new_role >= interaction.guild.me.top_role:
        return await interaction.response.send_message(
            "That role is higher than (or equal to) my top role.", ephemeral=True
        )
    await interaction.response.defer()
    count = 0
    for member in target.members:
        try:
            await member.add_roles(new_role)
            count += 1
        except discord.HTTPException:
            pass
    await interaction.followup.send(f"Added {new_role.mention} to {count} member(s).")


@bot.tree.command(name="nukechannel", description="Wipe this channel by recreating it")
@app_commands.checks.has_permissions(manage_channels=True)
async def nukechannel(interaction: discord.Interaction):
    channel = interaction.channel
    await interaction.response.send_message("Nuking...", ephemeral=True)
    new_channel = await channel.clone(reason=f"Nuked by {interaction.user}")
    await new_channel.edit(position=channel.position)
    await channel.delete()
    await new_channel.send("💥 Channel nuked!")


@bot.tree.command(name="nukeroles", description="Delete all roles the bot is able to delete")
@app_commands.checks.has_permissions(administrator=True)
async def nukeroles(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    top = interaction.guild.me.top_role
    deleted = 0
    for role in interaction.guild.roles:
        if role.is_default() or role.managed or role >= top:
            continue
        try:
            await role.delete(reason=f"Nuked by {interaction.user}")
            deleted += 1
        except discord.HTTPException:
            pass
    await interaction.followup.send(f"Deleted {deleted} role(s).")


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("You don't have permission for that.", ephemeral=True)

@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")

bot.run(os.environ["APP_TOKEN"])
