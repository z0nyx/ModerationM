
import disnake

from core.functions import *
from Buttons.ActionButtons import Action_Buttons
from core.enums import *
from Functions.dicts import *
from Functions.Checker import *

"""
jail_types
1 - voice mute 
2 - text mute
3 - unmute  #
4 - ban
5 - unban  # 
6 - warn
7 - unwarn  #
"""


class Action(commands.Cog):
    def __init__(self, bot: disnake.Client):
        self.bot = bot

    @commands.slash_command(
        name='action',
        description=f'Открыть меню взаимодействия с пользователем',
        dm_permission=False,
        options=[
            disnake.Option(
                name='user',
                description=f'Укажите пользователя для взаимодействия с ним',
                required=False,
                type=disnake.OptionType.user
            )
        ]
    )
    async def action_command(self, interaction: disnake.GuildCommandInteraction, user: disnake.Member = None):
        await interaction.response.defer()
        if len([role.id for role in interaction.author.roles if role.id in staff_roles]) == 0:
            return await interaction.send(embed=generate_classic_embed("У вас **нет** доступа!"), ephemeral=True)
        find = moderator_statistic_db.find_one({"member_id": interaction.author.id})
        if staff_check(user):
            return await interaction.send(embed = generate_classic_embed("Произошла ошибка! Вы не можете выполнить эту команду над этим пользователем!"), ephemeral=True)
        if not find:
            generate_moderator_profile_post(guild=interaction.guild, member=interaction.author)
        if user and user.bot:
            return await interaction.send(embed=generate_classic_embed(f'Данная команда **недоступна** для применения на **ботов**!'), ephemeral=True)
        if not user:
            member = interaction.author
            desc = f'Выберите, что хотите **сделать** с **собой**!'
        else:
            member = user
            desc = f'Выберите, что хотите **сделать** с пользователем {user.mention}!'
        emb = disnake.Embed(
            title='Панель управления пользователем',
            description=desc,
            colour=0x2f3136
        )
        emb.set_thumbnail(url=member.display_avatar.url)
        btns = Action_Buttons(bot=self.bot, author=interaction.author, member=member)
        btns.msg = await interaction.edit_original_message(embed=emb, view=btns)


def setup(bot):
    bot.add_cog(Action(bot))
    print('Ког: "/action" загрузился!')
