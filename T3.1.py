# -*- coding: utf-8 -*-
"""
Created on Sun Jun 26 12:42:56 2022

@author: Hello
"""

# 导入相关库
import os
from osgeo import ogr
import pandas as pd
from osgeo import osr
import glob

# 启动异常报错提示
ogr.UseExceptions()

# .shp文件保存路径
shp_path = r'E:\派森\期末\POI.shp'
# 输入的csv文件路径
csv_path = r'E:\派森\期末\2022期末试题-含DEM数据\POI.csv'

for csv_filename in glob.glob(os.path.join(csv_path,'*.csv')):

    # 读入csv文件信息，设置点几何的字段属性
    csv_df = pd.read_csv(csv_filename)

    # 利用.csv文件创建一个点shp文件
    
    # 获取驱动
    driver = ogr.GetDriverByName('ESRI Shapefile')
    
    # 创建数据源
    shp_filename = os.path.basename(csv_filename)[:-4] + '.shp'
    # 检查数据源是否已存在
    if os.path.exists(os.path.join(shp_path, shp_filename)):
        driver.DeleteDataSource(os.path.join(shp_path, shp_filename))    
    ds = driver.CreateDataSource(os.path.join(shp_path, shp_filename))
    
    # 图层名
    layer_name = os.path.basename(csv_filename)[:-4]
    
    # 定义坐标系对象
    sr = osr.SpatialReference()
    # 使用WGS84地理坐标系
    sr.ImportFromEPSG(4326)
    
    # 创建点图层, 并设置坐标系
    out_lyr = ds.CreateLayer(layer_name, srs = sr, geom_type=ogr.wkbPoint)
    
    # 创建图层定义
    # 利用csv文件中有四个字段创建4个属性字段
    # station字段
    station_fld = ogr.FieldDefn('station', ogr.OFTString)
    station_fld.SetWidth(6)
    out_lyr.CreateField(station_fld)
    # Latitude字段
    lat_fld = ogr.FieldDefn('latitude', ogr.OFTReal)
    lat_fld.SetWidth(9)
    lat_fld.SetPrecision(5)
    out_lyr.CreateField(lat_fld)
    # Longitude字段
    lon_fld = ogr.FieldDefn('longitude', ogr.OFTReal)
    lon_fld.SetWidth(9)
    lon_fld.SetPrecision(5)
    out_lyr.CreateField(lon_fld)
    
    # # pr字段
    # pr_fld = ogr.FieldDefn('pr', ogr.OFTReal)
    # pr_fld.SetWidth(5)
    # pr_fld.SetPrecision(2)
    # out_lyr.CreateField(pr_fld)

    ## tas字段
    #tas_fld = ogr.FieldDefn('tas', ogr.OFTReal)
   # tas_fld.SetWidth(6)
   # tas_fld.SetPrecision(2)
    #out_lyr.CreateField(tas_fld)
    # 从layer中读取相应的feature类型，并创建feature
    featureDefn = out_lyr.GetLayerDefn()
    feature = ogr.Feature(featureDefn)
    
    # 设定几何形状
    point = ogr.Geometry(ogr.wkbPoint)
    
    # 读入csv文件信息，设置点几何的字段属性
    for i in range(len(csv_df)):
        
        # 设置属性值部分
        # 站点Id
        feature.SetField('station', str(csv_df.iloc[i, 0]))
        # 纬度
        feature.SetField('latitude', float(csv_df.iloc[i, 1]))
        # 经度
        feature.SetField('longitude', float(csv_df.iloc[i, 2]))
        # # pr值
        # feature.SetField('pr', float(csv_df.iloc[i, 3]))
        # tas值
        #feature.SetField('tas', float(csv_df.iloc[i, 3]))
        
        # 设置几何信息部分
        # 利用经纬度创建点， X为经度， Y为纬度
        point.AddPoint(float(csv_df.iloc[i, 2]), float(csv_df.iloc[i, 1]))
        feature.SetGeometry(point)
        
        # 将feature写入layer
        out_lyr.CreateFeature(feature)
    
    # 从内存中清除 ds，将数据写入磁盘中
    ds.Destroy()