import pymongo
from pymongo import MongoClient
import os
import time

from dotenv import load_dotenv
load_dotenv()


cluster = MongoClient(os.getenv("MONGO_URI"))

# кластеры
cluster = cluster.ModerationMarmok
jail_db: pymongo.collection.Collection = cluster.jail
user_statistic_db: pymongo.collection.Collection = cluster.user_statistic
user_nicks_db: pymongo.collection.Collection = cluster.user_nicks
user_save_roles_db: pymongo.collection.Collection = cluster.user_save_roles

moderator_statistic_db: pymongo.collection.Collection = cluster.moderator_statistic
vacation_db: pymongo.collection.Collection = cluster.vacation_db  # отпуска
staff_db: pymongo.collection.Collection = cluster.Staff_db

# Запросы в коллекции

# Работа бд

#   Jail
{
          "member_id": id,
          "jail_type": int,
          "reason": str,
          "moderator_id": id,
          "time_start": time,
          "time_end": time
}

#   User_Statistic
{
          "member_id": id,
          "warns": int, # активные варны
          "all_warns": int,  # все варны
          "mutes": int,  # кол-во мутов
          "bans": int,
          "last_warns": int,  # кол-во банов(локальных)(при глобальном - очистка человека из бд)
          "history": [  # история наказаний пользователя
              {
                  "member_id": id,
                  "moderator_id": id,
                  "reason": str,
                  "jail_type": int,
                  "time_start": time,
                  "time_end": time
              },
              {
                  "member_id": id,
                  "moderator_id": id,
                  "reason": str,
                  "jail_type": int,
                  "time_start": time,
                  "time_end": time
              }
          ]
      }

#   Moder_Statistic
{
          "member_id": id,
          "warns": int, # всего выданных варнов
          "warns_week": int, # выданных варнов за неделю
          "mutes": int,  # всего выданных мутов
          "mutes_week": int,  # выданных мутов за неделю
          "bans": int,  # всего выданных банов
          "bans_week": int,
          "last_warns": int,
          "last_warns_week": int,  # выданных банов за неделю
          "history": [  # история наказаний пользователей
              {
                  "member_id": id,
                  "moderator_id": id,
                  "reason": str,
                  "jail_type": int,
                  "time_start": time,
                  "time_end": time
              },
              {
                  "member_id": id,
                  "moderator_id": id,
                  "reason": str,
                  "jail_type": int,
                  "time_start": int,
                  "time_end": int
              }
          ]
      }