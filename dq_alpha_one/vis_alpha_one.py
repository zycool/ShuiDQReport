# -*- coding: utf-8 -*-
"""
@author: Neo
@software: PyCharm
@file: vis_alpha_one.py
@time: 2023/5/22 19:29
说明:
"""
import pandas as pd
import panel as pn
import hvplot
import hvplot.pandas  # noqa

import holoviews as hv
from holoviews import opts

from ShuiDQReport.settings import BASE_DIR
from Datas import stat
from Datas.load_data import LoadData

pd.options.plotting.backend = 'holoviews'
hv.extension('bokeh')


class AlphaOweView(object):
    def __init__(self):
        self.inc_dir = str(BASE_DIR) + "/dq_alpha_one/templates/dq_alpha_one/"

        self.ld = LoadData()
        self.df_alpha = self.ld.get_alpha_one()

        self.df_alpha['净值日期'] = pd.to_datetime(self.df_alpha['净值日期'])
        self.df_alpha.sort_values('净值日期', inplace=True)

    def alpha_and_trade_loss(self):
        df_loss = self.ld.get_trade_loss()
        df_loss['净值日期'] = pd.to_datetime(df_loss['date'])
        df = pd.merge(df_loss, self.df_alpha, on="净值日期")
        # print(df)
        df_plot = df[['净值日期', 'mis_sum', '资产净值  (元)']].copy()
        df_plot['ma10'] = df['mis_sum'].rolling(10).mean()
        df_plot['ma10_a'] = df['资产净值  (元)'].rolling(10).mean()
        df_plot = df_plot.round(0)
        # print(df_plot)

        plot_1 = df_plot.plot.scatter(x='净值日期', y='mis_sum', color='DarkBlue', label='交易损失(元)').opts(
            xaxis=None)
        area1 = df_plot.hvplot.area(x='净值日期', y='mis_sum', label='交易损失(元)', )
        line1 = df_plot.hvplot.line(x='净值日期', y='ma10', color='Red', label='交易损失--MA10')
        layout1 = area1 * line1
        layout1.opts(
            legend_position='bottom_left',
            xaxis=None,
        )
        plot_2 = df_plot.plot.scatter(x='净值日期', y='资产净值  (元)', color='DarkGreen', label='资产净值(元)')
        area2 = df_plot.hvplot.area(x='净值日期', y='资产净值  (元)', label='资产净值(元)')
        line2 = df_plot.hvplot.line(x='净值日期', y='ma10_a', color='Red', label='资产净值--MA10', )
        layout2 = area2 * line2
        layout2.opts(
            legend_position='top_left',
            xaxis=None,
        )

        layout = plot_1 + layout1 + plot_2 + layout2
        layout.opts().cols(2)

        print(layout)

        hv.save(layout, self.inc_dir + "alpha_and_trade_loss.html")

    def _load_by_year(self, year, **kwargs):
        df_plot = self.df_alpha.copy()

        df_year = df_plot[df_plot['year'] == year].copy()
        df_year = stat.stat_max(df_year)
        df_year['back'] = df_year['累计净值  (元)'] / df_year['max_value'] - 1
        df_year['back_per'] = (df_year.back * 100).round(2)

        line = hv.Curve(df_year, '净值日期', '累计净值  (元)').opts(xaxis=None)

        back_dim = hv.Dimension('back_per', label='回撤比列', unit='%')
        spikes = hv.Spikes(df_year, '净值日期', back_dim).opts(color='purple')

        the_date = df_year.loc[df_year.back.idxmin(), '净值日期']
        the_pos = df_year.loc[df_year.back.idxmin(), '累计净值  (元)']
        point_max_back = hv.Points(pd.DataFrame(dict(x=[the_date, ], y=[the_pos, ], )))
        text = '最大回撤点\n日期：{}，幅度：{:.2%}'.format(str(the_date)[:10], df_year.back.min())
        text_max_back = hv.Text(the_date, the_pos, text=text, valign='top', halign='left')
        layout = (line * point_max_back * text_max_back) + spikes
        alpha_chg = df_year.iloc[-1]['累计净值  (元)'] / df_year.iloc[0]['累计净值  (元)'] - 1
        alpha_std = 20 ** 0.5 * df_year.chg.std()
        alpha_sharp = 365 ** 0.5 * df_year.chg.mean() / df_year.chg.std()
        title = '{}年 --->>> 收益：{:.2%}，波动率：{:.2%}，年夏普率：{:.2f}'.format(year, alpha_chg, alpha_std,
                                                                               alpha_sharp)
        layout.opts(
            opts.Curve(framewise=True, height=self.ld.high, width=self.ld.width2, tools=['hover'], title=title, ),
            opts.Spikes(framewise=True, height=150, width=self.ld.width2, tools=['hover'], ),
            opts.Points(framewise=True, color='red', size=5),
        ).cols(1)
        return layout

    def html_alpha_dmap(self):
        df_plot = self.df_alpha.copy()
        year_list = df_plot.year.unique().tolist()
        variable = pn.widgets.Select(options=year_list)
        pn.Column(variable, )
        dmap = hv.DynamicMap(pn.bind(self._load_by_year, year=variable))
        app = pn.Row(pn.WidgetBox('## 按年展现', variable),
                     dmap.opts(framewise=True)).servable()
        print(app)
        app.save(self.inc_dir + "inc_alpha_dmap.html", embed=True)

    def html_alpha_all(self):
        df_plot = self.df_alpha.copy()
        df_plot = stat.stat_max(df_plot)
        df_plot['back'] = df_plot['累计净值  (元)'] / df_plot['max_value'] - 1
        df_plot['back_per'] = (df_plot.back * 100).round(2)

        the_date = df_plot.loc[df_plot.back.idxmin(), '净值日期']
        the_pos = df_plot.loc[df_plot.back.idxmin(), '累计净值  (元)']
        point_max_back = hv.Points(pd.DataFrame(dict(x=[the_date, ], y=[the_pos, ], ))).opts(size=6)
        text = '历史最大回撤点\n日期：{}，幅度：{:.2%}'.format(str(the_date)[:10], df_plot.back.min())
        text_max_back = hv.Text(the_date, the_pos, text=text, valign='top', halign='left')

        alpha_chg = df_plot.iloc[-1]['累计净值  (元)'] - 1
        # 策略年化收益率
        alpha_annual = (df_plot.iloc[-1]['累计净值  (元)']) ** (250 / df_plot.chg.size) - 1
        alpha_std = 20 ** 0.5 * df_plot.chg.std()
        alpha_sharp = 365 ** 0.5 * df_plot.chg.mean() / df_plot.chg.std()
        title = '【{} - {}】总收益：{:.2%}，年化收益：{:.2%}，波动率：{:.2%}，年化夏普率：{:.2f}'.format(
            str(df_plot.iloc[0]['净值日期'])[:10], str(df_plot.iloc[-1]['净值日期'])[:10],
            alpha_chg, alpha_annual, alpha_std, alpha_sharp)

        curve = hv.Curve(df_plot, '净值日期', '累计净值  (元)')
        back_dim = hv.Dimension('back_per', label='回撤比列', unit='%')
        spikes = hv.Spikes(df_plot, '净值日期', back_dim).opts(xaxis=None, color='blue', tools=['hover'])
        # spikes = hv.Spikes(df_plot, '净值日期', ['back']).opts(xaxis=None, color='blue', tools=['hover'])
        spikes1 = hv.Spikes(self.df_alpha, '净值日期', ['资产净值  (元)']).opts(xaxis=None, color='purple')
        spikes2 = hv.Spikes(self.df_alpha, '净值日期', ['实收资本  (元)']).opts(color='grey')
        layout = (curve * point_max_back * text_max_back) + spikes + spikes1 + spikes2
        #
        layout.opts(
            opts.Curve(height=self.ld.high, width=self.ld.width2, xaxis=None, line_width=1.50, color='red',
                       tools=['hover'], title=title),
            opts.Spikes(height=150, width=self.ld.width2, line_width=0.25)).cols(1)

        print(layout)
        hv.save(layout, self.inc_dir + "inc_alpha_all.html")


if __name__ == '__main__':
    alpha = AlphaOweView()
    alpha.alpha_and_trade_loss()
    alpha.html_alpha_all()
    alpha.html_alpha_dmap()
