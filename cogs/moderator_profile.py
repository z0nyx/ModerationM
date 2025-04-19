import time
import disnake
from disnake.ext import commands, tasks
from pymongo import MongoClient
import pymongo
import io
import os
import requests

from core.mod import *
from core.dbs import *
from core.enums import *

from Functions.TimeConvent import *
from Functions.Checker import *
from Functions.dicts import *

from Buttons.moderator_profile_buttons import *


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot: disnake.Client = bot

        # self.vacation_end_check.start()
        self.week_end_check.start()

    # @tasks.loop(seconds=5)
    # async def vacation_end_check(self):
    #     await self.bot.wait_until_ready()
    #     guild = self.bot.get_guild(ClientInfo.BOT_GUILD_ID)
    #     for find in list(vacation_db.find({"guild_id": guild.id, "status": True, "time_end": {"$lte": int(time.time())}})):
    #         emb = disnake.Embed(
    #             title='Отпуск - Moderator',
    #             description=f'Ваш отпуск **закончился**!\n\n'
    #                         f'> У вас есть освобождение от **недельной нормы** если ваш отпуск закончился в **середине** недели.',
    #             colour=0x2f3136
    #         )
    #         emb.set_footer(text='Удачной работы!')
    #         member = guild.get_member(find['member_id'])
    #         try:
    #             await member.send(embed=emb, content=f'{member.mention}')
    #         except full_errors:
    #             pass
    #         vacation_db.delete_one(find)
    #         moderator_statistic_db.update_one({"member_id": find['member_id'], "guild_id": guild.id},
    #                               {"$set": {"vacation": 0}})

    @tasks.loop(seconds=5)
    async def week_end_check(self):
        await self.bot.wait_until_ready()
        find = staff_db.find_one({"guild_id": ClientInfo.BOT_GUILD_ID})
        if find is not None:
            time_start = int(time.time())
            if time_start >= find['reset_week_moderator']:
                moderator_statistic_db.update_many({"guild_id": ClientInfo.BOT_GUILD_ID},
                                                {"$set": {"mutes_week": 0, "bans_week": 0, "warns_week": 0, "voice_week": 0, "last_warns_week": 0}})

                staff_db.update_one({"guild_id": ClientInfo.BOT_GUILD_ID},
                                    {"$inc": {"reset_week_moderator": (60 * 60 * 24 * 7) - (int(time.time()) - time_start)}})

    @tasks.loop(seconds=5)
    async def day_end_check(self):
        await self.bot.wait_until_ready()
        find = staff_db.find_one({"guild_id": ClientInfo.BOT_GUILD_ID})
        time_start = int(time.time())
        if time_start >= find['reset_day_moderator']:
            moderator_statistic_db.update_many({"guild_id": ClientInfo.BOT_GUILD_ID},
                                   {"$set": {"voice_day": 0}})

            staff_db.update_one({"guild_id": ClientInfo.BOT_GUILD_ID},
                                {"$inc": {"reset_day_moderator": (60 * 60 * 24 * 7) - (int(time.time()) - time_start)}})

    @commands.slash_command(
        name='mprofile',
        description='Открыть профиль модератора',
        dm_permission=False,
        options=[
            disnake.Option(
                name='member',
                description='Укажите пользователя для просмотра его профиля',
                required=False,
                type=disnake.OptionType.user
            )
        ]
    )
    async def moderator_profile_command(self, interaction: disnake.ApplicationCommandInteraction, member: disnake.Member = None):
        await interaction.response.defer()
        if not member:
            member = interaction.author

        if not moderator_check(member): return await interaction.edit_original_message(embed=disnake.Embed(
            description=f'Пользователь {member.mention} **не** является саппортом!', colour=0x2f3136
        ))
        find = moderator_statistic_db.find_one({"member_id": member.id})
        if not find:
            moderator_statistic_db.insert_one(generate_moderator_profile_post(guild=interaction.guild, member=member))
            find = moderator_statistic_db.find_one({"member_id": member.id})

        emb = disnake.Embed(
            title=f'Профиль модератора - {member}',
            colour=0x2f3136
        )
        emb.set_thumbnail(url=member.display_avatar.url)
        if member.id != interaction.author.id:
            emb.set_footer(text=f'Вызвал(а): {interaction.author}', icon_url=interaction.author.display_avatar.url)

        emb.add_field(name='Активность:', value=f'```{convert_time(find["voice"])}```')
        #emb.add_field(name='Баллы:', value=f'```{find["points"]}```')
        emb.add_field(name='Выговоров:', value=f'```{find["warns"]}/3```')
        # emb.add_field(name='Отпуск:', value=f'```{yes_no_dict[find["vacation"]]}```')

        emb.add_field(name='Муты', value=f'```{find["mutes_week"]} ({find["mutes"]})```')
        emb.add_field(name='Варны', value=f'```{find["warns_week"]} ({find["warns"]})```')
        emb.add_field(name='Баны', value=f'```{find["bans_week"]} ({find["bans"]})```')

        emb.add_field(name='Последнее предупреждение', value=f'```{find["last_warns_week"]} ({find["last_warns"]})```')

        emb.add_field(name='Активность за день:', value=f'```{convert_time(find["voice_day"])}```')
        emb.add_field(name='Активность за неделю', value=f'```{convert_time(find["voice_week"])}```')

        btns = MProfileButtons(bot=self.bot, author=interaction.author, member=member)

        await interaction.edit_original_message(embed=emb, view=btns)

    # @commands.Cog.listener("on_button_click")
    # async def feedback_listener(self, inter: disnake.MessageInteraction):
    #     if inter.component.custom_id == "accept_vacation":
    #         emb = inter.message.embeds[0].set_footer(text=f'Одобрил(а): {inter.author} | ID: {inter.author.id}', icon_url=inter.author.display_avatar.url)
    #         await inter.response.edit_message(embed=emb, components=[])

    #         find = vacation_db.find_one({"msg_id": inter.message.id})
    #         emb = disnake.Embed(
    #             title='Отпуск - Moderator',
    #             description=f'Ваш отпуск был **Одобрен**!',
    #             colour=0x2f3136
    #         )
    #         emb.set_footer(text='Удачного отдыха!')
    #         member = inter.guild.get_member(find['member_id'])
    #         try:
    #             await member.send(embed=emb, content=f'{member.mention}')
    #         except full_errors:
    #             pass
    #         await member.add_roles(inter.guild.get_role(RolesInfo.VACATION_ROLE))
    #         vacation_db.update_one({"msg_id": inter.message.id}, {"$set": {"time_end": int(time.time()) + find['time_seconds'], "status": True,
    #                                                                        "author_id": inter.author.id}})
    #         moderator_statistic_db.update_one({"member_id": find['member_id'], "guild_id": inter.guild.id}, {"$set": {"vacation": 1}})
    #     elif inter.component.custom_id == "deny_vacation":
    #         emb = inter.message.embeds[0].set_footer(text=f'Отклонил(а): {inter.author} | ID: {inter.author.id}',
    #                                                  icon_url=inter.author.display_avatar.url)
    #         await inter.response.edit_message(embed=emb, components=[])

    #         find = vacation_db.find_one({"msg_id": inter.message.id})
    #         emb = disnake.Embed(
    #             title='Отпуск - Moderator',
    #             description=f'Ваш отпуск был **Отклонён**!',
    #             colour=0x2f3136
    #         )
    #         emb.set_footer(text=f'Отклонил(а): {inter.author} | ID: {inter.author.id}',
    #                                                  icon_url=inter.author.display_avatar.url)
    #         member = inter.guild.get_member(find['member_id'])
    #         try:
    #             await member.send(embed=emb, content=f'{member.mention}')
    #         except full_errors:
    #             pass
    #         vacation_db.delete_one(find)


def setup(bot):
    bot.add_cog(Profile(bot))
    print('Ког: "Профиль саппорта" загрузился!')
