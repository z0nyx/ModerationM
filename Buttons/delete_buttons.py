import disnake
from disnake.ext import commands

from core.functions import *
from core.dbs import *
from core.enums import *


class Delete_Button(disnake.ui.View):
    def __init__(self, bot: disnake.Client, member: disnake.Member, author: disnake.Member, msg: disnake.Message):
        super().__init__(timeout=300)
        self.client = bot
        self.author = author
        self.member = member
        self.msg = msg

    @disnake.ui.button(label="Удалить", style=disnake.ButtonStyle.gray)
    async def delete_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.message.delete()

    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        if interaction.author.id != self.author.id:
            await interaction.send(embed=disnake.Embed(description=f'Вам **недоступна** данная кнопка!', colour=0x2f3136), ephemeral=True)
            return False
        else:
            return True

    async def on_timeout(self) -> None:
        if self.msg:
            try:
                await self.msg.edit(view=None)
            except default_error:
                return
