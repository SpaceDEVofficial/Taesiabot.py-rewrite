import math
import re
import discord
import lavalink
from discord.ext import commands

url_rx = re.compile("https?:\\/\\/(?:www\\.)?.+")  # noqa: W605


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.normal_color = 0x00FF00
        self.error_color = 0xFF4A4A
        self.warn_color = 0xF7F253
        if not hasattr(
            bot, "lavalink"
        ):  # This ensures the client isn't overwritten during cog reloads.
            bot.lavalink = lavalink.Client(766932365426819092)
            bot.lavalink.add_node('127.0.0.1', 3444, '1111', 'eu', 'taesia')  # Host, Port, Password, Region, Name
            bot.add_listener(bot.lavalink.voice_update_handler, "on_socket_response")
        bot.lavalink.add_event_hook(self.track_hook)

    def cog_unload(self):
        self.bot.lavalink._event_hooks.clear()

    async def cog_before_invoke(self, ctx):
        guild_check = ctx.guild is not None
        if guild_check:
            await self.ensure_voice(ctx)
        return guild_check

    async def track_hook(self, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            guild_id = int(event.player.guild_id)
            await self.connect_to(guild_id, None)

    async def connect_to(self, guild_id: int, channel_id: str):
        ws = self.bot._connection._get_websocket(guild_id)
        await ws.voice_state(str(guild_id), channel_id)

    @commands.command(aliases=["p", "재생", "ㅔㅣ묘"])
    async def play(self, ctx, *, query: str):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        query = query.strip("<>")
        if not url_rx.match(query):
            query = f"ytsearch:{query}"
        results = await player.node.get_tracks(query)
        if not results or not results["tracks"]:
            return await ctx.send("검색 결과가 없습니다!")
        embed = discord.Embed(color=self.normal_color)
        if results["loadType"] == "PLAYLIST_LOADED":
            tracks = results["tracks"]
            for track in tracks:
                player.add(requester=ctx.author.id, track=track)
            embed.title = "플레이리스트 추가 완료!"
            embed.description = "성공적으로 플레이리스트를 추가했습니다."
            embed.add_field(
                name="이름", value=f'{results["playlistInfo"]["name"]}', inline=True
            )
            embed.add_field(name="곡 수", value=str(len(tracks)) + "개", inline=True)
            embed.add_field(name="요청자", value=f"<@!{ctx.author.id}>", inline=True)
        else:
            track = results["tracks"][0]
            embed.title = "트랙 추가 완료!"
            embed.description = f'```{track["info"]["title"]}```'
            embed.add_field(
                name="**URL**", value=f'[클릭]({track["info"]["uri"]})', inline=True
            )
            embed.add_field(name="요청자", value=f"<@!{ctx.author.id}>", inline=True)
            embed.add_field(
                name="길이",
                value=f'{lavalink.utils.format_time(track["info"]["length"])}',
                inline=True,
            )
            embed.set_thumbnail(
                url=f'https://i.ytimg.com/vi/{track["info"]["identifier"]}/hqdefault.jpg'
            )
            player.add(requester=ctx.author.id, track=track)
            embed.set_footer(
            text=ctx.author.name + " | 태시아 봇#5919", icon_url=ctx.author.avatar_url
            )
        await ctx.send(embed=embed)
        if not player.is_playing:
            await player.play()

    @commands.command(aliases=["forceskip", "나ㅑㅔ", "스킵"])
    async def skip(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send("플레이 중 이지 않습니다.")
        await player.skip()
        await ctx.message.add_reaction("\U00002705")

    @commands.command(aliases=["ㄴ새ㅔ", "나가"])
    async def stop(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send("플레이 중 이지 않습니다.")
        player.queue.clear()
        await player.stop()
        await self.connect_to(ctx.guild.id, None)
        await ctx.message.add_reaction("\U00002705")

    @commands.command(aliases=["np", "n", "playing", "지금곡"])
    async def now(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.current:
            return await ctx.send("재생 중인 것이 없습니다.")
        position = lavalink.utils.format_time(player.position)
        if player.current.stream:
            duration = "라이브 (실시간)"
        else:
            duration = lavalink.utils.format_time(player.current.duration)
        song = f"**[{player.current.title}]()**\n()"
        embed = discord.Embed(
            color=self.normal_color,
            title="현재 플레이 중",
            description=f"```{player.current.title}```",
        )
        embed.add_field(name="URL", value=f"[클릭]({player.current.uri})", inline=True)
        embed.add_field(
            name="요청자", value=f"<@!{player.current.requester}>", inline=True
        )
        embed.add_field(name="길이", value=f"{position} / {duration}", inline=True)
        embed.set_thumbnail(
            url=f"https://i.ytimg.com/vi/{player.current.identifier}/hqdefault.jpg"
        )
        embed.set_footer(
            text=ctx.author.name + " | FreeAI#6129", icon_url=ctx.author.avatar_url
        )
        await ctx.send(embed=embed)

    @commands.command(aliases=["q", "재생목록"])
    async def queue(self, ctx, page: int = 1):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.queue:
            return await ctx.send("재생목록에 아무것도 없습니다.")
        items_per_page = 10
        pages = math.ceil(len(player.queue) / items_per_page)
        start = (page - 1) * items_per_page
        end = start + items_per_page
        queue_list = ""
        for index, track in enumerate(player.queue[start:end], start=start):
            queue_list += f"`{index + 1}.` [{track.title}]({track.uri})\n"
        embed = discord.Embed(
            colour=self.normal_color,
            description=f"{queue_list}",
            title=f"{page} / {pages}페이지 - **{len(player.queue)}개의 곡**",
        )
        embed.add_field(
            name="현재 플레이중인 곡", value=f"[{player.current.title}]({player.current.uri})"
        )
        embed.set_footer(
            text=ctx.author.name + " | FreeAI#6129", icon_url=ctx.author.avatar_url
        )
        await ctx.send(embed=embed)

    @commands.command(aliases=["resume", "일시정지"])
    async def pause(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send("플레이 중이지 않습니다.")
        if player.paused:
            await player.set_pause(False)
            await ctx.message.add_reaction("\U00002705")
        else:
            await player.set_pause(True)
            await ctx.message.add_reaction("\U00002705")

    @commands.command(aliases=["m", "move", "ㅡ", "seek"])
    async def 시간스킵(self, ctx, *, seconds: int):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        track_time = player.position + (seconds * 1000)
        await player.seek(track_time)

        await ctx.send(
            f":hammer_pick: | 시간 스킵: {lavalink.utils.format_time(track_time)}"
        )

    @commands.command(aliases=["vol", "v", "볼륨"])
    async def volume(self, ctx, volume: int = None):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not volume:
            return await ctx.send(f"현재 볼륨은 {player.volume}% 입니다.")
        await player.set_volume(volume)
        await ctx.message.add_reaction("\U00002705")

    @commands.command(aliases=["셔플"])
    async def shuffle(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send("재생 중인 것이 없습니다.")
        player.shuffle = not player.shuffle
        await ctx.message.add_reaction("\U00002705")

    @commands.command(aliases=["loop", "리핏", "반복"])
    async def repeat(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send("재생 중인 것이 없습니다.")
        player.repeat = not player.repeat
        await ctx.message.add_reaction("\U00002705")

    @commands.command(aliases=["큐삭제"])
    async def remove(self, ctx, index: int):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.queue:
            return await ctx.send("재생목록에 아무것도 없습니다.")
        if index > len(player.queue) or index < 1:
            return await ctx.send(f"인덱스는 1과 {len(player.queue)} 사이 정수여야 합니다.")
        removed = player.queue.pop(index - 1)  # Account for 0-index.
        await ctx.send(f"`{removed.title}`를 재생목록에서 제거했습니다.")

    @commands.command(aliases=["dc"])
    async def disconnect(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.is_connected:
            return await ctx.send("연결되지 않았습니다.")
        if not ctx.author.voice or (
            player.is_connected
            and ctx.author.voice.channel.id != int(player.channel_id)
        ):
            return await ctx.send("저랑 같은 채널에 들어와주세요!")
        player.queue.clear()
        await player.stop()
        await self.connect_to(ctx.guild.id, None)
        await ctx.message.add_reaction("👋")

    async def ensure_voice(self, ctx):
        player = player = self.bot.lavalink.player_manager.create(
            ctx.guild.id, endpoint=str(ctx.guild.region)
        )
        should_connect = ctx.command.name in ("play", "spotify")
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandInvokeError("먼저 음성 채널에 들어와주세요.")
        if not player.is_connected:
            if not should_connect:
                raise commands.CommandInvokeError("연결되지 않았습니다.")
            permissions = ctx.author.voice.channel.permissions_for(ctx.me)
            if not permissions.connect or not permissions.speak:
                raise commands.CommandInvokeError("권한이 없습니다! (Connect, Speak 권한을 주세요!)")
            player.store("channel", ctx.channel.id)
            await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
        else:
            if int(player.channel_id) != ctx.author.voice.channel.id:
                raise commands.CommandInvokeError("다른 음성 채널에 있어요! 제가 있는 음성 채널로 와주세요.")


def setup(bot):
    bot.add_cog(Music(bot))