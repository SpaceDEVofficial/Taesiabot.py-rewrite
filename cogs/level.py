import os
import asyncpg
from discord.ext import commands
#from asyncpg import connection
import discord
import datetime
from dotenv import load_dotenv
load_dotenv(verbose=True)
exp = [100,
       220,
       350,
       480,
       610,
       740,
       870,
       1100,
       1230,
       1360,
       1490,
       1620,
       1750,
       2000,
       2500,
       3000,
       3500,
       4000,
       6000,
       8000,
       10000,
       20000,
       35000,
       70000,
       100000]
class level(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.content.startswith(''):
            res = await self.bot.pg_con.fetch("SELECT * FROM ig_guild WHERE guild = $1", str(message.guild.id))
            if res == []:
                res2 = await self.bot.pg_con.fetch("SELECT * FROM ig_channel WHERE guild = $1 AND channel = $2", str(message.guild.id),str(message.channel.id))
                if res2 == []:
                    res3 = await self.bot.pg_con.fetch("SELECT * FROM ig_role WHERE guild = $1 AND roleid = $2",
                                            str(message.guild.id), str(message.author.top_role.id))
                    print(message.author.top_role.id)
                    print(res3)
                    if res3 == []:
                        res1 = await self.bot.pg_con.fetchrow("SELECT * FROM level WHERE _user = $1 and guild = $2", str(message.author.id),str(message.guild.id))
                        if res1 == None:
                            await self.bot.pg_con.execute("INSERT INTO level(_user,guild,exp,lv,color) VALUES($1,$2,$3,$4,$5)", str(message.author.id),str(message.guild.id),110,2,'#feb8ff')
                        else:
                            await self.bot.pg_con.execute(f"UPDATE level SET exp = exp + 1 WHERE _user = $1 AND guild = $2", str(message.author.id),str(message.guild.id))
                            if res1[2] >= exp[res1[3] - 1]:
                                await self.bot.pg_con.execute(
                                    f"UPDATE level SET lv = lv + 1 WHERE _user = $1 AND guild = $2", str(message.author.id),str(message.guild.id))
                                embed = discord.Embed(title="레벨업!🆙", colour=discord.Colour.gold())
                                embed.add_field(name="축하드립니다!",
                                                value="현재레벨:" + str(res1[3]) + ".Lv" "\n현재경험지:" + str(
                                                    res1[2]) + ".exp" + "\n다음레벨업까지:" + str(
                                                    int(exp[res1[3]]) - int(res1[2])) + ".exp 이상필요해요!")
                                embed.add_field(name="레벨업 알림 끄는법",value=f"[대시보드](http://taesiabot.kro.kr/dashboard/{message.guild.id}/config/lvl) 에서 설정하실수있습니다.")
                                embed.set_footer(text="아나타...좀 고여가시는군요?")
                                await message.channel.send(f"{message.author.mention}", embed=embed)
                    else:
                        pass
                else:
                    pass
            else:
                pass

    """@commands.Cog.listener()
    async def on_command(self, ctx):
        time = datetime.datetime.now()
        year = time.year
        month = time.month
        day = time.day
        hour = time.hour
        minuts = time.minute
        second = time.second
        times = f"{year}-{month}-{day},{hour}H {minuts}M {second}S"
        await self.bot.pg_con.execute("INSERT INTO command_log(guild,command,whos,whens) VALUES($1,$2,$3,$4)",
                                      str(ctx.guild.id), str(ctx.command), str(ctx.author.display_name),str(times))"""



def setup(bot):
    bot.add_cog(level(bot))
    print('cogs - `level` is loaded')