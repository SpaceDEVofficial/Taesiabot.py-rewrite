import os
import asyncpg
from discord.ext import commands
#from asyncpg import connection
import discord
import datetime
from dpytools.menus import multichoice
import json
import random
from dotenv import load_dotenv
load_dotenv(verbose=True)


class Quiz(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="퀴즈")
    async def quiz(self,ctx):
        while True:
            with open('./quiz_data/quiz.json', 'r',encoding='UTF8') as f:
                quiz = json.load(f)

            theme = quiz['theme']
            em = discord.Embed(title="주제 선택")
            #msg = await ctx.reply(embed=em)
            theme_choice = await multichoice(ctx, theme,base_embed=em)
            if theme_choice == None:
                break
            quest = quiz["quiz-Q"][theme_choice]
            q_show = random.choice(quest)
            q_show_qq = quiz['quiz-show'][q_show]
            em = discord.Embed(title=q_show)
            #await msg.edit(embed=em)
            q_show_choice = await multichoice(ctx, q_show_qq,base_embed=em)
            if q_show_choice == None:
                break
            qns = quiz["quiz-a"][q_show]
            if q_show_choice == qns:
                em = discord.Embed(title="결과!", description="정답!\n( 문제 출제 가능합니다. [링크](https://github.com/SpaceDEVofficial/Taesia-Bot-quiz) )")
                await ctx.reply(embed=em,delete_after=15)
                #await msg.edit(embed=em)
            else:
                em = discord.Embed(title="결과!", description="오답!\n( 문제 출제 가능합니다. [링크](https://github.com/SpaceDEVofficial/Taesia-Bot-quiz) )")
                await ctx.reply(embed=em,delete_after=15)
                #await msg.edit(embed=em)
        em = discord.Embed(title="퀴즈 게임 취소!", description="퀴즈 게임을 취소하셨습니다.\n( 문제 출제 가능합니다. [링크](https://github.com/SpaceDEVofficial/Taesia-Bot-quiz) )")
        await ctx.reply(embed=em)


def setup(bot):
    bot.add_cog(Quiz(bot))
    print('cogs - `quiz` is loaded')