# -*- coding: utf-8 -*-
"""
@author: Neo
@software: PyCharm
@file: vis_alpha_one.py
@time: 2023/5/26 13:57
说明:
"""
import numpy as np
import pandas as pd
import hvplot
import hvplot.pandas  # noqa

import holoviews as hv
from holoviews import opts
from holoviews import dim

from ShuiDQReport.settings import BASE_DIR
from Datas.load_data import LoadData
from Datas import stat

pd.options.plotting.backend = 'holoviews'
hv.extension('bokeh')


class StrategyView(object):
    def __init__(self, ld, stra_name="alpha_one"):
        self.stra_name = stra_name
        self.inc_dir = str(BASE_DIR) + "/mult_factor/templates/mult_factor/" + self.stra_name + "/"

        self.ld = ld
        self.df = self.ld.get_bt_strategy(stra_name=self.stra_name)

    def html_all(self):
        df_plot = self.df.copy()
        df_plot["date"] = pd.to_datetime(df_plot.date)
        df_plot = stat.stat_max(df_plot, col='net_value5')
        df_plot['back'] = df_plot['net_value5'] / df_plot['max_value'] - 1
        df_plot['back_per'] = (df_plot.back * 100).round(2)

        the_date = df_plot.loc[df_plot.back.idxmin(), 'date']
        the_pos = df_plot.loc[df_plot.back.idxmin(), 'net_value5']
        point_max_back = hv.Points(pd.DataFrame(dict(x=[the_date, ], y=[the_pos, ], ))).opts(size=6)
        text = '历史最大回撤点\n日期：{}，幅度：{:.2%}'.format(str(the_date)[:10], df_plot.back.min())
        text_max_back = hv.Text(the_date, the_pos, text=text, valign='top', halign='left')

        alpha_chg = df_plot.iloc[-1]['net_value5'] - 1
        # 策略年化收益率
        alpha_annual = (df_plot.iloc[-1]['net_value5']) ** (250 / df_plot.net_value5.size) - 1
        alpha_std = 20 ** 0.5 * df_plot.chg5.std()
        alpha_sharp = 365 ** 0.5 * df_plot.chg5.mean() / df_plot.chg5.std()
        title = '【{} - {}】总收益：{:.2%}，年化收益：{:.2%}，波动率：{:.2%}，年化夏普率：{:.2f}'.format(
            str(df_plot.iloc[0]['date'])[:10], str(df_plot.iloc[-1]['date'])[:10],
            alpha_chg, alpha_annual, alpha_std, alpha_sharp)
        curve = hv.Curve(df_plot, 'date', 'net_value5')
        lay1 = curve * point_max_back * text_max_back
        lay1.opts(
            opts.Curve(height=self.ld.high, width=self.ld.width2, line_width=1.50, color='red',
                       tools=['hover'], title=title, show_grid=True, ),
        )

        back_dim = hv.Dimension('back_per', label='回撤比列', unit='%')
        spikes = hv.Spikes(df_plot, 'date', back_dim).opts(xaxis=None, color='grey', tools=['hover'])
        turn_title = "换手率(标红) & 回撤(标灰) & 持仓量(蓝线) 指标 --->>> 平均单边换手率 {:.2%}）".format(
            df_plot.stra_turnover.mean())
        df_plot['stra_turnover_per'] = (df_plot.stra_turnover * 100).round(2)
        turnover_dim = hv.Dimension('stra_turnover_per', label='换手率', unit='%')
        turn_spikes = hv.Spikes(df_plot, 'date', turnover_dim).opts(
            xaxis=None, color='purple', title=turn_title, ylabel="换手率 & 回撤 & 持仓量")
        curve_hold = hv.Curve(df_plot, 'date', 'stra_hold_num')
        lay2 = spikes * turn_spikes * curve_hold
        lay2.opts(
            opts.Curve(height=self.ld.high, width=self.ld.width2, xaxis=None, line_width=1.50, color='blue',
                       tools=['hover'], title=title),
            opts.Spikes(height=200, width=self.ld.width2, line_width=0.25)
        )

        df_plot['chg5_per'] = (df_plot.chg5 * 100).round(2)
        chg5_dim = hv.Dimension('chg5_per', label='涨跌幅', unit='%')
        chg5_scatter = hv.Scatter(df_plot, 'date', chg5_dim).opts(size=abs(dim('chg5_per')),
                                                                  color=np.sign(dim('chg5_per')))

        lay3 = chg5_scatter * chg5_scatter.hist()
        lay3.opts(
            # opts.Scatter(color='z', size=dim('size') * 20),
            opts.Scatter(height=200, width=self.ld.width2, tools=['hover'], title="每日涨跌幅 & 分布"),
            opts.Histogram(tools=['hover']),
            # fill_color=hv.dim('y').bin(bins=[-10, 0, 10], labels=['red', 'blue']))
        )

        layout = lay1 + lay2 + lay3
        layout.opts().cols(1)

        print(layout)
        hv.save(layout, self.inc_dir + "inc_all.html")

    def html_des(self):
        df_des, the_date = self.ld.get_cap_and_money_for_strategy(self.stra_name)
        table = df_des.hvplot.table(columns=['index', 'market_cap', 'money'], sortable=True, selectable=True,
                                    title="{} 日，组合 {} 的市值(亿) & 成交金额(万)描述".format(the_date,
                                                                                               self.stra_name))
        print(table)
        hv.save(table, self.inc_dir + "inc_table.html")


if __name__ == '__main__':
    stra_list = ["alpha_one", "per_2", "per_2_4"]
    for stra in stra_list:
        alpha = StrategyView(ld=LoadData(), stra_name=stra)
        alpha.html_all()
        alpha.html_des()
