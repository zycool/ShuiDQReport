# -*- coding: utf-8 -*-
"""
@author: Neo
@software: PyCharm
@file: main.py
@time: 2023/5/26 11:29
说明:
"""
from bokeh.command.bootstrap import main

# main(["bokeh", "serve", "--show", "--allow-websocket-origin=*:5006", "app_alpha_one.py"])
main(["bokeh", "serve", "--show", "--allow-websocket-origin=*:5006", "app_trade_detail.py"])