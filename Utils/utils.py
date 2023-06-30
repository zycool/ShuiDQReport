# -*- coding: utf-8 -*-
"""
@author: Neo
@software: PyCharm
@file: utils.py
@time: 2023/3/2 13:37
说明:
"""
import os
import subprocess
import sys
import time
import ctypes
import pandas as pd
import datetime
from inspect import currentframe, stack, getmodule
from dateutil.relativedelta import relativedelta
from decimal import Decimal


def get_screen_size():
    user32 = ctypes.windll.user32
    screen_size0 = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    return screen_size0


def get_root_path():
    # 获取根目录
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # 修改成linux目录
    base_dir = base_dir.replace('\\', '/')
    return base_dir


class ParamsError(Exception):
    pass


def to_date(date):
    """
    >>> convert_date('2015-1-1')
    datetime.date(2015, 1, 1)

    >>> convert_date('2015-01-01 00:00:00')
    datetime.date(2015, 1, 1)

    >>> convert_date(datetime.datetime(2015, 1, 1))
    datetime.date(2015, 1, 1)

    >>> convert_date(datetime.date(2015, 1, 1))
    datetime.date(2015, 1, 1)
    """
    if date:
        if ':' in date:
            date = date[:10]
        return datetime.datetime.strptime(date, '%Y-%m-%d').date()
    elif isinstance(date, datetime.datetime):
        return date.date()
    elif isinstance(date, datetime.date):
        return date
    elif date is None:
        return None
    raise ParamsError("type error")


def is_list(l):
    return isinstance(l, (list, tuple))


def convert_fields_to_str(s):
    if isinstance(s, (list, tuple)):
        res = [str(item) for item in s]
        return res
    else:
        raise ParamsError("参数应该是 list or tuple")


def get_mac_address():
    import uuid
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:].upper()
    return '%s:%s:%s:%s:%s:%s' % (mac[0:2], mac[2:4], mac[4:6], mac[6:8], mac[8:10], mac[10:])


def get_security_type(security):
    exchange = security[-4:]
    code = security[:-5]
    if code.isdigit():
        if exchange == "XSHG":
            if code >= "600000" or code[0] == "9":
                return "stock"
            elif code >= "500000":
                return "fund"
            elif code[0] == "0":
                return "index"
            elif len(code) == 8 and code[0] == '1':
                return "option"
        elif exchange == "XSHE":
            if code[0] == "0" or code[0] == "2" or code[:3] == "300":
                return "stock"
            elif code[:3] == "399":
                return "index"
            elif code[0] == "1":
                return "fund"
        else:
            raise Exception("找不到标的%s" % security)
    else:
        if exchange in ("XSGE", "XDCE", "XZCE", "XINE", "CCFX"):
            if len(code) > 6:
                return "option"
            return "future"
    return 0


def isatty(stream=None):
    stream = stream or sys.stdout
    _isatty = getattr(stream, 'isatty', None)
    return _isatty and _isatty()


def get_season_key_day(today):
    """
    :param today: 为 datetime.datetime.date
    :return:
    """
    this_month_first_day = datetime.date(today.year, today.month - (today.month - 1) % 3 + 2, 1)  # 本月第一天
    this_season_end_day = this_month_first_day + relativedelta(months=1, days=-1)  # 本季度 最后一天
    last_seaon_end_day = this_season_end_day - relativedelta(months=3, )  # 上季度 最后一天
    last_seaon_end_day_2nd = last_seaon_end_day - relativedelta(months=3, )  # 上上季度 最后一天
    last_seaon_end_day_3nd = last_seaon_end_day_2nd - relativedelta(months=3, )  # 上上上季度 最后一天
    res_list = list(map(deal_with_31, [last_seaon_end_day, last_seaon_end_day_2nd, last_seaon_end_day_3nd]))

    year_end_day = datetime.date(today.year, 12, 31)  # 本年最后一天
    last_year_end_day = year_end_day + relativedelta(years=-1)  # 去年 最后一天
    res_list.append(last_year_end_day.isoformat())
    last_year_end_day_2nd = year_end_day + relativedelta(years=-2)  # 去去年 最后一天
    res_list.append(last_year_end_day_2nd.isoformat())
    return res_list


def deal_with_31(date):
    if date.month == 3 or date.month == 12:
        date = datetime.date(date.year, date.month, 31)
    return date.isoformat()


def get_cur_info():
    f_current_line = str(currentframe().f_back.f_lineno)  # 哪一行调用的此函数
    mod = getmodule(stack()[1][0])  # 调用函数的信息
    f = mod.__file__
    module_name = mod.__name__  # 函数名
    return {'文件': f.replace('\\', '/'), '模块': module_name, '行号': f_current_line}


def trans_str_to_decimal(df_src: pd.DataFrame, exp_cols=None, trans_cols=None) -> pd.DataFrame:
    """
    对df中指定 trans_cols 各个列(除了exp_cols中)转换为 Decimal
    如果exp_cols，trans_cols同时指定，最终返回的以 exp_cols 指定的为准
    :param trans_cols:
    :param df_src:
    :param exp_cols:
    :return:
    """
    if trans_cols is None and exp_cols is None:
        raise Exception("类型转换时，排除列列表和指定转换列列表不能同时为空，至少指定一个")
    if exp_cols is not None:
        for v in df_src.columns.values:
            if v not in exp_cols:
                df_src[v] = df_src[v].apply(Decimal)
    elif trans_cols is not None:
        for v in df_src.columns.values:
            if v in trans_cols:
                df_src[v] = df_src[v].apply(Decimal)
    return df_src


def trans_str_to_float64(df: pd.DataFrame, exp_cols=None, trans_cols=None) -> pd.DataFrame:
    df_src = df.copy()
    if trans_cols is None and exp_cols is None:
        raise Exception("类型转换时，排除列列表和指定转换列列表不能同时为空，至少指定一个")
    all_cols = list(df_src.columns.values)
    if exp_cols is not None:
        for col in exp_cols:
            all_cols.remove(col)
        df_src[all_cols] = df_src[all_cols].astype('float64')
    elif trans_cols is not None:
        df_src[trans_cols] = df_src[trans_cols].astype('float64')
    return df_src


def my_decimal_format(df, cols):
    df = df.copy()
    for col in cols:
        df[col] = df[col].apply(lambda x: format(x, '.10%'))
    return df


def throw_exception(name):
    print('子进程%s发生异常,进程号为%s' % (name, os.getpid()))
    cmd = 'taskkill /im ' + str(os.getpid()) + ' /F'
    res = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    print(res.stdout.read())
    print(res.stderr.read())
    time.sleep(2)


def get_week_month_date(week=False, month=False):
    """获取本周（本月）的第一天和最后一天"""
    today = datetime.datetime.today().date()
    if week:
        this_week_start = today - datetime.timedelta(days=today.weekday())
        this_week_end = today + datetime.timedelta(days=6 - today.weekday())
        return str(this_week_start), str(this_week_end)
    elif month:
        this_month_start = datetime.datetime(today.year, today.month, 1)
        this_month_end = datetime.datetime(today.year, today.month + 1, 1) - datetime.timedelta(
            days=1) + datetime.timedelta(
            hours=23, minutes=59, seconds=59)
        return str(this_month_start)[:10], str(this_month_end)[:10]
    return str(today), str(today)


def stamp2time(timeStamp, fmt='T'):
    """
    功能：将时间戳转换成日期函数 例如：1606708276268 ==》2020-11-30 11:51:16
    参数：timeStamp 时间戳，类型 double 例如：1606708276268
    返回值：日期， 类型：字符串 2020-11-30 11:51:16
    """
    time_local = time.localtime(timeStamp / 1000)
    if fmt == 'T':
        dt = time.strftime("%Y-%m-%d", time_local)
    elif fmt == 'D':
        dt = time.strftime("%H:%M:%S", time_local)
    else:
        dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
    return dt
