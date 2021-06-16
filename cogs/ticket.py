import discord
import asyncio
from discord.ext import commands

class Ticket(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def make_embed(self,ctx,title,desc,color,footer=None):
        em = discord.Embed(title=title,description=desc,colour=color)
        if footer==None:
            em.set_footer(icon_url=ctx.author.avatar_url)
            return em
        em.set_footer(icon_url=ctx.author.avatar_url,text=footer)
        return em


    @commands.command(name="티켓설정")
    @commands.has_permissions(administrator=True)
    async def ticket(self, ctx, ticket_channel:discord.TextChannel=None, log_channel:discord.TextChannel=None, role:discord.Role=None):
        res = await self.bot.pg_con.fetchrow("SELECT * FROM ticket_conf WHERE guild_id = $1",ctx.guild.id)
        if ticket_channel.id == log_channel.id:
            return await ctx.reply(embed=self.make_embed(ctx=ctx,
                                                         title="ERROR ⛔",
                                                         desc=f"티켓 신청채널과 로그채널은 다른 채널이어야만 합니다.\n다른 채널로 선책해주세요.",
                                                         color=discord.Colour.red()))
        if res != None:
            return await ctx.reply(embed=self.make_embed(ctx=ctx,
                                                         title="ERROR ⛔",
                                                         desc=f"이미 등록되어있습니다.\n티켓 생성 채널 - <#{res[1]}>\n티켓 로그 채널 - <#{res[2]}>\n채널 변경을 원하실경우 티켓서비스에서 탈퇴후 다시 설정해주세요.",
                                                         color=discord.Colour.red()))
        if ticket_channel == None:
            return await ctx.reply(embed=self.make_embed(ctx=ctx,
                                                         title="ERROR ⛔",
                                                         desc="티켓 전용 채널을 지정하지 않으셨습니다. `#채널명`으로 지정하여주세요.",
                                                         color=discord.Colour.red()))
        elif log_channel == None:
            return await ctx.reply(embed=self.make_embed(ctx=ctx,
                                                         title="ERROR ⛔",
                                                         desc="티켓 종료시 기록될 채널을 지정하지 않으셨습니다. `#채널명`으로 지정하여주세요.",
                                                         color=discord.Colour.red()))
        elif role == None:
            msg = await ctx.reply(embed=self.make_embed(ctx=ctx,
                                                        title="Continue?",
                                                        desc="티켓 생성시 맨션될 역할을 지정하지 않으셨습니다. \n`@역할이름`으로 지정하여주시거나 자동으로 생성합니다.",
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
                                                             desc=f"등록중입니다.잠시만 기다려주세요.",
                                                             color=discord.Colour.green()))
                        #chan = await self.bot.get_channel(ticket_channel.id)
                        await ticket_channel.set_permissions(ctx.guild.default_role, send_messages=False)
                        r = await ctx.guild.create_role(name="Support",colour=discord.Colour.from_rgb(4, 217, 213))
                        ticket_msg = await ticket_channel.send(embed=self.make_embed(ctx=ctx,
                                                        title="🎫티켓생성",
                                                        desc="아래 🎫모양 반응을 클릭해 티켓을 생성하세요. \n생성시 자동으로 지원팀의 역할을 맨션합니다. 신중히 생성하여주세요.",
                                                        color=discord.Colour.green()))
                        await ticket_msg.add_reaction("🎫")
                        await self.bot.pg_con.execute(
                            "INSERT INTO ticket_conf(guild_id,ticket_channel_id,log_channel_id,message_id,role_id) VALUES($1,$2,$3,$4,$5)",
                            ctx.guild.id,
                            ticket_channel.id,
                            log_channel.id,
                            ticket_msg.id,
                            r.id)
                        return await msg.edit(embed=self.make_embed(ctx=ctx,
                                                             title="Success! ✅",
                                                             desc=f"성공적으로 등록하였습니다.\n생성된 역할 {r.mention}을 지원담당멤버에게 부여해주세요",
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
                                                        desc=f"등록중입니다.잠시만 기다려주세요.",
                                                        color=discord.Colour.green()))
            try:
                ticket_msg = await ticket_channel.send(embed=self.make_embed(ctx=ctx,
                                                                             title="🎫티켓생성",
                                                                             desc="아래 🎫모양 반응을 클릭해 티켓을 생성하세요. \n생성시 자동으로 지원팀의 역할을 맨션합니다. 신중히 생성하여주세요.",
                                                                             color=discord.Colour.green()))
                await ticket_msg.add_reaction("🎫")
                await self.bot.pg_con.execute(
                    "INSERT INTO ticket_conf(guild_id,ticket_channel_id,log_channel_id,message_id,role_id) VALUES($1,$2,$3,$4,$5)",
                    ctx.guild.id,
                    ticket_channel.id,
                    log_channel.id,
                    ticket_msg.id,
                    role.id)
                return await msg.edit(embed=self.make_embed(ctx=ctx,
                                                            title="Success! ✅",
                                                            desc=f"성공적으로 등록하였습니다.",
                                                            color=discord.Colour.green()))
            except:
                await msg.clear_reactions()
                return await msg.edit(embed=self.make_embed(ctx=ctx,
                                                            title="Error! ⛔",
                                                            desc=f"권한 부족 또는 데이터베이스 오류로 실패하였습니다.",
                                                            color=discord.Colour.red()))

    @commands.command(name="티켓탈퇴")
    @commands.has_permissions(administrator=True)
    async def ticket_cancel(self,ctx):
        msg = await ctx.reply(embed=self.make_embed(ctx=ctx,
                                                    title="Continue?",
                                                    desc="티켓 서비스에서 탈퇴하시겠습니까?",
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
                                                         desc=f"탈퇴중입니다.잠시만 기다려주세요.",
                                                         color=discord.Colour.green()))
                    res = await self.bot.pg_con.fetch("SELECT * FROM ticket_value WHERE guild_id = $1", ctx.guild.id)
                    print(res)
                    if not res == []:
                        await msg.edit(embed=self.make_embed(ctx=ctx,
                                                             title="ERROR ⛔",
                                                             desc=f"아직 진행중인 티켓이 있습니다.\n탈퇴를 원하실경우 진행중인 티켓을 종료후 다시 시도해주세요.",
                                                             color=discord.Colour.red()))
                        em = discord.Embed(title="진행중인 티켓",colour=discord.Colour.blue())
                        num = 0
                        for i in res:
                            num += 1
                            chaname = self.bot.get_channel(i[1])
                            usname = self.bot.get_user(i[3])
                            em.add_field(name=f"{num}. 진행중인 티켓 채널: {chaname}",value=f"티켓 생성 유저: {usname.display_name}")
                        return await ctx.send(embed=em)
                    else:
                        res1 = await self.bot.pg_con.fetchrow("SELECT * FROM ticket_conf WHERE guild_id = $1", ctx.guild.id)
                        msgs = await self.bot.get_channel(res1[1]).fetch_message(res1[3])
                        await msgs.delete()
                        await self.bot.pg_con.execute(
                            "DELETE FROM ticket_conf WHERE guild_id = $1",
                            ctx.guild.id)
                        await msg.edit(embed=self.make_embed(ctx=ctx,
                                                             title="Success! ✅",
                                                             desc=f"탈퇴가 완료되었습니다. 이용해주셔서 감사드립니다.",
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



def setup(bot):
    bot.add_cog(Ticket(bot))