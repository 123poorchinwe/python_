# -*- coding: utf-8 -*-
"""
Created on Thu Jun 30 17:05:46 2022

@author: Hello
"""

import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
fig=plt.figure(figsize=(8,4))


df = pd.read_csv("E:\派森\期末\T5\data1.csv")  # 读取训练数据
peight=0
pnine=0
pten=0
peleven=0
ptwel=0
pthir=0
pfort=0
pseven=0
for item in range(0,len(df)-1):
        z=df['power'].iloc[item]
        if(z==8):
          peight+=1
        if(z==9):
          pnine=pnine+1
        if(z==10):
          pten+=1
        if(z==11):
          peleven+=1
        if(z==12):
          ptwel+=1
        if(z==13):
          pthir+=1
        if(z==14):
          pfort+=1
        if(z==7):
          pseven+=1
ax = fig.add_subplot(111)        
power_map = {
    '七级': (pseven, '#800080'),
    '八级': (peight, '#BA55D3'),
    '九级': (pnine, '#9400D3'),
    '十级':(pten,'#9932CC'),
    '十一级':(peleven,'#4B0082'),
    '十二级':(ptwel,'#8A2BE2'),
    '十三级':(pthir,'#9370D8'),
    '十四级':(pfort,'#7B68EE')
    
}
bar_width = 0.2 
ax.set_title('power时间段内出现次数专题图')  #子图标题
xticks = np.arange(8)
power = [x[0] for x in power_map.values()]
#设置x、y轴的范围
#ax.set_xlim([bar_width/2-1, 3-bar_width/2])
#ax.set_ylim([0, 125])
bars = ax.bar(xticks,power, width=bar_width, edgecolor='none',label='power')  #设置柱的边缘为透明


colors = [x[1] for x in power_map.values()]  #对应颜色
for bar, color in zip(bars, colors):  #给每个bar分配指定的颜色
    bar.set_color(color)
labels=( '','七级','八级','九级','十级','十一级','十二级','十三级','十四级')
ax.set_xticklabels(labels)
ax.legend()
plt.show()



