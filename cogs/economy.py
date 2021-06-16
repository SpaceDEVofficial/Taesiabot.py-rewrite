from datetime import datetime
from dpytools.menus import confirm
import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv(verbose=True)
import asyncio

class economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.companyname = {"fmsg":"사성전자(FMSG)","rg":"알쥐전자(RG)","sdev":"스페이스데브(SDEV)","ccn":"캣코인(CCN)","gpm":"굿프로모션(GPM)","otl":"아웃텔(OTL)"}
        self.companyname_list = ["fmsg","FMSG", "rg", "RG", "sdev", "SDEV", "ccn" ,"CCN",
                            "gpm","GPM", "otl", "OTL"]
        self.companyname_value = {"fmsg": "vlalues_1", "rg": "vlalues_2", "sdev": "vlalues_3", "ccn": "vlalues_4",
                            "gpm": "vlalues_5", "otl": "vlalues_6"}
        self.companyname_sql = {"fmsg": 2, "rg": 4, "sdev": 6, "ccn": 8,
                                  "gpm": 10, "otl": 12}


    @commands.command(name="주식")
    async def stock(self,ctx, mode=None,name:str=None,count=None):
        vl = await self.bot.pg_con.fetchrow("SELECT * FROM economy WHERE user_id = $1", ctx.author.id)
        if vl == None:
            return await ctx.reply("이코노미 시스템에 가입되어있지 않습니다. `(Prefix) + 가입`으로 가입하세요.")
        if mode==None and count==None and name==None:
            vl = await self.bot.pg_con.fetch("SELECT * FROM stock")
            tm = datetime.now().minute
            sc = datetime.now().second
            total = ""
            if int(tm) >= 31 and int(tm) <= 59:
                mm = 59 - int(tm)
                ss = 60 - int(sc)
                total += f"{mm}분 {ss}초"
            elif int(tm) <= 29 or int(tm) >= 1:
                mm = 29 - int(tm)
                ss = 60 - int(sc)
                total += f"{mm}분 {ss}초"
            em = discord.Embed(title="태시아 주식 현황",description=f"다음 변동까지 `{total}`남았습니다.")
            for i in vl:
                if i[2] == "down":
                    em.add_field(name=f"{self.companyname[i[0]]}",value=f"```diff\n{i[1]}\n-▼ ( {i[3]} )```")
                else:
                    em.add_field(name=f"{self.companyname[i[0]]}", value=f"```diff\n{i[1]}\n+▲ ( {i[3]} )```")
            await ctx.reply(embed=em)
        elif mode == "매수":
            if int(count) <= 0:
                em = discord.Embed(title="ERROR! ⛔",
                                   description=f"1개 이상 매수해야합니다.",
                                   colour=discord.Colour.red())
                return await ctx.send(embed=em)
            if name in self.companyname_list:
                nm = name.lower()
                vl = await self.bot.pg_con.fetchrow(f"SELECT * FROM stock WHERE company_name = $1",nm)
                mny = await self.bot.pg_con.fetchrow(f"SELECT * FROM economy WHERE user_id = $1",ctx.author.id)
                em = discord.Embed(title="Confirm?", description=f"진짜로 `{self.companyname[name]}`기업의 주식을 `{str(count)}주`개로 구매하시겠습니까?\n결제 예상금액: `{vl[1]*int(count)}원`", colour=discord.Colour.red())
                msg = await ctx.reply(embed=em)
                confirmation = await confirm(ctx, msg)
                if confirmation:
                    if vl[1]*int(count) > mny[1]:
                        em = discord.Embed(title="ERROR! ⛔", description=f"결제에 필요한 금액이 부족합니다.\n현재 자금: `{mny[1]}`\n부족한 금액: `{(vl[1]*int(count)) - mny[1]}`", colour=discord.Colour.red())
                        return await msg.edit(embed=em)
                    await self.bot.pg_con.execute(f"UPDATE economy SET money = money-$1 WHERE user_id = $2",vl[1]*int(count),ctx.author.id)
                    await self.bot.pg_con.execute(f"UPDATE stock_value SET {self.companyname_value[nm]} = {self.companyname_value[nm]}+$1 WHERE user_id = $2",int(count),ctx.author.id)
                    em1 = discord.Embed(title="Success! ✅", description="성공적으로 매수하였습니다.",
                                        colour=discord.Colour.blue())
                    await msg.edit(embed=em1)
                elif confirmation is False:
                    em1 = discord.Embed(title="Cancelled! ⛔", description="거부하셨습니다.", colour=discord.Colour.red())
                    await msg.edit(embed=em1)
                else:
                    em1 = discord.Embed(title="Time out! ⛔", description="취소되었습니다.", colour=discord.Colour.red())
                    await msg.edit(embed=em1)
        elif mode == "매도":
            nm = name.lower()
            vl = await self.bot.pg_con.fetchrow(f"SELECT * FROM stock WHERE company_name = $1", nm)
            vl1 = await self.bot.pg_con.fetchrow(f"SELECT * FROM stock_value WHERE user_id = $1", ctx.author.id)
            if count == "올" or count == "모두":
                if vl1[int(self.companyname_sql[nm])] == 0:
                    em = discord.Embed(title="ERROR! ⛔",
                                       description=f"{self.companyname[nm]}의 가진 주식은 없으므로 팔수없습니다.",
                                       colour=discord.Colour.red())
                    return await ctx.send(embed=em)
                em = discord.Embed(title="Confirm?",
                                   description=f"진짜로 `{self.companyname[nm]}`기업의 주식을 `{str(count)}주`개로 판매하시겠습니까?\n예상수익: `{vl[1] * vl1[int(self.companyname_sql[nm])]}원`",
                                   colour=discord.Colour.red())
                msg = await ctx.reply(embed=em)
                confirmation = await confirm(ctx, msg)
                if confirmation:
                    await self.bot.pg_con.execute(f"UPDATE economy SET money = money+$1 WHERE user_id = $2",
                                                  vl[1] * vl1[int(self.companyname_sql[nm])], ctx.author.id)
                    await self.bot.pg_con.execute(
                        f"UPDATE stock_value SET {self.companyname_value[nm]} = {self.companyname_value[nm]}-$1 WHERE user_id = $2",
                        vl1[int(self.companyname_sql[nm])], ctx.author.id)
                    em1 = discord.Embed(title="Success! ✅", description=f"성공적으로 매도하였습니다.\n얻은 수익: `{vl[1] * vl1[int(self.companyname_sql[nm])]}`",
                                        colour=discord.Colour.blue())
                    await msg.edit(embed=em1)
                elif confirmation is False:
                    em1 = discord.Embed(title="Cancelled! ⛔", description="거부하셨습니다.", colour=discord.Colour.red())
                    await msg.edit(embed=em1)
                else:
                    em1 = discord.Embed(title="Time out! ⛔", description="취소되었습니다.", colour=discord.Colour.red())
                    await msg.edit(embed=em1)
            else:
                if vl1[int(self.companyname_sql[nm])] == 0:
                    em = discord.Embed(title="ERROR! ⛔",
                                       description=f"{self.companyname[nm]}의 가진 주식은 없으므로 팔수없습니다.",
                                       colour=discord.Colour.red())
                    return await ctx.send(embed=em)
                em = discord.Embed(title="Confirm?",
                                   description=f"진짜로 `{self.companyname[nm]}`기업의 주식을 `{str(count)}주`개로 판매하시겠습니까?\n예상수익: `{vl[1] * int(count)}원`",
                                   colour=discord.Colour.red())
                msg = await ctx.reply(embed=em)
                confirmation = await confirm(ctx, msg)
                if confirmation:
                    await self.bot.pg_con.execute(f"UPDATE economy SET money = money+$1 WHERE user_id = $2",
                                                  vl[1] * int(count), ctx.author.id)
                    await self.bot.pg_con.execute(
                        f"UPDATE stock_value SET {self.companyname_value[nm]} = {self.companyname_value[nm]}-$1 WHERE user_id = $2",
                        int(count), ctx.author.id)
                    em1 = discord.Embed(title="Success! ✅",
                                        description=f"성공적으로 매도하였습니다.\n얻은 수익: `{vl[1] * vl1[int(self.companyname_sql[nm])]}`",
                                        colour=discord.Colour.blue())
                    await msg.edit(embed=em1)
                elif confirmation is False:
                    em1 = discord.Embed(title="Cancelled! ⛔", description="거부하셨습니다.", colour=discord.Colour.red())
                    await msg.edit(embed=em1)
                else:
                    em1 = discord.Embed(title="Time out! ⛔", description="취소되었습니다.", colour=discord.Colour.red())
                    await msg.edit(embed=em1)
        elif mode == "지갑":
            vl1 = await self.bot.pg_con.fetchrow(f"SELECT * FROM stock_value WHERE user_id = $1", ctx.author.id)
            mny = await self.bot.pg_con.fetchrow(f"SELECT * FROM economy WHERE user_id = $1", ctx.author.id)
            em = discord.Embed(title=f"{ctx.author.display_name}님의 주식 지갑",description=f"현재 자금: {mny[1]}",colour=discord.Colour.blue())
            em.add_field(name=f"{self.companyname[vl1[1].lower()]}",value=f"{vl1[2]}개")
            em.add_field(name=f"{self.companyname[vl1[3].lower()]}", value=f"{vl1[4]}개")
            em.add_field(name=f"{self.companyname[vl1[5].lower()]}", value=f"{vl1[6]}개")
            em.add_field(name=f"{self.companyname[vl1[7].lower()]}", value=f"{vl1[8]}개")
            em.add_field(name=f"{self.companyname[vl1[9].lower()]}", value=f"{vl1[10]}개")
            em.add_field(name=f"{self.companyname[vl1[11].lower()]}", value=f"{vl1[12]}개")
            await ctx.reply(embed=em)

    @commands.command(name="가입")
    async def join_economy(self, ctx):
        vl = await self.bot.pg_con.fetchrow("SELECT * FROM economy WHERE user_id = $1",ctx.author.id)
        if vl == None:
            em = discord.Embed(title="Confirm?",description="이코노미 시스템에 가입하시겠습니까?",colour=discord.Colour.red())
            msg = await ctx.reply(embed=em)
            confirmation = await confirm(ctx, msg)
            if confirmation:
                await self.bot.pg_con.execute("INSERT INTO economy(user_id,money) VALUES ($1,$2)",ctx.author.id,50000)
                await self.bot.pg_con.execute("INSERT INTO stock_value(user_id,company_name_1,vlalues_1,company_name_2,vlalues_2,company_name_3,vlalues_3,company_name_4,vlalues_4,company_name_5,vlalues_5,company_name_6,vlalues_6) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13)",
                                              ctx.author.id,
                                              "FMSG",
                                              0,
                                              "RG",
                                              0,
                                              "SDEV",
                                              0,
                                              "CCN",
                                              0,
                                              "GPM",
                                              0,
                                              "OTL",
                                              0)
                em1 = discord.Embed(title="Success! ✅", description="성공적으로 가입되셨습니다.\n초기 지원금 `50,000원`을 지급해드렸습니다.", colour=discord.Colour.blue())
                await msg.edit(embed=em1)
            elif confirmation is False:
                em1 = discord.Embed(title="Cancelled! ⛔", description="거부하셨습니다.", colour=discord.Colour.red())
                await msg.edit(embed=em1)
            else:
                em1 = discord.Embed(title="Time out! ⛔", description="취소되었습니다.", colour=discord.Colour.red())
                await msg.edit(embed=em1)
        else:
            em = discord.Embed(title="ERROR! ⛔", description="이미 가입되어있습니다.", colour=discord.Colour.red())
            await ctx.reply(embed=em)

    @commands.command(name="탈퇴")
    async def out_economy(self, ctx):
        vl = await self.bot.pg_con.fetchrow("SELECT * FROM economy WHERE user_id = $1", ctx.author.id)
        if vl != None:
            em = discord.Embed(title="Confirm?", description="이코노미 시스템에서 탈퇴하시겠습니까?", colour=discord.Colour.red())
            msg = await ctx.reply(embed=em)
            confirmation = await confirm(ctx, msg)
            if confirmation:
                await self.bot.pg_con.execute("DELETE FROM economy WHERE user_id=$1", ctx.author.id)
                await self.bot.pg_con.execute(
                    "DELETE FROM stock_value WHERE user_id=$1",
                    ctx.author.id)
                em1 = discord.Embed(title="Success! ✅", description="성공적으로 탈퇴되셨습니다.",
                                    colour=discord.Colour.blue())
                await msg.edit(embed=em1)
            elif confirmation is False:
                em1 = discord.Embed(title="Cancelled! ⛔", description="거부하셨습니다.", colour=discord.Colour.red())
                await msg.edit(embed=em1)
            else:
                em1 = discord.Embed(title="Time out! ⛔", description="취소되었습니다.", colour=discord.Colour.red())
                await msg.edit(embed=em1)
        else:
            em = discord.Embed(title="ERROR! ⛔", description="가입되어있지 않습니다.", colour=discord.Colour.red())
            await ctx.reply(embed=em)


def setup(bot):
    bot.add_cog(economy(bot))
    print('cogs - `economy` is loaded')
