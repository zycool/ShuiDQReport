# -*- coding: utf-8 -*-
"""
@author: Neo
@software: PyCharm
@file: load_datas.py
@time: 2023/5/11 12:18
说明:
"""
import ctypes
import pandas as pd
import pymongo
from ShuiDQReport.settings import CLIENT, DATABASE_STAT, DATABASE_BASIC
from Utils.utils import trans_str_to_float64

pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
# 显示所有列
pd.set_option('display.max_columns', None)
# True就是可以换行显示。设置成False的时候不允许换行
pd.set_option('expand_frame_repr', False)


def get_screen_size():
    user32 = ctypes.windll.user32
    screen_size0 = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    return screen_size0


class LoadData:
    def __init__(self):
        self._client = pymongo.MongoClient(CLIENT)
        self.db_stat = self._client[DATABASE_STAT]
        self.db_basic = self._client[DATABASE_BASIC]
        self.df_loss = None
        self.screen_size = get_screen_size()

    def close(self):
        self._client.close()

    def _load_df_loss(self):
        if self.df_loss is None:
            df_loss = pd.DataFrame(self.db_stat['trade_loss'].find({}, {"_id": 0, }))
            self.df_loss = df_loss
        return self.df_loss

    def _load_tips_date(self):
        df_loss = self._load_df_loss()
        df_loss['date'] = df_loss.date.apply(lambda x: x[:4] + "-" + x[4:6] + "-" + x[-2:])
        dates = df_loss.date.unique().tolist()
        df1 = df_loss[['date', 'mis_sum', 'mis_mean_sum', 'mis_cent', 'mis_mean_cent']].copy()
        df1['类型'] = "All"
        df1['size'] = abs(df1.mis_sum)
        df1['hue'] = df1.mis_sum.apply(lambda x: 1 if x > 0 else 0)
        df1['size_m'] = abs(df1.mis_mean_sum)
        df1['hue_m'] = df1.mis_mean_sum.apply(lambda x: 1 if x > 0 else 0)

        df2 = df_loss[['date', 'b_mis_sum', 'b_mis_mean_sum', 'b_mis_cent', 'b_mis_mean_cent']].copy()
        df2.rename(columns={"b_mis_sum": "mis_sum", "b_mis_mean_sum": "mis_mean_sum", "b_mis_cent": "mis_cent",
                            "b_mis_mean_cent": "mis_mean_cent"}, inplace=True)
        df2['类型'] = "Rebalance"
        df2['size'] = abs(df2.mis_sum)
        df2['hue'] = df2.mis_sum.apply(lambda x: 1 if x > 0 else 0)
        df2['size_m'] = abs(df2.mis_mean_sum)
        df2['hue_m'] = df2.mis_mean_sum.apply(lambda x: 1 if x > 0 else 0)

        df = pd.concat([df1, df2], axis=0)
        df.sort_values('date', inplace=True)

        df_rm = pd.DataFrame(self.db_basic['w_wind_A'].find(
            {"date": {'$lte': dates[-1], '$gte': dates[0]}}, {"_id": 0, }))
        df_rm = trans_str_to_float64(df_rm, trans_cols=['rm', ])
        df = pd.merge(df, df_rm, on='date')
        # df['month'] = df.date.apply(lambda x: x[:7])
        return df

    def load_test_data(self, t="tips"):
        match t:
            case "tips":
                return self._load_tips_date()
            case "line":
                return self._load_df_loss()
