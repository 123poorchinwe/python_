# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 13:23:22 2022

@author: Hello
"""

import DEMslopeAspect as dem
from DEMslopeAspect import Drawgrid
import datetime

# 程序入口
if __name__ == "__main__":

    startime = datetime.datetime.now() # 程序开始时间
    # 读取ASTER GDEM遥感影像
    demgrid, proj, geotrans, row, column, band, type =dem.read_img(r"E:\派森\期末\T4\new_dem.tif")
    # geotrans = (114.79763889, 0.00027777777778, 0.0, 38.21347222, 0.0, -0.00027777777778)
    # row = 13777
    # col = 28449
    
    demgridata = demgrid
    # 为计算梯度给影像添加周围一圈数据
    demgrid = dem.AddRound(demgrid)
    # 梯度计算
    dx1,dy1,dx2,dy2 = dem.Cacdxdy(demgrid,30,30)
    # 坡度、坡向计算
    slope,aspect =dem.CacSlopAsp(dx1,dy1,dx2,dy2)
    # 设置要投影的投影信息，此处是WGS84-UTM-50N
    tar_proj = '''PROJCS["WGS 84 / UTM zone 50N",
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
    # 输出TIFF格式遥感影像,并设置投影坐标
    slopeT = dem.write_img(r"E:\派森\期末\T4\slope1.tif", tar_proj, geotrans, slope, type)
    aspectT = dem.write_img(r"E:\派森\期末\T4\aspect1.tif", tar_proj, geotrans, aspect, type)

    endtime = datetime.datetime.now()  # 程序结束时间
    runtime = endtime - startime  # 程序运行时间
    print('运行时间为： %d 秒' % (runtime.seconds))

   