# -*- coding: utf-8 -*-
"""
@author: Neo
@software: PyCharm
@file: test_01.py
@time: 2023/5/11 11:39
说明:
"""
from OnlyTest.load_datas import LoadData
import matplotlib.pyplot as plt
from pylab import mpl
# Import seaborn
import seaborn as sns

# Apply the default theme
sns.set_theme()

# 设置显示中文字体
mpl.rcParams["font.sans-serif"] = ["SimHei"]
# 设置正常显示符号
mpl.rcParams["axes.unicode_minus"] = False

# 加载测试数据，返回一个Pandas.DataFrame
ld = LoadData()
df_data = ld.load_test_data()

# 离散图
# sns.relplot(
#     data=df_data,
#     col="类型",  # col根据参数的值决定画布会产生几个子图，
#     x="mis_cent", y="mis_sum",  # xy参数决定了点的位置，
#     size="size",  # size参数决定了点形状的大小，
#     hue="hue",  # hue和style决定了点的色调和形状。
#     style="hue",
# )
# plt.savefig("tops.png", bbox_inches='tight', dpi=350)  # 保存在当前目录

# # 离散图 + 回归模型
# sns.lmplot(data=df_data,
#            x="mis_mean_sum", y="mis_mean_cent",
#            col="类型",
#            )
# plt.savefig("tops.png", bbox_inches='tight', dpi=350)  # 保存在当前目录

# 防止散点重叠，分类出图
# sns.catplot(data=df_data, kind="swarm", x="类型", y="rm", hue="hue")
# plt.savefig("swarm.png", bbox_inches='tight', dpi=350)

# 小提琴
# sns.catplot(data=df_data, kind="violin", x="类型", y="rm", hue="hue", split=True)
# plt.savefig("violin.png", bbox_inches='tight', dpi=350)

# 箱体图，这种图显示了分布的三个四分位数和极值。
# “胡须”延伸到位于下四分位数和上四分位数 1.5 IQR 内的点，然后独立显示超出此范围的观测值。这意味着箱线图中的每个值都对应于数据中的一个实际观察值。
# sns.catplot(data=df_data, kind="box", x="类型", y="rm", hue="hue")
# plt.savefig("box.png", bbox_inches='tight', dpi=350)

# 箱体图，绘制类似于箱线图但经过优化以显示有关分布形状的更多信息的图。它最适合更大的数据集
# sns.catplot(data=df_data, kind="boxen", x="类型", y="rm", hue="hue")
# plt.savefig("boxen.png", bbox_inches='tight', dpi=350)

# 显示值集中趋势的估计值，而不是显示每个类别内的分布
# sns.catplot(data=df_data, kind="bar", x="类型", y="rm", hue="hue")
# plt.savefig("bar.png", bbox_inches='tight', dpi=350)

# 直方图
# sns.displot(data=df_data,
#             x='mis_mean_sum',  # 统计的字段
#             col="类型",  # col根据参数的值决定画布会产生几个子图，
#             kde=True  # 显示核密度曲线
#             )
# plt.savefig("distributions.png", bbox_inches='tight', dpi=350)

# 双变量、多维度
# sns.jointplot(data=df_data[df_data["类型"] == 'Rebalance'], x="mis_sum", y="mis_cent",
#               # hue="类型",  # 多维度参数，与下面的二选一
#               kind="reg"  # 增加线性拟合,kind：{ “scatter” | “kde” | “hist” | “hex” | “reg” | “resid” }
#               )
# plt.savefig("jointplot_reg.png", bbox_inches='tight', dpi=350)

# 按维度对多变量进行两两出图
df_tmp = df_data[['mis_sum', 'mis_mean_sum', 'rm', "类型"]].copy()
sns.pairplot(data=df_tmp, hue="类型")
plt.savefig("jointplot_all.png", bbox_inches='tight', dpi=350)
