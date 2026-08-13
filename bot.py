import os
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")


# =========================================================
# REALSPIDY IDs
# =========================================================

VERIFY_CHANNEL_ID = 1489640453023469659
WEBBOUND_ROLE_ID = 1489268339736838405
WELCOME_CHANNEL_ID = 1489264475100938490


# =========================================================
# FILES
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
WELCOME_GIF = BASE_DIR / "welcome.gif"


# =========================================================
# INTENTS
# =========================================================

intents = discord.Intents.default()

# Needed for !setupverify and !testwelcome
intents.message_content = True

# Needed for on_member_join
intents.members = True


# =========================================================
# BOT
# =========================================================

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# =========================================================
# VERIFICATION VIEW
# =========================================================

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
                "❌ This button only works inside RealSpidy.",
                ephemeral=True
            )
            return

        role = interaction.guild.get_role(WEBBOUND_ROLE_ID)

        if role is None:
            print(
                f"ERROR: Webbound role {WEBBOUND_ROLE_ID} "
                "could not be found."
            )

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

            print(
                f"VERIFIED: {member} ({member.id}) "
                f"received {role.name}"
            )

            await interaction.response.send_message(
                "🕷️ **Welcome to RealSpidy!**\n"
                "You now have access to the community.",
                ephemeral=True
            )

        except discord.Forbidden:

            print(
                "VERIFICATION ERROR: RealSpidy does not have "
                "permission to assign the Webbound role."
            )

            await interaction.response.send_message(
                "❌ I don't have permission to give you access.",
                ephemeral=True
            )

        except Exception as error:

            print(f"VERIFICATION ERROR: {error}")

            if not interaction.response.is_done():

                await interaction.response.send_message(
                    "❌ Something went wrong while verifying you.",
                    ephemeral=True
                )


# =========================================================
# STARTUP
# =========================================================

@bot.event
async def setup_hook():

    # Keeps verification button working after restart
    bot.add_view(VerifyView())


@bot.event
async def on_ready():

    print("")
    print("=" * 50)
    print(f"Logged in as: {bot.user}")
    print(f"Bot ID: {bot.user.id}")
    print("")
    print("RealSpidy verification system is ready.")
    print("RealSpidy welcome system is ready.")
    print("")
    print(f"Welcome GIF path: {WELCOME_GIF}")
    print(f"Welcome GIF exists: {WELCOME_GIF.exists()}")
    print("=" * 50)
    print("")


# =========================================================
# WELCOME MESSAGE FUNCTION
# =========================================================

async def send_welcome(member: discord.Member):

    print("")
    print(
        f"WELCOME EVENT: Preparing welcome for "
        f"{member} ({member.id})"
    )

    # Don't welcome bots
    if member.bot:
        print("WELCOME SKIPPED: Member is a bot.")
        return

    # Try cached channel first
    channel = member.guild.get_channel(WELCOME_CHANNEL_ID)

    # Fallback to Discord API
    if channel is None:

        print(
            "WELCOME: Channel not found in cache. "
            "Trying Discord API..."
        )

        try:
            channel = await bot.fetch_channel(WELCOME_CHANNEL_ID)

        except Exception as error:
            print(f"WELCOME ERROR: Could not find channel: {error}")
            return

    print(
        f"WELCOME CHANNEL FOUND: "
        f"{getattr(channel, 'name', 'Unknown')}"
    )

    # -----------------------------------------------------
    # EMBED
    # -----------------------------------------------------

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

    # User avatar
    embed.set_thumbnail(
        url=member.display_avatar.url
    )

    embed.set_footer(
        text="🕸️ RealSpidy"
    )

    # -----------------------------------------------------
    # SEND WITH GIF
    # -----------------------------------------------------

    try:

        if WELCOME_GIF.exists():

            embed.set_image(
                url="attachment://welcome.gif"
            )

            gif = discord.File(
                str(WELCOME_GIF),
                filename="welcome.gif"
            )

            await channel.send(
                embed=embed,
                file=gif
            )

            print(
                f"WELCOME SUCCESS: Message + GIF sent "
                f"for {member}."
            )

        else:

            # Welcome still sends even if GIF is missing.
            print(
                "WELCOME WARNING: welcome.gif was not found. "
                "Sending welcome without GIF."
            )

            await channel.send(
                embed=embed
            )

            print(
                f"WELCOME SUCCESS: Message sent without GIF "
                f"for {member}."
            )

    except discord.Forbidden:

        print(
            "WELCOME ERROR: RealSpidy does not have permission "
            "to send messages/files in the welcome channel."
        )

    except Exception as error:

        print(f"WELCOME ERROR: {type(error).__name__}: {error}")


# =========================================================
# MEMBER JOIN EVENT
# =========================================================

@bot.event
async def on_member_join(member: discord.Member):

    print("")
    print("=" * 50)
    print(f"JOIN DETECTED: {member}")
    print(f"USER ID: {member.id}")
    print(f"SERVER: {member.guild.name}")
    print("=" * 50)

    await send_welcome(member)


# =========================================================
# TEST WELCOME
# =========================================================

@bot.command()
@commands.is_owner()
async def testwelcome(ctx):

    print(
        f"TEST WELCOME requested by "
        f"{ctx.author} ({ctx.author.id})"
    )

    await send_welcome(ctx.author)

    try:
        await ctx.message.delete()
    except discord.Forbidden:
        pass


# =========================================================
# SETUP VERIFICATION MESSAGE
# =========================================================

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

        print(
            f"VERIFY SETUP: Verification message sent "
            f"in {ctx.channel.name}."
        )

        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass

    except discord.Forbidden:

        print(
            "VERIFY SETUP ERROR: RealSpidy cannot send "
            "messages in the verification channel."
        )

    except Exception as error:

        print(
            f"VERIFY SETUP ERROR: "
            f"{type(error).__name__}: {error}"
        )


# =========================================================
# COMMAND ERROR HANDLING
# =========================================================

@setupverify.error
async def setupverify_error(ctx, error):

    if isinstance(error, commands.NotOwner):
        return

    print(f"setupverify ERROR: {error}")


@testwelcome.error
async def testwelcome_error(ctx, error):

    if isinstance(error, commands.NotOwner):
        return

    print(f"testwelcome ERROR: {error}")


# =========================================================
# RUN BOT
# =========================================================

if TOKEN is None:

    raise ValueError(
        "DISCORD_TOKEN was not found. "
        "Check Railway Variables."
    )


bot.run(TOKEN)
