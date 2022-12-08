# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 20:28:59 2022

@author: Hello
"""
#
#生成有关裁剪区域的点图层shp文件，然后运用裁剪获得所需区域
import shapefile
from osgeo import osr
#from osgeo import osr
outshp = r'E:\派森\期末\T4\所需区域.shp'
 
w = shapefile.Writer(outshp) # 注意，这里的参数不可以是shapeType=5，必须是文件路径，否则会报错
 
#设置字段，最大长度为254，C为字符串
w.field('FIRST_FLD')
w.field('SECOND_FLD','C','40')
#添加几何和添加字段信息，添加两个示例，字段顺序区分先后
with open(r'E:\派森\期末\T4\所需区域经纬度.txt')as f:
    arr = []
    for line in f:
        line = line.strip()
        line = line.split(',')
        # 第一列，第二列作为经纬度（x，y）创建点
        arr.append([float(line[0]), float(line[1])])
w.poly([arr])
w.record('First','Point')
# w.poly([[[123,37], [118,36], [116,32],[119,20], [124,24],[123,37]]])
# w.record('Second','Point')
#保存
w.close()
 
# 设置投影，通过.prj文件设置，需要写入一个wkt字符串
##gdal的GetProjection()返回的是wkt字符串，需要ImportFromWkt
#projstr="""PROJCS["WGS_1984_UTM_zone_50N",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433],AUTHORITY["EPSG","4326"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",117],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AUTHORITY["EPSG","32650"]]'"""
proj = osr.SpatialReference()
proj.ImportFromEPSG(4326)
#或 proj.ImportFromProj4(proj4str)等其他的来源
wkt = proj.ExportToWkt()
#写出prj文件
f = open(outshp.replace(".shp",".prj"), 'w')
f.write(wkt)
f.close()
