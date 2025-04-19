import disnake
from disnake.ext import commands
import time

from core.functions import *
from core.dbs import *
from Buttons.delete_buttons import *
from Functions.Page import *
from Functions.jail_checker import *
from Functions.TimeConvent import *
from Functions.dicts import *
from core.enums import *

type_name = {1: "Голосовой мут", 2: "Текстовый мут", 4: "Бан", 6: "Варн", 10: "ПП"}


class Back_Button(disnake.ui.View):
    def __init__(self, bot: disnake.Client, member: disnake.Member, author: disnake.Member, msg: disnake.Message):
        super().__init__(timeout=180)
        self.bot = bot
        self.author = author
        self.member = member
        self.msg = msg

    @disnake.ui.button(label="Назад", style=disnake.ButtonStyle.gray)
    async def delete_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        if self.member.id == self.author.id:
            member = interaction.author
            desc = f'Выберите, что хотите **сделать** с **собой**!'
        else:
            member = self.member
            desc = f'Выберите, что хотите **сделать** с пользователем {self.member.mention}!'
        emb = disnake.Embed(
            title='Панель управления пользователем',
            description=desc,
            colour=0x2f3136
        )
        emb.set_thumbnail(url=member.display_avatar.url)
        btns = Action_Buttons(bot=self.bot, author=interaction.author, member=member)
        btns.msg = await interaction.response.edit_message(embed=emb, view=btns)

    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        if interaction.author.id != self.author.id:
            await interaction.send(embed=generate_classic_embed(f'Вам **недоступна** данная кнопка!'), ephemeral=True)
            return False
        else:
            return True

    async def on_timeout(self) -> None:
        if self.msg:
            try:
                await self.msg.edit(view=None)
            except default_error:
                return


class ModalGiveJail(disnake.ui.Modal):  # выдача наказаний
    def __init__(self, jail_type: int, author: disnake.Member, member: disnake.Member, bot: disnake.Client,
                 msg: disnake.Message) -> None:
        components = [
            disnake.ui.TextInput(
                label="Длительность (1W|1D|1H|1M|1S)",
                placeholder="Укажите срок наказания",
                custom_id="latency",
                style=disnake.TextInputStyle.short,
                min_length=1,
                max_length=10,
            ),
            disnake.ui.TextInput(
                label="Причина",
                placeholder="Укажите причину наказания",
                custom_id="reason",
                style=disnake.TextInputStyle.short,
                min_length=1,
                max_length=100,
            ),
        ]
        super().__init__(title="Выдача наказания", custom_id="give_jail_user", components=components)
        self.jail_type = jail_type
        self.author = author
        self.member = member
        self.bot = bot
        self.msg = msg

    async def callback(self, inter: disnake.ModalInteraction) -> None:
        latency_str = inter.text_values["latency"]
        reason = inter.text_values["reason"]

        if latency_str == '0':
            return await inter.response.edit_message(
                embed=generate_classic_embed(f'Срок наказания **не может** быть **0**!'),
                view=Back_Button(bot=self.bot, author=inter.author, member=self.member, msg=self.msg))

        try:
            time_seconds, name_russian, time_number = convert_to_russion(latency_str)
        except commands.BadArgument as e:
            return await inter.send(embed=generate_classic_embed(f'При выполнении команды произошла ошибка: ```{e}```'),
             ephemeral=True, view=Delete_Button(author=inter.author, member=self.member, bot=self.bot, msg=self.msg))

        if self.jail_type == 1 or self.jail_type == 2:
            if self.jail_type == 1:
                mute_name = 'Голосовой'
                role_id = RolesInfo.VOICE_MUTE_ROLE
                jail_type_id = 1
            elif self.jail_type == 2:
                mute_name = 'Текстовый'
                role_id = RolesInfo.CHAT_MUTE_ROLE
                jail_type_id = 2
            else: return

            try:
                await self.member.add_roles(inter.guild.get_role(role_id))
            except default_error:
                return await inter.send(
                    embed=generate_classic_embed(
                        f'При выполнении команды произошла **ошибка**. Повторите попытку позже!'),
                    ephemeral=True,
                    view=Delete_Button(author=inter.author, member=self.member, bot=self.bot, msg=self.msg))

            emb = disnake.Embed(
                title='Выдача мута',
                description=f'{inter.author.mention}, вы **выдали** мут пользователю {self.member.mention}',
                colour=0x2f3136
            )
            emb.set_thumbnail(url=inter.guild.icon.url)
            emb.set_footer(text=f'Тип мута: {mute_name}')
            emb.add_field(name='Причина', value=f'```{reason}```')
            emb.add_field(name='Длительность', value=f'```{time_number} {name_russian}```')
            await inter.response.edit_message(embed=emb,
                                              view=Delete_Button(author=self.author, member=self.member, bot=self.bot,
                                                                 msg=self.msg))

            emb_user = disnake.Embed(
                title='Мут',
                description=f'Вам был **выдан** мут staff `{inter.author}`(ID: {inter.author.id})',
                colour=0x2f3136
            )
            emb_user.set_thumbnail(url=inter.guild.icon.url)
            emb_user.set_footer(text=f'Тип мута: {mute_name}')
            emb_user.add_field(name='Причина', value=f'```{reason}```')
            emb_user.add_field(name='Длительность', value=f'```{time_number} {name_russian}```')
            try:
                await self.member.send(embed=emb_user, content=f'{self.member.mention}')
            except default_error:
                pass

            emb_log = disnake.Embed(
                title='Выдача мута',
                description=f'Исполнитель: {inter.author.mention}\n'
                            f'Пользователь: {self.member.mention}',
                colour=0x2f3136
            )
            emb_log.set_thumbnail(url=inter.guild.icon.url)
            emb_log.set_footer(text=f'Тип мута: {mute_name}')
            emb_log.add_field(name='Причина', value=f'```{reason}```')
            emb_log.add_field(name='Длительность', value=f'```{time_number} {name_russian}```')
            await self.bot.get_channel(ChannelsInfo.LOG_MUTE_CHANNEL).send(embed=emb_log)

            post = {
                "member_id": self.member.id,
                "moderator_id": inter.author.id,
                "reason": reason,
                "jail_type": jail_type_id,
                "time_start": int(time.time()),
                "time_end": int(time.time()) + time_seconds
            }
            user_statistic_db.update_one({"member_id": self.member.id},
                                         {"$inc": {"warns": 0, "all_warns": 0, "bans": 0, "mutes": 1, "last_warns": 0},
                                          "$push": {"history": post}
                                          }, True)
            jail_db.insert_one(post)

            moderator_statistic_db.update_one({"member_id": inter.author.id},
                                              {"$inc": {"mutes": 1, "mutes_week": 1}})
        elif self.jail_type == 4:
            try:
                for role in self.member.roles:
                    try:
                        await self.member.remove_roles(role, reason=f'Блокировка пользователя')
                    except default_error:
                        pass
                await self.member.add_roles(inter.guild.get_role(RolesInfo.BAN_ROLE),
                                            reason=f'Выдача бана staff {inter.author.name[:25]}#{inter.author.discriminator}')
            except default_error:
                return await inter.send(
                    embed=generate_classic_embed(
                        f'При выполнении команды произошла **ошибка**. Повторите попытку позже!'),
                    ephemeral=True,
                    view=Delete_Button(author=inter.author, member=self.member, bot=self.bot, msg=self.msg))

            emb = disnake.Embed(
                title='Выдача бана',
                description=f'{inter.author.mention}, вы **выдали** бан пользователю {self.member.mention}',
                colour=0x2f3136
            )
            emb.set_thumbnail(url=inter.guild.icon.url)
            emb.add_field(name='Причина', value=f'```{reason}```')
            emb.add_field(name='Длительность', value=f'```{time_number} {name_russian}```')
            await inter.response.edit_message(embed=emb,
                                              view=Delete_Button(author=self.author, member=self.member, bot=self.bot,
                                                                 msg=self.msg))

            emb_user = disnake.Embed(
                title='Бан',
                description=f'Вам был **выдан** бан staff `{inter.author}`(ID: {inter.author.id})',
                colour=0x2f3136
            )
            emb_user.set_thumbnail(url=inter.guild.icon.url)
            emb_user.add_field(name='Причина', value=f'```{reason}```')
            emb_user.add_field(name='Длительность', value=f'```{time_number} {name_russian}```')
            try:
                await self.member.send(embed=emb_user, content=f'{self.member.mention}')
            except default_error:
                pass

            emb_log = disnake.Embed(
                title='Выдача бана',
                description=f'Исполнитель: {inter.author.mention}\n'
                            f'Пользователь: {self.member.mention}',
                colour=0x2f3136
            )
            emb_log.set_thumbnail(url=inter.guild.icon.url)
            emb_log.add_field(name='Причина', value=f'```{reason}```')
            emb_log.add_field(name='Длительность', value=f'```{time_number} {name_russian}```')
            await self.bot.get_channel(ChannelsInfo.LOG_BAN_CHANNEL).send(embed=emb_log)

            post = {
                "member_id": self.member.id,
                "moderator_id": inter.author.id,
                "reason": reason,
                "jail_type": 4,
                "time_start": int(time.time()),
                "time_end": int(time.time()) + time_seconds
            }

            user_statistic_db.update_one({"member_id": self.member.id},
                                         {"$inc": {"warns": 0, "all_warns": 0, "bans": 1, "mutes": 0, "last_warns": 0},
                                          "$push": {"history": post}
                                          }, True)

            moderator_statistic_db.update_one({"member_id": inter.author.id},
                                              {"$inc": {"bans": 1, "bans_week": 1}})

            jail_db.insert_one(post)

        elif self.jail_type == 10:
            try:
                for role in self.member.roles:
                    try:
                        await self.member.remove_roles(role, reason=f'Выдача последнего предупреждения пользователю')
                    except default_error:
                        pass
                await self.member.add_roles(inter.guild.get_role(RolesInfo.LAST_WARN),
                                            reason=f'Выдача оследнего предупреждения staff {inter.author.name[:25]}#{inter.author.discriminator}')
            except default_error:
                return await inter.send(
                    embed=generate_classic_embed(
                        f'При выполнении команды произошла **ошибка**. Повторите попытку позже!'),
                    ephemeral=True,
                    view=Delete_Button(author=inter.author, member=self.member, bot=self.bot, msg=self.msg))

            emb = disnake.Embed(
                title='Выдача последнего предупреждения',
                description=f'{inter.author.mention}, вы **выдали** последнее предупреждение пользователю {self.member.mention}',
                colour=0x2f3136
            )
            emb.set_thumbnail(url=inter.guild.icon.url)
            emb.add_field(name='Причина', value=f'```{reason}```')
            emb.add_field(name='Длительность', value=f'```{time_number} {name_russian}```')
            await inter.response.edit_message(embed=emb,
                                              view=Delete_Button(author=self.author, member=self.member, bot=self.bot,
                                                                 msg=self.msg))

            emb_user = disnake.Embed(
                title='Последнее предупреждение',
                description=f'Вам был **выдано** последнее предупреждение staff`{inter.author}`(ID: {inter.author.id})',
                colour=0x2f3136
            )
            emb_user.set_thumbnail(url=inter.guild.icon.url)
            emb_user.add_field(name='Причина', value=f'```{reason}```')
            emb_user.add_field(name='Длительность', value=f'```{time_number} {name_russian}```')
            try:
                await self.member.send(embed=emb_user, content=f'{self.member.mention}')
            except default_error:
                pass

            emb_log = disnake.Embed(
                title='Выдача Последнего предупреждения',
                description=f'Исполнитель: {inter.author.mention}\n'
                            f'Пользователь: {self.member.mention}',
                colour=0x2f3136
            )
            emb_log.set_thumbnail(url=inter.guild.icon.url)
            emb_log.add_field(name='Причина', value=f'```{reason}```')
            emb_log.add_field(name='Длительность', value=f'```{time_number} {name_russian}```')
            await self.bot.get_channel(ChannelsInfo.LOG_BAN_CHANNEL).send(embed=emb_log)

            post = {
                "member_id": self.member.id,
                "moderator_id": inter.author.id,
                "reason": reason,
                "jail_type": 10,
                "time_start": int(time.time()),
                "time_end": int(time.time()) + time_seconds
            }

            user_statistic_db.update_one({"member_id": self.member.id},
                                         {"$inc": {"warns": 0, "all_warns": 0, "bans": 0, "mutes": 0, "last_warns": 1},
                                          "$push": {"history": post}
                                          }, True)

            moderator_statistic_db.update_one({"member_id": inter.author.id},
                                              {"$inc": {"last_warns": 1, "last_warns_week": 1}})

            jail_db.insert_one(post)
            
    async def on_error(self, error: Exception, inter: disnake.ModalInteraction) -> None:
        await inter.response.send_message(
            embed=generate_classic_embed("Произошла проблема, пожалуйста повторите попытку!"), ephemeral=True)




class ModalGiveWarn(disnake.ui.Modal):  # выдача наказаний
    def __init__(self, author: disnake.Member, member: disnake.Member, bot: disnake.Client,
                 msg: disnake.Message) -> None:
        components = [
            disnake.ui.TextInput(
                label="Причина",
                placeholder="Укажите причину наказания",
                custom_id="reason",
                style=disnake.TextInputStyle.short,
                min_length=1,
                max_length=100,
            ),
        ]
        super().__init__(title="Выдача варна", custom_id="give_warn_jail_user", components=components)
        self.author = author
        self.member = member
        self.bot = bot
        self.msg = msg

    async def callback(self, inter: disnake.ModalInteraction) -> None:
        reason = inter.text_values["reason"]

        user_warns = get_warns_user(self.member)
        if user_warns + 1 >= 3:
            try:
                for role in self.member.roles:
                    try:
                        await self.member.remove_roles(role, reason=f'Блокировка пользователя')
                    except default_error:
                        pass
                await self.member.add_roles(inter.guild.get_role(RolesInfo.BAN_ROLE),
                                            reason=f'Выдача бана staff {inter.author.name[:25]}#{inter.author.discriminator}')
            except default_error:
                return await inter.send(
                    embed=generate_classic_embed(
                        f'При выполнении команды произошла **ошибка**. Повторите попытку позже!'), ephemeral=True,
                    view=Delete_Button(author=inter.author, member=self.member, bot=self.bot, msg=self.msg))

            emb = disnake.Embed(
                title='Выдача Бана',
                description=f'{inter.author.mention}, вы **выдали** бан пользователю {self.member.mention}',
                colour=0x2f3136
            )
            emb.set_thumbnail(url=inter.guild.icon.url)
            emb.add_field(name='Причина', value=f'```3 варна```')
            emb.add_field(name='Длительность', value=f'```30 дней``')
            await inter.response.edit_message(embed=emb,
                                              view=Delete_Button(author=self.author, member=self.member,
                                                                 bot=self.bot, msg=self.msg))

            emb_user = disnake.Embed(
                title='Бан',
                description=f'Вам был **выдан** бан staff `{inter.author}`(ID: {inter.author.id})',
                colour=0x2f3136
            )
            emb_user.set_thumbnail(url=inter.guild.icon.url)
            emb_user.add_field(name='Причина', value=f'```3 варна```')
            emb_user.add_field(name='Длительность', value=f'```30 дней```')
            try:
                await self.member.send(embed=emb_user, content=f'{self.member.mention}')
            except default_error:
                pass

            emb_log = disnake.Embed(
                title='Выдача бана',
                description=f'Исполнитель: {inter.author.mention}\n'
                            f'Пользователь: {self.member.mention}',
                colour=0x2f3136
            )
            emb_log.set_thumbnail(url=inter.guild.icon.url)
            emb_log.add_field(name='Причина', value=f'```3 варна```')
            emb_log.add_field(name='Длительность', value=f'```30 дней```')
            await self.bot.get_channel(ChannelsInfo.LOG_BAN_CHANNEL).send(embed=emb_log)

            post = {
                "member_id": self.member.id,
                "moderator_id": inter.author.id,
                "reason": '3 варна',
                "jail_type": 4,
                "time_start": int(time.time()),
                "time_end": int(time.time()) + 60*60*24*30
            }

            user_statistic_db.update_one({"member_id": self.member.id},
                                         {"$inc": {"warns": 1, "all_warns": 1, "bans": 1, "mutes": 0, "last_warns": 0},
                                          "$push": {"history": post},
                                          "$set": {"warns": 0}
                                          }, True)

            for find in list(jail_db.find({"member_id": self.member.id, "jail_type": 3})):
                jail_db.delete_one(find)

            moderator_statistic_db.update_one({"member_id": inter.author.id},
                                              {"$inc": {"warns": 1, "warns_week": 1, "bans": 1, "bans_week": 1}})

            jail_db.insert_one(post)
        else:
            emb = disnake.Embed(
                title='Выдача варна',
                description=f'{inter.author.mention}, вы **выдали** варн пользователю {self.member.mention}',
                colour=0x2f3136
            )
            emb.set_thumbnail(url=inter.guild.icon.url)
            emb.add_field(name='Причина', value=f'```{reason}```')
            emb.add_field(name='Длительность', value=f'```14 дней```')
            emb.add_field(name='Количество', value=f'```{user_warns + 1}/3```')
            await inter.response.edit_message(embed=emb,
                                              view=Delete_Button(author=self.author, member=self.member,
                                                                 bot=self.bot,
                                                                 msg=self.msg))

            emb_user = disnake.Embed(
                title='Варн',
                description=f'Вам был **выдан** варн staff `{inter.author}`(ID: {inter.author.id})',
                colour=0x2f3136
            )
            emb_user.set_thumbnail(url=inter.guild.icon.url)
            emb_user.add_field(name='Причина', value=f'```{reason}```')
            emb_user.add_field(name='Длительность', value=f'```14 дней```')
            emb_user.add_field(name='Количество', value=f'```{user_warns + 1}/3```')
            try:
                await self.member.send(embed=emb_user, content=f'{self.member.mention}')
            except default_error:
                pass

            emb_log = disnake.Embed(
                title='Выдача варна',
                description=f'Исполнитель: {inter.author.mention}\n'
                            f'Пользователь: {self.member.mention}',
                colour=0x2f3136
            )
            emb_log.set_thumbnail(url=inter.guild.icon.url)
            emb_log.add_field(name='Причина', value=f'```{reason}```')
            emb_log.add_field(name='Длительность', value=f'```14 дней```')
            emb_log.add_field(name='Количество', value=f'```{user_warns + 1}/3```')
            await self.bot.get_channel(ChannelsInfo.LOG_WARN_CHANNEL).send(embed=emb_log)

            post = {
                "member_id": self.member.id,
                "moderator_id": inter.author.id,
                "reason": reason,
                "jail_type": 6,
                "time_start": int(time.time()),
                "time_end": int(time.time()) + 60 * 60 * 24 * 14
            }

            user_statistic_db.update_one({"member_id": self.member.id},
                                         {"$inc": {"warns": 1, "all_warns": 1, "bans": 0, "mutes": 0, "last_warns": 0},
                                          "$push": {"history": post}
                                          }, True)

            moderator_statistic_db.update_one({"member_id": inter.author.id},
                                              {"$inc": {"warns": 1, "warns_week": 1}})

            jail_db.insert_one(post)

    async def on_error(self, error: Exception, inter: disnake.ModalInteraction) -> None:
        await inter.response.send_message(
            embed=generate_classic_embed("Произошла проблема, пожалуйста повторите попытку!"),
            ephemeral=True)


class SelectMuteButtons(disnake.ui.View):
    def __init__(self, bot: disnake.Client, member: disnake.Member, author: disnake.Member, msg: disnake.Message, action_type: int):
        super().__init__(timeout=180)
        self.bot = bot
        self.author = author
        self.member = member
        self.msg = msg
        self.action_type = action_type  # 1 - выдача, 2 - снятие

    @disnake.ui.button(label="Голосовой", style=disnake.ButtonStyle.gray, row=1)
    async def voice_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        if self.action_type == 1:  # выдаём
            if status_mute_user(member=self.member, guild=interaction.guild, mute_type=1):
                await interaction.response.edit_message(
                    embed=generate_classic_embed(f'Пользователь **уже замучен**!'),
                    view=Delete_Button(author=self.author, member=self.member, bot=self.bot, msg=self.msg)
                )

            else:
                await interaction.response.send_modal(
                    modal=ModalGiveJail(jail_type=1, bot=self.bot, author=interaction.author, member=self.member,
                                        msg=self.msg))
                await interaction.edit_original_message(
                    embed=generate_classic_embed(f'Следуйте инструкциям в модальном окне!'),
                    view=Back_Button(bot=self.bot, author=interaction.author, member=self.member, msg=self.msg))
        else:  # снимаем
            if not status_mute_user(member=self.member, guild=interaction.guild, mute_type=1):
                await interaction.response.edit_message(
                    embed=generate_classic_embed(f'Пользователь **не замучен**!'),
                    view=Delete_Button(author=self.author, member=self.member, bot=self.bot, msg=self.msg)
                )

            else:
                try:
                    await self.member.remove_roles(interaction.guild.get_role(RolesInfo.VOICE_MUTE_ROLE))
                except default_error:
                    return await interaction.response.edit_message(
                        embed=generate_classic_embed(f'У меня **недостаточно** прав для снятия мута!\n\n Обратитесь к **Администрации!**'),
                        view=Delete_Button(author=self.author, member=self.member, bot=self.bot, msg=self.msg)
                    )
                emb = disnake.Embed(
                    title='Снятие мута',
                    description=f'{interaction.author.mention}, вы **сняли** мут с пользователя {self.member.mention}',
                    colour=0x2f3136
                )
                emb.set_thumbnail(url=interaction.guild.icon.url)
                emb.set_footer(text='Тип мута: Голосовой')
                await interaction.response.edit_message(embed=emb,
                                                        view=Delete_Button(author=self.author, member=self.member,
                                                                           bot=self.bot, msg=self.msg))

                emb_user = disnake.Embed(
                    title='Мут',
                    description=f'Вам был **снят** мут staff `{interaction.author}`(ID: {interaction.author.id})',
                    colour=0x2f3136
                )
                emb_user.set_thumbnail(url=interaction.guild.icon.url)
                emb_user.set_footer(text='Тип мута: Голосовой')
                try:
                    await self.member.send(embed=emb_user, content=f'{self.member.mention}')
                except default_error:
                    pass

                emb_log = disnake.Embed(
                    title='Снятие мута',
                    description=f'Исполнитель: {interaction.author.mention}\n'
                                f'Пользователь: {self.member.mention}',
                    colour=0x2f3136
                )
                emb_log.set_thumbnail(url=interaction.guild.icon.url)
                emb_log.set_footer(text='Тип мута: Голосовой')
                await self.bot.get_channel(ChannelsInfo.LOG_MUTE_CHANNEL).send(embed=emb_log)

                find = jail_db.find_one({"member_id": self.member.id, "jail_type": 1})
                if find:
                    jail_db.delete_one(find)

    @disnake.ui.button(label="Текстовый", style=disnake.ButtonStyle.gray, row=1)
    async def text_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        if self.action_type == 1:  # выдаём
            if status_mute_user(member=self.member, guild=interaction.guild, mute_type=2):
                await interaction.response.edit_message(
                    embed=generate_classic_embed(f'Пользователь **уже замучен**!'),
                    view=Delete_Button(author=self.author, member=self.member, bot=self.bot, msg=self.msg)
                )

            else:
                await interaction.response.send_modal(
                    modal=ModalGiveJail(jail_type=2, bot=self.bot, author=interaction.author, member=self.member,
                                        msg=self.msg))
                await interaction.edit_original_message(
                    embed=generate_classic_embed(f'Следуйте инструкциям в модальном окне!'),
                    view=Back_Button(bot=self.bot, author=interaction.author, member=self.member, msg=self.msg))
        else:   # снимаем
            if not status_mute_user(member=self.member, guild=interaction.guild, mute_type=2):
                await interaction.response.edit_message(
                    embed=generate_classic_embed(f'Пользователь **не замучен**!'),
                    view=Delete_Button(author=self.author, member=self.member, bot=self.bot, msg=self.msg)
                )

            else:
                try:
                    await self.member.remove_roles(interaction.guild.get_role(RolesInfo.CHAT_MUTE_ROLE))
                except default_error:
                    return await interaction.response.edit_message(
                        embed=generate_classic_embed(
                            f'У меня **недостаточно** прав для снятия мута!\n\n Обратитесь к **Администрации!**'),
                        view=Delete_Button(author=self.author, member=self.member, bot=self.bot, msg=self.msg)
                    )
                emb = disnake.Embed(
                    title='Снятие мута',
                    description=f'{interaction.author.mention}, вы **сняли** мут с пользователя {self.member.mention}',
                    colour=0x2f3136
                )
                emb.set_footer(text='Тип мута: Текстовый')
                emb.set_thumbnail(url=interaction.guild.icon.url)
                await interaction.response.edit_message(embed=emb,
                                                        view=Delete_Button(author=self.author, member=self.member,
                                                                           bot=self.bot, msg=self.msg))

                emb_user = disnake.Embed(
                    title='Мут',
                    description=f'Вам был **снят** мут staff `{interaction.author}`(ID: {interaction.author.id})',
                    colour=0x2f3136
                )
                emb_user.set_thumbnail(url=interaction.guild.icon.url)
                emb_user.set_footer(text='Тип мута: Текстовый')
                try:
                    await self.member.send(embed=emb_user, content=f'{self.member.mention}')
                except default_error:
                    pass

                emb_log = disnake.Embed(
                    title='Снятие мута',
                    description=f'Исполнитель: {interaction.author.mention}\n'
                                f'Пользователь: {self.member.mention}',
                    colour=0x2f3136
                )
                emb_log.set_thumbnail(url=interaction.guild.icon.url)
                emb_log.set_footer(text='Тип мута: Текстовый')
                await self.bot.get_channel(ChannelsInfo.LOG_MUTE_CHANNEL).send(embed=emb_log)

                find = jail_db.find_one({"member_id": self.member.id, "jail_type": 2})
                if find:
                    jail_db.delete_one(find)


    @disnake.ui.button(label="Назад", style=disnake.ButtonStyle.red, row=2)
    async def delete_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        if self.member.id == self.author.id:
            member = interaction.author
            desc = f'Выберите, что хотите **сделать** с **собой**!'
        else:
            member = self.member
            desc = f'Выберите, что хотите **сделать** с пользователем {self.member.mention}!'
        emb = disnake.Embed(
            title='Панель управления пользователем',
            description=desc,
            colour=0x2f3136
        )
        emb.set_thumbnail(url=member.display_avatar.url)
        btns = Action_Buttons(bot=self.bot, author=interaction.author, member=member)
        btns.msg = await interaction.response.edit_message(embed=emb, view=btns)

    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        if interaction.author.id != self.author.id:
            await interaction.send(embed=generate_classic_embed(f'Вам **недоступна** данная кнопка!'), ephemeral=True)
            return False
        else:
            return True

    async def on_timeout(self) -> None:
        if self.msg:
            try:
                await self.msg.edit(view=None)
            except default_error:
                return


class Action_Buttons(disnake.ui.View):
    msg: disnake.Message

    def __init__(self, bot: disnake.Client, member: disnake.Member, author: disnake.Member):
        super().__init__(timeout=180)
        self.bot = bot
        self.author = author
        self.member = member

        if self.author.id == self.member.id:
            for i in [self.mute_button, self.un_mute_button, self.ban_button, self.un_ban_button,
                      self.warn_button, self.un_warn_button]:
                i.disabled = True

        if self.member.guild.get_role(StaffRoles.STAFF_ROLE) in self.member.roles:
            for i in [self.mute_button, self.un_mute_button, self.ban_button, self.un_ban_button,
                      self.warn_button, self.un_warn_button]:
                i.disabled = True

        if not bool({StaffRoles.ADMINISTRATOR, StaffRoles.DEVELOPER, StaffRoles.SECURITY} & set(
                list([i.id for i in self.member.roles]))):
            for i in [self.un_mute_button, self.un_ban_button, self.un_warn_button]:
                i.disabled = False

    @disnake.ui.button(label="Мут", style=disnake.ButtonStyle.gray, row=1)
    async def mute_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        emb = disnake.Embed(
            title='Выдача мута',
            description=f'{interaction.author.mention}, **Выберите** тип **мута**, который хотите **выдать** пользователю {self.member.mention}',
            colour=0x2f3136
        )
        btns = SelectMuteButtons(bot=self.bot, member=self.member, author=interaction.author, msg=interaction.message,
                                 action_type=1)
        await interaction.response.edit_message(embed=emb, view=btns)

    @disnake.ui.button(label="АнМут", style=disnake.ButtonStyle.gray, row=1)
    async def un_mute_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        emb = disnake.Embed(
            title='Снятие мута',
            description=f'{interaction.author.mention}, **Выберите** тип **мута**, который хотите **снять** с пользователя {self.member.mention}',
            colour=0x2f3136
        )
        btns = SelectMuteButtons(bot=self.bot, member=self.member, author=interaction.author, msg=interaction.message,
                                 action_type=2)
        await interaction.response.edit_message(embed=emb, view=btns)

    @disnake.ui.button(label="Бан", style=disnake.ButtonStyle.gray, row=1)
    async def ban_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        if status_ban_user(member=self.member, guild=interaction.guild):
            await interaction.response.edit_message(
                embed=generate_classic_embed(f'Пользователь **уже забанен**!'),
                view=Delete_Button(author=self.author, member=self.member, bot=self.bot, msg=self.msg)
            )

        else:
            await interaction.response.send_modal(
                modal=ModalGiveJail(jail_type=4, bot=self.bot, author=interaction.author, member=self.member, msg=self.msg))
            await interaction.edit_original_message(
                embed=generate_classic_embed(f'Следуйте инструкциям в модальном окне!'),
                view=Back_Button(bot=self.bot, author=interaction.author, member=self.member, msg=self.msg))

    @disnake.ui.button(label="АнБан", style=disnake.ButtonStyle.gray, row=1)
    async def un_ban_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        if not status_ban_user(member=self.member, guild=interaction.guild):
            await interaction.response.edit_message(
                embed=generate_classic_embed(f'Пользователь **не забанен**!'),
                view=Delete_Button(author=self.author, member=self.member, bot=self.bot, msg=self.msg)
            )

        else:
            try:
                await self.member.remove_roles(interaction.guild.get_role(RolesInfo.BAN_ROLE),
                                               reason=f'Снятие бана staff {interaction.author.name[:25]}#{interaction.author.discriminator}')
            except default_error:
                return await interaction.response.edit_message(
                    embed=generate_classic_embed(f'Произошла **ошибка** при снятии бана. Повторите попытку позже!'),
                    view=Back_Button(bot=self.bot, author=interaction.author, member=self.member, msg=self.msg)
                )

            find = jail_db.find_one({"member_id": self.member.id, "jail_type": 4})
            if find:
                jail_db.delete_one(find)

            emb = disnake.Embed(
                title='Снятие бана',
                description=f'{interaction.author.mention}, вы **сняли** бан с пользователя {self.member.mention}',
                colour=0x2f3136
            )
            emb.set_thumbnail(url=interaction.guild.icon.url)
            await interaction.response.edit_message(embed=emb,
                                                    view=Delete_Button(author=self.author, member=self.member,
                                                                       bot=self.bot, msg=self.msg))

            emb_user = disnake.Embed(
                title='Бан',
                description=f'Вам был **снят** бан staff `{interaction.author}`(ID: {interaction.author.id})',
                colour=0x2f3136
            )
            emb_user.set_thumbnail(url=interaction.guild.icon.url)
            try:
                await self.member.send(embed=emb_user, content=f'{self.member.mention}')
            except default_error:
                pass

            emb_log = disnake.Embed(
                title='Снятие бана',
                description=f'Исполнитель: {interaction.author.mention}\n'
                            f'Пользователь: {self.member.mention}',
                colour=0x2f3136
            )
            emb_log.set_thumbnail(url=interaction.guild.icon.url)
            await self.bot.get_channel(ChannelsInfo.LOG_BAN_CHANNEL).send(embed=emb_log)

    @disnake.ui.button(label="Варн", style=disnake.ButtonStyle.gray, row=2)
    async def warn_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_modal(
            modal=ModalGiveWarn(bot=self.bot, author=interaction.author, member=self.member, msg=self.msg))
        await interaction.edit_original_message(
            embed=generate_classic_embed(f'Следуйте инструкциям в модальном окне!'),
            view=Back_Button(bot=self.bot, author=interaction.author, member=self.member, msg=self.msg))

    @disnake.ui.button(label="АнВарн", style=disnake.ButtonStyle.gray, row=2)
    async def un_warn_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        warns_user = get_warns_user(self.member)
        if warns_user == 0:
            await interaction.response.edit_message(
                embed=generate_classic_embed(f'У пользователя **нет** варнов!'),
                view=Delete_Button(author=self.author, member=self.member, bot=self.bot, msg=self.msg)
            )
        else:
            list_warns = list(jail_db.find({"member_id": self.member.id, "jail_type": 3}).sort([("time_start", 1)]))
            find_warn = list_warns[0]
            jail_db.delete_one(find_warn)

            emb = disnake.Embed(
                title='Снятие варна',
                description=f'{interaction.author.mention}, вы **сняли** варн с пользователя {self.member.mention}',
                colour=0x2f3136
            )
            emb.set_thumbnail(url=interaction.guild.icon.url)
            await interaction.response.edit_message(embed=emb,
                                                    view=Delete_Button(author=self.author, member=self.member,
                                                                       bot=self.bot, msg=self.msg))

            emb_user = disnake.Embed(
                title='Варн',
                description=f'Вам был **снят** варн staff `{interaction.author}`(ID: {interaction.author.id})',
                colour=0x2f3136
            )
            emb_user.set_thumbnail(url=interaction.guild.icon.url)
            emb.set_footer(text=f'Теперь у вас {get_warns_user(self.member)} варн(а)')
            try:
                await self.member.send(embed=emb_user, content=f'{self.member.mention}')
            except default_error:
                pass

            emb_log = disnake.Embed(
                title='Снятие варна',
                description=f'Исполнитель: {interaction.author.mention}\n'
                            f'Пользователь: {self.member.mention}',
                colour=0x2f3136
            )
            emb_log.set_thumbnail(url=interaction.guild.icon.url)
            await self.bot.get_channel(ChannelsInfo.LOG_WARN_CHANNEL).send(embed=emb_log)

    @disnake.ui.button(label="ПП", style=disnake.ButtonStyle.gray, row=2)
    async def last_warn_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        if status_last_warn_user(member=self.member, guild=interaction.guild):
            await interaction.response.edit_message(
                embed=generate_classic_embed(f'Пользователь **уже с пп**!'),
                view=Delete_Button(author=self.author, member=self.member, bot=self.bot, msg=self.msg)
            )

        else:
            await interaction.response.send_modal(
                modal=ModalGiveJail(jail_type=10, bot=self.bot, author=interaction.author, member=self.member, msg=self.msg))
            await interaction.edit_original_message(
                embed=generate_classic_embed(f'Следуйте инструкциям в модальном окне!'),
                view=Back_Button(bot=self.bot, author=interaction.author, member=self.member, msg=self.msg))

    @disnake.ui.button(label="Снять ПП", style=disnake.ButtonStyle.gray, row=2)
    async def un_last_warn_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        if not status_last_warn_user(member=self.member, guild=interaction.guild):
            await interaction.response.edit_message(
                embed=generate_classic_embed(f'Пользователь **без ПП**!'),
                view=Delete_Button(author=self.author, member=self.member, bot=self.bot, msg=self.msg)
            )

        else:
            try:
                await self.member.remove_roles(interaction.guild.get_role(RolesInfo.LAST_WARN),
                                               reason=f'Снятие последнего предупреждения staff {interaction.author.name[:25]}#{interaction.author.discriminator}')
            except default_error:
                return await interaction.response.edit_message(
                    embed=generate_classic_embed(f'Произошла **ошибка** при снятии ПП. Повторите попытку позже!'),
                    view=Back_Button(bot=self.bot, author=interaction.author, member=self.member, msg=self.msg)
                )

            find = jail_db.find_one({"member_id": self.member.id, "jail_type": 10})
            if find:
                jail_db.delete_one(find)

            emb = disnake.Embed(
                title='Снятие ПП',
                description=f'{interaction.author.mention}, вы **сняли** последнее предупрежденее с пользователя {self.member.mention}',
                colour=0x2f3136
            )
            emb.set_thumbnail(url=interaction.guild.icon.url)
            await interaction.response.edit_message(embed=emb,
                                                    view=Delete_Button(author=self.author, member=self.member,
                                                                       bot=self.bot, msg=self.msg))

            emb_user = disnake.Embed(
                title='ПП',
                description=f'Вам было **снято** последнее предупреждение staff `{interaction.author}`(ID: {interaction.author.id})',
                colour=0x2f3136
            )
            emb_user.set_thumbnail(url=interaction.guild.icon.url)
            try:
                await self.member.send(embed=emb_user, content=f'{self.member.mention}')
            except default_error:
                pass

            emb_log = disnake.Embed(
                title='Снятие ПП',
                description=f'Исполнитель: {interaction.author.mention}\n'
                            f'Пользователь: {self.member.mention}',
                colour=0x2f3136
            )
            emb_log.set_thumbnail(url=interaction.guild.icon.url)
            await self.bot.get_channel(ChannelsInfo.LOG_LAST_WARN_CHANNEL).send(embed=emb_log)

    @disnake.ui.button(label="История наказаний", style=disnake.ButtonStyle.blurple, row=3)
    async def history_jail_member(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        find_stats = user_statistic_db.find_one({"member_id": self.member.id})
        if not find_stats:
            return await interaction.response.edit_message(
                embed=generate_classic_embed(f'История **наказаний** пользователя **пуста**!'),
                view=Back_Button(bot=self.bot, author=interaction.author, member=self.member, msg=self.msg))
        finds = sorted(find_stats["history"], key=sorts_, reverse=True)
        find = group_list(finds, 10)
        mutes = find_stats['mutes']
        bans = find_stats['bans']
        all_warns = find_stats['all_warns']
        last_warns = find_stats['last_warns']
        embed = disnake.Embed(
            title=f'История наказаний - {self.member.name[:50]}#{self.member.discriminator}',
            description=f'Всего наказаний: **{mutes + bans + all_warns + last_warns}**\n'
                        f'Мутов: **{mutes}** | Банов: **{bans}** | Варнов: **{all_warns}** | ПП: **{last_warns}**\n\n',
            colour=0x2f3136
        )
        embeds = []
        text_type_status = f''
        text_date = f''
        text_author_reason = f''
        finds_jail = list(jail_db.find({"member_id": self.member.id}))
        for i in finds_jail:
            i.pop("_id", None)
        for page, group in enumerate(find):
            for index, user in enumerate(group):
                moderator = interaction.guild.get_member(user['moderator_id'])
                if moderator:
                    author = f'{moderator.mention}'
                else:
                    author = f'<@{user["moderator_id"]}>'
                text_type_status += f'{type_name[user["jail_type"]]} | {status_jail(user, finds_jail)}\n'
                text_date += f'<t:{user["time_start"]}>\n'
                text_author_reason += f'{author} | {user["reason"]}\n'
            embed.add_field(name='Тип | Статус', value=text_type_status)
            embed.add_field(name='Дата', value=text_date)
            embed.add_field(name='Исполнитель | Причина', value=text_author_reason)
            embeds.append(embed.copy())
            text_type_status = f''
            text_date = f''
            text_author_reason = f''
        if len(embeds) > 1:
            btns = Pages_Standart(embeds=embeds, time_end=180)
            await interaction.response.edit_message(embed=embeds[0], view=btns)
        else:
            await interaction.response.edit_message(embed=embeds[0], view=None)

    @disnake.ui.button(label="История ников", style=disnake.ButtonStyle.blurple, row=3)
    async def history_nicks_member(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        finds = user_nicks_db.find_one({"member_id": self.member.id})
        if not finds:
            return await interaction.response.edit_message(
                embed=generate_classic_embed(f'История **ников** пользователя **пуста**!'),
                view=Back_Button(bot=self.bot, author=interaction.author, member=self.member, msg=self.msg))

        new_list = sorted(list(finds["nicks"]), key=sorts, reverse=True)
        find = group_list(new_list, 10)
        embed = disnake.Embed(
            title=f'История ников - {self.member.name[:50]}#{self.member.discriminator}',
            description=f'Всего ников: **{len(new_list)}**\n\n',
            colour=0x2f3136
        )
        embed.set_thumbnail(url=interaction.guild.icon.url)
        embeds = []
        for page, group in enumerate(find):
            for index, user in enumerate(group):
                embed.description += f'```css\n[{user["date"]}] «{user["after_nick"]}»```'
            embeds.append(embed.copy())
            embed.description = ''
        if len(embeds) > 1:
            btns = Pages_Standart(embeds=embeds, time_end=180)
            await interaction.response.edit_message(embed=embeds[0], view=btns)
        else:
            await interaction.response.edit_message(embed=embeds[0], view=None)

    @disnake.ui.button(label="Удалить", style=disnake.ButtonStyle.red, row=4)
    async def delete_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.message.delete()

    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        if interaction.author.id != self.author.id:
            await interaction.send(embed=generate_classic_embed(f'Вам **недоступна** данная кнопка!'), ephemeral=True)
            return False
        else:
            return True

    async def on_timeout(self) -> None:
        if self.msg:
            try:
                await self.msg.edit(view=None)
            except default_error:
                return
