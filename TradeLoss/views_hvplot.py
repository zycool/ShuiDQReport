# -*- coding: utf-8 -*-
"""
@author: Neo
@software: PyCharm
@file: views_hvplot.py
@time: 2023/5/15 9:19
说明:
"""
import ctypes
import holoviews as hv
import hvplot.pandas
import numpy as np
import pandas as pd
import pymongo
from ShuiDQReport.settings import CLIENT, DATABASE_STAT, DATABASE_BASIC, BASE_DIR
from bokeh.plotting import show

pd.options.plotting.backend = 'holoviews'
hv.extension('bokeh')

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


class ViewHvplot:
    def __init__(self, show=False):
        self.show = show
        self._client = pymongo.MongoClient(CLIENT)
        self.db_stat = self._client[DATABASE_STAT]
        self.db_basic = self._client[DATABASE_BASIC]
        self.df_loss = None
        screen_size = get_screen_size()
        self.width = int(screen_size[0] * 2 / 3)
        self.high = int(self.width * 2 / 3)
        if self.df_loss is None:
            self._load_df_loss()

    def close(self):
        self._client.close()

    def save_show(self, save=True):
        plot = (self.get_describe_to_table() +
                self.get_latest_cent_to_bar() +
                self.get_cent_to_scatter() +
                self.get_cent_to_line()).cols(1)
        print(plot)
        if save:
            hvplot.save(plot, str(BASE_DIR) + "/TradeLoss/templates/TradeLoss/inc_trade_loss.html")
        else:
            show(hv.render(plot))

    def _load_df_loss(self):
        if self.df_loss is None:
            df_loss = pd.DataFrame(self.db_stat['trade_loss'].find({}, {"_id": 0, }))
            # df_loss.describe(include=[np.number])
            self.df_loss = df_loss
        return self.df_loss

    def get_describe_to_table(self):
        """对各个统计字段 做均值、STD等展示"""
        df_loss = self.df_loss.copy()
        df_loss.set_index('date', inplace=True)
        df = df_loss.describe(include=[np.number]).transpose()
        df.reset_index(inplace=True)
        res_hv = df.hvplot.table(title="对历史全量统计字段 做均值、STD等展示",
                                 fit_columns=True, sortable=True, selectable=True,
                                 legend='top_left',
                                 width=self.width)
        # res_hv.title
        if self.show:
            show(hv.render(res_hv))
        return res_hv

    def get_latest_cent_to_bar(self, count=10):
        # 图1：日期序列，所有；展示千分位曲线---相对损失、平均损失
        df = self.df_loss.iloc[-count:].copy()
        df.set_index('date', inplace=True)
        df_plot = df.round(4) * 1000

        res_hv = df_plot.hvplot.bar(title="最近10个交易日详情",
                                    y=['mis_cent', 'mis_mean_cent', 'b_mis_cent', 'b_mis_mean_cent'],
                                    ylabel="千分比", rot=90, legend='top_left', width=self.width, )
        df.sort_index(ascending=False, inplace=True)
        table = df.hvplot.table(columns=['date', 'mis_sum', 'mis_cent', 'mis_mean_sum', 'mis_mean_cent',
                                         'b_mis_mean_sum', 'b_mis_mean_cent', ],
                                sortable=True, selectable=True, width=self.width)
        lay = res_hv + table
        lay.opts().cols(1)
        if self.show:
            show(hv.render(lay))
        return lay

    def get_cent_to_scatter(self):
        df1 = self.df_loss[['date', 'mis_cent']].copy()
        df1.rename(columns={"mis_cent": "cent"}, inplace=True)
        df1['species'] = '相对损失'

        df2 = self.df_loss[['date', 'mis_mean_cent']].copy()
        df2.rename(columns={"mis_mean_cent": "cent"}, inplace=True)
        df2['species'] = '平均损失'

        df3 = self.df_loss[['date', 'b_mis_cent']].copy()
        df3.rename(columns={"b_mis_cent": "cent"}, inplace=True)
        df3['species'] = 'R_相对损失'

        df4 = self.df_loss[['date', 'b_mis_mean_cent']].copy()
        df4.rename(columns={"b_mis_mean_cent": "cent"}, inplace=True)
        df4['species'] = 'R_平均损失'

        df = pd.concat([df1, df2, df3, df4], axis=0)
        df['date'] = pd.to_datetime(df.date)
        df.set_index('date', inplace=True)
        df.sort_index(inplace=True)
        df['cent'] = df.cent.round(4) * 1000

        res_hv = df.hvplot.scatter(title="全量散点图",
                                   y='cent', by='species', legend='top_left',
                                   width=self.width, height=self.high,
                                   hover_cols=["species", "cent"])

        if self.show:
            show(hv.render(res_hv))
        return res_hv

    def get_cent_to_line(self):
        df = self.df_loss[['date', 'mis_cent']].copy()
        df['ma10'] = df['mis_cent'].rolling(10).mean()
        df['ma40'] = df['mis_cent'].rolling(40).mean()
        df['date'] = pd.to_datetime(df.date)
        df.set_index('date', inplace=True)
        df.sort_index(inplace=True)
        df = df.round(4) * 1000
        res_hv = df.hvplot.line(title="全量相对损失，及MA10、MA40走势",
                                legend='top_left',
                                width=self.width, height=self.high,
                                ylabel="千分比",
                                )
        if self.show:
            show(hv.render(res_hv))
        return res_hv


if __name__ == '__main__':
    # print(str(BASE_DIR) + "/TradeLoss/templates/TradeLoss/iframe_trade_loss.html")
    vh = ViewHvplot()
    vh.save_show()
    # vh.get_describe_to_table()
    # vh.get_latest_cent_to_bar()
    # vh.get_cent_to_scatter()
    # vh.get_cent_to_line()
