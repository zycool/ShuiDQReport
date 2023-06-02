# -*- coding: utf-8 -*-
"""
@author: Neo
@software: PyCharm
@file: vis_stat.py
@time: 2023/6/1 17:00
说明:每日收盘后统计日、周、月频 涨跌幅数据
"""
import numpy as np
import pandas as pd
import panel as pn
import hvplot
import hvplot.pandas  # noqa

import holoviews as hv
from holoviews import opts
from holoviews import dim
from ShuiDQReport.settings import BASE_DIR, SHAP_DAYS
from Datas import stat
from Datas.load_data import LoadData
from Utils.utils import get_week_month_date

pd.options.plotting.backend = 'holoviews'
hv.extension('bokeh')
pn.extension()


class StatisticView(object):
    def __init__(self):
        self.inc_dir = str(BASE_DIR) + "/layer_bt/templates/statistic/"

        self.ld = LoadData()
        self.df_yestoday = self.ld.get_group_by_cap_chg()
        self.df_today = self.ld.get_jq_today()

    def __html_cap(self, df, daily=True):
        df_cap = df.sort_values('market_cap')
        df_cap.reset_index(inplace=True, drop=True)
        group_num = 10
        each_group = df_cap.shape[0] // group_num
        for i in range(0, group_num):
            df_cap.loc[i * each_group:((i + 1) * each_group) - 1, 'gro'] = i + 1
            ddf = df_cap.loc[i * each_group:((i + 1) * each_group) - 1]
            gro_mean_chg = ddf.chg.mean()
            df_cap.loc[i * each_group:((i + 1) * each_group) - 1, 'gro_mean_chg'] = gro_mean_chg
        df_cap.dropna(inplace=True)
        df_cap = df_cap[~(df_cap.duplicated(subset=['gro', ], keep='last'))].copy()
        df_cap.reset_index(inplace=True, drop=True)
        df_cap['gro_mean_chg_per'] = df_cap.gro_mean_chg.round(4) * 100
        df_cap['color'] = np.sign(df_cap['gro_mean_chg'].tolist())
        if daily:
            title = "交易日：{} 市值分组平均涨跌幅".format(df.iloc[0].date)
        else:
            title = "交易区间：{} -- {} ， 市值分组平均涨跌幅".format(df.iloc[0].date_s, df.iloc[0].date_e)
        bar_cap = df_cap.hvplot.bar(x="gro", y="gro_mean_chg_per", width=self.ld.width1, c="color",
                                    xlabel="按市值从小到大分组", ylabel="每组平均涨跌幅", title=title)
        return bar_cap

    def __html_chg(self, df, daily=True):
        df_chg = df.sort_values('chg')
        df_chg.reset_index(inplace=True, drop=True)
        df_chg['chg_per'] = df_chg.chg.round(4) * 100
        if daily:
            df_chg['chg_range'] = pd.cut(x=df_chg["chg_per"], bins=list(range(-20, 21, 1)),
                                         labels=list(range(-20, 20, 1)))
            title = "交易日：{} 涨跌幅分布".format(df.iloc[0].date)
        else:
            df_chg['chg_range'] = pd.cut(x=df_chg["chg_per"], bins=list(range(-50, 51, 2)),
                                         labels=list(range(-50, 50, 2)))
            title = "交易区间：{} -- {} ， 市值分组平均涨跌幅".format(df.iloc[0].date_s, df.iloc[0].date_e)
        a = df_chg["chg_range"].value_counts(sort=False)
        df_plot = pd.DataFrame({'涨跌幅区间': a.index, "股票数量": a.values})
        df_plot['color'] = np.sign(df_plot['涨跌幅区间'].tolist())
        bar_chg = df_plot.hvplot.bar(x="涨跌幅区间", y="股票数量", width=self.ld.width_h, c="color", rot=90,
                                     xlabel="涨跌幅区间(左开，右闭]", title=title)
        return bar_chg

    def __deal_with_today(self):
        df_y = self.df_yestoday.copy()
        df_t = self.df_today.copy()
        df_y_for_merge = df_y[['code', 'market_cap']].copy()
        df_t = pd.merge(df_t, df_y_for_merge, on='code')
        df_t['market_cap'] = df_t.market_cap * (df_t.chg + 1)
        print(df_t)
        return df_t[['date', 'code', 'market_cap', 'chg']].copy()

    def html_daily(self):
        df_y = self.df_yestoday.copy()
        df_t = self.__deal_with_today()
        bar_cap = self.__html_cap(df_y)
        bar_chg = self.__html_chg(df_y)
        layout = self.__html_cap(df_t) + self.__html_chg(df_t) + bar_cap + bar_chg
        layout.opts().cols(2)
        print(layout)
        hv.save(layout, self.inc_dir + "inc_daily.html")

    def __html_range(self, date_s=None, date_e=None):
        df_week = self.ld.get_group_by_cap_chg(date_s=date_s, date_e=date_e)
        df_t = self.__deal_with_today()
        df_week = pd.concat([df_week, df_t])

        ddf = df_week.groupby('code').apply(cal_range_chg_and_cap)
        layout = self.__html_cap(ddf, daily=False) + self.__html_chg(ddf, daily=False)
        layout.opts().cols(2)
        print(layout)
        return layout

    def html_weekly(self):
        week_s, week_e = get_week_month_date(week=True)
        layout = self.__html_range(week_s, week_e)
        hv.save(layout, self.inc_dir + "inc_weekly.html")

    def html_monthly(self):
        month_s, month_e = get_week_month_date(month=True)
        layout = self.__html_range(month_s, month_e)
        hv.save(layout, self.inc_dir + "inc_monthly.html")


def cal_range_chg_and_cap(df_from):
    df = df_from.copy()
    cap_mean = df.market_cap.mean()
    chg = (df.chg + 1).cumprod().iloc[-1] - 1
    res = pd.Series({'date_s': df.date.values[0], 'date_e': df.date.values[-1],
                     'market_cap': cap_mean, 'chg': chg})
    return res


if __name__ == '__main__':
    sv = StatisticView()
    sv.html_daily()
    sv.html_weekly()
    sv.html_monthly()
