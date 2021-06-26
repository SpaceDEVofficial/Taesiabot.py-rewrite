import os
import asyncpg
from discord.ext import commands
#from asyncpg import connection
import discord
import datetime
from dpytools.menus import multichoice
import laftel
from dotenv import load_dotenv
load_dotenv(verbose=True)
class ani(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="애니")
    async def ani_search(self,ctx,title=None):
        """
        애니 검색 기능입니다.
        """
        if title == None:
            return await ctx.reply("검색할 애니 제목을 입력해주세요!")
        emd = discord.Embed(title="<a:loading:854164770327232522>검색중",description="검색중입니다. 잠시만 기다려주세요. \n만일 작동이 안될시 `(Prefix) + 문의 +문의내용`으로 문의하시기 바랍니다.")
        msg = await ctx.reply(embed=emd)
        anis = await laftel.searchAnime(title)
        titles = []
        ani_data = {}
        for anii in anis:
            titles.append(anii.name)
            ani_data[anii.name] = anii.id
        print(ani_data)
        emd = discord.Embed(title="<a:loading:854164770327232522>검색완료!",
                            description="검색이 완료되었습니다. 아래의 목록중 원하는 애니의 번호의 반응을 클릭하세요. \n만일 작동이 안될시 `(Prefix) + 문의 +문의내용`으로 문의하시기 바랍니다.")
        await msg.edit(embed=emd)
        choice = await multichoice(ctx, titles)
        if choice == None:
            await msg.delete()
        emd = discord.Embed(title="<a:loading:854164770327232522>정보 불러오는 중",
                            description="정보를 불러오는 중입니다. 잠시만 기다려주세요. \n만일 작동이 안될시 `(Prefix) + 문의 +문의내용`으로 문의하시기 바랍니다.")
        await msg.edit(embed=emd)
        datas = await laftel.getAnimeInfo(ani_data[choice])
        ended = None
        awards = None
        content_rating = None
        viewable = None
        genres= None
        tags = None
        air_year_quarter = None
        air_day =None
        avg_rating = None
        view_all = None
        view_male = None
        view_female = None

        if datas.ended == True:
            ended = "<a:no:791451208275066910> 완결"
        else:
            ended = "<a:yes:791451388639051816> 미완결"

        if datas.awards != []:
            awards = datas.awards
        else:
            awards = "<a:no:791451208275066910> 정보 없음"

        if datas.content_rating == "성인 이용가":
            content_rating = "🔞 성인 이용가"
        else:
            content_rating = datas.content_rating

        if datas.viewable == True:
            viewable = "<a:yes:791451388639051816> 시청가능"
        else:
            viewable = "<a:no:791451208275066910> 시청불가"

        genres = datas.genres
        tags = datas.tags
        air_year_quarter = f"`{datas.air_year_quarter}`"
        if datas.air_day == None:
            air_day = "<a:no:791451208275066910> 정보가 없거나 방영종료입니다."
        else:
            air_day = f"`{datas.air_day}`"

        avg_rating ="`"+ str(datas.avg_rating)[:3] + "` 점"
        view_all = f"`{int(datas.view_male) + int(datas.view_female)}` 회"
        view_male = f"`{datas.view_male}` 명"
        view_female = f"`{datas.view_female}` 명"

        em = discord.Embed(title=f"** **",description=f"""
[ 줄거리 ]
`{datas.content}`

[ 별점 ]
{avg_rating}

[ 방영 분기 ]
{air_year_quarter}

[ 방영일 ]
{air_day}

[ 조회수(남/여) ]
{view_all}({view_male}/{view_female})

""")
        em.add_field(name="라프텔 태그",value=tags,inline=False)
        em.add_field(name="애니 상 목록", value=awards, inline=False)
        em.add_field(name="기본 태그",value=genres,inline=False)
        em.add_field(name="시청 가능 연령",value=content_rating,inline=False)
        em.add_field(name="완결 여부", value=ended, inline=False)
        em.add_field(name="라프텔 시청 가능 여부",value=viewable,inline=False)
        em.add_field(name="라프텔 태그",value=tags,inline=False)
        em.set_thumbnail(url = datas.image)
        em.set_author(name=f"{datas.name}(ID = {datas.id} ) 보러가기",url=datas.url,icon_url=datas.image)
        await msg.edit(embed=em)




def setup(bot):
    bot.add_cog(ani(bot))
    print('cogs - `ani` is loaded')
