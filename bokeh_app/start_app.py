# -*- coding: utf-8 -*-
"""
@author: Neo
@software: PyCharm
@file: start_app_trade_detail.py
@time: 2023/6/30 23:05
说明:
"""
from bokeh.command.bootstrap import main

main(["bokeh", "serve", "--show", "--allow-websocket-origin=*:5006", "app_trade_detail.py", "app_alpha_one.py"])