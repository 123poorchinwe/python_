# -*- coding: utf-8 -*-
"""
Created on Mon Jun 27 22:04:28 2022

@author: Hello
"""

#给图像设置投影
from osgeo import gdal,osr,gdalnumeric
from osgeo.gdalconst import *
from pyproj import CRS
 
# 1.获取原数据信息
# 该数据只有地理坐标WGS84
ds = gdal.Open('E:/派森/期末/T4/mosiac.tif')
im_geotrans = ds.GetGeoTransform()   #仿射矩阵信息
im_proj = ds.GetProjection()        #地图投影信息
# print(im_geotrans)
# print(im_proj)
im_width = ds.RasterXSize  # 栅格矩阵的列数
im_height = ds.RasterYSize  # 栅格矩阵的行数
im_bands = ds.RasterCount
ds_array = ds.ReadAsArray(0, 0, im_width, im_height)  # 获取原数据信息，包括数据类型int16，维度，数组等信息
 
# # 设置数据类型(原图像有负值)
datatype = gdal.GDT_Float32
 
 
 
# 2.原图像的仿射变换矩阵参数，即im_geotransfor,m()
#ds.GetGeoTransform()
#Out[7]: 
#(117.99986111111112,0.0002777777777777778,0.0,33.00013888888889,0.0,-0.0002777777777777778)
img_transf = (117.99986111111112,
 0.0002777777777777778,
 0.0,
 33.00013888888889,
 0.0,
 -0.0002777777777777778)
# # 网站查询的WGS84-UTM50N坐标信息https://spatialreference.org/ref/epsg/32650/html/
img_proj = '''PROJCS["WGS 84 / UTM zone 50N",
    GEOGCS["WGS 84",
        DATUM["WGS_1984",
            SPHEROID["WGS 84",6378137,298.257223563,
                AUTHORITY["EPSG","7030"]],
            AUTHORITY["EPSG","6326"]],
        PRIMEM["Greenwich",0,
            AUTHORITY["EPSG","8901"]],
        UNIT["degree",0.01745329251994328,
            AUTHORITY["EPSG","9122"]],
        AUTHORITY["EPSG","4326"]],
    UNIT["metre",1,
        AUTHORITY["EPSG","9001"]],
    PROJECTION["Transverse_Mercator"],
    PARAMETER["latitude_of_origin",0],
    PARAMETER["central_meridian",117],
    PARAMETER["scale_factor",0.9996],
    PARAMETER["false_easting",500000],
    PARAMETER["false_northing",0],
    AUTHORITY["EPSG","32650"],
    AXIS["Easting",EAST],
    AXIS["Northing",NORTH]]'''
 
 
 
# 3.设置新文件及各项参数
filename = 'E:/派森/期末/T4/mosiac1.tif'
driver = gdal.GetDriverByName("GTiff")  # 创建文件驱动
dataset = driver.Create(filename, im_width, im_height, im_bands, datatype)
dataset.SetGeoTransform(img_transf)  # 写入仿射变换参数
dataset.SetProjection(img_proj)  # 写入投影
 
# 写入影像数据
dataset.GetRasterBand(1).WriteArray(ds_array)
 
del dataset
