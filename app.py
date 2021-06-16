import asyncio
import os


from api.api import API
from quart import Quart, redirect, url_for, render_template, request, flash
from quart_discord import DiscordOAuth2Session, requires_authorization, Unauthorized
from discord.ext import ipc
from dotenv import load_dotenv
load_dotenv(verbose=True)

app = Quart(__name__)
ipc_client = ipc.Client(secret_key=os.getenv('IPCSECRET'))
app.url_map.host_matching = False
app.secret_key = os.getenv('APPSECRET')# secret_key must be the same as your server
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = os.getenv('OAUTHLIB_INSECURE_TRANSPORT')
app.config["SECRET_KEY"] = os.getenv('APPSECRET')
app.config["DISCORD_CLIENT_ID"] = os.getenv('DISCORD_CLIENT_ID')    # Discord client ID.
app.config["DISCORD_CLIENT_SECRET"] = os.getenv('DISCORD_CLIENT_SECRET')             # Discord client secret.
app.config["DISCORD_REDIRECT_URI"] = os.getenv('DISCORD_REDIRECT_URI')                 # URL to your callback endpoint.
app.config["DISCORD_BOT_TOKEN"] = os.getenv('DISCORD_BOT_TOKEN')                    # Required to access BOT resources.

discord = DiscordOAuth2Session(app)

files = []



@app.route("/login")
async def login():
    return await discord.create_session(scope=['identify','guilds'])

@app.route("/invite/<int:id>")
async def invite(id):
    return redirect(f'https://discord.com/api/oauth2/authorize?client_id=766932365426819092&permissions=8&scope=bot&guild_id={id}&disable_guild_select=true')

@app.route("/logout")
async def logout():
    discord.revoke()
    return redirect(url_for('index'))


@app.route("/callback")
async def callback():
    await discord.callback()
    return redirect(url_for("select"))

@app.errorhandler(Unauthorized)
async def redirect_unauthorized(e):
    return redirect(url_for("login"))


@app.route("/")
async def index():
    return await render_template('index_nolog.html',log=False)

@app.route('/select')
@requires_authorization
async def select():
    users = await discord.fetch_user()
    guild = await ipc_client.request('get_guilds',us=users.id)
    guilds = await discord.fetch_guilds()
    bot = []
    nonbot = []
    for i in guilds:
        for ch in guild:
            if i.id == ch:
                bot.append(i.id)
            elif not i.id == ch:
                nonbot.append(i.id)
    clean = set(nonbot)
    nonbot = list(clean)
    nobot = []
    for i in nonbot:
        if not i in bot:
            nobot.append(i)
    return await render_template('select.html', user=users, render_guild=guilds,bots=bot,nobots=nobot,server=False)

@app.route('/dashboard/<string:id>')
@requires_authorization
async def dashboard(id):
    users = await discord.fetch_user()
    info = await ipc_client.request('get_guild_info',id=id)
    perm = await ipc_client.request('check_guild_permission',id=id)
    prefix = await API.get_prefix(id)
    count = await API.get_count_command(guild=id)
    print(count)
    members = await ipc_client.request('get_members',id=id)
    if prefix['error'] == True:
        return await render_template('index.html', user=users, name=info["name"], icon=info["icon"], perm=perm['perm'],
                                     role=perm['role'], id=id,prefix='ㅌ',counts=count,member=members)
    return await render_template('index.html',user=users,name=info["name"],icon=info["icon"],perm=perm['perm'],role=perm['role'],id=id,prefix=prefix['msg'],counts=count,member=members)

@app.route('/lvlcard/<string:id>')
@requires_authorization
async def dashboard_lvl(id):
    if not files == []:
        for i in files:
            print(i)
            os.remove(f"./static/images/{i}")
        files.clear()
    print(files)
    users = await discord.fetch_user()
    info = await ipc_client.request('get_guild_info', id=id)
    card = await API.save_lvl_card(user=users.id,guild=id,name=f"{users.name}#{users.discriminator}",avater=users.avatar_url or users.default_avatar_url)
    code = await API.get_color_code(user=users.id,guild=id)
    print(card)
    files.append(f"userlvl-{card['code']}.png")
    if card["error"] == False:
        return await render_template('card.html', user=users, name=info["name"], icon=info["icon"], id=id,code=card["code"],color=code["item"])
    await flash('레벨카드를 생성하는 도중에 에러가 발생하여 실패하였습니다.','danger')
    return redirect(f'/dashboard/{id}')

@app.route('/dashboard/<string:id>/config/lvl')
async def config_lvl(id):
    users = await discord.fetch_user()
    info = await ipc_client.request('get_guild_info', id=id)
    channels = await ipc_client.request('get_all_channels',id=id)
    roles = await ipc_client.request('get_all_roles', id=id)
    lvl = await API.check_ignore_lvl_mode(id=id)
    lvl_channel = await API.get_ignore_lvl_channel(id=id)
    lvl_role = await API.get_ignore_lvl_role(id=id)
    print(lvl_channel)
    print(f"11 - {lvl_role}")
    return await render_template('config_lvl.html', user=users, name=info["name"], icon=info["icon"],id=id,channels=channels,roles=roles,mode=lvl,igchannel=lvl_channel,igrole=lvl_role)

######################################################## A P I ##################################################

@app.route('/api/senddm/<string:id>',methods=['POST'])
async def api_send_dm(id):
    if request.method == 'POST':
        req = await request.form
        res = await ipc_client.request('send_dm', value=req['text'])
        await flash(res['msg'], res['state'])
        return redirect(f'/dashboard/{id}')

@app.route('/api/prefix/<string:id>',methods=["POST"])
async def api_prefix(id):
    if request.method == 'POST':
        req = await request.form
        res = await API.edit_prefix(id,req['prefix'])
        await flash(res['msg'],res['state'])
        return redirect(f'/dashboard/{id}')

@app.route('/api/lvlcard/<string:id>/<string:usid>',methods=["POST"])
async def api_lvlcard_card(id,usid):
    if request.method == 'POST':
        req = await request.form
        print(req)
        res = await API.edit_lvl_color(user=usid,guild=id,data=req['color'])
        await flash(res['msg'],res['state'])
        return redirect(f'/lvlcard/{id}')

@app.route('/api/changelvl/<string:id>',methods=["POST"])
async def api_chang_lvl_alert(id):
    if request.method == 'POST':
        info = await ipc_client.request('get_guild_info', id=id)
        res = await API.change_ignore_lvl_guild(guild=id,name=info['name'])
        await flash(res['msg'], res['state'])
        return redirect(f'/dashboard/{id}/config/lvl')

@app.route('/api/changelvl/channel/<string:id>',methods=["POST"])
async def api_chang_lvl_channel(id):
    if request.method == 'POST':
        req = await request.form
        print(req)
        cname = await ipc_client.request('get_channels',id=req['channel'])
        res = await API.change_ignore_lvl_channel(guild=id,channel=req['channel'],cname=cname)
        await flash(res['msg'], res['state'])
        return redirect(f'/dashboard/{id}/config/lvl')

@app.route('/api/deletelvl/channel/<string:id>/<string:cid>',methods=["POST"])
async def api_del_lvl_channel(id,cid):
    if request.method == 'POST':
        res = await API.delete_ignore_lvl_channel(guild=id,channel=cid)
        await flash(res['msg'], res['state'])
        return redirect(f'/dashboard/{id}/config/lvl')

@app.route('/api/changelvl/role/<string:id>',methods=["POST"])
async def api_chang_lvl_role(id):
    if request.method == 'POST':
        req = await request.form
        print(req)
        rname = await ipc_client.request('get_roles',id=req['role'],gid=id)
        print(rname)
        res = await API.change_ignore_lvl_role(guild=id,role=req['role'],rname=rname)
        await flash(res['msg'], res['state'])
        return redirect(f'/dashboard/{id}/config/lvl')

@app.route('/api/deletelvl/role/<string:id>/<string:rid>',methods=["POST"])
async def api_del_lvl_role(id,rid):
    if request.method == 'POST':
        res = await API.delete_ignore_lvl_role(guild=id,role=rid)
        await flash(res['msg'], res['state'])
        return redirect(f'/dashboard/{id}/config/lvl')

if __name__ == "__main__":
    app.run(host=os.getenv('HOST'),port=os.getenv('PORT'),debug=os.getenv('DEBUG'))