from enum import IntEnum

import disnake


class Color(IntEnum):
    GRAY = 0x2F3136
    GREEN = 0x00FF00
    RED = 0xFF0000
    BLUE = 0x0000FF


class ClientInfo(IntEnum):
    ZONYX = .
    BOT_GUILD_ID = .  #new era


class ChannelsInfo(IntEnum):
    LOG_MUTE_CHANNEL = .
    LOG_BAN_CHANNEL = .
    LOG_WARN_CHANNEL = .
    LOG_LAST_WARN_CHANNEL = .

    MODERATION_CHANNELS_CATEGORY = .
    VACATION_CHANNEL = .
    WARNS_LOG_CHANNEL = .  # staff
    REPORT_CHANNEL = . 


class RolesInfo(IntEnum):
    BAN_ROLE = .
    VOICE_MUTE_ROLE = .
    CHAT_MUTE_ROLE = .
    LAST_WARN = .

    BUST_ROLE = .
    EVERYONE_ID = .
    VACATION_ROLE = .


class StaffRoles(IntEnum):
    MARMOK = .
    OLEG = .
    SQUAD = .
    ADMINISTRATOR = . #moder
    DEVELOPER = .
    SECURITY = . #support
    CURATOR = . #high smotr
    MODERATOR = . #smotr

    STAFF_ROLE = .


staff_roles = [StaffRoles.MARMOK, StaffRoles.OLEG, StaffRoles.SQUAD,StaffRoles.ADMINISTRATOR, StaffRoles.DEVELOPER, StaffRoles.SECURITY, StaffRoles.CURATOR, StaffRoles.MODERATOR, StaffRoles.STAFF_ROLE]

default_error = (disnake.Forbidden, disnake.HTTPException)

full_errors = (disnake.Forbidden, disnake.HTTPException, disnake.NotFound, disnake.InvalidData, TypeError, ValueError)
