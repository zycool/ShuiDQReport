# -*- coding: utf-8 -*-
"""
@author: Neo
@software: PyCharm
@file: urls.py
@time: 2023/5/25 9:57
说明:
"""
from django.urls import path

from . import views

app_name = 'trade_loss'

urlpatterns = [
    path('', views.trade_loss, name='index'),
    path('alpha_one/', views.trade_alpha_one, name='alpha_one'),
    # path('<int:pk>/', views.PhoneNumDetailView.as_view(), name='detail'),
    #
    #
    # path('recover/<str:req>/', views.recover, name='recover'),

    # path('dashboard/', views.dashboard, name='dashboard'),

    #     path('search/', views.search, name='search'),
    #
    #     path('<int:pk>/export/', views.export_data, name="export"),
    #     path('import_sheet/', views.import_sheet, name="import_sheet"),
]
