# -*- coding: utf-8 -*-
"""
@author: Neo
@software: PyCharm
@file: update_vis_daily.py
@time: 2023/5/31 11:11
说明:
"""
from Datas.load_data import LoadData
from layer_bt.vis_layer import vis_key_factors
from mult_factor.vis_F_c import F_C_View
from mult_factor.vis_factor import FactorView
from mult_factor.vis_factors_pool import FactorsPoolView
from mult_factor.vis_strategy import StrategyView
from TradeLoss.views_hvplot import ViewHvplot

if __name__ == '__main__':
    ld = LoadData()
    print("关键因子单调性...")
    vis_key_factors(ld=ld)
    print("复合因子F_C...")
    fc = F_C_View(ld=ld)
    fc.html_ics_IR()
    # 这个3D模块要放最后执行
    fc.html_weights()

    print("各类单因子数据...")
    factors = ['F1', 'mv_vol',
               # 'F_C'
               ]
    for factor in factors:
        print("生成 {} 相关数据".format(factor))
        f1 = FactorView(ld_data=ld, factor=factor)
        f1.html_inds_and_cap()
        f1.html_chg_by_group()

    print("因子池相关数据...")
    fp = FactorsPoolView(ld=ld)
    fp.html_corr()
    fp.html_ics()
    fp.html_irs()

    print("策略组合相关数据...")
    stra_list = ["alpha_one", "per_2", "per_2_4"]
    for stra in stra_list:
        alpha = StrategyView(ld=ld, stra_name=stra)
        alpha.html_all()
        alpha.html_des()

    print("摩擦损失数据...")
    vh = ViewHvplot()
    vh.save_show()
    vh.close()

    print("全部更新完成！！！")
