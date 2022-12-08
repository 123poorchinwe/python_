# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 17:06:30 2022

@author: Hello
"""

#encoding:utf-8
import pandas as pd
import geopandas
import pyproj

#添加墨卡托投影的poi矢量文件
df= geopandas.read_file(r"E:\派森\期末\T3\POI.csv",encoding='utf-8')
df['Lon'] = df['Lon'].apply(pd.to_numeric)
df['Lat'] = df['Lat'].apply(pd.to_numeric)
gdf = geopandas.GeoDataFrame(df, geometry=geopandas.points_from_xy(df.Lon, df.Lat))
gdf.crs = pyproj.CRS.from_user_input('epsg:4326') #给输出的shp增加投影 
# gdf.rename(columns={'addrees':'area_ave_price'},inplace=True)
gdf.to_file(r"E:\派森\期末\T3\poi.shp", driver='ESRI Shapefile',encoding='utf-8')