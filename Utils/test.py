# -*- coding: utf-8 -*-
"""
@author: Neo
@software: PyCharm
@file: test.py
@time: 2023/3/5 15:34
说明:
"""
import datetime
import multiprocessing as mp
from utils import get_season_key_day,get_cur_info

today = datetime.date.today()
for day in ['2022-12-12', '2023-02-02', '2023-05-12', '2023-09-02']:
    today = datetime.datetime.strptime(day, '%Y-%m-%d')
    print(get_season_key_day(today))

# num_cores = int(mp.cpu_count())
# print("本地计算机有: " + str(num_cores) + " 核心")