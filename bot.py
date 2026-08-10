import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# =========================
# LOAD ENVIRONMENT VARIABLES
# =========================

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

# =========================
# SERVER IDs
# =========================

VERIFY_CHANNEL_ID = 1489640453023469659
WEBBOUND_ROLE_ID = 1489268339736838405

# =========================
# BOT INTENTS
# =========================

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# =========================
# VERIFY BUTTON
# =========================

class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Enter the Network",
        emoji="✅",
        style=discord.ButtonStyle.success,
        custom_id="realspidy_verify_button"
    )
    async def verify_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        # Make sure command is used inside a server
        if interaction.guild is None:
            await interaction.response.send_message(
                "This button only works inside RealSpidy Network.",
                ephemeral=True
            )
            return

        # Get Webbound role
        role = interaction.guild.get_role(WEBBOUND_ROLE_ID)

        if role is None:
            await interaction.response.send_message(
                "❌ Webbound role could not be found.",
                ephemeral=True
            )
            return

        member = interaction.user

        # Check if user already has the role
        if role in member.roles:
            await interaction.response.send_message(
                "✅ You're already part of the network.",
                ephemeral=True
            )
            return

        # Give Webbound role
        try:
            await member.add_roles(
                role,
                reason="RealSpidy Network verification"
            )

            await interaction.response.send_message(
                "🕷️ **Welcome to RealSpidy Network!**\n"
                "You now have access to the community.",
                ephemeral=True
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to give you access.",
                ephemeral=True
            )

        except Exception as error:
            print(f"Verification Error: {error}")

            await interaction.response.send_message(
                "❌ Something went wrong while verifying you.",
                ephemeral=True
            )


# =========================
# BOT STARTUP
# =========================

@bot.event
async def setup_hook():
    # Keeps Verify button working after bot restart
    bot.add_view(VerifyView())


@bot.event
async def on_ready():
    print("=" * 40)
    print(f"Logged in as {bot.user}")
    print("RealSpidy verification system is ready.")
    print("=" * 40)


# =========================
# SETUP VERIFY MESSAGE
# =========================

@bot.command()
@commands.is_owner()
async def setupverify(ctx):

    # Only allow command inside verify channel
    if ctx.channel.id != VERIFY_CHANNEL_ID:
        await ctx.send(
            "❌ Run this command inside the verification channel."
        )
        return

    embed = discord.Embed(
        title="🕷️ Welcome to RealSpidy Network",
        description=(
            "You’re one step away from entering the community.\n\n"

            "Please read the server rules before continuing. "
            "Once you’re ready, verify below to unlock the server.\n\n"

            "**Verification gives you access to the community.**\n\n"

            "*By verifying, you confirm that you have read and agree "
            "to follow all server rules.*"
        ),
        color=discord.Color.red()
    )

    embed.set_footer(
        text="🕸️ RealSpidy Network"
    )

    await ctx.send(
        embed=embed,
        view=VerifyView()
    )

    # Delete !setupverify command message
    try:
        await ctx.message.delete()

    except discord.Forbidden:
        pass


# =========================
# RUN BOT
# =========================

if TOKEN is None:
    raise ValueError(
        "DISCORD_TOKEN was not found. "
        "Check your .env file or Railway Variables."
    )

bot.run(TOKEN)
