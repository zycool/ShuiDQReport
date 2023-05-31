# -*- coding: utf-8 -*-
"""
@author: Neo
@software: PyCharm
@file: views.py
@time: 2023/5/22 19:27
说明:
"""

from django.shortcuts import render
from bokeh.embed import components


def home_page(request):
    context = {}
    return render(request, 'home_page.html', context)


def dq_alpha_one(request):
    # plot = html_weights_pie()
    # script, div = components(plot)
    # context = {'script': script, 'div': div}
    context = {}
    return render(request, 'dq_alpha_one/index.html', context)
