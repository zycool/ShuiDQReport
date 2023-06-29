# -*- coding: utf-8 -*-
"""
@author: Neo
@software: PyCharm
@file: app_trade_detail.py
@time: 2023/6/29 11:09
说明:
"""

import sys
from datetime import datetime

sys.path.append("D:/Neo/WorkPlace/ShuiDQReport/")

import pandas as pd
import holoviews as hv
from holoviews import opts
# import hvplot.pandas  # noqa
from bokeh.io import curdoc
from bokeh.layouts import layout
from bokeh.models import Slider, Button, DatePicker, PreText, DatetimeRangeSlider

from Datas.load_data import LoadData
from Datas import stat

renderer = hv.renderer('bokeh').instance(mode='server')


def update_plot_data(the_date):
    global df_data
    df = df_data[df_data.date == the_date].copy()
    df['str_datetime'] = df['Date Time'].astype(str)
    df.set_index('成交时间', inplace=True)
    df.sort_index(inplace=True)
    return df


def plot_dyn(end_index):
    global df_plot
    # df_plot = df_data.loc[:end_index].copy()


def handler_slider_update(attrname, old, new):
    print(f"Previous slider: {old}")
    print(f"Updated slider: {new}")
    # stream.event(end_index=new)


def modify_doc(doc, default_date, min_date, max_date):
    global df_plot, trade_times, trade_times_str

    time_min, time_max = trade_times[0], trade_times[-1]
    callback_id = None

    def handler_date_picker(attr, old, new):
        global df_plot, trade_times, trade_times_str
        print("Previous label: " + old)
        print("Updated label: " + new)
        df_plot = update_plot_data(new)
        print(df_plot)
        trade_times = df_plot['Date Time'].unique().tolist()
        trade_times_str = df_plot.str_datetime.unique().tolist()
        datetime_range_slider.start = trade_times[0]
        datetime_range_slider.end = trade_times[-1]
        datetime_range_slider.value = (trade_times[0], trade_times[0])

    date_picker = DatePicker(title="选择交易日期", value=default_date, min_date=min_date, max_date=max_date)
    date_picker.on_change("value", handler_date_picker)

    # pre = PreText(text="""注意，这天没有交易！！！""", width=50, height=20)

    datetime_range_slider = DatetimeRangeSlider(value=(time_min, time_min), start=time_min, end=time_max,
                                                width=ld.width2, format='%Y-%m-%d %H:%M:%S',
                                                step=1000)
    datetime_range_slider.on_change('value', handler_slider_update)

    def animate_update():
        current_values = datetime_range_slider.value
        print(trade_times[:5])

        print(current_values)
        current_index = trade_times.index(str(datetime.fromtimestamp(current_values[1] / 1000)))
        # current_index = trade_times.index(current_values[1] / 1000)
        print(current_index)
        if current_index == len(trade_times) - 1:
            next_time = trade_times[0]
        else:
            next_time = trade_times[current_index + 1]
        datetime_range_slider.value = (trade_times[0], next_time)

    def animate():
        global callback_id
        if button.label == '► Play':
            button.label = '❚❚ Pause'
            callback_id = doc.add_periodic_callback(animate_update, 1000)
        else:
            button.label = '► Play'
            doc.remove_periodic_callback(callback_id)

    button = Button(label='► Play', width=60)
    button.on_click(animate)

    plot = layout([[], [date_picker, datetime_range_slider, button]], sizing_mode='fixed')

    doc.add_root(plot)
    return doc


# if __name__ == '__main__':

ld = LoadData()
df_data = ld.load_latest_month_statement_of_account(start_date='20230101')
default_day = df_data.date.max()
min_day = df_data.date.min()
df_plot = update_plot_data(default_day)
trade_times = df_plot['Date Time'].unique().tolist()
trade_times_str = df_plot.str_datetime.unique().tolist()

my_doc = modify_doc(curdoc(), default_day, min_day, default_day)
my_doc.title = '策略净值走势动态展示'
