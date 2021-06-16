import os
import asyncpg
import psycopg2
import requests
from PIL import Image, ImageDraw
import random
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

conn_string = f"host={os.getenv('DB_HOST')} dbname ={os.getenv('DB_DB')} user={os.getenv('DB_USER')} password={os.getenv('DB_PW')}"

class API:


    async def check_prefix(id):
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM prefix WHERE guild = %s",(str(id),))
        if cursor.fetchall() == []:
            conn.close()
            return False
        else:
            conn.close()
            return True

    async def check_ignore_lvl_mode(id):
        try:
            conn = psycopg2.connect(conn_string)
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM ig_guild WHERE guild = %s",(str(id),))
            if cursor.fetchall() == []:
                conn.close()
                return False
            else:
                conn.close()
                return True
        except psycopg2.Error as e:
            conn.commit()
            conn.close()

    async def get_prefix(id):
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM prefix WHERE guild = %s",(str(id),))
        res1 = cursor.fetchone()
        if res1 == None:
            conn.close()
            return {"error":True,"msg":"none"}
        else:
            conn.close()
            return {"error":False,"msg":str(res1[1])}

    async def edit_prefix(id,data):
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        res = await API.check_prefix(id=id)
        if res == False:
            try:
                cursor.execute(f"INSERT INTO prefix(guild,prefix) VALUES(%s,%s)",(str(id),str(data)))
                conn.commit()
                conn.close()
                return {"error":False,"msg":f"정상적으로 프리픽스를 ' {data} '로 변경하였습니다.","state":"success"}
            except:
                conn.close()
                return {"error": True, "msg": f"프리픽스를 변경하는 도중 알수없는 문제로 실패하였습니다.", "state": "danger"}

        else:
            try:
                cursor.execute(f"UPDATE prefix SET prefix=%s WHERE guild = %s",(data,str(id)))
                conn.commit()
                conn.close()
                return {"error": False, "msg": f"정상적으로 프리픽스를 ' {data} '로 변경하였습니다.", "state": "success"}
            except:
                conn.close()
                return {"error": True, "msg": f"프리픽스를 변경하는 도중 알수없는 문제로 실패하였습니다.", "state": "danger"}

    async def edit_lvl_color(user,guild,data):
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE level SET color=%s WHERE guild = %s AND _user = %s", (data, str(guild),str(user)))
            conn.commit()
            conn.close()
            return {"error": False, "msg": f"정상적으로 색상을 ' {data} '로 변경하였습니다.", "state": "success"}
        except:
            conn.close()
            return {"error": True, "msg": f"색상을 변경하는 도중 알수없는 문제로 실패하였습니다.", "state": "danger"}

    async def get_color_code(user,guild):
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM level WHERE _user = %s and guild = %s", (str(user),
                                       str(guild)))
            res1 = cursor.fetchone()
            conn.close()
            return {"error":False,"item":res1[4]}
        except:
            conn.close()
            return {"error": True}

    async def get_count_command(guild):
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM command_log WHERE guild = %s", (str(guild),))
            res1 = cursor.fetchall()
            if res1 == []:
                return {"error": False, "item": '0'}
            num = 0
            for i in res1:
                num += 1
            conn.close()
            return {"error":False,"item":str(num)}
        except:
            conn.close()
            return {"error": True}


    async def save_lvl_card(user,guild,name,avater):
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        try:
            im = Image.open('./api/source/progress.png').convert('RGB')
            draw = ImageDraw.Draw(im)
            cursor.execute("SELECT * FROM level WHERE _user = %s and guild = %s", (str(user),
                                       str(guild)))
            res1 = cursor.fetchone()
            print(res1)
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
            im.save('./api/source/result.png', quality=100)

            progress = Image.open('./api/source/result.png').convert('RGB')
            bg = Image.open('./api/source/source3.png').convert('RGB')
            merged = Image.new('L', (934, 282)).convert('RGB')

            merged.paste(bg)
            merged.paste(progress, (250, 170))
            merged.save('./api/source/final.png', quality=100)

            img = Image.open('./api/source/final.png').convert('RGB')
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype('./api/source/fonts/NanumSquareRoundL.ttf', 50)
            font2 = ImageFont.truetype('./api/source/fonts/NanumSquareRoundL.ttf', 25)
            draw.text((310, 120), f"{name}", (255, 255, 255), font=font)
            draw.text((740, 40), f"{res1[3]}", color,
                      font=ImageFont.truetype('./api/source/fonts/NanumSquareRoundB.ttf', 60))
            draw.text((820, 40), f".LV", color,
                      font=ImageFont.truetype('./api/source/fonts/NanumSquareRoundB.ttf', 60))
            draw.text((550, 220), f"{res1[2]}/{exp[int(res1[3]) - 1]} XP; 달성도: {str(round(percent, 2))}%", (255, 255, 255),
                      font=font2)
            img.save('./api/source/sample-out.png', quality=100)
            im1 = Image.open("./api/source/sample-out.png")
            with requests.get(avater) as r:
                img_data = r.content
            with open('./api/source/profile.jpg', 'wb') as handler:
                handler.write(img_data)
            im2 = Image.open("./api/source/profile.jpg")
            size = 180

            im2 = im2.resize((size, size), resample=0)
            # Creates the mask for the profile picture
            mask_im = Image.new("L", im2.size, 0)
            draw = ImageDraw.Draw(mask_im)
            draw.ellipse((0, 0, size, size), fill=255)

            mask_im.save('./api/source/mask_circle.png', quality=100)
            back_im = im1.copy()
            back_im.paste(im2, (52, 50), mask_im)
            code = random.randint(1000,99999)
            print(code)
            back_im.save(f'./static/images/userlvl-{code}.png', quality=100)
            conn.close()
            return {"error":False,"code":str(code)}
        except:
            conn.close()
            return {"error":True}

    async def change_ignore_lvl_guild(guild,name):
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        try:
            res = await API.check_ignore_lvl_mode(id=guild)
            print(res)
            if res == False:
                cursor.execute("INSERT INTO ig_guild(guild,name) VALUES(%s,%s)", (str(guild),str(name)))
                conn.commit()
                conn.close()
                return {"error": False, "msg": f"정상적으로 레벨링 모드를 비활성화하였습니다.", "state": "success"}
            else:
                cursor.execute("DELETE FROM ig_guild WHERE guild=%s", (str(guild),))
                conn.commit()
                conn.close()
                return {"error": False, "msg": f"정상적으로 레벨링 모드를 활성화하였습니다.", "state": "success"}
        except:
            conn.close()
            return {"error": True, "msg": f"레벨링 모드를 변경하는 도중 알수없는 에러로 실패하였습니다.", "state": "danger"}

    async def get_ignore_lvl_channel(id):
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM ig_channel WHERE guild = %s", (str(id),))
            it = cursor.fetchall()
            if it == []:
                conn.close()
                return {"error":True}
            else:
                conn.close()
                return {"error":False,"item":it}
        except psycopg2.Error as e:
            conn.commit()
            conn.close()

    async def get_ignore_lvl_role(id):
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        print(id)
        try:
            cursor.execute("SELECT * FROM ig_role WHERE guild = %s", (str(id),))
            it = cursor.fetchall()
            if it == []:
                conn.close()
                return {"error":True}
            else:
                print(f"12 - {it}")
                conn.close()
                return {"error":False,"item":it}
        except psycopg2.Error as e:
            conn.commit()
            conn.close()

    async def get_ignore_lvl_channel_row(gid,cid):
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ig_channel WHERE guild = %s AND channel = %s", (str(gid),str(cid)))
        if cursor.fetchone() == None:
            conn.close()
            return {"error":True}
        else:
            it = cursor.fetchone()
            conn.close()
            return {"error":False,"item":it}

    async def get_ignore_lvl_role_row(gid,rid):
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ig_role WHERE guild = %s AND roleid = %s", (str(gid),str(rid)))
        if cursor.fetchone() == None:
            conn.close()
            return {"error":True}
        else:
            it = cursor.fetchone()
            conn.close()
            return {"error":False,"item":it}

    async def change_ignore_lvl_channel(guild,channel,cname):
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        try:
            res = await API.get_ignore_lvl_channel_row(gid=guild,cid=channel)
            if res["error"] == True:
                cursor.execute("INSERT INTO ig_channel(guild,channel,name) VALUES(%s,%s,%s)", (str(guild), str(channel),str(cname)))
                conn.commit()
                conn.close()
                return {"error": False, "msg": f"정상적으로 ' {cname} '(을)를 무시하였습니다.", "state": "success"}
            else:
                if res["item"][1] == channel:
                    conn.close()
                    return {"error": True, "msg": f"' {cname} '(은)는 이미 무시된 채널입니다.", "state": "danger"}
                else:
                    cursor.execute("INSERT INTO ig_channel(guild,channel) VALUES($s,%s)", (str(guild), str(channel)))
                    conn.commit()
                    conn.close()
                    return {"error": False, "msg": f"정상적으로 ' {cname} '(을)를 무시하였습니다.", "state": "success"}
        except:
            conn.close()
            return {"error": True, "msg": f"레벨링 설정을 수정하는 도중 알수없는 에러로 실패하였습니다.", "state": "danger"}

    async def delete_ignore_lvl_channel(guild,channel):
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM ig_channel WHERE guild = %s AND channel=%s", (str(guild), str(channel)))
            conn.commit()
            conn.close()
            return {"error": False, "msg": f"정상적으로 삭제하였습니다.", "state": "success"}
        except:
            conn.close()
            return {"error": True, "msg": f"레벨링 설정을 수정하는 도중 알수없는 에러로 실패하였습니다.", "state": "danger"}

    async def change_ignore_lvl_role(guild,role,rname):
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        try:
            res = await API.get_ignore_lvl_role_row(gid=guild,rid=role)
            print(res)
            if res["error"] == True:
                cursor.execute("INSERT INTO ig_role(guild,roleid,name) VALUES(%s,%s,%s)", (str(guild), str(role),str(rname)))
                conn.commit()
                conn.close()
                return {"error": False, "msg": f"정상적으로 ' @{rname} '(을)를 무시하였습니다.", "state": "success"}
            else:
                if res["item"][1] == role:
                    conn.close()
                    return {"error": True, "msg": f"' {rname} '(은)는 이미 무시된 역할입니다.", "state": "danger"}
                else:
                    cursor.execute("INSERT INTO ig_role(guild,roleid) VALUES(%s,%s)", (str(guild), str(rname)))
                    conn.commit()
                    conn.close()
                    return {"error": False, "msg": f"정상적으로 ' {rname} '(을)를 무시하였습니다.", "state": "success"}
        except:
            conn.close()
            return {"error": True, "msg": f"레벨링 설정을 수정하는 도중 알수없는 에러로 실패하였습니다.", "state": "danger"}

    async def delete_ignore_lvl_role(guild,role):
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM ig_role WHERE guild = %s AND roleid=%s", (str(guild), str(role)))
            conn.commit()
            conn.close()
            return {"error": False, "msg": f"정상적으로 삭제하였습니다.", "state": "success"}
        except:
            conn.close()
            return {"error": True, "msg": f"레벨링 설정을 수정하는 도중 알수없는 에러로 실패하였습니다.", "state": "danger"}


