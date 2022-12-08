# -*- coding: utf-8 -*-
"""
Created on Fri Jun 24 21:09:13 2022

@author: Hello
"""

#读取图像

import matplotlib.pyplot as plt
import numpy as np
#解决中文显示问题
plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus'] = False

img=plt.imread("E:\派森\期末\T1\my_picture.png")
axe=plt.subplot(111)
axe.imshow(img)
#axe.set_title("我的哈哈照")
axe.annotate('10200409 朱沁韦\nDate:27th June ,2022',
             bbox={'facecolor':'Lavender', 
               'edgecolor':'OliveDrab',
               'alpha':0.9,#类似于像素透明度，0是透明
               'pad':6#填充形状的大小
                   },
             xy=(750,400),#此时的文字会默认出现在右边
             xytext=(850,100),#划定文本开头的位置
             arrowprops=dict(facecolor='Tan' ,shrink=0.1),#箭头收缩
             horizontalalignment='center',#平面线形
             verticalalignment='center')#垂直线性
axe.set_xticks([])
axe.set_yticks([])

plt.savefig("E:\派森\期末\T1\my_picture1.png")
plt.show()