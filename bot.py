import os

import DiscordUtils
import asyncpg
import psycopg2
import discord
from discord.ext import commands, ipc
from discord.ext.commands import when_mentioned_or
from tools.autocogs import AutoCogs
from dotenv import load_dotenv
load_dotenv(verbose=True)


class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        AutoCogs(self)
        self.remove_command("help")
        self.ipc = ipc.Server(self, secret_key=os.getenv('IPCSECRET'))  # create our IPC Server
        self.tracker = DiscordUtils.InviteTracker(self)
    async def on_ready(self):
        """Called upon the READY event"""
        await self.change_presence(status=discord.Status.online, activity=discord.Activity(name="@태시아 봇 도움 | OpenBetaTest중",
                                                                                               type=discord.ActivityType.playing))
        await self.tracker.cache_invites()
        print("Bot is ready.")

    async def on_invite_create(self,invite):
        await self.tracker.update_invite_cache(invite)

    async def on_guild_join(self,guild):
        await self.tracker.update_guild_cache(guild)

    async def on_invite_delete(self,invite):
        await self.tracker.remove_invite_cache(invite)

    async def on_guild_remove(self,guild):
        await self.tracker.remove_guild_cache(guild)

    async def on_member_join(self,member):
        inviter = await self.tracker.fetch_inviter(member)  # inviter is the member who invited
        tag = str(inviter).replace(f"{str(inviter)[:-5]}","")
        print(str(inviter)[:-5])
        print(tag)
        ID = discord.utils.get(self.get_all_members(), name=f"{str(inviter)[:-5]}", discriminator=tag[1:]).id
        print(ID)
        channel = member.guild.system_channel
        await channel.send(f"{member.mention}님! 어서오세요! - 이 초대는 <@{ID}>님이 생성한 초대링크로 입장하셨습니다.")
        """try:
            channel = member.guild.system_channel
            await channel.send(f"{member.mention}님! 어서오세요! - 이 초대는 <@{ID}>님이 생성한 초대링크로 입장하셨습니다.")
        except:
            channel = member.guild.get_channel(cid)
            await channel.send(f"{member.mention}님! 어서오세요! - 이 초대는 <@{ID}>님이 생성한 초대링크로 입장하셨습니다.")"""


    async def on_ipc_ready(self):
        """Called upon the IPC Server being ready"""
        print("Ipc is ready.")

    async def on_ipc_error(self, endpoint, error):
        """Called upon an error being raised within an IPC route"""
        print(endpoint, "raised", error)

    async def create_db_pool(self=None):
        MyBot.pg_con = await asyncpg.create_pool(user=os.getenv('DB_USER'), password=os.getenv('DB_PW'),
                                         database=os.getenv('DB_DB'), host=os.getenv('DB_HOST'))

def get_prefix(bot, message:discord.Message):
    conn_string = f"host={os.getenv('DB_HOST')} dbname ={os.getenv('DB_DB')} user={os.getenv('DB_USER')} password={os.getenv('DB_PW')}"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    cursor.execute(f'SELECT prefix FROM prefix WHERE guild = {str(message.guild.id)}::TEXT')
    try:
        prefix = cursor.fetchone()[0]
    except:
        prefix = 'ㅌ'
    conn.commit()
    return when_mentioned_or(prefix)(bot, message)

INTENTS = discord.Intents.default()
INTENTS.members = True
my_bot = MyBot(command_prefix=get_prefix, intents=INTENTS)


if __name__ == "__main__":
    my_bot.ipc.start()  # start the IPC Server
    my_bot.loop.run_until_complete(MyBot.create_db_pool())
    my_bot.run(os.getenv('DISCORD_BOT_TOKEN'))