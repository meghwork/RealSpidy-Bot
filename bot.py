import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

VERIFY_CHANNEL_ID = 1489640453023469659
WEBBOUND_ROLE_ID = 1489268339736838405

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Verify",
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
                "This button only works inside RealSpidy Network.",
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

        if role in member.roles:
            await interaction.response.send_message(
                "✅ You're already verified.",
                ephemeral=True
            )
            return

        try:
            await member.add_roles(
                role,
                reason="RealSpidy Network verification"
            )

            await interaction.response.send_message(
                "🕷️ **Verification complete!**\n"
                "Welcome to **RealSpidy Network**.",
                ephemeral=True
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to give you the Webbound role.",
                ephemeral=True
            )

        except Exception as error:
            print(error)

            await interaction.response.send_message(
                "❌ Something went wrong while verifying you.",
                ephemeral=True
            )


@bot.event
async def setup_hook():
    bot.add_view(VerifyView())


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print("RealSpidy verification system is ready.")


@bot.command()
@commands.is_owner()
async def setupverify(ctx):

    if ctx.channel.id != VERIFY_CHANNEL_ID:
        await ctx.send("Run this command inside the verification channel.")
        return

    embed = discord.Embed(
        title="🕷️ Welcome to RealSpidy Network",
        description=(
            "Before accessing the server, please read the rules and verify yourself.\n\n"
            "Click the **Verify** button below to unlock the community.\n\n"
            "**By verifying, you confirm that you have read and agree to follow all server rules.**"
        ),
        color=discord.Color.red()
    )

    embed.set_footer(text="🕸️ RealSpidy Network")

    await ctx.send(
        embed=embed,
        view=VerifyView()
    )

    try:
        await ctx.message.delete()
    except discord.Forbidden:
        pass


bot.run(TOKEN)