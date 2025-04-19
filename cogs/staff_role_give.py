import asyncio
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

from Buttons.delete_buttons import *

dict_custom_id_to_role_id = {
    "curator": 1352394901463109662,
    "moderator": 1352394960472903691,
    "support": 1352385685918715934,
    "prover": 1352395014847860836,
    "eventer": 1353061760663556218,
    "bohemia": 1352403311201882214,
    "artist": 1352403373319651389,
    "painter": 1352403498548854834,
    "staff": 1353671241088634920,
}


class StaffRoleGive(commands.Cog):
    def __init__(self, bot):
        self.bot: disnake.Client = bot

    @commands.slash_command(
        name='staff_roles',
        description=f'Редактирование стафф ролей пользователя',
        dm_permission=False,
        default_member_permissions=disnake.Permissions(8),
        options=[
            disnake.Option(
                name='member',
                description=f'Укажите пользователя, с чьими стафф ролями хотите взаимодействовать',
                required=True,
                type=disnake.OptionType.user
            )
        ]
    )
    async def staff_give_roles(self, interaction: disnake.ApplicationCommandInteraction, member: disnake.Member):
        await interaction.response.defer()
        emb = disnake.Embed(
            title=f'Редактирование стафф ролей - {member.display_name}',
            description=f'{interaction.author.mention}, **Выберите** какие роли хотите редактировать у {member.display_name}',
            colour=0x2f3136
        )
        emb.set_thumbnail(url=interaction.author.display_avatar.url)
        row = disnake.ui.ActionRow()
        options_select = [
            disnake.SelectOption(label='Support', value='support'),  # 1011700154652434484
            disnake.SelectOption(label='Старый смотр.', value='curator'),  # 1011700082300694629
            disnake.SelectOption(label='Смотрящий', value='moderator'),  # 1011700191268720650
            disnake.SelectOption(label='Проверяющий', value='prover'),  # 1011750947136995478
            disnake.SelectOption(label='Ивентер', value='eventer'),  # 1011700212315725824
            disnake.SelectOption(label='Bohemia', value='bohemia'),  # 1012496747857186866
            disnake.SelectOption(label='Артист', value='artist'),  # 1013013567903125594
            disnake.SelectOption(label='Художник', value='painter'),  # 1129390774556049418

            disnake.SelectOption(label='Staff', value='staff')  # 1014527933794222203
        ]

        row.add_string_select(placeholder='Выберите роли!', min_values=1, max_values=9, options=options_select, custom_id='select_staff_roles')
        msg = await interaction.edit_original_message(embed=emb, components=[row])

        try: inter: disnake.MessageInteraction = await self.bot.wait_for(
            
            "dropdown",
            check=lambda i: i.author.id == interaction.author.id and msg.id == i.message.id, timeout=60
        )
        except asyncio.TimeoutError:
            try: await msg.delete()
            except (disnake.HTTPException, disnake.Forbidden, disnake.NotFound): return
            return

        if inter.component.custom_id == 'select_staff_roles':
            roles_list = []
            roles_text = f''
            for custom_id in inter.values:
                role = interaction.guild.get_role(dict_custom_id_to_role_id[custom_id])
                roles_list.append(role)
                roles_text += f'{role.mention}, '

            emb = disnake.Embed(
                title=f'Редактирование стафф ролей - {member.display_name}',
                description=f'{interaction.author.mention}, **Выберите** что хотите сделать ролями для пользователя {member.mention}',
                colour=0x2f3136
            )
            emb.set_thumbnail(url=interaction.author.display_avatar.url)
            emb.add_field(name='Выбранные роли:', value=f'{roles_text[:-2]}')
            row = disnake.ui.ActionRow()
            row.add_button(label='Выдать', custom_id='give_staff_roles', style=disnake.ButtonStyle.green)
            row.add_button(label='Снять', custom_id='remove_staff_roles', style=disnake.ButtonStyle.red)
            await inter.response.edit_message(embed=emb, components=[row])
            try:
                inter: disnake.MessageInteraction = await self.bot.wait_for("button_click", timeout=120,
                      check=lambda i: i.author.id == interaction.author.id and i.message.id == msg.id)
            except asyncio.TimeoutError:
                await inter.edit_original_message(components=[])
                return
            if inter.component.custom_id == 'give_staff_roles':
                try:
                    await member.add_roles(*roles_list)
                except default_error:
                    return await inter.response.edit_message(
                        embed=generate_classic_embed('При **выдаче** ролей произошла ошибка! Повторите попытку!'),
                        view=Delete_Button(author=inter.author, member=member, bot=self.bot, msg=msg))

                emb = disnake.Embed(
                    title=f'Редактирование стафф ролей - {member.display_name}',
                    description=f'{interaction.author.mention}, **Вы** успешно **выдали** стафф роли пользователяю {member.mention}',
                    colour=0x2f3136
                )
                emb.add_field(name='Выбранные роли:', value=f'{roles_text[:-2]}')
                emb.set_thumbnail(url=interaction.author.display_avatar.url)
                await inter.response.edit_message(embed=emb, components=[])
            elif inter.component.custom_id == 'remove_staff_roles':
                try:
                    await member.remove_roles(*roles_list)
                except default_error:
                    return await inter.response.edit_message(
                        embed=generate_classic_embed('При **снятии** ролей произошла ошибка! Повторите попытку!'),
                        view=Delete_Button(author=inter.author, member=member, bot=self.bot, msg=msg))

                emb = disnake.Embed(
                    title=f'Редактирование стафф ролей - {member.display_name}',
                    description=f'{interaction.author.mention}, **Вы** успешно **сняли** стафф роли пользователяю {member.mention}',
                    colour=0x2f3136
                )
                emb.add_field(name='Выбранные роли:', value=f'{roles_text[:-2]}')
                emb.set_thumbnail(url=interaction.author.display_avatar.url)
                await inter.response.edit_message(embed=emb, components=[])


def setup(bot):
    bot.add_cog(StaffRoleGive(bot))
    print('Ког: "Выдача стафф ролей" загрузился!')
