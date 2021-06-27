from discord.ext import commands
import psycopg2
import os
from config import OWNERS
from . import execption
from dotenv import load_dotenv
load_dotenv(verbose=True)
async def check_owner(ctx):
    if ctx.author.id in OWNERS:
        return True
    raise execption.PermError.NotOwnerUser

def is_owner():
    return commands.check(check_owner)

async def not_bot(ctx):
    if not ctx.author.bot:
        return True
    raise commands.CheckFailure

async def is_black(ctx):
    conn_string = f"host={os.getenv('DB_HOST')} dbname ={os.getenv('DB_DB')} user={os.getenv('DB_USER')} password={os.getenv('DB_PW')}"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    id = str(ctx.author.id)
    cursor.execute(f'SELECT * FROM black_list WHERE user_id={id}::TEXT')
    data = cursor.fetchall()
    print(data)
    if data == []:
        return True
    else:
        raise execption.PermError.BlacklistedUser

def not_black():
    return commands.check(is_black)