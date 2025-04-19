import disnake
import time
from core.enums import *
from core.dbs import *


def status_mute_user(member: disnake.Member, guild: disnake.Guild, mute_type: int) -> bool:
    if mute_type == 1:  # voice
        return guild.get_role(RolesInfo.VOICE_MUTE_ROLE) in member.roles
    elif mute_type == 2:  # chat
        return guild.get_role(RolesInfo.CHAT_MUTE_ROLE) in member.roles
    else:
        return False


def status_ban_user(member: disnake.Member, guild: disnake.Guild) -> bool:
    return guild.get_role(RolesInfo.BAN_ROLE) in member.roles

def status_last_warn_user(member: disnake.Member, guild: disnake.Guild) -> bool:
    return guild.get_role(RolesInfo.LAST_WARN) in member.roles

async def status_permban_user(member: disnake.Member, guild: disnake.Guild) -> bool:
    try:
        a = await guild.fetch_ban(member)
    except disnake.NotFound:
        return False
    except (disnake.Forbidden, disnake.HTTPException):
        return True
    return bool(a)


def get_warns_user(member: disnake.Member) -> int:
    find = user_statistic_db.find_one({"member_id": member.id})
    if find:
        return find['warns']
    else:
        return 0


def status_jail(find: dict, finds: list) -> str:
    if find in finds:
        return 'Активен'
    else:
        return 'Истек'

