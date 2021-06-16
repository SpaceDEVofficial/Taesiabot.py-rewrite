from datetime import datetime
import random
import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv(verbose=True)
import asyncio

class core(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.call = []
        self.join = []
        self.company=["fmsg","rg","sdev","ccn","gpm","otl"]
        self.snipe_message_author = {}
        self.snipe_message_content = {}
        self.snipe_message_author_avatar = {}
        loop = asyncio.get_event_loop()
        loop.create_task(self.stock_loop())


    @commands.Cog.listener()
    async def on_message_delete(self,message):
        self.snipe_message_author[message.channel.id] = message.author
        self.snipe_message_author_avatar[message.channel.id] = message.author.avatar_url
        self.snipe_message_content[message.channel.id] = message.content
        await asyncio.sleep(60)
        del self.snipe_message_author[message.channel.id]
        del self.snipe_message_content[message.channel.id]
        del self.snipe_message_author_avatar[message.channel.id]

    @commands.command(name='snipe')
    async def snipe(self,ctx):
        channel = ctx.channel
        try:
            snipeEmbed = discord.Embed(title=f"Last deleted message in #{channel.name}",
                                       description=self.snipe_message_content[channel.id])
            snipeEmbed.set_thumbnail(url=self.snipe_message_author_avatar[channel.id])
            snipeEmbed.set_footer(text=f'Deleted by {self.snipe_message_author[channel.id]}')
            await ctx.send(embed=snipeEmbed)
        except:
            await ctx.send(f"There are no deleted message in #{channel.name}")

    async def stock_loop(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            await asyncio.sleep(1)
            now = datetime.now()
            current_time = now.strftime("%M:%S")
            print("stock timer loop Current Time =", current_time)
            if current_time == "00:00":
                for i in self.company:
                    updown = random.randint(1,2) # 1은 하락,2는 상승
                    price = random.randint(100,3000)
                    if updown == 1:
                        pr = await self.bot.pg_con.fetchrow("SELECT price FROM stock WHERE company_name = $1",i)
                        prices = pr[0]
                        if prices - price <= 50:
                            price = 100
                        await self.bot.pg_con.execute("UPDATE stock SET price=price-$1 WHERE company_name = $2",price,i)
                        await self.bot.pg_con.execute("UPDATE stock SET down_up=$1 WHERE company_name = $2", "down", i)
                        await self.bot.pg_con.execute("UPDATE stock SET down_up_value=$1 WHERE company_name = $2", price, i)
                    else:
                        await self.bot.pg_con.execute("UPDATE stock SET price=price+$1 WHERE company_name = $2", price, i)
                        await self.bot.pg_con.execute("UPDATE stock SET down_up=$1 WHERE company_name = $2", "up", i)
                        await self.bot.pg_con.execute("UPDATE stock SET down_up_value=$1 WHERE company_name = $2", price, i)
            elif current_time == "30:00":
                for i in self.company:
                    updown = random.randint(1,2) # 1은 하락,2는 상승
                    price = random.randint(100,3000)
                    if updown == 1:
                        await self.bot.pg_con.execute("UPDATE stock SET price=price-$1 WHERE company_name = $2",price,i)
                        await self.bot.pg_con.execute("UPDATE stock SET down_up=$1 WHERE company_name = $2", "down", i)
                        await self.bot.pg_con.execute("UPDATE stock SET down_up_value=$1 WHERE company_name = $2", price, i)
                    else:
                        await self.bot.pg_con.execute("UPDATE stock SET price=price+$1 WHERE company_name = $2", price, i)
                        await self.bot.pg_con.execute("UPDATE stock SET down_up=$1 WHERE company_name = $2", "up", i)
                        await self.bot.pg_con.execute("UPDATE stock SET down_up_value=$1 WHERE company_name = $2", price, i)

    def cog_unload(self):
        self.stock_loop().close()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        es3 = await self.bot.pg_con.fetchrow("SELECT * FROM join_out WHERE guild_id = $1", member.guild.id)
        if es3[0] == member.guild.id:
            if not member.id in self.join:
                self.join.append(member.id)
                await asyncio.sleep(es3[2])
                self.join.remove(member.id)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        es3 = await self.bot.pg_con.fetchrow("SELECT * FROM join_out WHERE guild_id = $1", member.guild.id)
        if es3[0] == member.guild.id and member.id in self.join:
            em = discord.Embed(title="들낙로그",description=f"`{member}` | `{member.id}`\n들낙하여 밴처리되었습니다.",colour=discord.Colour.red())
            await member.ban()
            await self.bot.get_channel(es3[1]).send(embed=em)
            ban = discord.Embed(title="들낙으로 인한 밴안내",description=f"안녕하세요.\n들낙방지 설정이 되어있는 `{member.guild.name}`에서 들낙행위를 하여 밴처리되었습니다.\n자세한 사항은 길드 오너에게 문의하세요.")
            await member.send(embed=ban)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            pass
        else:
            res1 = await self.bot.pg_con.fetch("SELECT * FROM rr_conf WHERE guild_id = $1",payload.guild_id)
            if res1 == []:
                return
            for i in res1:
                if payload.message_id != i[2]:
                    res3 = await self.bot.pg_con.fetchrow("SELECT * FROM ticket_conf WHERE guild_id = $1", payload.guild_id)
                    print(res3)
                    if res3 == None:
                        return
                    if payload.message_id != res3[3]:
                        channel_id = payload.channel_id
                        channel = self.bot.get_channel(channel_id)

                        message_id = payload.message_id

                        user_id = payload.user_id
                        user = self.bot.get_user(user_id)

                        guild_id = payload.guild_id
                        guild = self.bot.get_guild(guild_id)
                        res5 = await self.bot.pg_con.fetchrow("SELECT * FROM ticket_value WHERE guild_id = $1 AND channel_id = $2",
                                                              guild_id,channel_id)
                        try:
                            if message_id == res5[2] and guild_id == res5[0] and channel_id == res5[
                                1] and payload.emoji.name == "📢" and user.bot == False:
                                message = await channel.fetch_message(message_id)
                                await message.remove_reaction("📢", user)
                                if user_id in self.call:
                                    await channel.send("이미 호출하였습니다.")
                                    return
                                self.call.append(user_id)
                                role = guild.get_role(res3[4])
                                for member in guild.members:
                                    if role in member.roles:
                                        em = discord.Embed(title="대기중인 티켓",description=f"현재 `{guild}`의 `{channel}`에서 `{user}`님이 대기중입니다.")
                                        await member.send(embed=em)
                                await channel.send("정상적으로 호출하였습니다.")
                            if message_id == res5[2] and guild_id == res5[0] and channel_id == res5[
                                1] and payload.emoji.name == "🔒":
                                embed = discord.Embed(
                                    title="티켓 종료 요청!",
                                    description=f"``🎟️ {user.name}님이 티켓종료 요청을 하셨습니다 10초후 종료합니다.``",
                                    color=0xf7fcfd)

                                await channel.send(embed=embed)
                                await asyncio.sleep(10)
                                await channel.delete()
                                log_channel = self.bot.get_channel(res3[2])
                                embed = discord.Embed(
                                    title="티켓 종료 로그",
                                    description=f"`{channel}`은 {user.display_name}님에 의해 종료되었습니다.",
                                    timestamp=datetime.utcnow(),
                                    color=0xf7fcfd)
                                await log_channel.send(embed=embed)
                                try:
                                    self.call.remove(str(user_id))
                                except:
                                    pass
                                await self.bot.pg_con.execute("DELETE FROM ticket_value WHERE channel_id = $1", channel_id)
                        except:
                            pass
                    else:
                        channel_id = payload.channel_id
                        channel = self.bot.get_channel(channel_id)

                        message_id = payload.message_id

                        user_id = payload.user_id
                        user = self.bot.get_user(user_id)

                        guild_id = payload.guild_id
                        guild = self.bot.get_guild(guild_id)
                        if message_id == res3[3] and guild_id == res3[0] and channel_id == res3[
                            1] and payload.emoji.name == "🎫":
                            message = await channel.fetch_message(message_id)
                            await message.remove_reaction("🎫", user)
                            res4 = await self.bot.pg_con.fetchrow("SELECT * FROM ticket_value WHERE guild_id = $1",
                                                                  guild_id)
                            if not res4 == None:
                                if res4[3] == user_id:
                                    return await channel.send(
                                        f"<@{user_id}>님, 이미 진행중인 티켓이 있습니다.\n진행중인 채널 - <#{res4[1]}>\n재생성하실려면 기존 티켓을 종료후 다시 시도해주세요.",
                                        delete_after=20)
                            member = discord.utils.find(lambda m: m.id == payload.user_id, guild.members)
                            support_role = self.bot.get_guild(guild_id).get_role(res3[4])
                            category = discord.utils.get(guild.categories, name="Tickets")
                            if category is None:
                                new_category = await guild.create_category(name="Tickets")
                                category = guild.get_channel(new_category.id)

                            overwrites = {
                                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                                member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                                support_role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                            }
                            ticket_channel_name = await category.create_text_channel(f'ticket-{user.display_name}',
                                                                                     overwrites=overwrites)
                            ticket_channel_id = ticket_channel_name.id
                            embed = discord.Embed(title="무엇을 도와드릴까요?", color=0xf7fcfd)
                            embed.add_field(name="📢 지원팀 맨션",
                                            value="```15분 이상 지원팀이 응답하지 않는다면 이용해주세요.\n(한번만 사용이 가능하며 악의적으로 사용시 서버별 규칙에따라 제재받으실수있습니다.)```",
                                            inline=False)
                            embed.add_field(name="🔒 티켓 종료",
                                            value="```티켓에서의 용무가 끝나셨다면 이용해주세요. 10초뒤에 채널이 삭제됩니다.```",
                                            inline=False)

                            await ticket_channel_name.send(f"<@&{res3[4]}>")
                            await ticket_channel_name.send(f"<@{user_id}>")
                            ticket_channel_message = await ticket_channel_name.send(embed=embed)
                            await ticket_channel_message.add_reaction("📢")
                            await ticket_channel_message.add_reaction("🔒")
                            await self.bot.pg_con.execute(
                                "INSERT INTO ticket_value(guild_id,channel_id,message_id,user_id) VALUES($1,$2,$3,$4)",
                                guild_id,
                                ticket_channel_id,
                                ticket_channel_message.id,
                                user_id)
                else:
                    res2 = await self.bot.pg_con.fetch("SELECT * FROM rr_value")
                    for a in res2:
                        aa = str(a[1]).replace(" ","")
                        if aa.startswith("<:"):
                            if f"<:{payload.emoji.name}:{payload.emoji.id}>" == aa and payload.message_id == i[2] and payload.guild_id == a[2]:
                                guild = self.bot.get_guild(payload.guild_id)
                                role = guild.get_role(int(a[0]))
                                await payload.member.add_roles(role)
                        elif payload.emoji.name == aa and payload.message_id == i[2] and payload.guild_id == a[2]:
                            guild = self.bot.get_guild(payload.guild_id)
                            role = guild.get_role(int(a[0]))
                            await payload.member.add_roles(role)



    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        res1 = await self.bot.pg_con.fetch("SELECT * FROM rr_conf WHERE guild_id = $1", payload.guild_id)
        print(res1)
        if res1 == []:
            return
        for i in res1:
            if payload.message_id != i[2] and payload.channel_id != i[1] and payload.guild_id != i[0]:
                print("psdd")
                return
            else:
                if payload.guild_id == i[0] and payload.message_id == i[2]:
                    res2 = await self.bot.pg_con.fetch("SELECT * FROM rr_value")
                    for a in res2:
                        aa = str(a[1]).replace(" ", "")
                        if aa.startswith("<:"):
                            if f"<:{payload.emoji.name}:{payload.emoji.id}>" == aa and payload.message_id == i[2] and payload.guild_id == a[2]:
                                guild = self.bot.get_guild(payload.guild_id)
                                role = guild.get_role(int(a[0]))
                                member = guild.get_member(payload.user_id)
                                await member.remove_roles(role)
                        elif payload.emoji.name == aa and payload.message_id == i[2] and payload.guild_id == a[2]:
                            guild = self.bot.get_guild(payload.guild_id)
                            role = guild.get_role(int(a[0]))
                            member = guild.get_member(payload.user_id)
                            await member.remove_roles(role)



def setup(bot):
    bot.add_cog(core(bot))
    print('cogs - `core` is loaded')
