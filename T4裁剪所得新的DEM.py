# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 20:30:57 2022

@author: Hello
"""

from osgeo import gdal,osr,os
import shapefile
#要裁剪的原图
input_raster = r"E:\派森\期末\T4\mosiac.tif"
input_raster=gdal.Open(input_raster)

#shp文件所在的文件夹
path=r"E:/派森/期末/T4/"

#裁剪结果保存的文件夹
savepath=r"E:/派森/期末/T4/new_dem"

#读取shp文件所在的文件夹
files= os.listdir(path)

for f in files: # 循环读取路径下的文件并筛选输出
  if os.path.splitext(f)[1] == '.shp':
    name=os.path.splitext(f)[0]
    input_shape=path+f
    r = shapefile.Reader(input_shape)
    output_raster=savepath+'.tiff'
    ds=gdal.Warp(output_raster,
        input_raster,
        format = 'GTiff',
       outputBounds=r.bbox,
       cutlineDSName = input_shape,
       cutlineWhere="FIELD = 'whatever'",
       dstNodata = -1000)
ds=None
#给图像设置投影

 
# 1.获取原数据信息
# 该数据只有地理坐标WGS84
ds1 = gdal.Open("E:\派森\期末\T4\mosiac.tiff")
im_geotrans1 = ds1.GetGeoTransform()   #仿射矩阵信息
im_proj1 = ds1.GetProjection()        #地图投影信息
# print(im_geotrans)
# print(im_proj)
im_width1 = ds1.RasterXSize  # 栅格矩阵的列数
im_height1 = ds1.RasterYSize  # 栅格矩阵的行数
im_bands1 = ds1.RasterCount
ds_array1 = ds1.ReadAsArray(0, 0, im_width1, im_height1)  # 获取原数据信息，包括数据类型int16，维度，数组等信息
 
# # 设置数据类型(原图像有负值)
datatype1 = gdal.GDT_Float32
 
 
 
# 2.原图像的仿射变换矩阵参数，即im_geotransfor,m()
#ds.GetGeoTransform()
#Out[7]: 
#(117.99986111111112,0.0002777777777777778,0.0,33.00013888888889,0.0,-0.0002777777777777778)
img_transf1 = (117.99986111111112,
 0.0002777777777777778,
 0.0,
 33.00013888888889,
 0.0,
 -0.0002777777777777778)
# # 网站查询的WGS84-UTM50N坐标信息https://spatialreference.org/ref/epsg/32650/html/
img_proj1 = '''PROJCS["WGS 84 / UTM zone 50N",
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
filename = "E:\派森\期末\T4\new_dem.tiff"
driver = gdal.GetDriverByName("GTiff")  # 创建文件驱动
dataset = driver.Create(filename, im_width1, im_height1, im_bands1, datatype1)
dataset.SetGeoTransform(img_transf1)  # 写入仿射变换参数
dataset.SetProjection(img_proj1)  # 写入投影
 
# 写入影像数据
dataset.GetRasterBand(1).WriteArray(ds_array1)
 
del dataset