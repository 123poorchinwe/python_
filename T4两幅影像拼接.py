# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 20:26:42 2022

@author: Hello
"""

import matplotlib.pyplot as plt
#import numpy as np

import os, sys, gdal
from gdalconst import *
os.chdir("E:/派森/期末/2022期末试题-含DEM数据")#改变文件夹路径
# 注册gdal(required)
gdal.AllRegister()

# 读入第一幅图像
ds1 = gdal.Open("E:/派森/期末/2022期末试题-含DEM数据/ASTGTM2_N31E118_dem.tif")
band1 = ds1.GetRasterBand(1)
rows1 = ds1.RasterYSize
cols1 = ds1.RasterXSize

# 获取图像角点坐标
transform1 = ds1.GetGeoTransform()
minX1 = transform1[0]
maxY1 = transform1[3]
pixelWidth1 = transform1[1]
pixelHeight1 = transform1[5]#是负值（important）
maxX1 = minX1 + (cols1 * pixelWidth1)
minY1 = maxY1 + (rows1 * pixelHeight1)

# 读入第二幅图像
ds2 = gdal.Open("E:/派森/期末/2022期末试题-含DEM数据/ASTGTM2_N32E118_dem.tif")
band2 = ds2.GetRasterBand(1)
rows2 = ds2.RasterYSize
cols2 = ds2.RasterXSize

# 获取图像角点坐标
transform2 = ds2.GetGeoTransform()
minX2 = transform2[0]
maxY2 = transform2[3]
pixelWidth2 = transform2[1]
pixelHeight2 = transform2[5]
maxX2 = minX2 + (cols2 * pixelWidth2)
minY2 = maxY2 + (rows2 * pixelHeight2)

# 获取输出图像坐标
minX = min(minX1, minX2)
maxX = max(maxX1, maxX2)
minY = min(minY1, minY2)
maxY = max(maxY1, maxY2)

#获取输出图像的行与列
cols = int((maxX - minX) / pixelWidth1)
rows = int((maxY - minY) / abs(pixelHeight1))

# 计算图1左上角的偏移值（在输出图像中）
xOffset1 = int((minX1 - minX) / pixelWidth1)
yOffset1 = int((maxY1 - maxY) / pixelHeight1)

# 计算图2左上角的偏移值（在输出图像中）
xOffset2 = int((minX2 - minX) / pixelWidth1)
yOffset2 = int((maxY2 - maxY) / pixelHeight1)

# 创建一个输出图像
driver = ds1.GetDriver()
dsOut = driver.Create('E:/派森/期末/T4/mosiac.tif', cols, rows, 1, band1.DataType)#1是bands，默认
bandOut = dsOut.GetRasterBand(1)

# 读图1的数据并将其写到输出图像中
data1 = band1.ReadAsArray(0, 0, cols1, rows1)
bandOut.WriteArray(data1, xOffset1, yOffset1)

#读图2的数据并将其写到输出图像中
data2 = band2.ReadAsArray(0, 0, cols2, rows2)
bandOut.WriteArray(data2, xOffset2, yOffset2)
''' 写图像步骤'''
# 统计数据
bandOut.FlushCache()#刷新磁盘
stats = bandOut.GetStatistics(0, 1)#第一个参数是1的话，是基于金字塔统计，第二个
#第二个参数是1的话：整幅图像重度，不需要统计
# 设置输出图像的几何信息和投影信息
geotransform = [minX, pixelWidth1, 0, maxY, 0, pixelHeight1]
dsOut.SetGeoTransform(geotransform)
dsOut.SetProjection(ds1.GetProjection())

# 建立输出图像的金字塔
gdal.SetConfigOption('HFA_USE_RRD', 'YES')
dsOut.BuildOverviews(overviewlist=[2,4,8,16])#4层



