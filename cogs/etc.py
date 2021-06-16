import asyncio
import os
import asyncpg
import requests
from discord.ext import commands
import DiscordUtils
import discord
from PIL import Image, ImageDraw

# Open template and get drawing context
from PIL import ImageFont
from PIL import ImageColor
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

class etc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def make_embed(self,ctx,title,desc,color,footer=None):
        em = discord.Embed(title=title,description=desc,colour=color)
        if footer==None:
            em.set_footer(icon_url=ctx.author.avatar_url)
            return em
        em.set_footer(icon_url=ctx.author.avatar_url,text=footer)
        return em

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def warn(self,ctx,user:discord.Member,*,reason):
        conf = await self.bot.pg_con.fetchrow("SELECT * FROM warn_conf WHERE guild_id=$1",ctx.guild.id)
        if not conf == None:
            num_count = await self.bot.pg_con.fetch("SELECT * FROM warn_value WHERE guild_id=$1 AND warn_to=$2",ctx.guild.id,user.id)
            if num_count == []:
                await self.bot.pg_con.execute("INSERT INTO warn_value(guild_id,num,warn_to,reason,warn_from) VALUES($1,$2,$3,$4,$5)",
                                              ctx.guild.id,1,user.id,reason,ctx.author.id)
                em = discord.Embed(title="🚨 경고 로그 - #1 🚨",colour=discord.Colour.red())
                em.add_field(name="👮‍♂️경고 요청자",value=f"{ctx.author.mention}",inline=False)
                em.add_field(name="📌경고 대상자",value=f"{user.mention}",inline=False)
                em.add_field(name="경고 횟수",value=f"1/{conf[1]}")
                em.add_field(name="사유",value=reason,inline=False)
                await ctx.send(embed=em)
                await self.bot.get_channel(conf[4]).send(embed=em)
            else:
                num = 1
                for i in num_count:
                    num += 1
                await self.bot.pg_con.execute(
                    "INSERT INTO warn_value(guild_id,num,warn_to,reason,warn_from) VALUES($1,$2,$3,$4,$5)",
                    ctx.guild.id, num, user.id, reason, ctx.author.id)
                em = discord.Embed(title=f"🚨 경고 로그 - #{num} 🚨", colour=discord.Colour.red())
                em.add_field(name="👮‍♂️경고 요청자", value=f"{ctx.author.mention}", inline=False)
                em.add_field(name="📌경고 대상자", value=f"{user.mention}", inline=False)
                em.add_field(name="경고 횟수", value=f"{num}/{conf[1]}")
                em.add_field(name="사유", value=reason, inline=False)
                await ctx.send(embed=em)
                await self.bot.get_channel(conf[4]).send(embed=em)
        else:
            await ctx.reply("경고 설정이 되어있지 않습니다. `(Prefix) + 경고설정가이드`를 참고하여 설정을 완료하여주세요.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unwarn(self,ctx,user:discord.Member,ID,*,reason):
        conf = await self.bot.pg_con.fetchrow("SELECT * FROM warn_conf WHERE guild_id=$1", ctx.guild.id)
        warn = await self.bot.pg_con.fetchrow("SELECT * FROM warn_value WHERE guild_id=$1 AND warn_to = $2 AND num = $3", ctx.guild.id,user.id,int(ID))
        if not conf == None:
            if not warn == None:
                await self.bot.pg_con.execute("DELETE FROM warn_value WHERE guild_id = $1 AND warn_to = $2 AND num = $3",ctx.guild.id,user.id,int(ID))
                num_count = await self.bot.pg_con.fetch("SELECT * FROM warn_value WHERE guild_id=$1 AND warn_to=$2",
                                                        ctx.guild.id, user.id)
                num = 1
                if num_count != []:
                    for i in num_count:
                        num += 1
                else:
                    num = 0
                em = discord.Embed(title=f"🚨 경고 취소 - #{ID} 🚨", colour=discord.Colour.red())
                em.add_field(name="👮‍♂️경고 취소 요청자", value=f"{ctx.author.mention}", inline=False)
                em.add_field(name="📌경고 취소 대상자", value=f"{user.mention}", inline=False)
                em.add_field(name="경고 횟수", value=f"{num}/{conf[1]}")
                em.add_field(name="사유", value=reason, inline=False)
                await ctx.send(embed=em)
                await self.bot.get_channel(conf[4]).send(embed=em)
            else:
                await ctx.send(f"해당 ID( `{ID}` )는 없는 ID입니다.")
        else:
            await ctx.reply("경고 설정이 되어있지 않습니다. `(Prefix) + 경고설정가이드`를 참고하여 설정을 완료하여주세요.")

    @commands.command(name="경고설정가이드")
    async def warn_guide(self,ctx):
        em = discord.Embed(title="경고 설정 하는법",description="(Prefix) + 경고설정 + #경고로그채널 + 최대경고수 + 처벌 + @뮤트역할(옵션)")
        em.add_field(name="#경고로그채널",value="경고 부여 및 처벌시에 기록될 채널.",inline=False)
        em.add_field(name="최대경고수", value="자동으로 처벌하기위한 기준입니다.", inline=False)
        em.add_field(name="처벌", value="자동으로 처벌할수있도록하는 카테고리입니다. 입력시 아래 카테고리의 이름을 **__정확히__**입력해주세요.\n지원 처벌기능:\n강제퇴장\n밴\n뮤트", inline=False)
        em.add_field(name="@뮤트역할", value="처벌 카테고리를 `뮤트`로 하였을때 뮤트전용 역할을 선택합니다.\n뮤트 역할이 없을시 비워두시면 자동으로 생성합니다.\n뮤트로 하지않았을때는 입력하지 않아도 됩니다.", inline=False)
        await ctx.reply(embed=em)

    @commands.command(name="들낙설정")
    @commands.has_permissions(administrator=True)
    async def setup_joinout(self, ctx, log_channel: discord.TextChannel, times: int):
        conf = await self.bot.pg_con.fetchrow("SELECT * FROM join_out WHERE guild_id=$1", ctx.guild.id)
        msg = await ctx.send(embed=self.make_embed(ctx=ctx,
                                                   title="Loading.. ⏳",
                                                   desc=f"설정중입니다.잠시만 기다려주세요.",
                                                   color=discord.Colour.green()))
        if conf == None:

            await self.bot.pg_con.execute("INSERT INTO join_out(guild_id,channel_id,sleep) VALUES($1,$2,$3)",ctx.guild.id,log_channel.id,times)
            await msg.edit(embed=self.make_embed(ctx=ctx,
                                                 title="SUCCESS ✅",
                                                 desc=f"설정되었습니다.",
                                                 color=discord.Colour.green()))
        else:
            await msg.edit(embed=self.make_embed(ctx=ctx,
                                                 title="ERROR! ⛔",
                                                 desc=f"이미 설정되어있습니다.\n로그채널: <#{conf[1]}>\n제한시간: {conf[2]}\n변경을 원하실경우 `(Prefix) + 들낙삭제`로 데이터삭제후 다시 등록해주세요.",
                                                 color=discord.Colour.green()))

    @commands.command(name="들낙삭제")
    @commands.has_permissions(administrator=True)
    async def del_joinout(self, ctx):
        conf = await self.bot.pg_con.fetchrow("SELECT * FROM join_out WHERE guild_id=$1", ctx.guild.id)
        msg = await ctx.send(embed=self.make_embed(ctx=ctx,
                                                   title="Loading.. ⏳",
                                                   desc=f"삭제중입니다.잠시만 기다려주세요.",
                                                   color=discord.Colour.green()))
        if conf == None:
            await msg.edit(embed=self.make_embed(ctx=ctx,
                                                 title="ERROR! ⛔",
                                                 desc=f"설정되어있지 않습니다. `(Prefix) + 들낙설정 + #로그채널 + 제한시간(초)`로 설정해주세요.",
                                                 color=discord.Colour.green()))
        else:
            await self.bot.pg_con.execute("DELETE FROM join_out WHERE guild_id=$1",
                                          ctx.guild.id)
            await msg.edit(embed=self.make_embed(ctx=ctx,
                                                 title="SUCCESS ✅",
                                                 desc=f"삭제되었습니다.",
                                                 color=discord.Colour.green()))

    @commands.command(name="경고설정")
    @commands.has_permissions(administrator=True)
    async def setup_warn(self,ctx,log_channel:discord.TextChannel,count:int,punish,mute_role:discord.Role=None):
        conf = await self.bot.pg_con.fetchrow("SELECT * FROM warn_conf WHERE guild_id=$1", ctx.guild.id)
        if conf == None:
            if punish == "뮤트" and mute_role == None:
                msg = await ctx.reply(embed=self.make_embed(ctx=ctx,
                                                            title="Continue?",
                                                            desc="뮤트 역할을 지정하지 않으셨습니다. \n`@역할이름`으로 지정하여주시거나 자동으로 생성합니다.",
                                                            color=discord.Colour.green()))
                await msg.add_reaction("⭕")
                await msg.add_reaction("❌")

                def notice_check(reaction, user):
                    return (
                            user == ctx.author
                            and str(reaction) in ["⭕", "❌"]
                            and msg.id == reaction.message.id
                    )

                try:
                    reaction, user = await self.bot.wait_for(
                        "reaction_add", timeout=60.0, check=notice_check
                    )
                    if str(reaction) == "⭕":
                        try:
                            await msg.clear_reactions()
                            await msg.edit(embed=self.make_embed(ctx=ctx,
                                                                 title="Loading.. ⏳",
                                                                 desc=f"설정중입니다.잠시만 기다려주세요.",
                                                                 color=discord.Colour.green()))
                            guild = ctx.guild
                            mutedRole = await guild.create_role(name="Muted")
                            channels = guild.channels
                            for channel in channels:
                                await channel.set_permissions(mutedRole, speak=False, send_messages=False)
                            await self.bot.pg_con.execute("INSERT INTO warn_conf(guild_id,warn_max,punish,mute_id,log_channel) VALUES($1,$2,$3,$4,$5)",
                                                          guild.id,count,punish,mutedRole.id,log_channel.id)
                            return await msg.edit(embed=self.make_embed(ctx=ctx,
                                                                        title="Success! ✅",
                                                                        desc=f"성공적으로 설정하였습니다.",
                                                                        color=discord.Colour.green()))
                        except:
                            await msg.clear_reactions()
                            return await msg.edit(embed=self.make_embed(ctx=ctx,
                                                                        title="Error! ⛔",
                                                                        desc=f"권한 부족 또는 데이터베이스 오류로 실패하였습니다.",
                                                                        color=discord.Colour.red()))
                    else:
                        await msg.clear_reactions()
                        return await msg.edit(embed=self.make_embed(ctx=ctx,
                                                                    title="Cancelled! ⛔",
                                                                    desc=f"취소하셨습니다.",
                                                                    color=discord.Colour.red()))
                except asyncio.TimeoutError:
                    await msg.clear_reactions()
                    return await msg.edit(embed=self.make_embed(ctx=ctx,
                                                                title="Cancelled! ⛔",
                                                                desc=f"취소되었습니다.",
                                                                color=discord.Colour.red()))
            else:
                msg = await ctx.reply(embed=self.make_embed(ctx=ctx,
                                                            title="Loading.. ⏳",
                                                            desc=f"설정중입니다.잠시만 기다려주세요.",
                                                            color=discord.Colour.green()))
                try:
                    await self.bot.pg_con.execute(
                        "INSERT INTO warn_conf(guild_id,warn_max,punish,mute_id,log_channel) VALUES($1,$2,$3,$4,$5)",
                        ctx.guild.id, count, punish, 1, log_channel.id)
                    return await msg.edit(embed=self.make_embed(ctx=ctx,
                                                                title="Success! ✅",
                                                                desc=f"성공적으로 설정하였습니다.",
                                                                color=discord.Colour.green()))
                except:
                    await msg.clear_reactions()
                    return await msg.edit(embed=self.make_embed(ctx=ctx,
                                                                title="Error! ⛔",
                                                                desc=f"권한 부족 또는 데이터베이스 오류로 실패하였습니다.",
                                                                color=discord.Colour.red()))
        else:
            if conf[3] == 1:
                await ctx.send(embed=self.make_embed(ctx=ctx,
                                                    title="Error! ⛔",
                                                    desc=f"이미 설정되어있습니다.\n\n설정값\n\n한계경고횟수: {conf[1]}\n자동처벌기능: {conf[2]}\n뮤트역할: 설정되어있지않음\n로그채널: <#{conf[4]}>",
                                                    color=discord.Colour.red()))
            else:
                await ctx.send(embed=self.make_embed(ctx=ctx,
                                                     title="Error! ⛔",
                                                     desc=f"이미 설정되어있습니다.\n\n설정값\n\n한계경고횟수: {conf[1]}\n자동처벌기능: {conf[2]}\n뮤트역할: <@&{conf[3]}>\n로그채널: <#{conf[4]}>",
                                                     color=discord.Colour.red()))
    @commands.command(name="도움")
    async def helps(self,ctx:discord.Message):
        embed1 = discord.Embed(title="메인 페이지",
                               description="""
안녕하세요. 태시아 봇을 이용해주셔서 감사드립니다.
태시아 봇은 서버관리,주식,애니검색등등 다양한 기능을 가진 봇입니다.

목차
(모든 커맨드의 필수요소는 ' * '로 표시하며 선택적요소는 ' () '로 표시합니다. 
실사용시 표시된 모든 기호는 제외하여 사용해주세요.)

• 1페이지: (현재페이지) 메인 페이지
• 2페이지: 서버관리
• 3페이지: 이코노미
• 4페이지: 기타
""",
                               color=ctx.author.color)
        embed1.set_footer(text='1 / 3',icon_url=ctx.author.avatar_url)
        embed2 = discord.Embed(title="서버관리",color=ctx.author.color)
        embed2.add_field(name="(Prefix) + 경고설정 + #로그채널* + 한계경고수* + 처벌항목* + (뮤트역할)",
                         value="한계경고 수치에 달할경우 자동으로 처벌하기위한 설정 기능입니다.\n뮤트역할은 처벌항목을 뮤트로 할경우 설정해야합니다.",
                         inline=False)
        embed2.add_field(name="(Prefix) + warn + @유저* + 사유*",
                         value="대상유저에세 경고를 부여합니다.",
                         inline=False)
        embed2.add_field(name="(Prefix) + unwarn + @유저* + 경고아이디* +사유*",
                         value="대상유저에게 부여된 경고를 취소합니다.",
                         inline=False)
        embed2.add_field(name="(Prefix) + 들낙설정 + #로그채널* + 최소활동시간*",
                         value="서버에 들어왔다가 최소활동시간전 나갈시 자동으로 밴합니다.\n최소 활동시간은 초단위입니다.",
                         inline=False)
        embed2.add_field(name="(Prefix) + 들낙삭제",
                         value="들낙설정데이터를 지웁니다.",
                         inline=False)
        embed2.add_field(name="(Prefix) + 셋업 + #채널* + 메시지*",
                         value="반응 역할기능을 사용하기위한 기능입니다.",
                         inline=False)
        embed2.add_field(name="(Prefix) + 수정 + 메시지ID* + 수정할 메시지*",
                         value="설정된 메시지의 내용을 수정합니다.",
                         inline=False)
        embed2.add_field(name="(Prefix) + 등록 + 메시지ID* + 이모지* + @역할*",
                         value="등록된 메시지에 반응을 달고 역할을 할당합니다.",
                         inline=False)
        embed2.add_field(name="(Prefix) + 삭제 + 메시지ID*",
                         value="반응 역할에 할당된 데이터를 지웁니다.",
                         inline=False)
        embed2.add_field(name="(Prefix) + 티켓설정 + #티켓채널* + #로그채널* + (@지원역할)",
                         value="티켓기능을 사용하기위한 설정입니다.",
                         inline=False)
        embed2.add_field(name="(Prefix) + 티켓탈퇴",
                         value="티켓기능을 비활성화합니다.",
                         inline=False)
        embed2.set_footer(text='2 / 4',icon_url=ctx.author.avatar_url)


        embed3 = discord.Embed(title="이코노미",color=ctx.author.color)
        embed3.add_field(name="(Prefix) + 가입",
                         value="이코노미 시스템에 가입합니다.",
                         inline=False)
        embed3.add_field(name="(Prefix) + 주식",
                         value="주식 현황을 보여줍니다.",
                         inline=False)
        embed3.add_field(name="(Prefix) + 주식 + 매수* + 회사코드* + 갯수*",
                         value="지정한 회사의 주식을 갯수만큼 매수합니다.",
                         inline=False)
        embed3.add_field(name="(Prefix) + 주식 + 매도* + 회사코드 + 갯수*",
                         value="지정한 회사의 주식을 갯수만큼 팝니다.\n갯수에 '올' 또는 '모두'를 입력할경우 지정한 회사의 가지고있는 주식을 모두 팝니다.",
                         inline=False)
        embed3.add_field(name="(Prefix) + 주식 + 지갑*",
                         value="가지고있는 주식을 보여줍니다.",
                         inline=False)
        embed3.set_footer(text='3 / 4', icon_url=ctx.author.avatar_url)

        embed4 = discord.Embed(title="기타", color=ctx.author.color)
        embed4.add_field(name="준비중",value="** **",inline=False)
        embed4.set_footer(text='4 / 4', icon_url=ctx.author.avatar_url)
        paginator = DiscordUtils.Pagination.AutoEmbedPaginator(ctx)
        embeds = [embed1, embed2, embed3,embed4]
        await paginator.run(embeds)
        #await ctx.reply("```\n도움말\n\n(접두사) + 야 : 잘살아있는지 확인합니다.\n(접두사) + 프픽변경 : 접두사를 변경할수있는 대시보드 URL을 알려줍니다.\n(접두사) + 프픽 : 커스텀 접두사를 알려줍니다.\n(접두사) + 레벨: 레벨카드를 보여줍니다.```")


    @commands.command(name='야')
    async def prefix(self,ctx:discord.Message):
        await ctx.reply("?")

    async def check_prefix(self,id):
        vl = await self.bot.pg_con.fetch(f"SELECT * FROM prefix WHERE guild = $1",str(id))
        if vl == []:
            return False
        else:
            return True

    async def edit_prefix(self,id,data):
        res = await self.check_prefix(id=id)
        if res == False:
            try:
                await self.bot.pg_con.execute(f"INSERT INTO prefix(guild,prefix) VALUES($1,$2)",str(id),str(data))
                return {"error":False,"msg":f"정상적으로 프리픽스를 ' {data} '로 변경하였습니다.","state":"success"}
            except:
                return {"error": True, "msg": f"프리픽스를 변경하는 도중 알수없는 문제로 실패하였습니다.", "state": "danger"}

        else:
            try:
                await self.bot.pg_con.execute(f"UPDATE prefix SET prefix=$1 WHERE guild = $2",(data,str(id)))
                return {"error": False, "msg": f"정상적으로 프리픽스를 ' {data} '로 변경하였습니다.", "state": "success"}
            except:
                return {"error": True, "msg": f"프리픽스를 변경하는 도중 알수없는 문제로 실패하였습니다.", "state": "danger"}

    @commands.command(name='프픽변경')
    @commands.has_permissions(administrator=True)
    async def change_prefix(self, ctx: discord.Message,prefix):
        mn = await self.edit_prefix(id=ctx.guild.id,data=prefix)
        if mn["error"] == False:
            await ctx.reply(mn["msg"])
        else:
            await ctx.reply(mn["msg"])
        #await ctx.reply(f"프리픽스 변경은 대시보드에서 해주세요.\nhttp://taesiabot.kro.kr/dashboard/{ctx.guild.id}")

    @commands.command(name='프픽')
    async def get_prefix(self,ctx: discord.Message):
        my_list = await self.bot.get_prefix(ctx)
        await ctx.reply(f"기본 접두사(prefix)는 <@!728820788278329424> 입니다.\n이 서버의 커스텀 접두사는 ' `{my_list[2]}` '입니다.")

    """@commands.command(name='레벨')
    async def show_lvl(self, ctx: discord.Message):
        res1 = await self.bot.pg_con.fetch("SELECT _user,exp,lv FROM level WHERE guild = $1 ORDER BY exp + 0 DESC LIMIT 9999999", str(ctx.guild.id))
        for i, x in enumerate(res1, 1):
            if str(x[0]) == str(ctx.author.id):
                path = "C:/Users/Administrator/Desktop/dashboard/cogs/source/userlvl.png"
                im = Image.open('./cogs/source/progress.png').convert('RGB')
                draw = ImageDraw.Draw(im)
                res1 = await self.bot.pg_con.fetchrow("SELECT * FROM level WHERE _user = $1 and guild = $2",
                                                      str(ctx.author.id),
                                                      str(ctx.guild.id))
                # Cyan-ish fill colour
                RGB = ImageColor.getcolor(str(res1[4]), "RGB")
                color = RGB
                percent = ((exp[int(res1[3]) - 1] - exp[int(res1[3]) - 2]) - (exp[int(res1[3]) - 1] - int(res1[2]))) / (
                            exp[int(res1[3]) - 1] - exp[
                        int(res1[3]) - 2]) * 100  # (다음 lv에 해당하는 xp -(다음 lv에 해당하는 xp-현재xp))/다음lv에 해당하는 xp*100
                X = ((580 * (percent / 100)) + 10)
                print(exp[int(res1[3]) - 2])
                print(percent)
                print(((580 * (percent / 100)) + 10))
                # Draw circle at right end of progress bar
                x, y, diam = X, 8, 34  # mx 590 mn 10
                draw.ellipse([x, y, x + diam, y + diam], fill=color)

                # Flood-fill from extreme left of progress bar area to behind circle
                ImageDraw.floodfill(im, xy=(14, 24), value=color, thresh=40)

                # Save result
                im.save('./cogs/source/result.png', quality=100)

                progress = Image.open('./cogs/source/result.png').convert('RGB')
                bg = Image.open('./cogs/source/source3.png').convert('RGB')
                merged = Image.new('L', (934, 282)).convert('RGB')

                merged.paste(bg)
                merged.paste(progress, (250, 170))
                merged.save('./cogs/source/final.png', quality=100)

                img = Image.open('./cogs/source/final.png').convert('RGB')
                draw = ImageDraw.Draw(img)
                font = ImageFont.truetype('./cogs/source/fonts/NanumSquareRoundL.ttf', 50)
                font2 = ImageFont.truetype('./cogs/source/fonts/NanumSquareRoundL.ttf', 25)
                draw.text((310, 120), f"{ctx.author}", (255, 255, 255), font=font)
                draw.text((610, 40), f"#{i} / {res1[3]}", color,
                          font=ImageFont.truetype('./cogs/source/fonts/NanumSquareRoundB.ttf', 60))
                draw.text((820, 40), f".LV", color,
                          font=ImageFont.truetype('./cogs/source/fonts/NanumSquareRoundB.ttf', 60))
                draw.text((550, 220), f"{res1[2]}/{exp[int(res1[3]) - 1]} XP; 달성도: {str(round(percent, 2))}%",
                          (255, 255, 255), font=font2)
                img.save('./cogs/source/sample-out.png', quality=100)
                im1 = Image.open("./cogs/source/sample-out.png")
                with requests.get(ctx.author.avatar_url) as r:
                    img_data = r.content
                with open('./cogs/source/profile.jpg', 'wb') as handler:
                    handler.write(img_data)
                im2 = Image.open("./cogs/source/profile.jpg")
                size = 180

                im2 = im2.resize((size, size), resample=0)
                # Creates the mask for the profile picture
                mask_im = Image.new("L", im2.size, 0)
                draw = ImageDraw.Draw(mask_im)
                draw.ellipse((0, 0, size, size), fill=255)

                mask_im.save('./cogs/source/mask_circle.png', quality=100)
                back_im = im1.copy()
                back_im.paste(im2, (52, 50), mask_im)
                back_im.save('./cogs/source/userlvl.png', quality=100)
                f = discord.File(path, filename="LV.png")

                return await ctx.reply(file=f)"""

    @commands.command(name="셋업")
    async def settup_rr(self, ctx, channel: discord.TextChannel, *, msg):
        try:
            Msg = await self.bot.get_channel(channel.id).send(msg)
            await self.bot.pg_con.execute("INSERT INTO rr_conf(guild_id,channel_id,message_id) VALUES($1,$2,$3)",
                                          ctx.guild.id, channel.id, Msg.id)
            await ctx.reply("✅")
        except:
            await ctx.reply("설정에 실패하였습니다.해당 채널에 메시지를 보낼권한, 또는 데이터베이스 에러입니다.")

    @commands.command(name="수정")
    async def edit_rr(self, ctx,chid:int, *, val):
        res1 = await self.bot.pg_con.fetchrow("SELECT * FROM rr_conf WHERE guild_id = $1 AND message_id = $2",
                                              ctx.guild.id,chid)
        if res1 == None:
            return await ctx.reply(f"설정되어있지 않습니다.")
        else:
            try:
                ch = self.bot.get_channel(res1[1])
                msg = await ch.fetch_message(res1[2])
                # await msg.add_reaction(":wave:")
                await msg.edit(content=val)
                return await ctx.reply("✅")
            except:
                await ctx.reply("수정에 실패하였습니다.해당 채널에 메시지권한, 또는 데이터베이스 에러입니다.")

    @commands.command(name="등록")
    async def setting_rr_add(self, ctx, chid:int,emoji=None, role: discord.Role = None):
        res1 = await self.bot.pg_con.fetchrow("SELECT * FROM rr_conf WHERE guild_id = $1 AND message_id = $2",
                                              ctx.guild.id,chid)
        if res1 == None:
            return await ctx.reply(f"설정되어있지 않습니다.")
        else:
            try:
                if self.bot.get_guild(ctx.guild.id).get_role(role.id) == None:
                    return await ctx.reply(f"{role.mention}은 없는 역할입니다.")
                if type(emoji) == "<class 'discord.emoji.Emoji'>":
                    em = emoji
                    emj = ctx.message.guild.emojis
                    for i in emj:
                        if f":{i.name}:" == em:
                            dbemj = self.bot.get_emoji(int(i.id))
                            await self.bot.pg_con.execute(
                                "INSERT INTO rr_value(role_id,emoji,guild_id) VALUES($1,$2::TEXT,$3)", role.id,
                                str(dbemj), ctx.guild.id)
                            ch = self.bot.get_channel(res1[1])
                            msg = await ch.fetch_message(res1[2])
                            await msg.add_reaction(emoji)
                            return await ctx.reply("✅")
                else:
                    await self.bot.pg_con.execute(
                        "INSERT INTO rr_value(role_id,emoji,guild_id) VALUES($1,$2,$3)", role.id,
                        str(emoji), ctx.guild.id)
                    ch = self.bot.get_channel(res1[1])
                    msg = await ch.fetch_message(res1[2])
                    await msg.add_reaction(emoji)
                    return await ctx.reply("✅")
            except:
                await ctx.reply("등록에 실패하였습니다.해당 채널에 메시지권한, 또는 데이터베이스 에러입니다.")

    @commands.command(name="역할생성")
    async def role_create(self, ctx, name, red: int = None, green: int = None, blue: int = None):
        try:
            if red == None and green == None and blue == None:
                await ctx.guild.create_role(name=name)
                return await ctx.reply("✅")
            else:
                await ctx.guild.create_role(name=name, colour=discord.Colour.from_rgb(red, green, blue))
                return await ctx.reply("✅")
        except:
            await ctx.reply("등록에 실패하였습니다.역할권한에러입니다.")

    @commands.command(name="삭제")
    async def delete_rr(self, ctx, chid:int):
        res1 = await self.bot.pg_con.fetchrow("SELECT * FROM rr_conf WHERE guild_id = $1 AND message_id = $2",
                                              ctx.guild.id,chid)
        if res1 == None:
            return await ctx.reply(f"설정되어있지 않습니다.")
        else:
            try:
                ch = self.bot.get_channel(res1[1])
                msg = await ch.fetch_message(res1[2])
                await msg.delete()
                await self.bot.pg_con.execute("DELETE FROM rr_conf WHERE guild_id = $1 AND message_id = $2", ctx.guild.id, chid)
                #await self.bot.pg_con.execute("DELETE FROM rr_value WHERE guild_id = $1", ctx.guild.id)
                await ctx.reply("✅")
            except:
                await ctx.reply("❌실패하였습니다. 다시 시도해주세요.")

    @commands.command(name="뮤트")
    async def mute(self,ctx, member: discord.Member, *, reason=None):
        guild = ctx.guild
        mutedRole = discord.utils.get(guild.roles, name="Muted")

        if not mutedRole:
            mutedRole = await guild.create_role(name="Muted")
            channels = guild.channels
            for channel in channels:
                await channel.set_permissions(mutedRole, speak=False, send_messages=False)

        await member.add_roles(mutedRole, reason=reason)
        await ctx.send(f"{member.mention}님을 뮤트하였습니다.\n이유 : {reason}")
        await member.send(f"{guild.name} 에서 뮤트되셨습니다.")

    @commands.command(name="언뮤트")
    async def unmute(self, ctx, member: discord.Member):
        guild = ctx.guild
        mutedRole = discord.utils.get(guild.roles, name="Muted")

        await member.remove_roles(mutedRole)
        await ctx.send(f"{member.mention}님을 언뮤트하였습니다.")
        await member.send(f"{guild.name} 에서 언뮤트되셨습니다.")


def setup(bot):
    bot.add_cog(etc(bot))
    print('cogs - `etc` is loaded')
