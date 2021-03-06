import traceback
from datetime import datetime
import random

import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv(verbose=True)
import asyncio
import random
import hcskr
from utils.execption import PermError
class core(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.call = []
        self.join = []
        self.company = ["fmsg", "rg", "sdev", "ccn", "gpm", "otl"]
        self.snipe_message_author = {}
        self.snipe_message_content = {}
        self.snipe_message_author_avatar = {}
        self.stock=self.bot.loop.create_task(self.stock_loop())
        self.hcs=self.bot.loop.create_task(self.hcs_loop())
        self.black=self.bot.loop.create_task(self.black_loop())

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        self.snipe_message_author[message.channel.id] = message.author
        self.snipe_message_author_avatar[message.channel.id] = message.author.avatar_url
        self.snipe_message_content[message.channel.id] = message.content
        await asyncio.sleep(60)
        del self.snipe_message_author[message.channel.id]
        del self.snipe_message_content[message.channel.id]
        del self.snipe_message_author_avatar[message.channel.id]

    @commands.command(name='snipe')
    async def snipe(self, ctx):
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
                    updown = random.randint(1,2) # 1??? ??????,2??? ??????
                    price = random.randint(100,3000)
                    if updown == 1:
                        pr = await self.bot.pg_con.fetchrow("SELECT price FROM stock WHERE company_name = $1", i)
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
                    updown = random.randint(1,2) # 1??? ??????,2??? ??????
                    price = random.randint(100,3000)
                    if updown == 1:
                        await self.bot.pg_con.execute("UPDATE stock SET price=price-$1 WHERE company_name = $2",price,i)
                        await self.bot.pg_con.execute("UPDATE stock SET down_up=$1 WHERE company_name = $2", "down", i)
                        await self.bot.pg_con.execute("UPDATE stock SET down_up_value=$1 WHERE company_name = $2", price, i)
                    else:
                        await self.bot.pg_con.execute("UPDATE stock SET price=price+$1 WHERE company_name = $2", price, i)
                        await self.bot.pg_con.execute("UPDATE stock SET down_up=$1 WHERE company_name = $2", "up", i)
                        await self.bot.pg_con.execute("UPDATE stock SET down_up_value=$1 WHERE company_name = $2", price, i)

    async def black_loop(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            await asyncio.sleep(60)
            black=await self.bot.pg_con.fetch("SELECT * FROM black_list")
            for i in black:
                date = datetime.strptime(i[1], '%Y-%m-%d %H:%M')

                if date < datetime.now():
                    try:
                        await self.bot.pg_con.execute("DELETE FROM black_list WHERE user_id=$1",i[0])
                        black_em = discord.Embed(title="??????????????????.",
                                              description=f"""
??????????????????? `{await self.bot.fetch_user(int(i[0]))}`?????? ????????????????????? ????????? ?????? ??????DM??? ?????????????????????.\n

???????????? ?????? ???????????? ??????????????????????????????.

???????????????.
""")
                        await (await self.bot.fetch_user(int(i[0]))).send(embed=black_em)
                        await self.bot.get_user(281566165699002379).send(f"`{await self.bot.fetch_user(int(i[0]))}`was deleted from black list")
                    except Exception as e:
                        await self.bot.get_user(281566165699002379).send(f"```py\n{e}\n```")



    async def hcs_loop(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            await asyncio.sleep(60)
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            print("hcs loop Current Time =", current_time)
            if current_time == "07:00":
                delay = random.randint(1,30)
                await self.bot.get_channel(856531776863076402).send(f"????????????????????? `{delay}`??? ?????? ???????????????.")
                await asyncio.sleep(60*delay)
                await self.bot.get_channel(856531776863076402).send(f"??????????????????????????????.")
                datas = await self.bot.pg_con.fetch("SELECT * FROM hcs")
                num = 0
                suc = 0
                fail = 0
                for i in datas:
                    print(i)
                    if not i[2] =="true":
                        num +=1
                        prc = await hcskr.asyncTokenSelfCheck(i[1])
                        if prc["code"] == "SUCCESS":
                            suc +=1
                            await self.bot.pg_con.execute("UPDATE hcs SET status=$1 WHERE user_id=$2",
                                                          "true", i[0])
                            await self.bot.pg_con.execute("UPDATE hcs SET times=$1 WHERE user_id=$2",
                                                          str(datetime.now()), i[0])
                            await self.bot.get_channel(856531776863076402).send(f"**#{num}**. "+prc["message"])
                        else:
                            fail +=1
                            await self.bot.get_channel(856531776863076402).send(f"**#{num}**. "+prc["message"])
                    else:
                        pass
                await self.bot.get_channel(856531776863076402).send(f"??????????????? - {num}\n?????? - {suc}\n?????? - {fail}")
                await asyncio.sleep(43200)
                #await asyncio.sleep(30)
                await self.bot.get_channel(856531776863076402).send(f"?????????????????????????????????..")
                datas1 = await self.bot.pg_con.fetch("SELECT * FROM hcs")
                num1=0
                for i in datas1:
                    num1 +=1
                    await self.bot.pg_con.execute("UPDATE hcs SET status=$1 WHERE user_id=$2",
                                                      "false", i[0])
                    await self.bot.get_channel(856531776863076402).send(f"**#{num1}**?????????????????????.")
                await self.bot.get_channel(856531776863076402).send(f"????????????????????????????????????!")



    def cog_unload(self):
        self.stock.cancel()
        self.hcs.cancel()
        self.black.cancel()
        print("TEST")

    @commands.Cog.listener()
    async def on_command_error(self,ctx: commands.Context, error: Exception):
        if isinstance(error, PermError.BlacklistedUser):
            await ctx.reply(f"You are black list user.(????????? ??????????????????????????????.)\n```py\n{type(error)}\n\n{'*****'*5}\n\n{traceback.print_exc()}\n```")
        elif isinstance(error, PermError.NotOwnerUser):
            await ctx.reply(f"You are not owner.(????????? ????????? ????????????.)\n```py\n{type(error)}\n\n{'*****'*5}\n\n{traceback.print_exc()}\n```")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            pass
        else:
            res1 = await self.bot.pg_con.fetch("SELECT * FROM rr_conf WHERE guild_id = $1", payload.guild_id)
            if res1 == []:
                return
            for i in res1:
                if payload.message_id != i[2]:
                    res3 = await self.bot.pg_con.fetchrow("SELECT * FROM ticket_conf WHERE guild_id = $1",
                                                          payload.guild_id)
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
                        res5 = await self.bot.pg_con.fetchrow(
                            "SELECT * FROM ticket_value WHERE guild_id = $1 AND channel_id = $2",
                            guild_id, channel_id)
                        try:
                            if message_id == res5[2] and guild_id == res5[0] and channel_id == res5[
                                1] and payload.emoji.name == "????" and user.bot == False:
                                message = await channel.fetch_message(message_id)
                                await message.remove_reaction("????", user)
                                if user_id in self.call:
                                    await channel.send("?????? ?????????????????????.")
                                    return
                                self.call.append(user_id)
                                role = guild.get_role(res3[4])
                                for member in guild.members:
                                    if role in member.roles:
                                        em = discord.Embed(title="???????????? ??????",
                                                           description=f"?????? `{guild}`??? `{channel}`?????? `{user}`?????? ??????????????????.")
                                        await member.send(embed=em)
                                await channel.send("??????????????? ?????????????????????.")
                            if message_id == res5[2] and guild_id == res5[0] and channel_id == res5[
                                1] and payload.emoji.name == "????":
                                embed = discord.Embed(
                                    title="?????? ?????? ??????!",
                                    description=f"``??????? {user.name}?????? ???????????? ????????? ??????????????? 10?????? ???????????????.``",
                                    color=0xf7fcfd)

                                await channel.send(embed=embed)
                                await asyncio.sleep(10)
                                await channel.delete()
                                log_channel = self.bot.get_channel(res3[2])
                                embed = discord.Embed(
                                    title="?????? ?????? ??????",
                                    description=f"`{channel}`??? {user.display_name}?????? ?????? ?????????????????????.",
                                    timestamp=datetime.utcnow(),
                                    color=0xf7fcfd)
                                await log_channel.send(embed=embed)
                                try:
                                    self.call.remove(str(user_id))
                                except:
                                    pass
                                await self.bot.pg_con.execute("DELETE FROM ticket_value WHERE channel_id = $1",
                                                              channel_id)
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
                            1] and payload.emoji.name == "????":
                            message = await channel.fetch_message(message_id)
                            await message.remove_reaction("????", user)
                            res4 = await self.bot.pg_con.fetchrow("SELECT * FROM ticket_value WHERE guild_id = $1",
                                                                  guild_id)
                            if not res4 == None:
                                if res4[3] == user_id:
                                    return await channel.send(
                                        f"<@{user_id}>???, ?????? ???????????? ????????? ????????????.\n???????????? ?????? - <#{res4[1]}>\n????????????????????? ?????? ????????? ????????? ?????? ??????????????????.",
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
                            embed = discord.Embed(title="????????? ???????????????????", color=0xf7fcfd)
                            embed.add_field(name="???? ????????? ??????",
                                            value="```15??? ?????? ???????????? ???????????? ???????????? ??????????????????.\n(????????? ????????? ???????????? ??????????????? ????????? ????????? ??????????????? ??????????????????????????????.)```",
                                            inline=False)
                            embed.add_field(name="???? ?????? ??????",
                                            value="```??????????????? ????????? ??????????????? ??????????????????. 10????????? ????????? ???????????????.```",
                                            inline=False)

                            await ticket_channel_name.send(f"<@&{res3[4]}>")
                            await ticket_channel_name.send(f"<@{user_id}>")
                            ticket_channel_message = await ticket_channel_name.send(embed=embed)
                            await ticket_channel_message.add_reaction("????")
                            await ticket_channel_message.add_reaction("????")
                            await self.bot.pg_con.execute(
                                "INSERT INTO ticket_value(guild_id,channel_id,message_id,user_id) VALUES($1,$2,$3,$4)",
                                guild_id,
                                ticket_channel_id,
                                ticket_channel_message.id,
                                user_id)
                else:
                    res2 = await self.bot.pg_con.fetch("SELECT * FROM rr_value")
                    for a in res2:
                        aa = str(a[1]).replace(" ", "")
                        if aa.startswith("<:"):
                            if f"<:{payload.emoji.name}:{payload.emoji.id}>" == aa and payload.message_id == i[
                                2] and payload.guild_id == a[2]:
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
        if res1 == []:
            return
        for i in res1:
            if payload.message_id != i[2] and payload.channel_id != i[1] and payload.guild_id != i[0]:
                return
            else:
                if payload.guild_id == i[0] and payload.message_id == i[2]:
                    res2 = await self.bot.pg_con.fetch("SELECT * FROM rr_value")
                    for a in res2:
                        aa = str(a[1]).replace(" ", "")
                        if aa.startswith("<:"):
                            if f"<:{payload.emoji.name}:{payload.emoji.id}>" == aa and payload.message_id == i[
                                2] and payload.guild_id == a[2]:
                                guild = self.bot.get_guild(payload.guild_id)
                                role = guild.get_role(int(a[0]))
                                member = guild.get_member(payload.user_id)
                                await member.remove_roles(role)
                        elif payload.emoji.name == aa and payload.message_id == i[2] and payload.guild_id == a[2]:
                            guild = self.bot.get_guild(payload.guild_id)
                            role = guild.get_role(int(a[0]))
                            member = guild.get_member(payload.user_id)
                            await member.remove_roles(role)

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
            em = discord.Embed(title="????????????", description=f"`{member}` | `{member.id}`\n???????????? ????????????????????????.",
                               colour=discord.Colour.red())
            await member.ban()
            await self.bot.get_channel(es3[1]).send(embed=em)
            ban = discord.Embed(title="???????????? ?????? ?????????",
                                description=f"???????????????.\n???????????? ????????? ???????????? `{member.guild.name}`?????? ??????????????? ?????? ????????????????????????.\n????????? ????????? ?????? ???????????? ???????????????.")
            await member.send(embed=ban)

def setup(bot):
    bot.add_cog(core(bot))
    print('cogs - `core` is loaded')
