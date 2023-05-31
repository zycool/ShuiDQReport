# -*- coding: utf-8 -*-
"""
@author: Neo
@software: PyCharm
@file: views.py
@time: 2023/5/29 17:32
说明:
"""
from django.shortcuts import render
from Datas.load_data import LoadData


def layer_bt(request):
    context = {}
    return render(request, 'layer_bt/layer_bt.html', context)
