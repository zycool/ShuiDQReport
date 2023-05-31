# -*- coding: utf-8 -*-
"""
@author: Neo
@software: PyCharm
@file: urls.py
@time: 2023/5/22 11:21
说明:
"""
from django.urls import path

from . import views

app_name = 'stra'

urlpatterns = [
    path('F_C_weight/', views.F_C_weight, name='F_C_weight'),
    path('f_c_values/', views.F_C_values, name='f_c_values'),
    path('F1/', views.F1_about, name='F1_about'),
    path('mv_vol/', views.mv_vol, name='mv_vol'),
    path('bt_alpha_one/', views.bt_alpha_one, name='bt_alpha_one'),
    path('bt_per_2/', views.bt_per_2, name='bt_per_2'),
    path('bt_per_2_4/', views.bt_per_2_4, name='bt_per_2_4'),
    path('bt_cap_and_money/', views.bt_cap_and_money, name='bt_cap_and_money'),

    path('corr/', views.corr_about, name='corr_about'),
    path('ics/', views.ics_about, name='ics_about'),
    path('irs/', views.irs_about, name='irs_about'),

    # path('<int:pk>/', views.PhoneNumDetailView.as_view(), name='detail'),
    #
    #
    # path('recover/<str:req>/', views.recover, name='recover'),

    # path('dashboard/', views.dashboard, name='dashboard'),

    #
    #
    #     path('<int:pk>/export/', views.export_data, name="export"),
    #     path('import_sheet/', views.import_sheet, name="import_sheet"),
]
