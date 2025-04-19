import disnake
from core.enums import *
from delorean import Delorean


def prime_time_checker(key: int) -> bool:
    """
    :param key:
    1 - 06:00 - 12:00;
    2 - 12:00 - 18:00;
    3 - 18:00 - 00:00;
    4 - 00:00 - 06:00;
    :return: Сейчас прайм тайм человека или нет
    """
    d = Delorean(timezone='Europe/Moscow')
    dict_prime_times = {
        0: 4, 1: 4, 2: 4, 3: 4, 4: 4, 5: 4,
        6: 4, 7: 1, 8: 1, 9: 1, 10: 1, 11: 1,
        12: 1,13: 2, 14: 2, 15: 2, 16: 2, 17: 2,
        18: 2, 19: 3, 20: 3, 21: 3, 22: 3, 23: 3
    }
    hour = d.datetime.hour
    return key == dict_prime_times[hour]

def staff_check(member: disnake.Member):
    guild = member.guild
    roles = [
        StaffRoles.MARMOK,
        StaffRoles.OLEG,
        StaffRoles.SQUAD,
        StaffRoles.ADMINISTRATOR,
        StaffRoles.DEVELOPER,
        StaffRoles.SECURITY,
        StaffRoles.CURATOR,
        StaffRoles.MODERATOR,
        StaffRoles.STAFF_ROLE
        ]
    return any(guild.get_role(role_id) in member.roles for role_id in roles)

def chief_check(member: disnake.Member):
    guild = member.guild
    roles = [StaffRoles.MARMOK, StaffRoles.OLEG, StaffRoles.SQUAD, StaffRoles.ADMINISTRATOR, StaffRoles.DEVELOPER, StaffRoles.SECURITY]
    for role_id in roles:
        if guild.get_role(role_id) in member.roles:
            return True  # значит высший стафф

    return False  # обычный


def moderator_check(member: disnake.Member):
    guild = member.guild
    support_role = guild.get_role(StaffRoles.STAFF_ROLE)
    return support_role in member.roles
