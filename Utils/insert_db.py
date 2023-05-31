# -*- coding: utf-8 -*-
"""
@author: Neo
@software: PyCharm
@file: insert_db_.py
@time: 2023/3/9 12:44
说明:
"""
import json
from pymongo.errors import DuplicateKeyError
import pandas as pd


def insert_db_from_df(table=None, df=None):
    if table is None or df is None:
        raise Exception("必须传入数据表，数据(df格式)")
    if df.empty:
        raise Exception("数据 df 为空，请检查！目标table：{}".format(table))
    df = df.copy()
    df.reset_index(inplace=True, drop=True)  # 丢弃DF索引后插入数据库
    data = list(json.loads(df.T.to_json()).values())
    txt_errors = []
    try:
        table.insert_many(data)
    except DuplicateKeyError:
        pass  # 插入重复数据，不做处理
    except Exception as e:
        txt_errors.append("插入错误（非重复），将试着一条一条的插入。数据表：{}，第一条记录：{}".format(table, data[0]))
        for d in data:
            try:
                table.insert_one(d)
            except DuplicateKeyError:
                pass  # 插入重复数据，不做处理
            except Exception as e:
                txt_errors.append("有条信息没插入 {}，请检查:{}".format(table, d))
    return txt_errors


def df_trans_to_str_and_insert_db(table, df: pd.DataFrame):
    df_str = df.astype(str)
    errors = insert_db_from_df(table, df_str)
    if len(errors) > 0:
        print(errors)
    return errors
