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

from src.ytdl import YTDLSource

load_dotenv()
client = commands.Bot(command_prefix="!", intents=discord.Intents().default())
client.remove_command("help")
capturing: bool = False
name: str = str(datetime.now().strftime("%Y-%m-%d-%H%M"))


responses = {
    "online": "{} is online!",
    "what": "Excuse me??? I don't know that command.",
    "alive": "Hello, I'm still alive!",
    "downloading": "Just a sec, I am downloading the song...",
    "no_connection": "Dude, you need to be in a voice channel to record your voice.",
    "not_recording": "Dude, I am not even recording your voice. You can ask me to start recording with the `!join` command.",
    "recording": "I am recording your voice!",
    "stoprecord": "Ask me with the `!stoprecord` command to stop the recording",
    "bot_no_connection": "I am not connected to a voice channel.",
    "wait": "Just a sec {}",
    "talktome": "Hey {}, Wassup? I am so sorry, but I am just a bot. You need to get a real friend.",
    "help_title": "Here are the commands you can use:",
    "send_record": "It was a pleasure to record your voice, see you later! I am sending the recording from <#{}> voice channel",
    "start_song": "Enjoy the song: {}",
    "description": """
            `!wassup` to check if I am alive
            `!record` to record your voice
            `!stoprecord` to stop the voice recording
            `!play <url>` to play a song
            `!pause` to pause the song
            `!resume` to resume the song
            `!stop` to stop the song
            `!leave` to leave a voice channel
            `!capture` to record your screen
            `!stopcapture` to stop the recording of your screen
            `!saygoodbye` to shutdown the bot
            Feeling lonely? `!talktome` to talk to you""",
    "not_mac": "Jeeez, I don't work on Windows or on Linux.",
    "not_recording_screen": "Dude, I am not even recording your screen. You can ask me to start recording with the `!capture` command.",
    "sending_screen_record": "Hey {}, Thanks for using me, but I am not able to send the recording from {} to you, please ask my owner to send it to you.",
    "offilne": "I'm going to be offline. See ya!",
    "shoutdown": "I have an announcement, {} stopped screen recording and I am also shutting down myself by this process. Please ask my owner to restart me. Thanks! Bye!",
    "start_screen_record": "My lord, I am starting recording your screen, {}",
}


def run_discord_bot() -> None:
    @client.event
    async def on_ready():
        print(responses["online"].format(client.user))

    @client.event
    async def on_command_error(ctx: commands.Context, error: commands.CommandNotFound):
        if isinstance(error, CommandNotFound):
            return await ctx.send(responses["what"])
        raise error

    @client.command()
    async def talktome(ctx: commands.Context):
        await ctx.send(responses["wait"].format(str(ctx.author.mention)))
        await ctx.author.send(responses["talktome"].format(str(ctx.author.mention)))

    @client.command()
    async def help(ctx: commands.Context):
        await ctx.send(
            embed=discord.Embed(
                title=responses["help_title"],
                description=responses["description"],
                color=0xFEC939,
            )
        )

    @client.command()
    async def wassup(ctx: commands.Context):
        await ctx.send(responses["alive"])

    @client.command()
    async def record(ctx: commands.Context):
        if not ctx.author.voice:
            return await ctx.send(responses["no_connection"])
        await ctx.message.author.voice.channel.connect(cls=NativeVoiceClient)
        ctx.voice_client.record(lambda e: print(f"Exception: {e}"))
        embedVar = discord.Embed(
            title=responses["recording"],
            description=responses["stoprecord"],
            color=0xFEC939,
        )
        await ctx.send(embed=embedVar)

    @client.command()
    async def stoprecord(ctx: commands.Context):
        global name
        if not ctx.voice_client:
            return await ctx.send(responses["not_recording"])

        with open(f"{name}.mp3", "wb") as f:
            f.write(await ctx.voice_client.stop_record())

        saved_file = os.getcwd() + "/" + name + ".mp3"
        await ctx.send(
            responses["send_record"].format(ctx.guild.me.voice.channel.id),
            file=discord.File(saved_file),
        )
        await ctx.voice_client.disconnect()
        subprocess.run(f"rm {saved_file}", shell=True, check=True)

    @client.command()
    async def play(ctx: commands.Context, url: str):
        await ctx.message.author.voice.channel.connect()
        try:
            await ctx.author.send(responses["downloading"])
            filename = await YTDLSource.from_url(url, loop=client.loop)
            ctx.message.guild.voice_client.play(
                discord.FFmpegPCMAudio(executable="ffmpeg", source=filename)
            )
            await ctx.send(responses["start_song"].format(filename[0:-4]))
        except:
            await ctx.send(responses["bot_no_connection"])

    @client.command()
    async def pause(ctx: commands.Context):
        if ctx.message.guild.voice_client.is_playing():
            ctx.message.guild.voice_client.pause()

    @client.command()
    async def resume(ctx: commands.Context):
        if ctx.message.guild.voice_client.is_paused():
            ctx.message.guild.voice_client.resume()

    @client.command()
    async def stop(ctx: commands.Context):
        if ctx.message.guild.voice_client.is_playing():
            ctx.message.guild.voice_client.stop()

    @client.command()
    async def leave(ctx: commands.Context):
        await ctx.voice_client.disconnect()

    @client.command()
    async def capture(ctx: commands.Context):
        global capturing, name
        if not platform == "darwin":
            await ctx.send(responses["not_mac"])
        else:
            await ctx.send(
                responses["start_screen_record"].format(str(ctx.author.mention))
            )
            capturing = True
            cmd = f"screencapture -v -g {os.getcwd()}/{name}.mov"
            subprocess.run(cmd, check=False)

    @client.command()
    async def stopcapture(ctx: commands.Context):
        global capturing
        if not capturing:
            await ctx.send(responses["not_recording_screen"])
        else:
            await ctx.author.send(
                responses["sending_screen_record"].format(str(ctx.author.mention), name)
            )
            await ctx.send(responses["shoutdown"].format(str(ctx.author.mention)))
            sys.exit()

    @client.command()
    async def saygoodbye(ctx: commands.Context):
        await ctx.send(responses["offline"])
        sys.exit()

    client.run(os.getenv("TOKEN"))
