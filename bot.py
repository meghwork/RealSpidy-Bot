import os
from pathlib import Path

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
WELCOME_CHANNEL_ID = 1489264475100938490


# =========================
# FILE PATHS
# =========================

BASE_DIR = Path(__file__).resolve().parent
WELCOME_GIF = BASE_DIR / "welcome.gif"


# =========================
# BOT INTENTS
# =========================

intents = discord.Intents.default()

# Needed for !setupverify
intents.message_content = True

# Needed for member join welcome messages
intents.members = True


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

        if interaction.guild is None:
            await interaction.response.send_message(
                "This button only works inside RealSpidy.",
                ephemeral=True
            )
            return

        role = interaction.guild.get_role(WEBBOUND_ROLE_ID)

        if role is None:
            await interaction.response.send_message(
                "❌ Webbound role could not be found.",
                ephemeral=True
            )
            return

        member = interaction.user

        # Already verified
        if role in member.roles:
            await interaction.response.send_message(
                "✅ You're already part of RealSpidy.",
                ephemeral=True
            )
            return

        try:
            await member.add_roles(
                role,
                reason="RealSpidy verification"
            )

            await interaction.response.send_message(
                "🕷️ **Welcome to RealSpidy!**\n"
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

            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ Something went wrong while verifying you.",
                    ephemeral=True
                )


# =========================
# BOT STARTUP
# =========================

@bot.event
async def setup_hook():

    # Keeps the verification button working
    # even after the bot restarts.
    bot.add_view(VerifyView())


@bot.event
async def on_ready():

    print("=" * 45)
    print(f"Logged in as {bot.user}")
    print("RealSpidy verification system is ready.")
    print("RealSpidy welcome system is ready.")
    print("=" * 45)


# =========================
# WELCOME SYSTEM
# =========================

@bot.event
async def on_member_join(member: discord.Member):

    # Don't welcome bots
    if member.bot:
        return

    channel = member.guild.get_channel(WELCOME_CHANNEL_ID)

    if channel is None:
        print("Welcome channel could not be found.")
        return

    embed = discord.Embed(
        title=f"🕷️ Welcome to RealSpidy, {member.display_name}!",
        description=(
            "You’ve just joined the community. 🕸️\n\n"
            "We’re glad to have you here. Explore the server, "
            "meet new people, and enjoy your stay.\n\n"
            "**Welcome to RealSpidy.**"
        ),
        color=discord.Color.red()
    )

    # Member avatar
    embed.set_thumbnail(
        url=member.display_avatar.url
    )

    # Bottom GIF
    embed.set_image(
        url="attachment://welcome.gif"
    )

    embed.set_footer(
        text="🕸️ RealSpidy"
    )

    try:

        if not WELCOME_GIF.exists():
            print(
                f"Welcome GIF could not be found at: "
                f"{WELCOME_GIF}"
            )
            return

        gif = discord.File(
            WELCOME_GIF,
            filename="welcome.gif"
        )

        await channel.send(
            content=member.mention,
            embed=embed,
            file=gif
        )

        print(
            f"Welcome message sent for "
            f"{member} ({member.id})"
        )

    except discord.Forbidden:
        print(
            "Welcome Error: Bot does not have permission "
            "to send messages/files in the welcome channel."
        )

    except Exception as error:
        print(f"Welcome Error: {error}")


# =========================
# SETUP VERIFICATION MESSAGE
# =========================

@bot.command()
@commands.is_owner()
async def setupverify(ctx):

    if ctx.channel.id != VERIFY_CHANNEL_ID:
        await ctx.send(
            "❌ Run this command inside the verification channel."
        )
        return

    embed = discord.Embed(
        title="🕷️ Welcome to RealSpidy",
        description=(
            "You’re one step away from entering the community.\n\n"

            "Please read the server rules before continuing. "
            "Once you’re ready, verify below to unlock the server.\n\n"

            "**Verification gives you access to the community.**\n\n"

            "*By verifying, you confirm that you have read and "
            "agree to follow all server rules.*"
        ),
        color=discord.Color.red()
    )

    embed.set_footer(
        text="🕸️ RealSpidy"
    )

    try:

        await ctx.send(
            embed=embed,
            view=VerifyView()
        )

        # Delete the !setupverify command message
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass

    except discord.Forbidden:
        print(
            "Setup Verify Error: Bot cannot send messages "
            "in the verification channel."
        )

    except Exception as error:
        print(f"Setup Verify Error: {error}")


# =========================
# COMMAND ERROR HANDLER
# =========================

@setupverify.error
async def setupverify_error(ctx, error):

    if isinstance(error, commands.NotOwner):
        return

    print(f"setupverify command error: {error}")


# =========================
# RUN BOT
# =========================

if TOKEN is None:
    raise ValueError(
        "DISCORD_TOKEN was not found. "
        "Check your .env file or Railway Variables."
    )


bot.run(TOKEN)
