# -*- coding: utf-8 -*-
"""
@author: Neo
@software: PyCharm
@file: load_data.py
@time: 2023/5/22 17:19
说明:
"""
import ctypes
import difflib
import numpy as np
import pandas as pd
import pymongo
from pymongo import IndexModel, ASCENDING
from Utils.insert_db import insert_db_from_df
from ShuiDQReport.settings import CLIENT, DATABASE_STAT, DATABASE_BASIC, DATABASE_STRATEGY
from Utils.utils import trans_str_to_float64

pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
# 显示所有列
pd.set_option('display.max_columns', None)
# True就是可以换行显示。设置成False的时候不允许换行
pd.set_option('expand_frame_repr', False)


class InsertDb:
    def __init__(self):
        self.csv_dir = 'D:/ShareDoc/实盘净值/'
        client = pymongo.MongoClient(CLIENT)
        self.db_stat = client[DATABASE_STAT]

    def close(self):
        self.db_stat.client.close()

    def insert_db(self, csv_name='2022Q3交割单查询.xls.csv', update=True):
        csv_file = self.csv_dir + csv_name
        df_csv = pd.read_excel(csv_file, engine="openpyxl", header=0)
        # print(df_csv)

        table = self.db_stat['dq_alpha_one']
        if update:
            date = list(table.find({}, {"_id": 0, "净值日期": 1}).sort('净值日期', -1).limit(1))[0]['净值日期']
            print("上次更新日期：{}".format(date))
            df_csv = df_csv[df_csv['净值日期'] > date].copy()
            df_csv.dropna(inplace=True)
            if df_csv.empty:
                print("没有最新数据，不做更新")
                return
            print(df_csv)
        else:
            table.create_index([("净值日期", pymongo.DESCENDING)], background=True, unique=True)
        #
        insert_db_from_df(table=table, df=df_csv)


def update_db():
    inst = InsertDb()
    inst.insert_db(csv_name='产品净值_碓泉可变阿尔法成长一号私募证券投资基金_2019-02-01_2023-05-22.xlsx')
    inst.close()


if __name__ == '__main__':
    update_db()
