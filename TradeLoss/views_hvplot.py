# -*- coding: utf-8 -*-
"""
@author: Neo
@software: PyCharm
@file: views_hvplot.py
@time: 2023/5/15 9:19
说明:
"""
import ctypes
import datetime

import holoviews as hv
from holoviews import opts
import hvplot.pandas
import numpy as np
import pandas as pd
import pymongo
from ShuiDQReport.settings import CLIENT, DATABASE_STAT, DATABASE_BASIC, BASE_DIR
from bokeh.plotting import show
import panel as pn

pd.options.plotting.backend = 'holoviews'
hv.extension('bokeh')
pn.extension()

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

        self.inc_dir = str(BASE_DIR) + "/TradeLoss/templates/TradeLoss/"

    def close(self):
        self._client.close()

    def save_show(self, save=True):
        plot = (
                self.get_latest_table() +
                self.get_describe_to_table() +
                self.get_cent_to_scatter() +
                self.get_cent_to_line()
        ).cols(1)
        print(plot)
        if save:
            hvplot.save(plot, self.inc_dir + "inc_trade_loss.html")
        else:
            show(hv.render(plot))

    def _load_df_loss(self):
        if self.df_loss is None:
            df_loss = pd.DataFrame(self.db_stat['trade_loss'].find({}, {"_id": 0, }))
            # df_loss['mis_sum'] = df_loss.mis_sum.astype(int)
            # df_loss = df_loss.round(5, columns=['dogs', 'cats'])
            df_loss = df_loss.astype(
                {'mis_sum': 'int', 'mis_mean_sum': 'int', 'b_mis_sum': 'int', 'b_mis_mean_sum': 'int', })
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

    def get_latest_table(self, count=10):
        # 图1：日期序列，所有；展示千分位曲线---相对损失、平均损失
        df = self.df_loss.iloc[-count:].copy()
        df.set_index('date', inplace=True)
        df.sort_index(ascending=True, inplace=True)
        table = df.T.reset_index().hvplot.table(
            # columns=['date', 'mis_sum', 'mis_cent', 'mis_mean_sum', 'mis_mean_cent',
            #                                'b_mis_mean_sum', 'b_mis_mean_cent', ],
            title="最近10个交易日详情",
            sortable=True, selectable=True, width=self.width)
        return table

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
                                   width=self.width,
                                   # height=self.high,
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
                                width=self.width,
                                # height=self.high,
                                ylabel="千分比",
                                )
        if self.show:
            show(hv.render(res_hv))
        return res_hv

    def __layout_by_select(self, freq=None, count=10):
        df = self.df_loss.copy()
        df['mis_sum'] = df.mis_sum / 10000
        df['mis_cent'] = df.mis_cent.round(4) * 1000
        df['date'] = pd.to_datetime(df.date)
        if freq == "礼拜":
            df['freq_day'] = df.date.map(lambda x: str(x - datetime.timedelta(days=x.weekday()))[5:10])
            res_file = self.inc_dir + "inc_freq_weekly.html"
        elif freq == '月':
            df['freq_day'] = df.date.map(lambda x: str(datetime.datetime(x.year, x.month, 1))[:7])
            res_file = self.inc_dir + "inc_freq_monthly.html"
        else:
            return
        freqs = df.freq_day.unique().tolist()
        df = df[df.freq_day.isin(freqs[-count:])]
        df.drop(index=df.mis_cent.idxmin(), inplace=True)  # 为了除掉4.28日的异常值
        boxplot_sum = df.hvplot.box(y='mis_sum', by='freq_day', shared_axes=False, tools=['hover'],
                                    title="损失金额（与13：05分相比）分布图，平均值：{:.2f}，单位：万".format(
                                        df.mis_sum.mean()), width=int(self.width / 2), legend=False,
                                    xlabel=f'最近 {count} 个{freq} 损失金额的箱体分布图', ylabel="损失金额，单位：万",
                                    )
        boxplot_cent = df.hvplot.box(y='mis_cent', by='freq_day', shared_axes=False, tools=['hover'],
                                     title="损失比例分布图，平均值：{:.2f}，单位：千分位".format(
                                         df.mis_cent.mean()), width=int(self.width / 2),
                                     xlabel=f'最近 {count} 个{freq} 损失比例的箱体分布图',
                                     ylabel="损失比例，单位：千分位", legend=False,
                                     )
        line_zero = hv.HLine(0).opts(color='red', line_width=1.5)
        layout = boxplot_sum * line_zero + boxplot_cent * line_zero
        layout.opts(
            opts.BoxWhisker(shared_axes=False, show_legend=False, tools=['hover'], ),
        ).cols(2)
        print(layout)
        hv.save(layout, res_file)

    def html_by_range(self):
        self.__layout_by_select(freq='礼拜')
        self.__layout_by_select(freq='月')

    def html_laest_sum_and_cent(self, count=10):
        df = self.df_loss.iloc[-count:].copy()
        df['date'] = pd.to_datetime(df.date)
        df['date'] = df.date.map(lambda x: str(x)[5:10])
        df['mis_sum'] = df.mis_sum / 10000
        df['mis_cent'] = df.mis_cent.round(4) * 1000

        res_hv1 = df.hvplot.bar(
            title="损失金额（与13：05分相比），平均值：{:.2f}，单位：万".format(df.mis_sum.mean()),
            x='date', xlabel='最近{}个交易日'.format(count),
            y=['mis_sum', ], ylabel="摩擦损失金额", )
        res_hv2 = df.hvplot.bar(
            title="损失比例 = 损失金额 / 累计成交金额，平均值：{:.1f}，单位：千分位".format(df.mis_cent.mean()),
            x='date', xlabel='最近{}个交易日'.format(count),
            y=['mis_cent', ], ylabel="千分比", )
        # line_zero = hv.HLine(0).opts(color='red', line_width=1.5)
        res_hv = res_hv1 + res_hv2
        res_hv.opts(
            opts.Bars(show_grid=True, shared_axes=False, width=int(self.width / 2)),
        ).cols(2)

        print(res_hv)
        hv.save(res_hv, self.inc_dir + "inc_laest_sum_and_cent_bar.html")


if __name__ == '__main__':
    vh = ViewHvplot()
    vh.save_show()
    vh.html_laest_sum_and_cent()
    vh.html_by_range()
