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


    @commands.command(name="eval")
    @is_owner()
    async def eval_fn(self, ctx, *, cmd):
        if cmd.startswith('```') and cmd.endswith('```'):
            cmd = cmd[3:-3]
            if cmd.startswith('py'): cmd = cmd[2:]
        oldcmd = cmd
        embed = discord.Embed(title="EVAL", description="evaling...")
        embed.add_field(name="📥INPUT📥", value=f"""```py
{oldcmd}
        ```""", inline=False)
        embed.add_field(name="📤OUTPUT📤", value="""```py
evaling...
        ```""", inline=False)
        embed.add_field(name="🔧 Type 🔧", value="""```py
evaling...
        ```""", inline=False)
        embed.add_field(name="🏓 Latency 🏓", value=f"""```py
{str((datetime.datetime.now() - ctx.message.created_at) * 1000).split(":")[2]}
        ```""", inline=False)

        try:
            msg = await ctx.send(embed=embed)
        except discord.HTTPException:
            msg = await ctx.send("evaling...")

        try:

            fn_name = "_eval_expr"
            cmd = cmd.strip("` ")
            cmd = "\n".join(f"    {i}" for i in cmd.splitlines())
            body = f"async def {fn_name}():\n{cmd}"
            parsed = ast.parse(body)
            body = parsed.body[0].body
            insert_returns(body)
            env = {
                "bot": self.bot,
                "discord": discord,
                "commands": commands,
                "ctx": ctx,
                "__import__": __import__,
            }
            exec(compile(parsed, filename="<ast>", mode="exec"), env)
            result = await eval(f"{fn_name}()", env)

            try:

                embed = discord.Embed(title="EVAL", description="Done!")
                embed.add_field(name="📥INPUT📥", value=f"""```py
{oldcmd}
        ```""", inline=False)
                embed.add_field(name="📤OUTPUT📤", value=f"""```py
{result}
        ```""", inline=False)
                embed.add_field(name="🔧 Type 🔧", value=f"""```py
{type(result)}
        ```""", inline=False)
                embed.add_field(name="🏓 Latency 🏓", value=f"""```py
{str((datetime.datetime.now() - ctx.message.created_at) * 1000).split(":")[2]}
        ```""", inline=False)

                try:
                    await msg.edit(embed=embed)
                except discord.HTTPException:
                    await ctx.send(result)

            except discord.errors.HTTPException:
                with open("eval_result.txt", "w") as pf:
                    pf.write("eval : " + cmd + "\r\n-----\r\n" + str(result))
                await msg.edit(content="length of result is over 1000. here is text file of result")
                await ctx.send(file=discord.File("eval_result.txt"))
                os.remove("eval_result.txt")

        except Exception as e:
            try:
                embed = discord.Embed(title="EVAL", description="Done!")
                embed.add_field(name="📥INPUT📥", value=f"""```py
{oldcmd}
        ```""", inline=False)
                embed.add_field(name="📤OUTPUT📤", value=f"""```py
{str(traceback.format_exc())}
        ```""", inline=False)
                embed.add_field(name="🔧 Type 🔧", value=f"""```py
{type(e)}
        ```""", inline=False)
                embed.add_field(name="🏓 Latency 🏓", value=f"""```py
{str((datetime.datetime.now() - ctx.message.created_at) * 1000).split(":")[2]}
        ```""", inline=False)
                try:
                    await msg.edit(embed=embed)
                except discord.HTTPException:
                    await ctx.send(traceback.format_exc())
            except discord.errors.HTTPException:
                pf = open("eval_result.txt", "w")
                ps = "eval : " + cmd + "\r\n-----\r\n" + str(traceback.format_exc())
                pf.write(ps)
                pf.close()
                await msg.edit(content="length of result is over 1000. here is text file of result")
                await ctx.send(file=discord.File("eval_result.txt"))
                os.remove("eval_result.txt")

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