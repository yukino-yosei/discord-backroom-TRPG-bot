import discord
from discord import app_commands
from collections import deque
from random import randint
import sqlite3

db = sqlite3.connect("bot.db")
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    level INTEGER DEFAULT -1
)
""")

db.commit()

def sum_cal(inp) :
    while inp :
        if inp[1] == '끝' :
            return inp[0]
        elif inp[1] == '+' :
            f = inp.popleft()
            inp.popleft()
            b = inp.popleft()
            inp.appendleft(str(int(f) + int(b)))
        else :
            f = inp.popleft()
            inp.popleft()
            b = inp.popleft()
            inp.appendleft(str(int(f) - int(b)))

def random_cal(inp) :
    front, back = map(int, inp.split("d"))
    rst = []
    rnt = 0
    for i in range(front) :
        a = randint(1, back)
        rst.append(str(a))
        rnt += a
    
    return (rnt, f"[{"+".join(rst)}]")

def dnd(inp) :
    inp_list = deque(list(inp.replace(" ", "")) + ['끝'])
    split_list = deque([])
    final_list = []
    while inp_list :
        crr = []
        while inp_list[0] not in ['+', '-', "끝"] :
            crr.append(inp_list.popleft())
        split_list.append("".join(crr))
        split_list.append(inp_list.popleft())
    
    for i in range(len(split_list)) :
        if "d" in split_list[i] :
            result = random_cal(split_list[i])
            split_list[i] = result[0]
            final_list.append(result[1])
        elif split_list[i] in ['+', '-'] :
            final_list.append(split_list[i])
        elif split_list[i].isdigit() :
            final_list.append(split_list[i])

    return_sum = split_list.copy()
    sum_result = sum_cal(split_list)

    return (sum_result, final_list, return_sum)


from config import TOKEN, GM_id


class MyBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)

        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()


bot = MyBot()


@bot.event
async def on_ready():
    print(f"로그인 완료: {bot.user}")


@bot.tree.command(
    name="roll",
    description="표현식 (숫자)d(숫자)"
)
@app_commands.describe(
    입력값 = "표현식"
)
async def roll(interaction: discord.Interaction, 입력값: str):

    result = dnd(입력값)

    embed = discord.Embed(title = "주사위 결과")

    embed.add_field(
        name = "표현식",
        value = 입력값,
        inline = False
    )

    for i in range(0, len(result[1]), 2) :
        embed.add_field(
            name = f"{i // 2 + 1}차 파생 결과",
            value = f"{result[1][i]} -> **{result[2][i]}**",
            inline = False
        )
    
    embed.add_field(
        name = "결과값",
        value = f"**{result[0]}**",
        inline = False
    )

    await interaction.response.send_message(embed = embed)

@bot.tree.command(
    name = "레벨변경",
    description = "현재 자신의 레벨을 변경합니다."
)
@app_commands.describe(
    현재레벨 = "현재레벨(숫자값 입력)"
)
async def 레벨변경(interaction: discord.Interaction, 현재레벨: int) :
    user_id = interaction.user.id

    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
        (user_id,)
    )

    db.commit()

    cursor.execute(
        "SELECT level FROM users WHERE user_id = ?",
        (interaction.user.id,)
    )

    front_level = cursor.fetchone()


    embed = discord.Embed(title = "레별 변경 결과")

    embed.add_field(
        name = "이전 레벨",
        value = f"레벨 {front_level}\n",
        inline = False
    )

    embed.add_field(
        name = "변경된 레벨",
        value = f"레벨 {현재레벨}\n",
        inline = False
    )

    if front_level is None or front_level[0] == -1 :
        front_level = 0
    else :
        front_level = front_level[0]

    embed.add_field(
        name = "",
        value = f"총 {abs(front_level - 현재레벨)}층 이동하였습니다.",
        inline = False
    )

    await interaction.response.send_message(embed = embed)
    cursor.execute(
        "UPDATE users SET level = ? WHERE user_id = ?",
        (현재레벨, interaction.user.id,)
    )

    db.commit()

@bot.tree.command(
    name = "레벨조회",
    description = "현재 자신의 레벨을 조회합니다."
)
async def 레벨조회(interaction: discord.Interaction) :
    cursor.execute(
        "SELECT level FROM users WHERE user_id = ?",
        (interaction.user.id,)
    )

    current_level = cursor.fetchone()

    if current_level is None or current_level[0] == -1 :
        current_level = "없음"
    else :
        current_level = current_level[0]

    embed = discord.Embed(title = "레벨 조회")
    
    embed.add_field(
        name = "현재 레벨",
        value = f"레벨 {current_level}",
        inline = False
    )

    await interaction.response.send_message(embed = embed)

@bot.tree.command(
    name = "랜덤레벨",
    description = "레벨을 랜덤으로 설정합니다 (0~999)"
)
async def 랜덤레벨(interaction: discord.Interaction) :
    user_id = interaction.user.id
    random_level = randint(0, 999)

    cursor.execute(
        "SELECT level FROM users WHERE user_id = ?",
        (user_id,)
    )

    front_level = cursor.fetchone()

    if front_level is None or front_level[0] == -1 :
        front_level = "없음"
    else :
        front_level = front_level[0]

    embed = discord.Embed(title = "랜덤 레벨 결과")

    embed.add_field(
        name = "변동 결과",
        value = f"레벨 {front_level} -> **레벨 {random_level}**",
        inline = False
    )

    embed.add_field(
        name = "",
        value = f"총 {abs(front_level - random_level)}층 이동하였습니다.",
        inline = False
    )

    await interaction.response.send_message(embed = embed)

    cursor.execute(
        "UPDATE users SET level = ? WHERE user_id = ?",
        (random_level, user_id)
    )

    db.commit()

@bot.tree.command(
    name = "도박"
    description = "1d2000을 굴려 도박을 합니다. (하루 1회 제한)"
)
async def 도박(interaction: discord.Interaction) :

    gamble = randint(1, 2000)

    embed.add_field(
        name = "도박 결과"
        value = f"{"성공" if gamble == 1 else "실패"}"
        inline = False
    )

    embed.add_field(
        name = "보너스 결과"
        value = f"{"성공" if gamble < 100 else "실패"}"
        inline = False
    )

    embed.add_field(
        name = "GM 멘션"
        value = f"@{GM_id}"
        inline = False
    )

    await interaction.response.send_message(embed = embed)

bot.run(TOKEN)