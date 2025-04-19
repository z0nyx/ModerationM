import disnake

dict_prime_times = {
    1: '6:00-12:00',
    2: '12:00-18:00',
    3: '18:00-00:00',
    4: '00-6:00',
    0: 'Отсутствует'
}

yes_no_dict = {
    1: "Активен",
    0: "Отсутствует"
}

dict_bool = {
    True: "🟢",
    False: "⚪"
}


def generate_moderator_profile_post(
        guild: disnake.Guild,
        member: disnake.Member
):
    post = {
        "guild_id": guild.id,
        "member_id": member.id,
        "points": 0,  # баллы стаффа

        "voice": 0,  # скок войс актива. Всего
        "voice_day": 0,  # войс за день
        "voice_week": 0,  # войс за неделю

        "mutes": 0,  # мутов. Всего
        "mutes_week": 0,  # мутов. Неделя

        "bans": 0,  # банов. Всего
        "bans_week": 0,  # банов. Неделя

        "warns": 0,  # варнов. Всего
        "warns_week": 0,  # варнов. Неделя

        "last_warns": 0, #последних пп. Всего
        "last_warns_week": 0, #последних пп. Неделя

        "staff_warns": 0,  # выговоры
        "vacation": 0,  # отпуск. Если есть - время до которого

        "prime_time": 0,  # когда прайм тайм
        "prime_voice": 0  # скок по прайм тайму. Онли неделя
    }
    return post

