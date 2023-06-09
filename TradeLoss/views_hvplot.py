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
            df_loss = pd.DataFrame(self.db_stat['trade_loss_2307'].find({}, {"_id": 0, }))
            # df_loss['mis_sum'] = df_loss.mis_sum.astype(int)
            # df_loss = df_loss.round(5, columns=['dogs', 'cats'])
            # df_loss = df_loss.astype({'mis_sum': 'int', 'mis_mean_sum': 'int'})
            # df_loss.sort_values('date', inplace=True)
            self.df_loss = df_loss
        return self.df_loss

    def get_describe_to_table(self):
        """对各个统计字段 做均值、STD等展示"""
        df_loss = self.df_loss.copy()
        df_loss.set_index('date', inplace=True)
        df = df_loss.describe(include=[np.number]).transpose()
        df.reset_index(inplace=True)
        res_hv = df.hvplot.table(title="对历史全量统计字段 做均值、STD等展示",
                                 fit_columns=True, sortable=True, selectable=True, height=self.high,
                                 legend='top_left', width=self.width)
        # res_hv.title
        if self.show:
            show(hv.render(res_hv))
        return res_hv

    def get_latest_table(self, count=10):
        # 图1：日期序列，所有；展示千分位曲线---相对损失、平均损失
        df = self.df_loss.iloc[-count:].copy()
        df.set_index('date', inplace=True)
        df.sort_index(ascending=True, inplace=True)
        table = df.T.reset_index().hvplot.table(title="最近10个交易日详情", height=self.high,
                                                sortable=True, selectable=True, width=self.width)
        return table

    def get_cent_to_scatter(self):
        df1 = self.df_loss[['date', 'mis_cent']].copy()
        df1.rename(columns={"mis_cent": "cent"}, inplace=True)
        df1['species'] = '全量'

        df3 = self.df_loss[['date', 'mis_cent_reb']].copy()
        df3.rename(columns={"mis_cent_reb": "cent"}, inplace=True)
        df3['species'] = 'R_全量'

        df5 = self.df_loss[['date', 'mis_cent_turn']].copy()
        df5.rename(columns={"mis_cent_turn": "cent"}, inplace=True)
        df5['species'] = '换手'

        df6 = self.df_loss[['date', 'mis_cent_buy']].copy()
        df6.rename(columns={"mis_cent_buy": "cent"}, inplace=True)
        df6['species'] = '换入'

        df7 = self.df_loss[['date', 'mis_cent_sell']].copy()
        df7.rename(columns={"mis_cent_sell": "cent"}, inplace=True)
        df7['species'] = '换出'

        df8 = self.df_loss[['date', 'mis_cent_buy_all']].copy()
        df8.rename(columns={"mis_cent_buy_all": "cent"}, inplace=True)
        df8['species'] = '买单'

        df9 = self.df_loss[['date', 'mis_cent_sell_all']].copy()
        df9.rename(columns={"mis_cent_sell_all": "cent"}, inplace=True)
        df9['species'] = '卖单'

        df = pd.concat([df1, df3, df5, df6, df7, df8, df9], axis=0)
        df['date'] = pd.to_datetime(df.date)
        df.set_index('date', inplace=True)
        df.sort_index(inplace=True)
        df['cent'] = df.cent.round(4) * 1000

        res_hv = df.hvplot.scatter(title="全量散点图", y='cent', by='species', legend='right',
                                   width=self.width, height=self.high, grid=True,
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
                                legend='top_left', width=self.width,
                                # height=self.high,
                                ylabel="千分比", )
        if self.show:
            show(hv.render(res_hv))
        return res_hv

    def __layout_by_select(self, freq=None, count=10):
        df = self.df_loss.copy()
        df['mis_sum'] = df.mis_sum / 10000
        df['mis_cent'] = df.mis_cent.round(4) * 1000
        df['date'] = pd.to_datetime(df.date)
        # df.drop(index=df.mis_cent.idxmin(), inplace=True)  # 为了除掉4.28日的异常值
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
        boxplot_sum = df.hvplot.box(y='mis_sum', by='freq_day', shared_axes=False, tools=['hover'],
                                    title="损失金额分布图，平均值：{:.2f}，单位：万".format(
                                        df.mis_sum.mean()), width=int(self.width / 2), legend=False,
                                    xlabel=f'最近 {count} 个{freq} 损失金额的箱体分布图', ylabel="损失金额", )
        boxplot_cent = df.hvplot.box(y='mis_cent', by='freq_day', shared_axes=False, tools=['hover'],
                                     title="损失比例分布图，平均值：{:.2f}，单位：千分位".format(
                                         df.mis_cent.mean()), width=int(self.width / 2),
                                     xlabel=f'最近 {count} 个{freq} 损失比例的箱体分布图',
                                     ylabel="损失比例", legend=False, )
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

        df_plot = df[['date', 'trade_sum', 'mis_sum', 'mis_cent', 'mis_sum_mean', 'mis_cent_mean', 'sub_sum',
                      'sub_mis_cent']].copy()
        df_plot['sub_mis_sum'] = (df_plot.trade_sum - abs(df_plot.sub_sum)) * df_plot.sub_mis_cent
        df_plot.loc[df_plot['sub_sum'] == 0, 'sub_mis_sum'] = df_plot[df_plot['sub_sum'] == 0]['mis_sum']
        df_plot.loc[df_plot['sub_sum'] == 0, 'sub_mis_cent'] = df_plot[df_plot['sub_sum'] == 0]['mis_cent']
        # print(df_plot[df_plot['sub_sum'] == 0])

        df_plot['含申赎'] = df_plot.mis_sum / 10000
        df_plot['剔申赎'] = df_plot.sub_mis_sum / 10000
        df_plot['平均价'] = df_plot.mis_sum_mean / 10000
        res_hv1 = df_plot.hvplot.bar(
            title="损失金额，平均值(含申赎)：{:.2f}，平均值(剔申赎)：{:.2f}     单位：万".format(
                df_plot['含申赎'].mean(), df_plot['剔申赎'].mean()),
            x='date', xlabel='最近{}个交易日'.format(count), y=['含申赎', '剔申赎', '平均价'], ylabel="摩擦损失金额")

        df_plot['含申赎'] = df_plot.mis_cent.round(6) * 10000
        df_plot['剔申赎'] = df_plot.sub_mis_cent.round(6) * 10000
        df_plot['平均价'] = df_plot.mis_cent_mean.round(6) * 10000
        res_hv2 = df_plot.hvplot.bar(
            title="损失比例，平均值(含申赎)：{:.2f}，平均值(剔申赎)：{:.2f}     单位：万分位".format(
                df_plot['含申赎'].mean(), df_plot['剔申赎'].mean()),
            x='date', xlabel='最近{}个交易日'.format(count), y=['含申赎', '剔申赎', '平均价'], ylabel="万分位")
        res_hv = res_hv1 + res_hv2
        res_hv.opts(
            opts.Bars(show_grid=True, shared_axes=False, width=int(self.width / 2), xrotation=90),
        ).cols(2)

        print(res_hv)
        hv.save(res_hv, self.inc_dir + "inc_laest_sum_and_cent_bar.html")

    def html_line_and_area(self, start_date='20190101'):
        df = self.df_loss[self.df_loss['date'] > start_date].copy()
        df['date'] = pd.to_datetime(df.date)
        # df.drop(index=df.mis_cent.idxmin(), inplace=True)  # 为了除掉4.28日的异常值

        df_plot = df[['date', 'trade_sum', 'mis_sum', 'mis_cent', 'sub_sum', 'sub_mis_cent']].copy()
        df_plot['sub_mis_sum'] = (df_plot.trade_sum - abs(df_plot.sub_sum)) * df_plot.sub_mis_cent
        df_plot.loc[df_plot['sub_sum'] == 0, 'sub_mis_sum'] = df_plot[df_plot['sub_sum'] == 0]['mis_sum']
        df_plot.loc[df_plot['sub_sum'] == 0, 'sub_mis_cent'] = df_plot[df_plot['sub_sum'] == 0]['mis_cent']
        # print(df_plot[df_plot['sub_sum'] == 0])
        # print(df_plot.loc[df_plot.sub_mis_cent.idxmax()])

        df_plot['mis_sum'] = df_plot.mis_sum / 10000
        df_plot['ma10'] = df_plot['mis_sum'].rolling(10).mean()
        df_plot['sub_mis_sum'] = df_plot.sub_mis_sum / 10000
        df_plot['sub_ma10'] = df_plot['sub_mis_sum'].rolling(10).mean()

        df_plot['mis_cent'] = df_plot.mis_cent.round(4) * 1000
        df_plot['ma10_cent'] = df_plot['mis_cent'].rolling(10).mean()

        x_lable = "全量区间【{} - {}】".format(str(df_plot.iloc[0]['date'])[:10], str(df_plot.iloc[-1]['date'])[:10])
        x_lable2 = "全量区间【{} - {}】".format(str(df_plot.iloc[0]['date'])[:10], str(df_plot.iloc[-1]['date'])[:10])

        area1_0 = df_plot.hvplot.area(x='date', y='mis_sum', label='含申赎', xlabel=x_lable, ylabel="摩擦损失金额",
                                      title="损失金额(含申赎)    -->> MEAN：{:.1f}，MA10：{:.1f}     单位：万".format(
                                          df_plot.mis_sum.mean(), df_plot.iloc[-1]['ma10']), grid=True
                                      )
        line1_0 = df_plot.hvplot.line(x='date', y='ma10', c='red', label='MA10(含申赎)')
        layout1_0 = area1_0 * line1_0
        layout1_0.opts(legend_position='bottom_left', width=int(self.width / 2))

        area1_1 = df_plot.hvplot.area(x='date', y='mis_cent', label='含申赎', xlabel=x_lable2, ylabel="摩擦损失比例",
                                      title="损失比例(含申赎)    -->> MEAN：{:.1f}，MA10：{:.1f}     单位：千分位".format(
                                          df_plot.mis_cent.mean(), df_plot.iloc[-1]['ma10_cent']), grid=True
                                      )
        line1_1 = df_plot.hvplot.line(x='date', y='ma10_cent', c='red', label='MA10(含申赎)')
        layout1_1 = area1_1 * line1_1
        layout1_1.opts(legend_position='bottom_left', width=int(self.width / 2))

        df_plot.drop(index=df_plot.sub_mis_cent.idxmax(), inplace=True)  # 为了除掉2022-09-30日的异常值
        df_plot['sub_mis_cent'] = df_plot.sub_mis_cent.round(4) * 1000
        df_plot['sub_ma10_cent'] = df_plot['sub_mis_cent'].rolling(10).mean()

        area2_0 = df_plot.hvplot.area(x='date', y='sub_mis_sum', label='不含申赎', xlabel=x_lable,
                                      ylabel="摩擦损失金额", grid=True,
                                      title="损失金额(不含申赎) -->> MEAN：{:.1f}，MA10：{:.1f}".format(
                                          df_plot.sub_mis_sum.mean(), df_plot.iloc[-1]['sub_ma10'])
                                      )
        line2_0 = df_plot.hvplot.line(x='date', y='sub_ma10', c='red', label='MA10(不含)', )
        layout2_0 = area2_0 * line2_0
        layout2_0.opts(legend_position='bottom_left', width=int(self.width / 2))

        area2_1 = df_plot.hvplot.area(x='date', y='sub_mis_cent', label='不含申赎', xlabel=x_lable2,
                                      ylabel="摩擦损失比例", grid=True,
                                      title="损失比例(不含申赎) -->> MEAN：{:.1f}，MA10：{:.1f}".format(
                                          df_plot.sub_mis_cent.mean(), df_plot.iloc[-1]['sub_ma10_cent'])
                                      )

        line2_1 = df_plot.hvplot.line(x='date', y='sub_ma10_cent', c='red', label='MA10(不含)', )
        layout2_1 = area2_1 * line2_1
        layout2_1.opts(legend_position='bottom_left', width=int(self.width / 2))

        layout = layout1_0 + layout1_1 + layout2_0 + layout2_1
        layout.opts(shared_axes=False).cols(2)
        print(layout)
        hv.save(layout, self.inc_dir + "inc_area_and_lines.html")


if __name__ == '__main__':
    vh = ViewHvplot()
    vh.save_show()
    vh.html_laest_sum_and_cent()
    vh.html_by_range()
    vh.html_line_and_area(start_date='20190101')
    vh.close()
