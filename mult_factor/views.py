# -*- coding: utf-8 -*-
"""
@author: Neo
@software: PyCharm
@file: views.py
@time: 2023/5/22 11:18
说明:
"""

from django.shortcuts import render
from bokeh.embed import components
from Datas.load_data import LoadData
from .vis_F_c import html_weights_pie


def bt_alpha_one(request):
    context = {}
    return render(request, 'mult_factor/alpha_one/index_bt_alpha_one.html', context)


def bt_per_2(request):
    context = {}
    return render(request, 'mult_factor/per_2/index_bt_per_2.html', context)


def bt_per_2_4(request):
    context = {}
    return render(request, 'mult_factor/per_2_4/index_bt_per_2_4.html', context)


def bt_cap_and_money(request):
    context = {}
    return render(request, 'mult_factor/per_2_4/index_cap_and_money.html', context)


def bt_VaR_ES(request):
    context = {}
    return render(request, 'mult_factor/per_2_4/index_VaR_ES.html', context)


def mv_vol(request):
    ld = LoadData()
    the_date = ld.get_the_date()
    context = {"the_date": the_date}
    return render(request, 'mult_factor/mv_vol/mv_vol.html', context)


def F1_about(request):
    ld = LoadData()
    the_date = ld.get_the_date()
    context = {"the_date": the_date}
    return render(request, 'mult_factor/F1/F1.html', context)


def F_C_values(request):
    ld = LoadData()
    the_date = ld.get_the_date()
    context = {"the_date": the_date}
    return render(request, 'mult_factor/F_C/f_c_values.html', context)


def F_C_weight(request):
    plot = html_weights_pie()
    script, div = components(plot)
    context = {'script': script, 'div': div}
    return render(request, 'mult_factor/F_C/index_weight.html', context)


def corr_about(request):
    ld = LoadData()
    the_date = ld.get_the_date()
    context = {"the_date": the_date}
    return render(request, 'mult_factor/factors_pool/corr.html', context)


def ics_about(request):
    ld = LoadData()
    the_date = ld.get_the_date()
    context = {"the_date": the_date}
    return render(request, 'mult_factor/factors_pool/ics.html', context)


def irs_about(request):
    ld = LoadData()
    the_date = ld.get_the_date()
    context = {"the_date": the_date}
    return render(request, 'mult_factor/factors_pool/irs.html', context)
