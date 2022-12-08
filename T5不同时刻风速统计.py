# -*- coding: utf-8 -*-
"""
Created on Thu Jun 30 23:06:46 2022

@author: Hello
"""
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np

fig=plt.figure(figsize=(8,4),dpi=300)
df = pd.read_csv("E:\派森\期末\T5\data1.csv")  # 读取训练数据
speed1=0
speed2=0
speed3=0
for item in range(0,len(df)-1):
        speed=df['move_speed'].iloc[item]
        if(4<speed<11):
          speed1+=1
        if(10<speed<16):
          speed2+=1
        if(15<speed<21):
          speed3+=1
        
ax = fig.add_subplot(224)        
speed_map = {
    '风速[5,10]': (speed1, '#CC3366'),
    '风速[11,15]': (speed2, '#CC0099'),
    '风速[16,20]': (speed3, '#CC0000')
   
    
}
bar_width = 0.2 
ax.set_title('move_speed强度出现次数专题图')  #子图标题
xticks = np.arange(3)
power = [x[0] for x in speed_map.values()]
#设置x、y轴的范围
#ax.set_xlim([bar_width/2-1, 3-bar_width/2])
#ax.set_ylim([0, 125])
bars = ax.bar(xticks,power, width=bar_width, edgecolor='none',label='power')  #设置柱的边缘为透明


colors = [x[1] for x in speed_map.values()]  #对应颜色
for bar, color in zip(bars, colors):  #给每个bar分配指定的颜色
    bar.set_color(color)
labels=( ' ','风速[5,10]',' ',' 风速[11,15]',' ','风速[16,20]')
ax.set_xticklabels(labels)
ax.legend()
plt.show()
plt.savefig("E:\派森\期末\T5\move_speed强度出现次数专题图.png")
