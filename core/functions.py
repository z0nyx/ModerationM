import disnake
from disnake.ext import commands
from typing import List
import re
from core.dbs import *
from delorean import Delorean
import time


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


def generate_classic_embed(text: str) -> disnake.Embed:
    emb = disnake.Embed(description=text, colour=0x2f3136)
    return emb


def sorts(dicts: dict):  # функция для сортировки
    return dicts["times"]


def sorts_(dicts: dict):  # функция для сортировки
    return dicts["time_start"]

