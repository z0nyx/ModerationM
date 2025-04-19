from disnake.ext import commands
import time
import disnake
import pymongo
from typing import List
import re
import asyncio
import requests
from delorean import Delorean

from core.dbs import *
from core.enums import *


def convert_time(online: int) -> str:
    hour = online // 60
    minute = online % 60
    if hour < 1: hour = 0
    if minute < 1 or minute >= 60: minute = 0
    return f'{hour} ч, {minute} м'


def now_time(option: int) -> str:
    d = Delorean(timezone='Europe/Moscow')
    hour = d.datetime.hour
    minute = d.datetime.minute

    year = d.datetime.year
    month = d.datetime.month
    day = d.datetime.day
    if option == 1:
        return f'{hour}'
    elif option == 2:
        return f'{hour}:{minute}'
    elif option == 3:
        return f'{day}.{month}.{year}'
    else:
        return f'{hour}:{minute} {day}.{month}.{year}'


def group_list(
        array: (list, tuple, set), # type: ignore
        group_len: int = 2,
        space: int = 0,
        *,
        limit: int = None,
        add_lost: bool = True,
        reverse_groups: bool = True
) -> (list, tuple, set): # type: ignore
    length = len(array)
    group_len = int(group_len)
    space = int(space)
    if limit is None:
        limit = length

    if group_len == 0:
        raise ValueError('You can\'t group using Zero size group!')
    elif space < 0:
        raise ValueError('You can\'t use spaces which are less than Zero!')
    elif limit < 0:
        raise ValueError('You can\'t use limit which is less than Zero')
    elif limit == 0:
        return []
    elif length <= group_len:
        return [array]

    new_array = []

    def dry_appending(p, h):
        if group_len > 0:
            appending = array[p:h]
        else:
            if not position:
                appending = array[h:]
            else:
                appending = array[h:p]
            if reverse_groups:
                appending = appending[::-1]
        if appending:
            new_array.append(appending)

    k = 1 if group_len >= 0 else -1
    position = 0

    while abs(hold := position + group_len) <= length and limit:
        dry_appending(position, hold)
        position = hold + space * k

        if abs(position) >= length:
            position -= space * k
        limit -= 1
    else:
        if add_lost and limit:
            dry_appending(position, position + group_len)
    return new_array


