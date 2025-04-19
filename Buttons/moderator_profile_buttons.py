import disnake
import asyncio

from Functions.TimeConvent import *
from Functions.Checker import *
from Functions.dicts import *

from core.dbs import *
from core.mod import *


class MProfileButtons(disnake.ui.View):
    msg: disnake.Message

    def __init__(self, bot: disnake.Client, author: disnake.Member, member: disnake.Member):
        super().__init__(timeout=180)
        self.bot = bot
        self.author = author
        self.member = member

        self.find = moderator_statistic_db.find_one({"member_id": member.id})

        # if author.id != member.id:
        #     self.remove_item(self.vacation_button)

        if not chief_check(author):
            self.remove_item(self.get_warn_button)
            self.remove_item(self.remove_warn_button)
            # self.remove_item(self.remove_vacation_button)

            # self.remove_item(self.give_points_button)
            # self.remove_item(self.remove_points_button)

    # @disnake.ui.button(label='Отпуск', style=disnake.ButtonStyle.green, row=1)
    # async def vacation_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
    #     await interaction.response.send_modal(
    #         title="Запрос отпуска",
    #         custom_id="vacation_request",
    #         components=[
    #             disnake.ui.TextInput(
    #                 label="Причина",
    #                 placeholder="Укажите причину отпуска",
    #                 custom_id="reason",
    #                 style=disnake.TextInputStyle.paragraph,
    #                 min_length=3,
    #                 max_length=1200
    #             ),
    #             disnake.ui.TextInput(
    #                 label="Длительность (1W|1D|1H|1M|1S)",
    #                 placeholder="Укажите длительность отпуска",
    #                 custom_id="latency",
    #                 style=disnake.TextInputStyle.paragraph,
    #                 min_length=2,
    #                 max_length=10
    #             )
    #         ]
    #     )
    #     try:
    #         modal_inter: disnake.ModalInteraction = await self.bot.wait_for(
    #             "modal_submit", timeout=600,
    #             check=lambda i: i.custom_id == "vacation_request" and i.author.id == interaction.author.id)
    #     except asyncio.TimeoutError:
    #         return

    #     reason = modal_inter.text_values["reason"]
    #     latency = modal_inter.text_values["latency"]
    #     if latency == '0':
    #         return await modal_inter.response.edit_message(
    #             embed=disnake.Embed(description=f'Длительность **не** может быть **0**!', colour=0x2f3136),
    #             view=None)

    #     try:
    #         time_seconds, name_russian, time_number = convert_to_russion(latency)
    #     except commands.BadArgument as e:
    #         return await modal_inter.response.edit_message(
    #             embed=disnake.Embed(description=f'При выполнении команды произошла ошибка: ```{e}```',
    #                                 colour=0x2f3136), view=None)
    #     emb = disnake.Embed(
    #         title='Запрос на отпуск',
    #         description=f'{interaction.author.mention}, Вы **успешно** отправили запрос на отпуск!',
    #         colour=0x2f3136
    #     )
    #     emb.add_field(name='> Причина:', value=f'```{reason}```')
    #     emb.add_field(name='> Длительность:', value=f'```{time_number} {name_russian}```')
    #     await modal_inter.response.edit_message(embed=emb, components=[])

    #     emb = disnake.Embed(
    #         title='Запрос на Отпуск - Moderator',
    #         description=f'**Пользователь:**\n'
    #                     f'· {interaction.author.mention}\n'
    #                     f'· ID: {interaction.author.id}\n',
    #         colour=0x2f3136
    #     )
    #     emb.add_field(name='> Причина:', value=f'```{reason}```')
    #     emb.add_field(name='> Длительность:', value=f'```{time_number} {name_russian}```')
    #     row = disnake.ui.ActionRow()
    #     row.add_button(label='Одобрить', custom_id=f'accept_vacation', style=disnake.ButtonStyle.green)
    #     row.add_button(label='Отклонить', custom_id=f'deny_vacation', style=disnake.ButtonStyle.red)
    #     msg = await self.bot.get_channel(ChannelsInfo.VACATION_CHANNEL).send(embed=emb, components=[row])
    #     post = {
    #         "msg_id": msg.id,
    #         "guild_id": interaction.guild.id,
    #         "member_id": interaction.author.id,
    #         "status": False,
    #         'time_seconds': int(time_seconds)
    #     }
    #     vacation_db.insert_one(post)

    @disnake.ui.button(label='Объявить выговор', style=disnake.ButtonStyle.red, row=2)
    async def get_warn_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_modal(
            title="Выдача выговора staff",
            custom_id="get_warn_moderator_modal",
            components=[
                disnake.ui.TextInput(
                    label="Причина",
                    placeholder="Укажите причину выговора",
                    custom_id="reason",
                    style=disnake.TextInputStyle.paragraph,
                    min_length=3,
                    max_length=1200,
                )
            ]
        )
        try:
            modal_inter: disnake.ModalInteraction = await self.bot.wait_for(
                "modal_submit", timeout=600,
                check=lambda i: i.custom_id == "get_warn_moderator_modal" and i.author.id == interaction.author.id)
        except asyncio.TimeoutError:
            return

        reason = modal_inter.text_values["reason"]
        emb = disnake.Embed(
            title='Выговор',
            description=f'Вы выдали выговор **Staff** {self.member.mention}!',
            colour=0x2f3136
        )
        emb.add_field(name='Причина:', value=f'{reason}')
        emb.add_field(name='Выговоров:', value=f'{self.find["warns"] + 1}/3')
        await modal_inter.response.edit_message(embed=emb, components=[], content=f'{interaction.author.mention}')
        moderator_statistic_db.update_one({"member_id": self.member.id, "guild_id": interaction.guild.id},
                              {"$inc": {'warns': 1}})

        emb = disnake.Embed(
            title='Вы получили выговор - Staff',
            colour=0x2f3136
        )
        emb.add_field(name='> Причина:', value=f'{reason}')
        emb.add_field(name='> Кол-во', value=f'{self.find["warns"] + 1}/3')
        emb.set_footer(text=f'Выполнил(а): {interaction.author} | ID: {interaction.author.id}',
                       icon_url=interaction.author.display_avatar.url)
        try:
            await self.member.send(embed=emb)
        except full_errors:
            pass

        emb_log = disnake.Embed(
            title='Выдача выговора',
            description=f'Staff: {self.member.mention}\n'
                        f'· ID: {self.member.id}\n',
            colour=0x2f3136
        )
        emb_log.set_footer(text=f'Выполнила(а): {interaction.author} | ID: {interaction.author.id}',
                           icon_url=interaction.author.display_avatar.url)
        emb_log.add_field(name='Причина:', value=f'{reason}')
        emb_log.add_field(name='Выговоров:', value=f'{self.find["warns"] + 1}/3')
        await self.bot.get_channel(ChannelsInfo.WARNS_LOG_CHANNEL).send(embed=emb_log)

    @disnake.ui.button(label='Снять выговор', style=disnake.ButtonStyle.green, row=2)
    async def remove_warn_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        emb = disnake.Embed(
            title='Выговор',
            description=f'Вы сняли выговор **Staff** {self.member.mention}!',
            colour=0x2f3136
        )
        emb.add_field(name='Выговоров:', value=f'{self.find["warns"] - 1}/3')
        await interaction.response.edit_message(embed=emb, components=[], content=f'{interaction.author.mention}')
        moderator_statistic_db.update_one({"member_id": self.member.id, "guild_id": interaction.guild.id},
                              {"$inc": {'warns': -1}})

        emb = disnake.Embed(
            title='С вас был снят выговор - Staff',
            colour=0x2f3136
        )
        emb.add_field(name='> Кол-во', value=f'{self.find["warns"] - 1}/3')
        emb.set_footer(text=f'Выполнил(а): {interaction.author} | ID: {interaction.author.id}',
                       icon_url=interaction.author.display_avatar.url)
        try:
            await self.member.send(embed=emb)
        except full_errors:
            pass

        emb_log = disnake.Embed(
            title='Амнистия выговора',
            description=f'Staff: {self.member.mention}\n'
                        f'· ID: {self.member.id}\n',
            colour=0x2f3136
        )
        emb_log.set_footer(text=f'Выполнила(а): {interaction.author} | ID: {interaction.author.id}',
                           icon_url=interaction.author.display_avatar.url)
        emb_log.add_field(name='Выговоров:', value=f'{self.find["warns"] - 1}/3')
        await self.bot.get_channel(ChannelsInfo.WARNS_LOG_CHANNEL).send(embed=emb_log)

    # @disnake.ui.button(label='Снять отпуск', style=disnake.ButtonStyle.red, row=2)
    # async def remove_vacation_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
    #     emb = disnake.Embed(
    #         title='Отпуск',
    #         description=f'Вы сняли отпуск **Staff** {self.member.mention}!',
    #         colour=0x2f3136
    #     )
    #     await interaction.response.edit_message(embed=emb, components=[], content=f'{interaction.author.mention}')
    #     vacation_db.delete_one({"member_id": self.find['member_id'], "guild_id": interaction.guild.id, "status": True})
    #     moderator_statistic_db.update_one({"member_id": self.find['member_id'], "guild_id": interaction.guild.id},
    #                           {"$set": {"vacation": 0}})

    #     emb = disnake.Embed(
    #         title='Отпуск - Moderator',
    #         colour=0x2f3136,
    #         description=f'Ваш отпуск был **анулирован**. Возвращайтесь к работе как можно скорее!'
    #     )

    #     emb.set_footer(text=f'Выполнил(а): {interaction.author} | ID: {interaction.author.id}',
    #                    icon_url=interaction.author.display_avatar.url)
    #     try:
    #         await self.member.send(embed=emb)
    #     except full_errors:
    #         pass

    #     emb_log = disnake.Embed(
    #         title='Амнистия отпуска',
    #         description=f'Модератор: {self.member.mention}\n'
    #                     f'· ID: {self.member.id}\n',
    #         colour=0x2f3136
    #     )
    #     emb_log.set_footer(text=f'Выполнила(а): {interaction.author} | ID: {interaction.author.id}',
    #                        icon_url=interaction.author.display_avatar.url)
    #     await self.bot.get_channel(ChannelsInfo.VACATION_CHANNEL).send(embed=emb_log)

    # @disnake.ui.button(label='Выдать баллы', style=disnake.ButtonStyle.green, row=3)
    # async def give_points_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
    #     await interaction.response.send_modal(
    #         title="Выдача баллы Staff",
    #         custom_id="get_points_moderator_modal",
    #         components=[
    #             disnake.ui.TextInput(
    #                 label="Количество",
    #                 placeholder="Укажите количество баллов",
    #                 custom_id="amount",
    #                 style=disnake.TextInputStyle.short,
    #                 min_length=1,
    #                 max_length=15,
    #             )
    #         ]
    #     )
    #     try:
    #         modal_inter: disnake.ModalInteraction = await self.bot.wait_for(
    #             "modal_submit", timeout=600,
    #             check=lambda i: i.custom_id == "get_points_moderator_modal" and i.author.id == interaction.author.id)
    #     except asyncio.TimeoutError:
    #         return

    #     amount_str = modal_inter.text_values["amount"]
    #     try:
    #         amount = int(amount_str)
    #     except ValueError:
    #         return await modal_inter.response.edit_message(
    #             embed=disnake.Embed(description=f'**{amount_str}** это **не** число!', colour=0x2f3136))

    #     if amount < 1:
    #         return await modal_inter.response.edit_message(
    #             embed=disnake.Embed(description=f'Выдавать баллы можно только числом **больше** 0!', colour=0x2f3136))

    #     emb = disnake.Embed(
    #         title='Выдача баллов',
    #         description=f'Вы успешно **выдали** {amount} баллов Staff {self.member.mention}!', colour=0x2f3136
    #     )
    #     await modal_inter.response.edit_message(embed=emb, components=[], content=f'{interaction.author.mention}')
    #     moderator_statistic_db.update_one({"member_id": self.member.id, "guild_id": interaction.guild.id},
    #                           {"$inc": {'points': amount}})

    # @disnake.ui.button(label='Снять баллы', style=disnake.ButtonStyle.red, row=3)
    # async def remove_points_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
    #     await interaction.response.send_modal(
    #         title="Снять баллы Staff",
    #         custom_id="remove_points_moderator_modal",
    #         components=[
    #             disnake.ui.TextInput(
    #                 label="Количество",
    #                 placeholder="Укажите количество баллов",
    #                 custom_id="amount",
    #                 style=disnake.TextInputStyle.short,
    #                 min_length=1,
    #                 max_length=15,
    #             )
    #         ]
    #     )
    #     try:
    #         modal_inter: disnake.ModalInteraction = await self.bot.wait_for(
    #             "modal_submit", timeout=600,
    #             check=lambda i: i.custom_id == "remove_points_moderator_modal" and i.author.id == interaction.author.id)
    #     except asyncio.TimeoutError:
    #         return

    #     amount_str = modal_inter.text_values["amount"]
    #     try:
    #         amount = int(amount_str)
    #     except ValueError:
    #         return await modal_inter.response.edit_message(
    #             embed=disnake.Embed(description=f'**{amount_str}** это **не** число!', colour=0x2f3136))

    #     if amount < 1:
    #         return await modal_inter.response.edit_message(
    #             embed=disnake.Embed(description=f'Снимать баллы можно только числом **больше** 0!', colour=0x2f3136))

    #     emb = disnake.Embed(
    #         title='Снятие баллов',
    #         description=f'Вы успешно **сняли** {amount} баллов Staff {self.member.mention}!', colour=0x2f3136
    #     )
    #     await modal_inter.response.edit_message(embed=emb, components=[], content=f'{interaction.author.mention}')
    #     moderator_statistic_db.update_one({"member_id": self.member.id, "guild_id": interaction.guild.id},
    #                           {"$inc": {'points': -amount}})

    @disnake.ui.button(label='Удалить', style=disnake.ButtonStyle.red, row=4)
    async def remove_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.message.delete()

    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        if self.author != interaction.author:
            await interaction.send(
                embed=disnake.Embed(description=f'{interaction.author.mention}, у вас **нет** доступа к этому меню!',
                                    color=disnake.Color.from_rgb(47, 49, 54)), ephemeral=True)
            return False
        return True

    async def on_timeout(self) -> None:
        if self.message:
            try:
                await self.message.delete()
            except (disnake.Forbidden, disnake.HTTPException, disnake.NotFound):
                pass
