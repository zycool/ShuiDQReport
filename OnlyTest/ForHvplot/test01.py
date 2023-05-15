# -*- coding: utf-8 -*-
"""
@author: Neo
@software: PyCharm
@file: test01.py
@time: 2023/5/12 19:29
说明:
"""
import numpy as np
import pandas as pd
import hvplot.pandas
import holoviews as hv
from OnlyTest.load_datas import LoadData
from bokeh.plotting import show

pd.options.plotting.backend = 'holoviews'
hv.extension('bokeh')
# hv.extension('matplotlib')

# going to use show() to open plot in browser


# 加载测试数据，返回一个Pandas.DataFrame
ld = LoadData()
df_data = ld.load_test_data(t="line")
df1 = df_data[['date', 'mis_cent', 'mis_mean_cent', 'b_mis_cent', 'b_mis_mean_cent']].copy()
df1['date'] = pd.to_datetime(df1.date)
df1.set_index('date', inplace=True)
df1 = df1.round(4) * 1000
# df1 = df1.applymap(lambda x: int(x * 10000))

# df2 = df_data[['date', 'mis_sum', 'mis_mean_sum', 'b_mis_sum', 'b_mis_mean_sum']].copy()
# index = pd.date_range('1/1/2000', periods=1000)
# df = pd.DataFrame(np.random.randn(1000, 4), index=index, columns=list('ABCD')).cumsum()

# show(hv.render(df1.hvplot(value_label='千分位',
#                           subplots=True,
#                           width=int(ld.screen_size[0] * 0.4), height=int(ld.screen_size[0] * 0.2),
#                           shared_axes=False
#                           ).cols(2)
#                ))
show(hv.render(
    df1.hvplot.bar(y=['mis_cent', 'mis_mean_cent'],
                   stacked=True,
                   rot=90,
                   # subplots=True,
                   width=int(ld.screen_size[0] * 0.4), height=int(ld.screen_size[0] * 0.2),
                   # shared_axes=False,
                   legend='top_left'
                   )
))
