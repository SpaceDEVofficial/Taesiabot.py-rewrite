import os
import asyncpg
from discord.ext import commands
#from asyncpg import connection
import discord
import datetime
from dpytools.menus import multichoice,confirm
import json
import random
import hcskr
from dotenv import load_dotenv
load_dotenv(verbose=True)


class hcs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="hcs")
    @commands.dm_only()
    async def hcs(self,ctx,mode,name=None,birth=None,loc=None,schoolname=None,schoolvl=None,pwd=None):
        if mode == "가입":
            chk = await self.bot.pg_con.fetchrow("SELECT * FROM hcs WHERE user_id=$1",ctx.author.id)
            if chk==None:
                pass
            else:
                return await ctx.send("이미 가입되어있습니다.")
            prc = await hcskr.asyncGenerateToken(name,birth,loc,schoolname,schoolvl,pwd)
            if prc["code"]=="SUCCESS":
                await self.bot.pg_con.execute("INSERT INTO hcs(user_id,token,status,times) VALUES($1,$2,$3,$4)",
                                              ctx.author.id,prc["token"],"false",f"{datetime.datetime.now()}")
                return await ctx.send(f"가입되었습니다.\n\n발급된 토큰(수동으로 진행할시 필요)\n||{prc['token']}||\n\n매일 아침 7시에서 7시 30분사이에 자동으로 자가진단을 진행합니다.\n이전에 코로나 의심증상이 있을시 탈퇴하시거나 `(Prefix)+hcs+패스`로 자동으로 수행하지 않도록 해주시고 이에 대한 책임은 본인에게 있음을 알립니다.")
            else:
                return await ctx.send(prc["message"])
        elif mode == "탈퇴":
            data = await self.bot.pg_con.fetchrow("SELECT * FROM hcs WHERE user_id=$1", ctx.author.id)
            if data == None:
                return await ctx.send(
                    "가입되어있지않습니다.`(Prefix) + hcs + 가입 + 이름 + 생년월일(6자리) + 학교이름 + 학교급 + 비밀번호(4자리)`로 가입하세요.")
            em = discord.Embed(title="Confirm?", description="자동자가진단 시스템에서 탈퇴하시겠습니까?", colour=discord.Colour.red())
            msg = await ctx.reply(embed=em)
            confirmation = await confirm(ctx, msg)
            if confirmation:
                await self.bot.pg_con.execute("DELETE FROM hcs WHERE user_id=$1",ctx.author.id)
                em1 = discord.Embed(title="Success! ✅", description="성공적으로 탈퇴되셨습니다.", colour=discord.Colour.blue())
                await msg.edit(embed=em1)
            elif confirmation is False:
                em1 = discord.Embed(title="Cancelled! ⛔", description="거부하셨습니다.", colour=discord.Colour.red())
                await msg.edit(embed=em1)
            else:
                em1 = discord.Embed(title="Time out! ⛔", description="취소되었습니다.", colour=discord.Colour.red())
                await msg.edit(embed=em1)
        elif mode == "수동수행":
            data = await self.bot.pg_con.fetchrow("SELECT * FROM hcs WHERE user_id=$1", ctx.author.id)
            if data == None:
                return await ctx.send(
                    "가입되어있지않습니다.`(Prefix) + hcs + 가입 + 이름 + 생년월일(6자리) + 학교이름 + 학교급 + 비밀번호(4자리)`로 가입하세요.")
            prc = await hcskr.asyncTokenSelfCheck(name)
            if prc["code"]=="SUCCESS":
                await self.bot.pg_con.execute("UPDATE hcs SET status=$1 WHERE user_id=$2",
                                              "true", ctx.author.id)
                await self.bot.pg_con.execute("UPDATE hcs SET times=$1 WHERE user_id=$2",
                                              str(datetime.datetime.now()), ctx.author.id)
                await ctx.send(prc["message"])
            else:
                await ctx.send(prc["message"])
        elif mode == "자동수행":
            data = await self.bot.pg_con.fetchrow("SELECT * FROM hcs WHERE user_id=$1",ctx.author.id)
            if data == None:
                return await ctx.send("가입되어있지않습니다.`(Prefix) + hcs + 가입 + 이름 + 생년월일(6자리) + 학교이름 + 학교급 + 비밀번호(4자리)`로 가입하세요.")
            prc = await hcskr.asyncTokenSelfCheck(data[1])
            if prc["code"]=="SUCCESS":
                await self.bot.pg_con.execute("UPDATE hcs SET status=$1 WHERE user_id=$2",
                                              "true",ctx.author.id)
                await self.bot.pg_con.execute("UPDATE hcs SET times=$1 WHERE user_id=$2",
                                              str(datetime.datetime.now()), ctx.author.id)
                await ctx.send(prc["message"])
            else:
                await ctx.send(prc["message"])
        elif mode == "패스":
            data = await self.bot.pg_con.fetchrow("SELECT * FROM hcs WHERE user_id=$1", ctx.author.id)
            if data == None:
                return await ctx.send(
                    "가입되어있지않습니다.`(Prefix) + hcs + 가입 + 이름 + 생년월일(6자리) + 학교이름 + 학교급 + 비밀번호(4자리)`로 가입하세요.")

            await self.bot.pg_con.execute("UPDATE hcs SET status=$1,times=$2 WHERE user_id=$3",
                                          "true",str(datetime.datetime.now()),ctx.author.id)
            await ctx.send("이번 자동자가진단은 무시되었습니다.")
        elif mode == "상태":
            data = await self.bot.pg_con.fetchrow("SELECT * FROM hcs WHERE user_id=$1", ctx.author.id)
            if data == None:
                return await ctx.send(
                    "가입되어있지않습니다.`(Prefix) + hcs + 가입 + 이름 + 생년월일(6자리) + 학교이름 + 학교급 + 비밀번호(4자리)`로 가입하세요.")
            state = None
            if data[2] == "true":
                state="자동자가진단시스템으로 진행되었거나 다음자동자가진단시스템에서 무시된상태입니다."
            else:
                state="아직 자가진단이 수행되지않은 상태입니다."
            em = discord.Embed(title=f"{ctx.author.name}님의 자가진단상태")
            em.add_field(name="수행상태",value=state,inline=False)
            em.add_field(name="최근수행시각",value=data[3],inline=False)
            await ctx.send(embed=em)




def setup(bot):
    bot.add_cog(hcs(bot))
    print('cogs - `hcs` is loaded')