from discord.ext import commands, ipc
import discord

class IpcRoutes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @ipc.server.route()
    async def get_guilds(self,data):
        print(f'{data.us}')
        li = []
        guild = self.bot.guilds
        for i in guild:
            li.append(i.id)

        return li

    @ipc.server.route()
    async def check_guild_permission(self,data):
        perm = self.bot.get_guild(int(data.id)).me.top_role.permissions.administrator
        role = self.bot.get_guild(int(data.id)).me.top_role
        return {"perm":perm,"role":str(role)}

    @ipc.server.route()
    async def get_guild_info(self,data):
        info = self.bot.get_guild(int(data.id))
        return {"name":str(info.name),"icon":str(info.icon_url)}

    @ipc.server.route()
    async def get_channels(self, data):
        name = self.bot.get_channel(int(data.id))
        return str(name)

    @ipc.server.route()
    async def get_roles(self, data):
        name = self.bot.get_guild(int(data.gid)).get_role(int(data.id))
        return str(name)

    @ipc.server.route()
    async def get_all_channels(self,data):
        li = {}
        guild = self.bot.get_guild(int(data.id))
        for channel in guild.channels:
            li[channel.name] = str(channel.id)
        return li

    @ipc.server.route()
    async def get_all_roles(self, data):
        li = {}
        guild = self.bot.get_guild(int(data.id))
        for role in guild.roles:
            li[role.name] = str(role.id)
        return li

    @ipc.server.route()
    async def get_members(self,data):
        guild = self.bot.get_guild(int(data.id))
        true_member_count = len([m for m in guild.members if not m.bot])
        return str(true_member_count)

    @ipc.server.route()
    async def send_dm(self,data):
        try:
            em = discord.Embed(title='대시보드 문의',description=str(data.value))
            user = await self.bot.fetch_user(281566165699002379)
            await user.send(embed=em)
            return {"error":False,"msg":"정상적으로 문의되었습니다. 욕설이나 비방 및 운영자에게 피해를 입힐수있는 내용을 전송할경우 블랙리스트대상이 되오니 주의바랍니다.","state":"success"}
        except:
            return {"error": True, "msg": "문의내용을 발송하는도중 알수없는 에러가 발생해 실패하였습니다.","state":"danger"}

def setup(bot):
    bot.add_cog(IpcRoutes(bot))
    print('cogs - `backend` is loaded')