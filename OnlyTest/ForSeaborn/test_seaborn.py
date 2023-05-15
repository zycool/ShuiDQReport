# -*- coding: utf-8 -*-
"""
@author: Neo
@software: PyCharm
@file: test_seaborn.py
@time: 2023/5/11 10:20
说明:
"""
from ShuiDQReport.settings import BASE_DIR
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from OnlyTest.load_datas import LoadData
from pylab import mpl

sns.set_theme(style="dark")
# 设置显示中文字体
mpl.rcParams["font.sans-serif"] = ["SimHei"]
# 设置正常显示符号
mpl.rcParams["axes.unicode_minus"] = False

# 加载测试数据，返回一个Pandas.DataFrame
ld = LoadData()
df_data = ld.load_test_data(t="line")

df_tmp = df_data[['date', 'mis_cent', 'mis_mean_cent', 'b_mis_cent', 'b_mis_mean_cent']].copy()
# df_tmp = df_data[['date', 'mis_cent', ]].copy()
print(df_tmp)
sns.lineplot(data=df_tmp,
             # palette="tab10",
             linewidth=1.5,
             x="date", y="mis_cent",
             )
xx = df_tmp.date.to_list()
plt.xticks(xx[0:-1:15], rotation=-90)
# locs, labels = plt.xticks(ticks=xx)
# plt.setp(labels, rotation=90)
plt.savefig("../res_seaborn/line.png", bbox_inches='tight', dpi=350)
