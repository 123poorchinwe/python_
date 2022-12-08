# -*- coding: utf-8 -*-
"""
Created on Sat Jun 25 20:19:08 2022

@author: Hello
"""

#期末T2
#平面上有矩形A和矩形B，它们的边分别平行于X轴和Y轴。
#编写一个程序，提示用户输入矩形A和矩形B在对角线上的顶点坐标，计算两个矩形的公共部分的面积（计算结果保存小数点后两位）。
from shapely.geometry import Polygon
def solution_merge(a,b):
    if a[0]>a[2]:
      a[0],a[2] = a[2],a[0]
    if a[1]>a[3]:
      a[1],a[3] = a[3],a[1]
    if b[0]>b[2]:
      b[0],b[2] = b[2],b[0]
    if b[1]>b[3]:
      b[1],b[3] = b[3],b[1]


    polygon1=Polygon([(a[0],a[1]),(a[0],a[3]),(a[2],a[3]),(a[2],a[1])])
    polygon2=Polygon([(b[0],b[1]),(b[0],b[3]),(b[2],b[3]),(b[2],b[1])])

    c=polygon1.intersection(polygon2)
    q=c.area
    print('\n')  
    print('结果如下')
    print("%.2f"%q)

    
def intersection_solution(a,b):
    

    if a[0]>a[2]:
      a[0],a[2] = a[2],a[0]
    if a[1]>a[3]:
      a[1],a[3] = a[3],a[1]
    if b[0]>b[2]:
      b[0],b[2] = b[2],b[0]
    if b[1]>b[3]:
      b[1],b[3] = b[3],b[1]

    x1 = max(a[0],b[0])
    y1 = max(a[1],b[1])
    x2 = min(a[2],b[2])
    y2 = min(a[3],b[3])


    if y2<y1 or x2<x1:
      c = 0
    else:
      c = (y2-y1)*(x2-x1)
    print('\n')  
    print('结果如下')
    print("{:.2f}".format(c))

    
if __name__ == '__main__' :
    print('请输入矩形1和矩形2的对线顶点坐标，一个矩形一行，共两行\n')
    print('矩形1')
    a = list(map(float, input().split()))
    print('\n')
    print('矩形2')
    b = list(map(float, input().split()))
   
    intersection_solution(a,b)
    
    solution_merge(a,b)
    