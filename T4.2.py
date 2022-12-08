# -*- coding: utf-8 -*-
"""
Created on Mon Jun 27 18:34:30 2022

@author: Hello
"""

from osgeo import gdal,ogr,osr
import numpy as np
import math
import datetime
 
 
# 读取TIFF遥感影像
def read_img(filename):
 
    dataset = gdal.Open(filename)  # 打开文件
    # dataset = gdal.Open(r'D:\ProfessionalProfile\DEMdata\slopeAspectPython0322\test.tif')
    im_width = dataset.RasterXSize  # 栅格矩阵的列数
    im_height = dataset.RasterYSize  # 栅格矩阵的行数
    im_bands = dataset.RasterCount  # 波段数
    im_geotrans = dataset.GetGeoTransform()  # 仿射矩阵，左上角像素的大地坐标和像素分辨率
    im_proj = dataset.GetProjection()  # 地图投影信息，字符串表示
    im_data = dataset.ReadAsArray(0, 0, im_width, im_height)
    datatype = im_data.dtype
    del dataset  # 关闭对象dataset，释放内存
 
    return   im_data, im_proj, im_geotrans, im_width, im_height, im_bands, datatype
 
 
# 为便于后续坡度计算，需要在原图像的周围添加一圈数值
def AddRound(npgrid):
 
    nx, ny = npgrid.shape[0], npgrid.shape[1]   # ny:行数，nx:列数;此处注意顺序
    # np.zeros()返回来一个给定形状和类型的用0填充的数组；
    zbc=np.zeros((nx+2,ny+2))
    # 填充原数据数组
    zbc[1:-1,1:-1]=npgrid
 
    #四边填充数据
    zbc[0,1:-1]=npgrid[0,:]  #上边；0行，所有列；
    zbc[-1,1:-1]=npgrid[-1,:] #下边；最后一行，所有列；
    zbc[1:-1,0]=npgrid[:,0]  #左边；所有行，0列。
    zbc[1:-1,-1]=npgrid[:,-1] #右边；所有行，最后一列
 
    #填充剩下四个角点值
    zbc[0,0]=npgrid[0,0]
    zbc[0,-1]=npgrid[0,-1]
    zbc[-1,0]=npgrid[-1,0]
    zbc[-1,-1]=npgrid[-1,0]
 
    return zbc
 
 
#计算xy方向的梯度
def Cacdxdy(npgrid,sizex,sizey):
 
    nx, ny = npgrid.shape
    s_dx = np.zeros((nx,ny))
    s_dy = np.zeros((nx,ny))
    a_dx = np.zeros((nx, ny))
    a_dy = np.zeros((nx, ny))
    # 忘记加range报错：object is not iterable
    # 坡度、坡向变化率的计算：https://help.arcgis.com/zh-cn/arcgisdesktop/10.0/help/index.html#/na/009z000000vz000000/
    for i in range(1,nx-1):
        for j in range(1,ny-1):
            s_dx[i,j] = ((npgrid[i-1,j+1]+2*npgrid[i,j+1]+npgrid[i+1,j+1])-(npgrid[i-1,j-1]+2*npgrid[i,j-1]+npgrid[i+1,j-1])) / (8 * sizex)
            s_dy[i, j] = ((npgrid[i+1, j-1] + 2 * npgrid[i+1, j] + npgrid[i+1,j+1])-(npgrid[i-1,j-1]+2 * npgrid[i-1,j] + npgrid[i-1,j+1])) / (8 * sizey)
 
    a_dx=s_dx*sizex
    a_dy=s_dy*sizey
    # 保留原数据区域的梯度值
    s_dx = s_dx[1:-1,1:-1]
    s_dy = s_dy[1:-1,1:-1]
    a_dx = a_dx[1:-1, 1:-1]
    a_dy = a_dy[1:-1, 1:-1]
    # np.savetxt(r"D:\ProfessionalProfile\DEMdata\slopeAspectPython0322\1dxdy.csv",dx,delimiter=",")
 
    return s_dx,s_dy,a_dx,a_dy
 
 
#计算坡度/坡向
def CacSlopAsp(s_dx,s_dy,a_dx,a_dy):
 
    # 坡度
    slope=(np.arctan(np.sqrt(s_dx*s_dx+s_dy*s_dy)))*180/math.pi    #转换成°
 
    #坡向
    # #出错：TypeError: only size-1 arrays can be converted to Python scalars
    # a2 = math.atan2(a_dy,-a_dx)*180/math.pi
    a=np.zeros((a_dy.shape[0],a_dy.shape[1]))
    for i in range(0,a_dx.shape[0]):
        for j in range(0,a_dx.shape[1]):
            a[i,j] = math.atan2(a_dy[i,j], -a_dx[i,j]) * 180 / math.pi
 
    # 输出
    aspect = a
    # 坡向值将根据以下规则转换为罗盘方向值（0 到 360 度）：
    # https://help.arcgis.com/zh-cn/arcgisdesktop/10.0/help/index.html#/na/009z000000vp000000/
    x, y = a.shape[0],a.shape[1]
    for m in range(0,x):
        for n in range(0,y):
            if a[m,n] < 0:
                aspect[m,n] = 90-a[m,n]
            elif a[m,n] > 90:
                aspect[m,n] = 360.0 - a[m,n] + 90.0
            else:
                aspect[m,n] =  90.0 - a[m,n]
 
    return slope,aspect
 
# 遥感影像的存储，写GeoTiff文件
def write_img(filename, tar_proj, im_geotrans, im_data, datatype):
 
    # 判断栅格数据的数据类型
    if 'int8' in im_data.dtype.name:
        datatype = gdal.GDT_Byte
    elif 'int16' in im_data.dtype.name:
        datatype = gdal.GDT_UInt16
    else:
        datatype = gdal.GDT_Float32
 
    # 判读数组维数
    if len(im_data.shape) == 3:
        # 注意数据的存储波段顺序：im_bands, im_height, im_width
        im_bands, im_height, im_width = im_data.shape
    else:
        im_bands, (im_height, im_width) = 1, im_data.shape
 
    # 创建文件时 driver = gdal.GetDriverByName("GTiff")，数据类型必须要指定，因为要计算需要多大内存空间。
    driver = gdal.GetDriverByName("GTiff")
    dataset = driver.Create(filename, im_width, im_height, im_bands, datatype)
    im_geotrans = (117.99986111111112,
 0.0002777777777777778,
 0.0,
 33.00013888888889,
 0.0,
 -0.0002777777777777778)
# # 网站查询的WGS84-UTM50N坐标信息https://spatialreference.org/ref/epsg/32650/html/
    tar_proj= '''PROJCS["WGS 84 / UTM zone 50N",
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
    AUTHORITY["EPSG","32650"]''',
 
    dataset.SetGeoTransform(im_geotrans)  # 写入仿射变换参数
    dataset.SetProjection(tar_proj)  # 写入投影
 
    if im_bands == 1:
        dataset.GetRasterBand(1).WriteArray(im_data)  # 写入数组数据
    else:
        for i in range(im_bands):
            dataset.GetRasterBand(i + 1).WriteArray(im_data[i])
 
    del dataset
 
# 定义投影函数（此次运行没有用到）
def SetPro(filename,tar_proj,outputfilename):
 
    ds = gdal.Open(filename)
    im_geotrans = ds.GetGeoTransform()  # 仿射矩阵信息
    im_proj = ds.GetProjection()  # 地图投影信息
    im_width = ds.RasterXSize  # 栅格矩阵的列数
    im_height = ds.RasterYSize  # 栅格矩阵的行数
    im_bands = ds.RasterCount
    ds_array = ds.ReadAsArray(0, 0, im_width, im_height)  # 获取原数据信息，包括数据类型int16，维度，数组等信息
 
    # 设置数据类型(原图像有负值)
    datatype = gdal.GDT_Float32
    # 目标投影
    img_proj = tar_proj
    # 输出影像路径及名称
    name = outputfilename
    driver = gdal.GetDriverByName("GTiff")  # 创建文件驱动
    dataset = driver.Create(name, im_width, im_height, im_bands, datatype)
    dataset.SetGeoTransform(im_geotrans)  # 写入原图像的仿射变换参数
    dataset.SetProjection(img_proj)  # 写入目标投影
 
    # 写入影像数据
    dataset.GetRasterBand(1).WriteArray(ds_array)
 
    del dataset
 
 
if __name__ == "__main__":
 
    startime = datetime.datetime.now() # 程序开始时间
    # 读取ASTER GDEM遥感影像
    demgrid, proj, geotrans, row, column, band, type = read_img(r"E:\派森\期末\T4\test.tif")
    oridata = demgrid
    # 为计算梯度给影像添加周围一圈数据
    demgrid = AddRound(demgrid)
    # 梯度计算
    dx1,dy1,dx2,dy2 = Cacdxdy(demgrid,30,30)
    # 坡度、坡向计算
    slope,aspect = CacSlopAsp(dx1,dy1,dx2,dy2)
    img_transf1 = (117.99986111111112,
 0.0002777777777777778,
 0.0,
 33.00013888888889,
 0.0,
 -0.0002777777777777778)
# # 网站查询的WGS84-UTM50N坐标信息https://spatialreference.org/ref/epsg/32650/html/

 
 
 
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
    slopeT = write_img(r'E:\派森\期末\T4\slopeSDpy0326.tif', tar_proj, geotrans, slope, type)
    aspectT = write_img(r'E:\派森\期末\T4\slopeAspectPython0322\aspectSDpy0326.tif', tar_proj, geotrans, aspect, type)
 
    endtime = datetime.datetime.now()   # 程序结束时间
    runtime = endtime-startime   # 程序运行时间
 
    print('运行时间为： %d 秒' %(runtime.seconds))