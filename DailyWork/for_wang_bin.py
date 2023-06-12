# -*- coding: utf-8 -*-
"""
@author: Neo
@software: PyCharm
@file: for_wang_bin.py
@time: 2023/6/5 16:10
说明:
"""
import datetime
import numpy as np
import pandas as pd
import pymongo
import jqdatasdk as jq
from ShuiDQReport.settings import CLIENT, DATABASE_STAT, DATABASE_BASIC, DATABASE_STRATEGY, DATABASE_BACKTEST
from Utils.utils import trans_str_to_float64, get_screen_size
from Datas.load_data import LoadData

client = pymongo.MongoClient(CLIENT)
db_basic = client[DATABASE_BASIC]

ld = LoadData()
df_data = ld.get_bt_strategy(stra_name="per_2_4")
df = df_data[df_data.date > '2009-01-01'].copy()
df['net_value5'] = (df.chg5 + 1).cumprod()

df.to_csv("stra_2_4.csv")
#
# df_bench = pd.DataFrame(db_basic['w_bench_close'].find(
#     {"date": {'$gte': '2018-01-01', '$lte': '2023-12-31'}}, {"_id": 0}, batch_size=1000000))
# df_bench['chg_300'] = df_bench['000300.SH'].pct_change()
# df_bench = df_bench[df_bench.date > '2019-01-01'].copy()
# df_bench['net_value'] = (df_bench.chg_300 + 1).cumprod()
# df_bench.to_csv("chg_300.csv")
