from discord.ext import commands
from config import OWNERS
from tools.autocogs import AutoCogsReload
import ast
import discord
import datetime
import traceback
from api.api import API
def is_owner():
    async def predicate(ctx):
        return ctx.author.id in OWNERS

    return commands.check(predicate)
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

    @commands.command(name="레벨링")
    @commands.has_permissions(administrator=True)
    async def leveling(self,ctx):
        res = API.check_ignore_lvl_mode(id=ctx.guild.id)
        print(res)
        if res == False:
            await self.bot.pg_con.execute("INSERT INTO ig_guild(guild,name) VALUES($1,$2)",str(ctx.guild.id),str(ctx.guild.name))
            await ctx.reply("정상적으로 레벨링모드를 비활성화하였습니다.")
        else:
            await self.bot.pg_con.execute("DELETE FROM ig_guild WHERE guild=$1",str(ctx.guild.id))
            await ctx.reply("정상적으로 레벨링모드를 활성화하였습니다.")

    @commands.command(name="레벨링설정")
    @is_owner()
    async def leveling_own(self, ctx):
        res = API.check_ignore_lvl_mode(id=ctx.guild.id)
        if res == False:
            await self.bot.pg_con.execute("INSERT INTO ig_guild(guild,name) VALUES($1,$2)", str(ctx.guild.id),
                                          str(ctx.guild.name))
            await ctx.reply("정상적으로 레벨링모드를 비활성화하였습니다.")
        else:
            await self.bot.pg_con.execute("DELETE FROM ig_guild WHERE guild=$1", str(ctx.guild.id))
            await ctx.reply("정상적으로 레벨링모드를 활성화하였습니다.")


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