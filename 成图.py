# -*- coding: utf-8 -*-
"""
Created on Thu Sep 29 18:51:36 2022

@author: Hello
"""

from pyecharts.charts import Geo
from pyecharts import options as opts
from pyecharts.globals import GeoType
def test_geo():
    city = '南京'
    g = Geo()
    Geo().add_schema(maptype=city)
    list=[]
    with open('D:/test1.xlsx', 'r') as f:
        file_read=f.readlines()
        for readline in file_read:
            rl=str(readline)
            a=rl.split(",")
            list.append(a)
    data_pair = []
    # 定义坐标对应的名称，添加到坐标库中 add_coordinate(name, lng, lat)
    for a in list:
        g.add_coordinate(a[0], a[1], a[2])
        # 定义数据对，
        data_pair.append((a[0],1))
        g.add('', data_pair, type_=GeoType.EFFECT_SCATTER, symbol_size=1)
    # 设置样式
    g.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    # 自定义分段 color 可以用取色器取色
    pieces = [
        {'max': 1, 'label': '0以下', 'color': '#50A3BA'},
        {'min': 1, 'max': 10, 'label': '1-10', 'color': '#3700A4'},
        {'min': 10, 'max': 20, 'label': '10-20', 'color': '#81AE9F'},
        {'min': 20, 'max': 30, 'label': '20-30', 'color': '#E2C568'},
        {'min': 30, 'max': 50, 'label': '30-50', 'color': '#FCF84D'},
        {'min': 50, 'max': 100, 'label': '50-100', 'color': '#DD0200'},
        {'min': 100, 'max': 200, 'label': '100-200', 'color': '#DD675E'},
        {'min': 200, 'label': '200以上', 'color': '#D94E5D'}  # 有下限无上限
    ]
    #  is_piecewise 是否自定义分段， 变为true 才能生效
    g.set_global_opts(
        visualmap_opts=opts.VisualMapOpts(is_piecewise=True, pieces=pieces),
        title_opts=opts.TitleOpts(title="{}-充电站情况".format(city)),
    )
    return g
g = test_geo()
# 渲染成html, 可用浏览器直接打开
g.render('test_render.html')    