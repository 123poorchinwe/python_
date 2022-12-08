# -*- coding: utf-8 -*-
"""
Created on Thu Jun 30 12:28:56 2022

@author: Hello
"""

import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
#warnings.filterwarnings('ignore')
#######################################路径##################################
extent= [110,135,20,45]

df = pd.read_csv("E:\派森\期末\T5\data1.csv")  # 读取训练数据
#print(data.shape)
x=df['lon'][:72]
y=df['lat'][:72]
x1=df['lon'][72:144]
y1=df['lat'][72:144]
x2=df['lon'][144:203]
y2=df['lat'][144:203]
fig = plt.figure(figsize=(10,10))
fig = plt.figure(figsize=(12, 8))
ax =fig.subplot(111, projection=ccrs.PlateCarree())
  #  url = 'http://map1c.vis.earthdata.nasa.gov/wmts-geo/wmts.cgi'
  #  layer = 'BlueMarble_ShadedRelief'
   # ax.add_wmts(url, layer)
   # ax.set_extent(extent,crs=ccrs.PlateCarree())
   # 用经纬度对地图区域进行截取，这里只展示我国沿海区域
ax.set_extent([85,170,-20,60], crs=ccrs.PlateCarree())
ax.plot(x,y,color='#900302',linestyle='-',label='2021/7/23 14:00:00前')
ax.plot(x1,y1,label='2021/7/26 14:00:00前')
ax.plot(x2,y2,label='2021/7/30 17:00:00前')
legend=('2021/7/23 14:00:00前','2021/7/26 14:00:00前','2021/7/30 17:00:00前')
ax.legend()
ax.set_title('2021年某台风不同时刻路径图',fontsize=16)
gl = ax.gridlines(draw_labels=False, linewidth=1, color='k', alpha=0.5, linestyle='--')
gl.xlabels_top = gl.ylabels_right = False  
# 设置地图属性，比如加载河流、海洋
ax.add_feature(cfeature.LAND)
ax.add_feature(cfeature.OCEAN)
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.RIVERS)
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.LAKES, alpha=0.5)
# 设置名称
    #ax.set_title('2021年台风路径图',fontsize=16)

    #ax.add_geometries([buffer],ccrs.PlateCarree(),facecolor='#F9009F', edgecolor='none')
   #ax.add_geometries([line],ccrs.PlateCarree(),facecolor='none', edgecolor='#9F0000')
gl = ax.gridlines(draw_labels=False, linewidth=1, color='k', alpha=0.5, linestyle='-')
gl.xlabels_top = gl.ylabels_right = False  
ax.set_xticks(np.arange(extent[0], extent[1]+5, 5))
ax.set_yticks(np.arange(extent[2], extent[3]+5, 5))
#ax.xaxis.set_major_formatter(LongitudeFormatter())
ax.xaxis.set_minor_locator(plt.MultipleLocator(1))
#ax.yaxis.set_major_formatter(LatitudeFormatter())
ax.yaxis.set_minor_locator(plt.MultipleLocator(1))
ax.tick_params(axis='both', labelsize=10, direction='out')
plt.rcParams['font.sans-serif'] = [u'SimHei']
plt.rcParams['axes.unicode_minus'] = False

ax.set_extent([85,170,-20,60], crs=ccrs.PlateCarree())

plt.savefig('../台风不同时刻路径图')


