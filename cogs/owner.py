from discord.ext import commands
from dpytools.menus import confirm

from api.api import API
from utils.checks import not_black,is_owner

from tools.autocogs import AutoCogsReload
import ast
import discord
import datetime
import traceback
import sys
import os
from dpytools.parsers import to_timedelta
from dpytools.checks import any_checks
def insert_returns(body):
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)
class owner(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self._last_result = None
        self.normal_color = 0x00FA6C
        self.error_color = 0xFF4A4A

    @any_checks
    @commands.has_permissions(administrator=True)
    @is_owner()
    @commands.command(name="레벨링")
    async def leveling(self, ctx):
        res = await API.check_ignore_lvl_mode(id=ctx.guild.id)
        print(res)
        if res == False:
            await self.bot.pg_con.execute("INSERT INTO ig_guild(guild,name) VALUES($1,$2)", str(ctx.guild.id),
                                          str(ctx.guild.name))
            await ctx.reply("정상적으로 레벨링모드를 비활성화하였습니다.")
        else:
            await self.bot.pg_con.execute("DELETE FROM ig_guild WHERE guild=$1", str(ctx.guild.id))
            await ctx.reply("정상적으로 레벨링모드를 활성화하였습니다.")


    @commands.command(name="공지")
    @is_owner()
    async def notice_send(self,ctx,*,value):
        notice = discord.Embed(title="태시아 봇 공지",description=value,colour=discord.Colour.blurple())
        notice.add_field(name=":link: Link :link:",value=f"[Support](https://discord.gg/zsBFHnTBr9)",inline=False)
        notice.set_footer(text=f"This notice was sent by {ctx.author}",icon_url=ctx.author.avatar_url)
        await ctx.send(embed=notice)
        em = discord.Embed(title="Confirm?",
                           description=f"위 내용으로 공지를 발송하시겠습니까?",
                           colour=discord.Colour.red())
        msg = await ctx.reply(embed=em)
        confirmation = await confirm(ctx, msg)
        if confirmation:
            data = await self.bot.pg_con.fetch("SELECT * FROM notice_setting")
            count = 0
            success = 0
            fail = 0
            em = discord.Embed(title="Processing..",
                               description=f"발송중입니다...",
                               colour=discord.Colour.red())
            await msg.edit(embed=em)
            for i in data:
                count += 1
                try:
                    success += 1
                    await self.bot.get_channel(i[1]).send(embed=notice)
                except Exception as e:
                    fail += 1
                    guild = self.bot.get_guild(i[0])
                    await self.bot.get_user(281566165699002379).send(f"```py\n{guild} 에서에러발생.\n\n{traceback.print_exc()}\n```")
                    pass
            em = discord.Embed(title="Complete!",
                               description=f"Count = {count}\nSuccess = {success}\nFail = {fail}",
                               colour=discord.Colour.red())
            await msg.edit(embed=em)
        elif confirmation is False:
            em1 = discord.Embed(title="Cancelled! ⛔", description="거부하셨습니다.", colour=discord.Colour.red())
            await msg.edit(embed=em1)
        else:
            em1 = discord.Embed(title="Time out! ⛔", description="취소되었습니다.", colour=discord.Colour.red())
            await msg.edit(embed=em1)


    @commands.command(name="블랙")
    @is_owner()
    async def black(self,ctx,mode,user:int,time:to_timedelta=None,*,reason=None):
        if mode=="add":
            end = datetime.datetime.now()+time
            end = end.strftime('%Y-%m-%d %H:%M')
            to_user= await self.bot.fetch_user(user)
            em = discord.Embed(title="Confirm?",
                               description=f"진짜로 `{to_user}`님을 `{end}`까지 다음과 같은 사유로\n```\n{reason}```블랙하시겠습니까?",
                               colour=discord.Colour.red())
            msg = await ctx.reply(embed=em)
            confirmation = await confirm(ctx, msg)
            if confirmation:
                black=discord.Embed(title="블랙추가안내.",
                                    description=f"""
안녕하십니까? `{to_user}`님은 블랙리스트에 추가가 되어 안내DM을 발송하였습니다.\n
추가된 사유는 아래와 같으며 해제 일시는 다음을 참고하세요.\n
\n
< 해제 일시 >
`{end}`
\n
< 사유 >
```\n
{reason}
```
\n
문의 사항이 있으시다면 이 DM채널에서 `ㅌ문의 <문의사항>`으로 문의 남겨주시기 바랍니다.
\n
감사합니다.
""")
                try:
                    await to_user.send(embed=black)
                except:
                    pass
                await self.bot.pg_con.execute("INSERT INTO black_list(user_id,ending,reason) VALUES($1,$2,$3)",
                                             str(user),str(end),reason)
                await ctx.send("ok")
            elif confirmation is False:
                em1 = discord.Embed(title="Cancelled! ⛔", description="거부하셨습니다.", colour=discord.Colour.red())
                await msg.edit(embed=em1)
            else:
                em1 = discord.Embed(title="Time out! ⛔", description="취소되었습니다.", colour=discord.Colour.red())
                await msg.edit(embed=em1)
        elif mode=="del":
            to_user = await self.bot.fetch_user(user)
            em = discord.Embed(title="Confirm?",
                               description=f"진짜로 `{to_user}`님을 블랙해제하시겠습니까?",
                               colour=discord.Colour.red())
            msg = await ctx.reply(embed=em)
            confirmation = await confirm(ctx, msg)
            if confirmation:
                black = discord.Embed(title="블랙해제안내.",
                                      description=f"""
안녕하십니까? `{to_user}`님은 블랙리스트에서 해제가 되어 안내DM을 발송하였습니다.\n

앞으로도 봇을 유용하게 사용해주시기바랍니다.

감사합니다.
""")
                try:
                    await to_user.send(embed=black)
                except:
                    pass
                await self.bot.pg_con.execute("DELETE FROM black_list WHERE user_id =$1",str(to_user.id))
                await ctx.send("ok")
            elif confirmation is False:
                em1 = discord.Embed(title="Cancelled! ⛔", description="거부하셨습니다.", colour=discord.Colour.red())
                await msg.edit(embed=em1)
            else:
                em1 = discord.Embed(title="Time out! ⛔", description="취소되었습니다.", colour=discord.Colour.red())
                await msg.edit(embed=em1)


    @commands.command(name="reload", aliases=["리로드", "r"])
    @is_owner()
    async def 리로드(self, ctx, extension=None):
        if extension is None:  # extension이 None이면 (그냥 !리로드 라고 썼을 때)
            try:
                AutoCogsReload(self.bot)
                await ctx.send(f"모든 모듈을 리로드했어요.")
            except Exception as a:
                await ctx.send(f"리로드에 실패했어요. [{a}]")
        else:
            try:
                self.bot.unload_extension(f"cogs.{extension}")
                self.bot.load_extension(f"cogs.{extension}")
                await ctx.send(f":white_check_mark: `{extension}`을(를) 다시 불러왔습니다!")
            except Exception as a:
                await ctx.send(f"[{extension}]모듈을 리로드도중 에러가 발생했습니다.```{a}```")

def setup(bot):
    bot.add_cog(owner(bot))
    print('cogs - `owner` is loaded')