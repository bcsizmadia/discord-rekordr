import os
import subprocess
import sys
from datetime import datetime
from sys import platform

import discord
from discord.ext import commands
from discord.ext.audiorec import NativeVoiceClient
from discord.ext.commands import CommandNotFound
from dotenv import load_dotenv

load_dotenv()
client = commands.Bot(command_prefix="!", intents=discord.Intents().default())
client.remove_command("help")
capturing: bool = False
name: str = str(datetime.now().strftime("%Y-%m-%d-%H%M"))


def run_discord_bot() -> None:
    @client.event
    async def on_ready():
        print(f"{client.user} is online!")

    @client.event
    async def on_command_error(ctx: commands.Context, error: commands.CommandNotFound):
        if isinstance(error, CommandNotFound):
            return await ctx.send("Excuse me??? I don't know that command.")
        raise error

    @client.command()
    async def talktome(ctx: commands.Context):
        await ctx.send(f"Just a sec {str(ctx.author.mention)}")
        await ctx.author.send(
            f"Hey {str(ctx.author.mention)}, Wassup? I am so sorry, but I am just a bot. You need to get a real friend."
        )

    @client.command()
    async def help(ctx: commands.Context):
        embedVar = discord.Embed(
            title="Here are the commands you can use:",
            description="""
            `!join` to start the recording
            `!stop` to stop the recording
            `!wassup` to check if I am alive
            `!capture` to record your screen
            `!stopcapture` to stop the recording of your screen
            Feeling lonely? `!talktome` to talk to you""",
            color=0xFEC939,
        )
        await ctx.send(embed=embedVar)

    @client.command()
    async def wassup(ctx: commands.Context):
        await ctx.send("Hello, I'm still alive!")

    @client.command()
    async def join(ctx: commands.Context):
        if not ctx.author.voice:
            return await ctx.send(
                "Boii, you are not connected to a voice channel. Plz connect to a voice channel and try again."
            )
        channel: discord.VoiceChannel = ctx.author.voice.channel
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)
        await channel.connect(cls=NativeVoiceClient)
        await ctx.invoke(client.get_command("rec"))

    @client.command()
    async def rec(ctx: commands.Context):
        ctx.voice_client.record(lambda e: print(f"Exception: {e}"))
        embedVar = discord.Embed(
            title="I am recording your voice!",
            description="Ask me with the `!stop` command to stop the recording",
            color=0xFEC939,
        )
        await ctx.send(embed=embedVar)

    @client.command()
    async def stop(ctx: commands.Context):
        global name
        if not ctx.voice_client:
            return await ctx.send(
                "Dude, I am not even recording your voice. You can ask me to start recording with the `!join` command."
            )

        with open(f"{name}.mp3", "wb") as f:
            f.write(await ctx.voice_client.stop_record())

        saved_file = os.getcwd() + "/" + name + ".mp3"
        await ctx.send(
            f"It was a pleasure to record your voice, see you later! I am sending the recording from <#{ctx.guild.me.voice.channel.id}> voice channel",
            file=discord.File(saved_file),
        )
        await ctx.voice_client.disconnect()
        subprocess.run(f"rm {saved_file}", shell=True, check=True)

    @client.command()
    async def capture(ctx: commands.Context):
        global capturing, name
        if not platform == "darwin":
            await ctx.send("Jeeez, I don't work on Windows or on Linux.")
        else:
            await ctx.send(
                f"My lord, I am starting recording your screen, {str(ctx.author.mention)}"
            )
            capturing = True
            cmd = f"screencapture -v -g {os.getcwd()}/{name}.mov"
            subprocess.run(cmd, check=False)

    @client.command()
    async def saygoodbye(ctx: commands.Context):
        await ctx.send("I'm going to be offline. See ya!")
        sys.exit()

    @client.command()
    async def stopcapture(ctx: commands.Context):
        global capturing
        if not capturing:
            await ctx.send(
                f"Dude, I am not even recording your screen. You can ask me to start recording with the `!capture` command."
            )
        else:
            await ctx.author.send(
                f"Hey {str(ctx.author.mention)}, Thanks for using me, but I am not able to send the recording from {name} to you, please ask my owner to send it to you."
            )
            await ctx.send(
                f"I have an announcement, {str(ctx.author.mention)} stopped screen recording and I am also shutting down myself by this process. Please ask my owner to restart me. Thanks! Bye!"
            )
            sys.exit()

    client.run(os.getenv("TOKEN"))
