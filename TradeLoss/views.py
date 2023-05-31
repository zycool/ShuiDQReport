# -*- coding: utf-8 -*-
"""
@author: Neo
@software: PyCharm
@file: views.py
@time: 2023/5/15 20:11
说明:
"""
from django.shortcuts import render


def trade_loss(request):
    context = {}
    return render(request, 'TradeLoss/trade_loss.html', context)


def trade_alpha_one(request):
    context = {}
    return render(request, 'TradeLoss/trade_alpha_one.html', context)
