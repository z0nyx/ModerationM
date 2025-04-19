import disnake
from disnake.ext import tasks
import asyncio

from core.enums import *
from core.functions import *
from core.dbs import *
from Functions.TimeConvent import *
from Functions.dicts import *


class Activity(commands.Cog):
    def __init__(self, bot: disnake.Client):
        self.bot = bot

        self.jail_check.start()
        self.moderator_active_voice.start()

    @tasks.loop(seconds=5)
    async def jail_check(self):
        await self.bot.wait_until_ready()
        guild = self.bot.get_guild(ClientInfo.BOT_GUILD_ID)
        if not guild:
            return
        for find in list(jail_db.find()):
            if find['time_end'] < int(time.time()):
                member = guild.get_member(find['member_id'])
                if not member:
                    return
                jail_id = find['jail_type']
                if jail_id == 1 or jail_id == 2:
                    if jail_id == 1:
                        mute_name = 'Голосовой'
                        role_id = RolesInfo.VOICE_MUTE_ROLE
                    elif jail_id == 2:
                        mute_name = 'Текстовый'
                        role_id = RolesInfo.CHAT_MUTE_ROLE
                    else: return

                    try:
                        await member.remove_roles(guild.get_role(role_id))
                    except default_error:
                        pass

                    emb_user = disnake.Embed(
                        title='Мут',
                        description=f'Вам был **снят** мут по истечению времени!',
                        colour=0x2f3136
                    )
                    emb_user.set_thumbnail(url=guild.icon.url)
                    emb_user.set_footer(text=f'Тип мута: {mute_name}')
                    try:
                        await member.send(embed=emb_user, content=f'{member.mention}')
                    except default_error:
                        pass

                    emb_log = disnake.Embed(
                        title='Снятие мута',
                        description=f'Исполнитель: `Система`\n'
                                    f'Пользователь: {member.mention}',
                        colour=0x2f3136
                    )
                    emb_log.add_field(name='Причина', value=f'Истечение срока действия мута')
                    emb_log.set_footer(text=f'Тип мута: {mute_name}')
                    emb_log.set_thumbnail(url=guild.icon.url)
                    await self.bot.get_channel(ChannelsInfo.LOG_MUTE_CHANNEL).send(embed=emb_log)

                    jail_db.delete_one(find)
                elif jail_id == 4:
                    try:
                        await member.remove_roles(guild.get_role(RolesInfo.BAN_ROLE))
                    except default_error:
                        pass

                    emb_user = disnake.Embed(
                        title='Снятие бана',
                        description=f'Вам был **снят** бан по истечению времени!',
                        colour=0x2f3136
                    )
                    emb_user.set_thumbnail(url=guild.icon.url)
                    emb_user.set_footer(text='Впредь будьте осторожны!')
                    try:
                        await member.send(embed=emb_user, content=f'{member.mention}')
                    except default_error:
                        pass

                    emb_log = disnake.Embed(
                        title='Снятие бана',
                        description=f'Исполнитель: `Система`\n'
                                    f'Пользователь: {member.mention}',
                        colour=0x2f3136
                    )
                    emb_log.add_field(name='Причина', value=f'Истечение срока действия бана')
                    emb_log.set_thumbnail(url=guild.icon.url)
                    await self.bot.get_channel(ChannelsInfo.LOG_BAN_CHANNEL).send(embed=emb_log)

                    jail_db.delete_one(find)
                elif jail_id == 6:
                    emb_user = disnake.Embed(
                        title='Варн',
                        description=f'Вам был **снят** варн по истечению времени!',
                        colour=0x2f3136
                    )
                    emb_user.set_thumbnail(url=guild.icon.url)
                    try:
                        await member.send(embed=emb_user, content=f'{member.mention}')
                    except default_error:
                        pass

                    emb_log = disnake.Embed(
                        title='Снятие варна',
                        description=f'Исполнитель: `Система`\n'
                                    f'Пользователь: {member.mention}',
                        colour=0x2f3136
                    )
                    emb_log.add_field(name='Причина', value=f'Истечение срока действия варна')
                    emb_log.set_thumbnail(url=guild.icon.url)
                    await self.bot.get_channel(ChannelsInfo.LOG_WARN_CHANNEL).send(embed=emb_log)

                    jail_db.delete_one(find)
                    user_statistic_db.update_one({"member_id": member.id}, {"$inc": {"warns": -1}})
                else:
                    ...

    @tasks.loop(seconds=60)
    async def moderator_active_voice(self):
        async def checks(member: disnake.Member, moderator_role: disnake.Role):
            if moderator_role in member.roles:
                if not member.voice.deaf and not member.voice.mute and not member.voice.self_deaf:
                    find = moderator_statistic_db.find_one({"member_id": member.id})
                    if not find:
                        moderator_statistic_db.insert_one(generate_moderator_profile_post(guild=member.guild, member=member))

                    moderator_statistic_db.update_one({"member_id": member.id, "guild_id": member.guild.id},
                                          {"$inc": {"voice": 1, "voice_day": 1, "voice_week": 1}}, True)

        await self.bot.wait_until_ready()
        guild: disnake.Guild = self.bot.get_guild(ClientInfo.BOT_GUILD_ID)
        verify_category: disnake.CategoryChannel = guild.get_channel(ChannelsInfo.MODERATION_CHANNELS_CATEGORY)
        moderator_role = guild.get_role(StaffRoles.MODERATOR)
        for channel in verify_category.voice_channels:
            for member in channel.members:
                asyncio.create_task(checks(member, moderator_role))

    @commands.Cog.listener()
    async def on_member_update(self, before: disnake.Member, after: disnake.Member):
        if before.nick != after.nick:
            after_nick = after.nick
            if not after.nick:
                after_nick = 'Сбросил'
            post = {
                "date": now_date_time(),
                "times": int(time.time()),
                "after_nick": after_nick
            }
            user_nicks_db.update_one({"member_id": after.id}, {"$push": {"nicks": post}}, True)

    @commands.Cog.listener()
    async def on_member_remove(self, member: disnake.Member):
        saved_roles = []
        bot_role_position = member.guild.me.top_role.position
        for role in member.roles:
            if role.id not in [RolesInfo.BUST_ROLE, RolesInfo.EVERYONE_ID]:
                if role.position < bot_role_position:
                    saved_roles.append(role.id)
        user_save_roles_db.insert_one({
            "member_id": member.id,
            "guild_id": member.guild.id,
            "roles": saved_roles
        })

    @commands.Cog.listener()
    async def on_member_join(self, member: disnake.Member):
        find_roles = user_save_roles_db.find_one({"member_id": member.id})
        if find_roles:
            roles_list = [member.guild.get_role(role) for role in find_roles['roles']]
            await member.add_roles(*roles_list)
        else:
            find_jail = list(jail_db.find({"member_id": member.id}))
            if find_jail:
                for find in find_jail:
                    if find['jail_type'] == 1:
                        await member.add_roles(member.guild.get_role(RolesInfo.VOICE_MUTE_ROLE))
                    elif find['jail_type'] == 2:
                        await member.add_roles(member.guild.get_role(RolesInfo.CHAT_MUTE_ROLE))
                    elif find["jail_type"] == 4:
                        await member.add_roles(member.guild.get_role(RolesInfo.BAN_ROLE))



def setup(bot):
    bot.add_cog(Activity(bot))
    print('Ког: "Активность" загрузился!')
