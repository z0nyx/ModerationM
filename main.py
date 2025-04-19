from colorama import init

init()
from colorama import Fore

import disnake
from disnake.ext import commands
import os
from core.dbs import *
from core.enums import *

from dotenv import load_dotenv
load_dotenv()

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or('!.!.!'), 
    intents=disnake.Intents.all(),
    test_guilds=[ClientInfo.BOT_GUILD_ID],
    status=disnake.Status.dnd,
    activity=disnake.Activity(
        type=disnake.ActivityType.watching,
        name="💗"
    ))
bot.remove_command('help')

def cogs_names():
    cogs_list = []
    for filename in os.listdir(f"./cogs"):
        if filename.endswith(".py"):
            cogs_list.append(disnake.OptionChoice(
                name=f'{filename[:-3]}',
                value=f'{filename[:-3]}'
            ))
    return cogs_list


@bot.slash_command(
    name='reload',
    description='Перезагрузка файла бота',
    options=[
        disnake.Option(
            name='extension',
            description="Название кога",
            type=disnake.OptionType.string,
            required=True,
            choices=cogs_names()
        )
    ]
)
async def reload(ctx: disnake.ApplicationCommandInteraction, extension: str):
    if ctx.author.id != 397414803473170432:
        await ctx.send(embed=disnake.Embed(description=f'Нет доступа!', colour=0x2f3136), ephemeral=True)
        return
    try:
        bot.reload_extension(f"cogs.{extension}")
    except Exception as e:
        await ctx.send(
            embed=disnake.Embed(description=f'Ког: **{extension}** -  **не** загружен!\n Ошибка: **```{e}```**',
                                colour=0x2f3136), ephemeral=True)
        return
    await ctx.send(embed=disnake.Embed(description=f'Ког: **{extension}** Успешно перезагружен!', colour=0x2f3136),
                   ephemeral=True)


@bot.event
async def on_ready():
    print(Fore.GREEN + "Бот запущен")
    print(Fore.GREEN + f'Вы вошли как {bot.user}')


for filename in os.listdir(f"./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")

bot.run(os.getenv("TOKEN"))
