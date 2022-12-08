# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 10:36:52 2022

@author: Hello
"""

from osgeo import gdal
from osgeo import ogr
from osgeo import osr

'''
通过Filter读取Shapefile中属性过滤后的数据
'''
shape_path = "E:\派森\期末\T3\county_popu.shp"
ds = ogr.Open(shape_path)
layer = ds.GetLayer(0)
srs = layer.GetSpatialRef()
layer_defn = layer.GetLayerDefn()
field_count = layer_defn.GetFieldCount()
filed_name_list = [] #暂存原始Shapefile的属性字段的名字
for iField in range(0, field_count):
    temp_field = layer_defn.GetFieldDefn(iField)
    temp_name = temp_field.GetName()
    filed_name_list.append(temp_name)
    print(temp_name)
#上海是310开头
layer.SetAttributeFilter('("PAC"/1)=310101')
feature_count = layer.GetFeatureCount()

layer.ResetReading()
feature_list = [] #暂存过滤后的Feature数据
temp_feature = layer.GetNextFeature()
while temp_feature:
    temp_geom = temp_feature.GetGeometryRef()
    temp_field_area = temp_feature.GetField('Shape_Area')
    temp_field_name = temp_feature.GetField('NAME')
    temp_calculatet_area = temp_geom.Area()
    print('Name:', temp_field_name,
          'Area:', temp_field_area, 
          'Cal_Area:', temp_calculatet_area)
    feature_list.append(temp_feature)
    temp_feature = layer.GetNextFeature()


'''
将过滤后的Feature保存到新的文件中
'''
gdal.SetConfigOption("SHAPE_ENCODING", "UTF-8") # IMPORTANT
new_shape_path = 'E:/派森/期末/T3/shanghai_黄浦区.shp'

driverName = "ESRI Shapefile"
driver = ogr.GetDriverByName(driverName)
ds = driver.CreateDataSource(new_shape_path) #创建DataSource

geomType = ogr.wkbPolygon #指定几何类型
#创建图层，注意srs借用的是原来的
poLayer = ds.CreateLayer('shanghai_黄浦区', srs, geomType)

#对原始数据的属性字段进行遍历
for iField in range(0, field_count):
    temp_field = layer_defn.GetFieldDefn(iField)
    poLayer.CreateField(temp_field, 1)
    
#创建完所有的属性字段之后，获取整个图层的定义
new_layerdef = poLayer.GetLayerDefn()

for iF in range(0, feature_count):
    temp_old_feature = feature_list[iF]
    temp_geom = temp_old_feature.GetGeometryRef()
    
    tempNewFeature = ogr.Feature(new_layerdef)
    tempNewFeature.SetGeometry(temp_geom)
    for temp_name in filed_name_list:
        tempNewFeature.SetField(temp_name,temp_old_feature.GetField(temp_name))

    poLayer.CreateFeature(tempNewFeature)
    del tempNewFeature

ds.FlushCache()
if ds != None: ds.Destroy()


'''
将过滤后的Feature保存到新的文件中, 并且做投影转换
'''
new_shape_path = "E:\派森\期末\T3\shanghai_wgs84_黄浦区.shp"

driverName = "ESRI Shapefile"
driver = ogr.GetDriverByName(driverName)
ds = driver.CreateDataSource(new_shape_path)

geomType = ogr.wkbPolygon
srs_4326 = osr.SpatialReference(osr.SRS_WKT_WGS84_LAT_LONG) # 指定新的空间参考
srs_4326.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER) # 按照传统先X后Y的顺序进行坐标转换
#注意此处，指定了options=["ENCODING=UTF-8"], 会生成了以 *.cpg的文件, 里面给出了文字编码
layerjs_4326 = ds.CreateLayer('sh_黄浦区', srs_4326, geomType, options=["ENCODING=UTF-8"])

#选用了某几个属性字段放到新的Shapefile中
field1 = ogr.FieldDefn("PAC", ogr.OFTInteger64)
layerjs_4326.CreateField(field1, 1)
field1.Destroy()

field2 = ogr.FieldDefn("NAME", ogr.OFTString)
layerjs_4326.CreateField(field2, 1)
field2.Destroy()

field3 = ogr.FieldDefn("AREA", ogr.OFTReal)
layerjs_4326.CreateField(field3, 1)
field3.Destroy()

#获取新数据的图层属性
layerjs_def = layerjs_4326.GetLayerDefn()

#根据原始坐标参考和新的坐标参考，构建一个投影转换器
trans = osr.CoordinateTransformation(srs, srs_4326)

for iF in range(0, feature_count):
    temp_feature = feature_list[iF]

    temp_geom = temp_feature.GetGeometryRef() # 拿到Feature的Geometry对象
    temp_geom_type = temp_geom.GetGeometryType() # 拿到Geometry的几何类型
    temp_geom_count = temp_geom.GetGeometryCount() # 有可能是Multi-Polygon
    
    temp_new_polygon = None
    if temp_geom_type == ogr.wkbMultiPolygon and temp_geom_count>1:
        print("geometry name:", temp_geom.GetGeometryName())
        #print(temp_geom.GetGeometryName())
        temp_new_polygon = ogr.Geometry(ogr.wkbMultiPolygon)
        for iGeo in range(0, temp_geom_count):
            temp_part = temp_geom.GetGeometryRef(iGeo) # 获取Multi中的每一个Part
            temp_part_ring_count = temp_part.GetGeometryCount() # 每个Polygon可能会有ExRing和InRing
            #print("polygon's ring count:", temp_part_ring_count)
            
            temp_new_part = ogr.Geometry(ogr.wkbPolygon)
            for iRing in range(0, temp_part_ring_count):
                temp_ring = temp_part.GetGeometryRef(iRing)

                temp_new_ring = ogr.Geometry(ogr.wkbLinearRing)
                
                # 第一种写法
                temp_ring_point_count = temp_ring.GetPointCount()
                for iP in range(0, temp_ring_point_count):
                    temp_point = temp_ring.GetPoint(iP)
                    new_p = trans.TransformPoint(temp_point[0], temp_point[1])
                    #print(new_p)
                    temp_new_ring.AddPoint(new_p[0], new_p[1])
                temp_new_part.AddGeometry(temp_new_ring)
            
            temp_new_polygon.AddGeometry(temp_new_part)
    else:
        print("geometry name:", temp_geom.GetGeometryName())
        temp_new_polygon = ogr.Geometry(ogr.wkbPolygon)

        temp_ring_count = temp_geom.GetGeometryCount() # Polygon有可能带岛
        #print("polygon's ring count:", temp_ring_count)
        for iRing in range(0, temp_ring_count):
            temp_ring = temp_geom.GetGeometryRef(iRing) # 遍历每一个Ring，默认第一个是外环
            
            # 第二种写法
            # new_points = trans.TransformPoints(temp_ring.GetPoints())
            # print(new_points)

            # 第三种写法
            import pyproj
            source_proj = pyproj.Proj(srs.ExportToProj4())
            target_proj = pyproj.Proj(4326)
            prjtrans = pyproj.Transformer.from_proj(source_proj, target_proj)
            # 注意以上四行应该写到循环外面
            temp_ring_point_count = temp_ring.GetPointCount()
            new_points = []
            for iP in range(0, temp_ring_point_count):
                temp_point = temp_ring.GetPoint(iP)
                new_p = prjtrans.transform(temp_point[0], temp_point[1])
                #print(new_p) #注意，转出来的经纬度是反的
                new_points.append((new_p[1], new_p[0]))

            temp_new_ring = ogr.Geometry(ogr.wkbLinearRing)
            for new_p in new_points:
                temp_new_ring.AddPoint(new_p[0], new_p[1])
            temp_new_polygon.AddGeometry(temp_new_ring)
    # end if-else geometry type

    if temp_new_polygon != None:
        tempNewFeature = ogr.Feature(layerjs_def)
        tempNewFeature.SetGeometry(temp_new_polygon)
        tempNewFeature.SetField("PAC",temp_feature.GetField("PAC"))
        tempNewFeature.SetField("NAME",temp_feature.GetField("NAME"))
        tempNewFeature.SetField("AREA",temp_feature.GetField("AREA"))

        layerjs_4326.CreateFeature(tempNewFeature)
        tempNewFeature.Destroy()

ds.FlushCache()
if ds != None: ds.Destroy()

shape_path = "E:\派森\期末\T3\county_popu.shp"
ds = ogr.Open(shape_path)
layer = ds.GetLayer(0)
srs = layer.GetSpatialRef()
layer_defn = layer.GetLayerDefn()
field_count = layer_defn.GetFieldCount()
filed_name_list = [] #暂存原始Shapefile的属性字段的名字
for iField in range(0, field_count):
    temp_field = layer_defn.GetFieldDefn(iField)
    temp_name = temp_field.GetName()
    filed_name_list.append(temp_name)
    print(temp_name)
#上海是310开头
layer.SetAttributeFilter('("PAC"/1)=310104')
feature_count = layer.GetFeatureCount()
# 注意此处不宜使用For循环直接遍历
# 如果要用，属性过滤器是不起作用的
# 还需要在循环内部进行If判断
# for i in range(0, feature_count): 
#     temp_feature = layer.GetFeature(i)
#     temp_field_pac = temp_feature.GetField('PAC')
#     if temp_field_pac/10000 != 32:
#         continue
layer.ResetReading()
feature_list = [] #暂存过滤后的Feature数据
temp_feature = layer.GetNextFeature()
while temp_feature:
    temp_geom = temp_feature.GetGeometryRef()
    temp_field_area = temp_feature.GetField('Shape_Area')
    temp_field_name = temp_feature.GetField('NAME')
    temp_calculatet_area = temp_geom.Area()
    print('Name:', temp_field_name,
          'Area:', temp_field_area, 
          'Cal_Area:', temp_calculatet_area)
    feature_list.append(temp_feature)
    temp_feature = layer.GetNextFeature()


'''
将过滤后的Feature保存到新的文件中
'''
gdal.SetConfigOption("SHAPE_ENCODING", "UTF-8") # IMPORTANT
new_shape_path = 'E:/派森/期末/T3/shanghai_徐汇区.shp'

driverName = "ESRI Shapefile"
driver = ogr.GetDriverByName(driverName)
ds = driver.CreateDataSource(new_shape_path) #创建DataSource

geomType = ogr.wkbPolygon #指定几何类型
#创建图层，注意srs借用的是原来的
poLayer = ds.CreateLayer('shanghai_徐汇区', srs, geomType)

#对原始数据的属性字段进行遍历
for iField in range(0, field_count):
    temp_field = layer_defn.GetFieldDefn(iField)
    poLayer.CreateField(temp_field, 1)
    
#创建完所有的属性字段之后，获取整个图层的定义
new_layerdef = poLayer.GetLayerDefn()

for iF in range(0, feature_count):
    temp_old_feature = feature_list[iF]
    temp_geom = temp_old_feature.GetGeometryRef()
    
    tempNewFeature = ogr.Feature(new_layerdef)
    tempNewFeature.SetGeometry(temp_geom)
    for temp_name in filed_name_list:
        tempNewFeature.SetField(temp_name,temp_old_feature.GetField(temp_name))

    poLayer.CreateFeature(tempNewFeature)
    del tempNewFeature

ds.FlushCache()
if ds != None: ds.Destroy()


'''
将过滤后的Feature保存到新的文件中, 并且做投影转换
'''
new_shape_path = "E:\派森\期末\T3\shanghai_wgs84_徐汇区.shp"

driverName = "ESRI Shapefile"
driver = ogr.GetDriverByName(driverName)
ds = driver.CreateDataSource(new_shape_path)

geomType = ogr.wkbPolygon
srs_4326 = osr.SpatialReference(osr.SRS_WKT_WGS84_LAT_LONG) # 指定新的空间参考
srs_4326.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER) # 按照传统先X后Y的顺序进行坐标转换
#注意此处，指定了options=["ENCODING=UTF-8"], 会生成了以 *.cpg的文件, 里面给出了文字编码
layerjs_4326 = ds.CreateLayer('sh_徐汇区', srs_4326, geomType, options=["ENCODING=UTF-8"])

#选用了某几个属性字段放到新的Shapefile中
field1 = ogr.FieldDefn("PAC", ogr.OFTInteger64)
layerjs_4326.CreateField(field1, 1)
field1.Destroy()

field2 = ogr.FieldDefn("NAME", ogr.OFTString)
layerjs_4326.CreateField(field2, 1)
field2.Destroy()

field3 = ogr.FieldDefn("AREA", ogr.OFTReal)
layerjs_4326.CreateField(field3, 1)
field3.Destroy()

#获取新数据的图层属性
layerjs_def = layerjs_4326.GetLayerDefn()

#根据原始坐标参考和新的坐标参考，构建一个投影转换器
trans = osr.CoordinateTransformation(srs, srs_4326)

for iF in range(0, feature_count):
    temp_feature = feature_list[iF]

    temp_geom = temp_feature.GetGeometryRef() # 拿到Feature的Geometry对象
    temp_geom_type = temp_geom.GetGeometryType() # 拿到Geometry的几何类型
    temp_geom_count = temp_geom.GetGeometryCount() # 有可能是Multi-Polygon
    
    temp_new_polygon = None
    if temp_geom_type == ogr.wkbMultiPolygon and temp_geom_count>1:
        print("geometry name:", temp_geom.GetGeometryName())
        #print(temp_geom.GetGeometryName())
        temp_new_polygon = ogr.Geometry(ogr.wkbMultiPolygon)
        for iGeo in range(0, temp_geom_count):
            temp_part = temp_geom.GetGeometryRef(iGeo) # 获取Multi中的每一个Part
            temp_part_ring_count = temp_part.GetGeometryCount() # 每个Polygon可能会有ExRing和InRing
            #print("polygon's ring count:", temp_part_ring_count)
            
            temp_new_part = ogr.Geometry(ogr.wkbPolygon)
            for iRing in range(0, temp_part_ring_count):
                temp_ring = temp_part.GetGeometryRef(iRing)

                temp_new_ring = ogr.Geometry(ogr.wkbLinearRing)
                
                # 第一种写法
                temp_ring_point_count = temp_ring.GetPointCount()
                for iP in range(0, temp_ring_point_count):
                    temp_point = temp_ring.GetPoint(iP)
                    new_p = trans.TransformPoint(temp_point[0], temp_point[1])
                    #print(new_p)
                    temp_new_ring.AddPoint(new_p[0], new_p[1])
                temp_new_part.AddGeometry(temp_new_ring)
            
            temp_new_polygon.AddGeometry(temp_new_part)
    else:
        print("geometry name:", temp_geom.GetGeometryName())
        temp_new_polygon = ogr.Geometry(ogr.wkbPolygon)

        temp_ring_count = temp_geom.GetGeometryCount() # Polygon有可能带岛
        #print("polygon's ring count:", temp_ring_count)
        for iRing in range(0, temp_ring_count):
            temp_ring = temp_geom.GetGeometryRef(iRing) # 遍历每一个Ring，默认第一个是外环
            
            # 第二种写法
            # new_points = trans.TransformPoints(temp_ring.GetPoints())
            # print(new_points)

            # 第三种写法
            import pyproj
            source_proj = pyproj.Proj(srs.ExportToProj4())
            target_proj = pyproj.Proj(4326)
            prjtrans = pyproj.Transformer.from_proj(source_proj, target_proj)
            # 注意以上四行应该写到循环外面
            temp_ring_point_count = temp_ring.GetPointCount()
            new_points = []
            for iP in range(0, temp_ring_point_count):
                temp_point = temp_ring.GetPoint(iP)
                new_p = prjtrans.transform(temp_point[0], temp_point[1])
                #print(new_p) #注意，转出来的经纬度是反的
                new_points.append((new_p[1], new_p[0]))

            temp_new_ring = ogr.Geometry(ogr.wkbLinearRing)
            for new_p in new_points:
                temp_new_ring.AddPoint(new_p[0], new_p[1])
            temp_new_polygon.AddGeometry(temp_new_ring)
    # end if-else geometry type

    if temp_new_polygon != None:
        tempNewFeature = ogr.Feature(layerjs_def)
        tempNewFeature.SetGeometry(temp_new_polygon)
        tempNewFeature.SetField("PAC",temp_feature.GetField("PAC"))
        tempNewFeature.SetField("NAME",temp_feature.GetField("NAME"))
        tempNewFeature.SetField("AREA",temp_feature.GetField("AREA"))

        layerjs_4326.CreateFeature(tempNewFeature)
        tempNewFeature.Destroy()

ds.FlushCache()
if ds != None: ds.Destroy()

shape_path = "E:\派森\期末\T3\county_popu.shp"
ds = ogr.Open(shape_path)
layer = ds.GetLayer(0)
srs = layer.GetSpatialRef()
layer_defn = layer.GetLayerDefn()
field_count = layer_defn.GetFieldCount()
filed_name_list = [] #暂存原始Shapefile的属性字段的名字
for iField in range(0, field_count):
    temp_field = layer_defn.GetFieldDefn(iField)
    temp_name = temp_field.GetName()
    filed_name_list.append(temp_name)
    print(temp_name)
#上海是310开头
layer.SetAttributeFilter('("PAC"/1)=310105')
feature_count = layer.GetFeatureCount()
# 注意此处不宜使用For循环直接遍历
# 如果要用，属性过滤器是不起作用的
# 还需要在循环内部进行If判断
# for i in range(0, feature_count): 
#     temp_feature = layer.GetFeature(i)
#     temp_field_pac = temp_feature.GetField('PAC')
#     if temp_field_pac/10000 != 32:
#         continue
layer.ResetReading()
feature_list = [] #暂存过滤后的Feature数据
temp_feature = layer.GetNextFeature()
while temp_feature:
    temp_geom = temp_feature.GetGeometryRef()
    temp_field_area = temp_feature.GetField('Shape_Area')
    temp_field_name = temp_feature.GetField('NAME')
    temp_calculatet_area = temp_geom.Area()
    print('Name:', temp_field_name,
          'Area:', temp_field_area, 
          'Cal_Area:', temp_calculatet_area)
    feature_list.append(temp_feature)
    temp_feature = layer.GetNextFeature()


'''
将过滤后的Feature保存到新的文件中
'''
gdal.SetConfigOption("SHAPE_ENCODING", "UTF-8") # IMPORTANT
new_shape_path = 'E:/派森/期末/T3/shanghai_长宁区.shp'

driverName = "ESRI Shapefile"
driver = ogr.GetDriverByName(driverName)
ds = driver.CreateDataSource(new_shape_path) #创建DataSource

geomType = ogr.wkbPolygon #指定几何类型
#创建图层，注意srs借用的是原来的
poLayer = ds.CreateLayer('shanghai_长宁区', srs, geomType)

#对原始数据的属性字段进行遍历
for iField in range(0, field_count):
    temp_field = layer_defn.GetFieldDefn(iField)
    poLayer.CreateField(temp_field, 1)
    
#创建完所有的属性字段之后，获取整个图层的定义
new_layerdef = poLayer.GetLayerDefn()

for iF in range(0, feature_count):
    temp_old_feature = feature_list[iF]
    temp_geom = temp_old_feature.GetGeometryRef()
    
    tempNewFeature = ogr.Feature(new_layerdef)
    tempNewFeature.SetGeometry(temp_geom)
    for temp_name in filed_name_list:
        tempNewFeature.SetField(temp_name,temp_old_feature.GetField(temp_name))

    poLayer.CreateFeature(tempNewFeature)
    del tempNewFeature

ds.FlushCache()
if ds != None: ds.Destroy()


'''
将过滤后的Feature保存到新的文件中, 并且做投影转换
'''
new_shape_path = "E:\派森\期末\T3\shanghai_wgs84_长宁区.shp"

driverName = "ESRI Shapefile"
driver = ogr.GetDriverByName(driverName)
ds = driver.CreateDataSource(new_shape_path)

geomType = ogr.wkbPolygon
srs_4326 = osr.SpatialReference(osr.SRS_WKT_WGS84_LAT_LONG) # 指定新的空间参考
srs_4326.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER) # 按照传统先X后Y的顺序进行坐标转换
#注意此处，指定了options=["ENCODING=UTF-8"], 会生成了以 *.cpg的文件, 里面给出了文字编码
layerjs_4326 = ds.CreateLayer('sh_长宁区', srs_4326, geomType, options=["ENCODING=UTF-8"])

#选用了某几个属性字段放到新的Shapefile中
field1 = ogr.FieldDefn("PAC", ogr.OFTInteger64)
layerjs_4326.CreateField(field1, 1)
field1.Destroy()

field2 = ogr.FieldDefn("NAME", ogr.OFTString)
layerjs_4326.CreateField(field2, 1)
field2.Destroy()

field3 = ogr.FieldDefn("AREA", ogr.OFTReal)
layerjs_4326.CreateField(field3, 1)
field3.Destroy()

#获取新数据的图层属性
layerjs_def = layerjs_4326.GetLayerDefn()

#根据原始坐标参考和新的坐标参考，构建一个投影转换器
trans = osr.CoordinateTransformation(srs, srs_4326)

for iF in range(0, feature_count):
    temp_feature = feature_list[iF]

    temp_geom = temp_feature.GetGeometryRef() # 拿到Feature的Geometry对象
    temp_geom_type = temp_geom.GetGeometryType() # 拿到Geometry的几何类型
    temp_geom_count = temp_geom.GetGeometryCount() # 有可能是Multi-Polygon
    
    temp_new_polygon = None
    if temp_geom_type == ogr.wkbMultiPolygon and temp_geom_count>1:
        print("geometry name:", temp_geom.GetGeometryName())
        #print(temp_geom.GetGeometryName())
        temp_new_polygon = ogr.Geometry(ogr.wkbMultiPolygon)
        for iGeo in range(0, temp_geom_count):
            temp_part = temp_geom.GetGeometryRef(iGeo) # 获取Multi中的每一个Part
            temp_part_ring_count = temp_part.GetGeometryCount() # 每个Polygon可能会有ExRing和InRing
            #print("polygon's ring count:", temp_part_ring_count)
            
            temp_new_part = ogr.Geometry(ogr.wkbPolygon)
            for iRing in range(0, temp_part_ring_count):
                temp_ring = temp_part.GetGeometryRef(iRing)

                temp_new_ring = ogr.Geometry(ogr.wkbLinearRing)
                
                # 第一种写法
                temp_ring_point_count = temp_ring.GetPointCount()
                for iP in range(0, temp_ring_point_count):
                    temp_point = temp_ring.GetPoint(iP)
                    new_p = trans.TransformPoint(temp_point[0], temp_point[1])
                    #print(new_p)
                    temp_new_ring.AddPoint(new_p[0], new_p[1])
                temp_new_part.AddGeometry(temp_new_ring)
            
            temp_new_polygon.AddGeometry(temp_new_part)
    else:
        print("geometry name:", temp_geom.GetGeometryName())
        temp_new_polygon = ogr.Geometry(ogr.wkbPolygon)

        temp_ring_count = temp_geom.GetGeometryCount() # Polygon有可能带岛
        #print("polygon's ring count:", temp_ring_count)
        for iRing in range(0, temp_ring_count):
            temp_ring = temp_geom.GetGeometryRef(iRing) # 遍历每一个Ring，默认第一个是外环
            
            # 第二种写法
            # new_points = trans.TransformPoints(temp_ring.GetPoints())
            # print(new_points)

            # 第三种写法
            import pyproj
            source_proj = pyproj.Proj(srs.ExportToProj4())
            target_proj = pyproj.Proj(4326)
            prjtrans = pyproj.Transformer.from_proj(source_proj, target_proj)
            # 注意以上四行应该写到循环外面
            temp_ring_point_count = temp_ring.GetPointCount()
            new_points = []
            for iP in range(0, temp_ring_point_count):
                temp_point = temp_ring.GetPoint(iP)
                new_p = prjtrans.transform(temp_point[0], temp_point[1])
                #print(new_p) #注意，转出来的经纬度是反的
                new_points.append((new_p[1], new_p[0]))

            temp_new_ring = ogr.Geometry(ogr.wkbLinearRing)
            for new_p in new_points:
                temp_new_ring.AddPoint(new_p[0], new_p[1])
            temp_new_polygon.AddGeometry(temp_new_ring)
    # end if-else geometry type

    if temp_new_polygon != None:
        tempNewFeature = ogr.Feature(layerjs_def)
        tempNewFeature.SetGeometry(temp_new_polygon)
        tempNewFeature.SetField("PAC",temp_feature.GetField("PAC"))
        tempNewFeature.SetField("NAME",temp_feature.GetField("NAME"))
        tempNewFeature.SetField("AREA",temp_feature.GetField("AREA"))

        layerjs_4326.CreateFeature(tempNewFeature)
        tempNewFeature.Destroy()

ds.FlushCache()
if ds != None: ds.Destroy()

shape_path = "E:\派森\期末\T3\county_popu.shp"
ds = ogr.Open(shape_path)
layer = ds.GetLayer(0)
srs = layer.GetSpatialRef()
layer_defn = layer.GetLayerDefn()
field_count = layer_defn.GetFieldCount()
filed_name_list = [] #暂存原始Shapefile的属性字段的名字
for iField in range(0, field_count):
    temp_field = layer_defn.GetFieldDefn(iField)
    temp_name = temp_field.GetName()
    filed_name_list.append(temp_name)
    print(temp_name)
#上海是310开头
layer.SetAttributeFilter('("PAC"/1)=310106')
feature_count = layer.GetFeatureCount()
# 注意此处不宜使用For循环直接遍历
# 如果要用，属性过滤器是不起作用的
# 还需要在循环内部进行If判断
# for i in range(0, feature_count): 
#     temp_feature = layer.GetFeature(i)
#     temp_field_pac = temp_feature.GetField('PAC')
#     if temp_field_pac/10000 != 32:
#         continue
layer.ResetReading()
feature_list = [] #暂存过滤后的Feature数据
temp_feature = layer.GetNextFeature()
while temp_feature:
    temp_geom = temp_feature.GetGeometryRef()
    temp_field_area = temp_feature.GetField('Shape_Area')
    temp_field_name = temp_feature.GetField('NAME')
    temp_calculatet_area = temp_geom.Area()
    print('Name:', temp_field_name,
          'Area:', temp_field_area, 
          'Cal_Area:', temp_calculatet_area)
    feature_list.append(temp_feature)
    temp_feature = layer.GetNextFeature()


'''
将过滤后的Feature保存到新的文件中
'''
gdal.SetConfigOption("SHAPE_ENCODING", "UTF-8") # IMPORTANT
new_shape_path = 'E:/派森/期末/T3/shanghai_静安区.shp'

driverName = "ESRI Shapefile"
driver = ogr.GetDriverByName(driverName)
ds = driver.CreateDataSource(new_shape_path) #创建DataSource

geomType = ogr.wkbPolygon #指定几何类型
#创建图层，注意srs借用的是原来的
poLayer = ds.CreateLayer('shanghai_静安区', srs, geomType)

#对原始数据的属性字段进行遍历
for iField in range(0, field_count):
    temp_field = layer_defn.GetFieldDefn(iField)
    poLayer.CreateField(temp_field, 1)
    
#创建完所有的属性字段之后，获取整个图层的定义
new_layerdef = poLayer.GetLayerDefn()

for iF in range(0, feature_count):
    temp_old_feature = feature_list[iF]
    temp_geom = temp_old_feature.GetGeometryRef()
    
    tempNewFeature = ogr.Feature(new_layerdef)
    tempNewFeature.SetGeometry(temp_geom)
    for temp_name in filed_name_list:
        tempNewFeature.SetField(temp_name,temp_old_feature.GetField(temp_name))

    poLayer.CreateFeature(tempNewFeature)
    del tempNewFeature

ds.FlushCache()
if ds != None: ds.Destroy()


'''
将过滤后的Feature保存到新的文件中, 并且做投影转换
'''
new_shape_path = "E:\派森\期末\T3\shanghai_wgs84_静安区.shp"

driverName = "ESRI Shapefile"
driver = ogr.GetDriverByName(driverName)
ds = driver.CreateDataSource(new_shape_path)

geomType = ogr.wkbPolygon
srs_4326 = osr.SpatialReference(osr.SRS_WKT_WGS84_LAT_LONG) # 指定新的空间参考
srs_4326.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER) # 按照传统先X后Y的顺序进行坐标转换
#注意此处，指定了options=["ENCODING=UTF-8"], 会生成了以 *.cpg的文件, 里面给出了文字编码
layerjs_4326 = ds.CreateLayer('sh_静安区', srs_4326, geomType, options=["ENCODING=UTF-8"])

#选用了某几个属性字段放到新的Shapefile中
field1 = ogr.FieldDefn("PAC", ogr.OFTInteger64)
layerjs_4326.CreateField(field1, 1)
field1.Destroy()

field2 = ogr.FieldDefn("NAME", ogr.OFTString)
layerjs_4326.CreateField(field2, 1)
field2.Destroy()

field3 = ogr.FieldDefn("AREA", ogr.OFTReal)
layerjs_4326.CreateField(field3, 1)
field3.Destroy()

#获取新数据的图层属性
layerjs_def = layerjs_4326.GetLayerDefn()

#根据原始坐标参考和新的坐标参考，构建一个投影转换器
trans = osr.CoordinateTransformation(srs, srs_4326)

for iF in range(0, feature_count):
    temp_feature = feature_list[iF]

    temp_geom = temp_feature.GetGeometryRef() # 拿到Feature的Geometry对象
    temp_geom_type = temp_geom.GetGeometryType() # 拿到Geometry的几何类型
    temp_geom_count = temp_geom.GetGeometryCount() # 有可能是Multi-Polygon
    
    temp_new_polygon = None
    if temp_geom_type == ogr.wkbMultiPolygon and temp_geom_count>1:
        print("geometry name:", temp_geom.GetGeometryName())
        #print(temp_geom.GetGeometryName())
        temp_new_polygon = ogr.Geometry(ogr.wkbMultiPolygon)
        for iGeo in range(0, temp_geom_count):
            temp_part = temp_geom.GetGeometryRef(iGeo) # 获取Multi中的每一个Part
            temp_part_ring_count = temp_part.GetGeometryCount() # 每个Polygon可能会有ExRing和InRing
            #print("polygon's ring count:", temp_part_ring_count)
            
            temp_new_part = ogr.Geometry(ogr.wkbPolygon)
            for iRing in range(0, temp_part_ring_count):
                temp_ring = temp_part.GetGeometryRef(iRing)

                temp_new_ring = ogr.Geometry(ogr.wkbLinearRing)
                
                # 第一种写法
                temp_ring_point_count = temp_ring.GetPointCount()
                for iP in range(0, temp_ring_point_count):
                    temp_point = temp_ring.GetPoint(iP)
                    new_p = trans.TransformPoint(temp_point[0], temp_point[1])
                    #print(new_p)
                    temp_new_ring.AddPoint(new_p[0], new_p[1])
                temp_new_part.AddGeometry(temp_new_ring)
            
            temp_new_polygon.AddGeometry(temp_new_part)
    else:
        print("geometry name:", temp_geom.GetGeometryName())
        temp_new_polygon = ogr.Geometry(ogr.wkbPolygon)

        temp_ring_count = temp_geom.GetGeometryCount() # Polygon有可能带岛
        #print("polygon's ring count:", temp_ring_count)
        for iRing in range(0, temp_ring_count):
            temp_ring = temp_geom.GetGeometryRef(iRing) # 遍历每一个Ring，默认第一个是外环
            
            # 第二种写法
            # new_points = trans.TransformPoints(temp_ring.GetPoints())
            # print(new_points)

            # 第三种写法
            import pyproj
            source_proj = pyproj.Proj(srs.ExportToProj4())
            target_proj = pyproj.Proj(4326)
            prjtrans = pyproj.Transformer.from_proj(source_proj, target_proj)
            # 注意以上四行应该写到循环外面
            temp_ring_point_count = temp_ring.GetPointCount()
            new_points = []
            for iP in range(0, temp_ring_point_count):
                temp_point = temp_ring.GetPoint(iP)
                new_p = prjtrans.transform(temp_point[0], temp_point[1])
                #print(new_p) #注意，转出来的经纬度是反的
                new_points.append((new_p[1], new_p[0]))

            temp_new_ring = ogr.Geometry(ogr.wkbLinearRing)
            for new_p in new_points:
                temp_new_ring.AddPoint(new_p[0], new_p[1])
            temp_new_polygon.AddGeometry(temp_new_ring)
    # end if-else geometry type

    if temp_new_polygon != None:
        tempNewFeature = ogr.Feature(layerjs_def)
        tempNewFeature.SetGeometry(temp_new_polygon)
        tempNewFeature.SetField("PAC",temp_feature.GetField("PAC"))
        tempNewFeature.SetField("NAME",temp_feature.GetField("NAME"))
        tempNewFeature.SetField("AREA",temp_feature.GetField("AREA"))

        layerjs_4326.CreateFeature(tempNewFeature)
        tempNewFeature.Destroy()

ds.FlushCache()
if ds != None: ds.Destroy()

shape_path = "E:\派森\期末\T3\county_popu.shp"
ds = ogr.Open(shape_path)
layer = ds.GetLayer(0)
srs = layer.GetSpatialRef()
layer_defn = layer.GetLayerDefn()
field_count = layer_defn.GetFieldCount()
filed_name_list = [] #暂存原始Shapefile的属性字段的名字
for iField in range(0, field_count):
    temp_field = layer_defn.GetFieldDefn(iField)
    temp_name = temp_field.GetName()
    filed_name_list.append(temp_name)
    print(temp_name)
#上海是310开头
layer.SetAttributeFilter('("PAC"/1)=310107')
feature_count = layer.GetFeatureCount()
# 注意此处不宜使用For循环直接遍历
# 如果要用，属性过滤器是不起作用的
# 还需要在循环内部进行If判断
# for i in range(0, feature_count): 
#     temp_feature = layer.GetFeature(i)
#     temp_field_pac = temp_feature.GetField('PAC')
#     if temp_field_pac/10000 != 32:
#         continue
layer.ResetReading()
feature_list = [] #暂存过滤后的Feature数据
temp_feature = layer.GetNextFeature()
while temp_feature:
    temp_geom = temp_feature.GetGeometryRef()
    temp_field_area = temp_feature.GetField('Shape_Area')
    temp_field_name = temp_feature.GetField('NAME')
    temp_calculatet_area = temp_geom.Area()
    print('Name:', temp_field_name,
          'Area:', temp_field_area, 
          'Cal_Area:', temp_calculatet_area)
    feature_list.append(temp_feature)
    temp_feature = layer.GetNextFeature()


'''
将过滤后的Feature保存到新的文件中
'''
gdal.SetConfigOption("SHAPE_ENCODING", "UTF-8") # IMPORTANT
new_shape_path = 'E:/派森/期末/T3/shanghai_普陀区.shp'

driverName = "ESRI Shapefile"
driver = ogr.GetDriverByName(driverName)
ds = driver.CreateDataSource(new_shape_path) #创建DataSource

geomType = ogr.wkbPolygon #指定几何类型
#创建图层，注意srs借用的是原来的
poLayer = ds.CreateLayer('shanghai_普陀区', srs, geomType)

#对原始数据的属性字段进行遍历
for iField in range(0, field_count):
    temp_field = layer_defn.GetFieldDefn(iField)
    poLayer.CreateField(temp_field, 1)
    
#创建完所有的属性字段之后，获取整个图层的定义
new_layerdef = poLayer.GetLayerDefn()

for iF in range(0, feature_count):
    temp_old_feature = feature_list[iF]
    temp_geom = temp_old_feature.GetGeometryRef()
    
    tempNewFeature = ogr.Feature(new_layerdef)
    tempNewFeature.SetGeometry(temp_geom)
    for temp_name in filed_name_list:
        tempNewFeature.SetField(temp_name,temp_old_feature.GetField(temp_name))

    poLayer.CreateFeature(tempNewFeature)
    del tempNewFeature

ds.FlushCache()
if ds != None: ds.Destroy()


'''
将过滤后的Feature保存到新的文件中, 并且做投影转换
'''
new_shape_path = "E:\派森\期末\T3\shanghai_wgs84_普陀区.shp"

driverName = "ESRI Shapefile"
driver = ogr.GetDriverByName(driverName)
ds = driver.CreateDataSource(new_shape_path)

geomType = ogr.wkbPolygon
srs_4326 = osr.SpatialReference(osr.SRS_WKT_WGS84_LAT_LONG) # 指定新的空间参考
srs_4326.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER) # 按照传统先X后Y的顺序进行坐标转换
#注意此处，指定了options=["ENCODING=UTF-8"], 会生成了以 *.cpg的文件, 里面给出了文字编码
layerjs_4326 = ds.CreateLayer('sh_普陀区', srs_4326, geomType, options=["ENCODING=UTF-8"])

#选用了某几个属性字段放到新的Shapefile中
field1 = ogr.FieldDefn("PAC", ogr.OFTInteger64)
layerjs_4326.CreateField(field1, 1)
field1.Destroy()

field2 = ogr.FieldDefn("NAME", ogr.OFTString)
layerjs_4326.CreateField(field2, 1)
field2.Destroy()

field3 = ogr.FieldDefn("AREA", ogr.OFTReal)
layerjs_4326.CreateField(field3, 1)
field3.Destroy()

#获取新数据的图层属性
layerjs_def = layerjs_4326.GetLayerDefn()

#根据原始坐标参考和新的坐标参考，构建一个投影转换器
trans = osr.CoordinateTransformation(srs, srs_4326)

for iF in range(0, feature_count):
    temp_feature = feature_list[iF]

    temp_geom = temp_feature.GetGeometryRef() # 拿到Feature的Geometry对象
    temp_geom_type = temp_geom.GetGeometryType() # 拿到Geometry的几何类型
    temp_geom_count = temp_geom.GetGeometryCount() # 有可能是Multi-Polygon
    
    temp_new_polygon = None
    if temp_geom_type == ogr.wkbMultiPolygon and temp_geom_count>1:
        print("geometry name:", temp_geom.GetGeometryName())
        #print(temp_geom.GetGeometryName())
        temp_new_polygon = ogr.Geometry(ogr.wkbMultiPolygon)
        for iGeo in range(0, temp_geom_count):
            temp_part = temp_geom.GetGeometryRef(iGeo) # 获取Multi中的每一个Part
            temp_part_ring_count = temp_part.GetGeometryCount() # 每个Polygon可能会有ExRing和InRing
            #print("polygon's ring count:", temp_part_ring_count)
            
            temp_new_part = ogr.Geometry(ogr.wkbPolygon)
            for iRing in range(0, temp_part_ring_count):
                temp_ring = temp_part.GetGeometryRef(iRing)

                temp_new_ring = ogr.Geometry(ogr.wkbLinearRing)
                
                # 第一种写法
                temp_ring_point_count = temp_ring.GetPointCount()
                for iP in range(0, temp_ring_point_count):
                    temp_point = temp_ring.GetPoint(iP)
                    new_p = trans.TransformPoint(temp_point[0], temp_point[1])
                    #print(new_p)
                    temp_new_ring.AddPoint(new_p[0], new_p[1])
                temp_new_part.AddGeometry(temp_new_ring)
            
            temp_new_polygon.AddGeometry(temp_new_part)
    else:
        print("geometry name:", temp_geom.GetGeometryName())
        temp_new_polygon = ogr.Geometry(ogr.wkbPolygon)

        temp_ring_count = temp_geom.GetGeometryCount() # Polygon有可能带岛
        #print("polygon's ring count:", temp_ring_count)
        for iRing in range(0, temp_ring_count):
            temp_ring = temp_geom.GetGeometryRef(iRing) # 遍历每一个Ring，默认第一个是外环
            
            # 第二种写法
            # new_points = trans.TransformPoints(temp_ring.GetPoints())
            # print(new_points)

            # 第三种写法
            import pyproj
            source_proj = pyproj.Proj(srs.ExportToProj4())
            target_proj = pyproj.Proj(4326)
            prjtrans = pyproj.Transformer.from_proj(source_proj, target_proj)
            # 注意以上四行应该写到循环外面
            temp_ring_point_count = temp_ring.GetPointCount()
            new_points = []
            for iP in range(0, temp_ring_point_count):
                temp_point = temp_ring.GetPoint(iP)
                new_p = prjtrans.transform(temp_point[0], temp_point[1])
                #print(new_p) #注意，转出来的经纬度是反的
                new_points.append((new_p[1], new_p[0]))

            temp_new_ring = ogr.Geometry(ogr.wkbLinearRing)
            for new_p in new_points:
                temp_new_ring.AddPoint(new_p[0], new_p[1])
            temp_new_polygon.AddGeometry(temp_new_ring)
    # end if-else geometry type

    if temp_new_polygon != None:
        tempNewFeature = ogr.Feature(layerjs_def)
        tempNewFeature.SetGeometry(temp_new_polygon)
        tempNewFeature.SetField("PAC",temp_feature.GetField("PAC"))
        tempNewFeature.SetField("NAME",temp_feature.GetField("NAME"))
        tempNewFeature.SetField("AREA",temp_feature.GetField("AREA"))

        layerjs_4326.CreateFeature(tempNewFeature)
        tempNewFeature.Destroy()

ds.FlushCache()
if ds != None: ds.Destroy()

shape_path = "E:\派森\期末\T3\county_popu.shp"
ds = ogr.Open(shape_path)
layer = ds.GetLayer(0)
srs = layer.GetSpatialRef()
layer_defn = layer.GetLayerDefn()
field_count = layer_defn.GetFieldCount()
filed_name_list = [] #暂存原始Shapefile的属性字段的名字
for iField in range(0, field_count):
    temp_field = layer_defn.GetFieldDefn(iField)
    temp_name = temp_field.GetName()
    filed_name_list.append(temp_name)
    print(temp_name)
#上海是310开头
layer.SetAttributeFilter('("PAC"/1)=310108')
feature_count = layer.GetFeatureCount()
# 注意此处不宜使用For循环直接遍历
# 如果要用，属性过滤器是不起作用的
# 还需要在循环内部进行If判断
# for i in range(0, feature_count): 
#     temp_feature = layer.GetFeature(i)
#     temp_field_pac = temp_feature.GetField('PAC')
#     if temp_field_pac/10000 != 32:
#         continue
layer.ResetReading()
feature_list = [] #暂存过滤后的Feature数据
temp_feature = layer.GetNextFeature()
while temp_feature:
    temp_geom = temp_feature.GetGeometryRef()
    temp_field_area = temp_feature.GetField('Shape_Area')
    temp_field_name = temp_feature.GetField('NAME')
    temp_calculatet_area = temp_geom.Area()
    print('Name:', temp_field_name,
          'Area:', temp_field_area, 
          'Cal_Area:', temp_calculatet_area)
    feature_list.append(temp_feature)
    temp_feature = layer.GetNextFeature()


'''
将过滤后的Feature保存到新的文件中
'''
gdal.SetConfigOption("SHAPE_ENCODING", "UTF-8") # IMPORTANT
new_shape_path = 'E:/派森/期末/T3/shanghai_闸北区.shp'

driverName = "ESRI Shapefile"
driver = ogr.GetDriverByName(driverName)
ds = driver.CreateDataSource(new_shape_path) #创建DataSource

geomType = ogr.wkbPolygon #指定几何类型
#创建图层，注意srs借用的是原来的
poLayer = ds.CreateLayer('shanghai_闸北区', srs, geomType)

#对原始数据的属性字段进行遍历
for iField in range(0, field_count):
    temp_field = layer_defn.GetFieldDefn(iField)
    poLayer.CreateField(temp_field, 1)
    
#创建完所有的属性字段之后，获取整个图层的定义
new_layerdef = poLayer.GetLayerDefn()

for iF in range(0, feature_count):
    temp_old_feature = feature_list[iF]
    temp_geom = temp_old_feature.GetGeometryRef()
    
    tempNewFeature = ogr.Feature(new_layerdef)
    tempNewFeature.SetGeometry(temp_geom)
    for temp_name in filed_name_list:
        tempNewFeature.SetField(temp_name,temp_old_feature.GetField(temp_name))

    poLayer.CreateFeature(tempNewFeature)
    del tempNewFeature

ds.FlushCache()
if ds != None: ds.Destroy()


'''
将过滤后的Feature保存到新的文件中, 并且做投影转换
'''
new_shape_path = "E:\派森\期末\T3\shanghai_wgs84_闸北区.shp"

driverName = "ESRI Shapefile"
driver = ogr.GetDriverByName(driverName)
ds = driver.CreateDataSource(new_shape_path)

geomType = ogr.wkbPolygon
srs_4326 = osr.SpatialReference(osr.SRS_WKT_WGS84_LAT_LONG) # 指定新的空间参考
srs_4326.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER) # 按照传统先X后Y的顺序进行坐标转换
#注意此处，指定了options=["ENCODING=UTF-8"], 会生成了以 *.cpg的文件, 里面给出了文字编码
layerjs_4326 = ds.CreateLayer('sh_闸北区', srs_4326, geomType, options=["ENCODING=UTF-8"])

#选用了某几个属性字段放到新的Shapefile中
field1 = ogr.FieldDefn("PAC", ogr.OFTInteger64)
layerjs_4326.CreateField(field1, 1)
field1.Destroy()

field2 = ogr.FieldDefn("NAME", ogr.OFTString)
layerjs_4326.CreateField(field2, 1)
field2.Destroy()

field3 = ogr.FieldDefn("AREA", ogr.OFTReal)
layerjs_4326.CreateField(field3, 1)
field3.Destroy()

#获取新数据的图层属性
layerjs_def = layerjs_4326.GetLayerDefn()

#根据原始坐标参考和新的坐标参考，构建一个投影转换器
trans = osr.CoordinateTransformation(srs, srs_4326)

for iF in range(0, feature_count):
    temp_feature = feature_list[iF]

    temp_geom = temp_feature.GetGeometryRef() # 拿到Feature的Geometry对象
    temp_geom_type = temp_geom.GetGeometryType() # 拿到Geometry的几何类型
    temp_geom_count = temp_geom.GetGeometryCount() # 有可能是Multi-Polygon
    
    temp_new_polygon = None
    if temp_geom_type == ogr.wkbMultiPolygon and temp_geom_count>1:
        print("geometry name:", temp_geom.GetGeometryName())
        #print(temp_geom.GetGeometryName())
        temp_new_polygon = ogr.Geometry(ogr.wkbMultiPolygon)
        for iGeo in range(0, temp_geom_count):
            temp_part = temp_geom.GetGeometryRef(iGeo) # 获取Multi中的每一个Part
            temp_part_ring_count = temp_part.GetGeometryCount() # 每个Polygon可能会有ExRing和InRing
            #print("polygon's ring count:", temp_part_ring_count)
            
            temp_new_part = ogr.Geometry(ogr.wkbPolygon)
            for iRing in range(0, temp_part_ring_count):
                temp_ring = temp_part.GetGeometryRef(iRing)

                temp_new_ring = ogr.Geometry(ogr.wkbLinearRing)
                
                # 第一种写法
                temp_ring_point_count = temp_ring.GetPointCount()
                for iP in range(0, temp_ring_point_count):
                    temp_point = temp_ring.GetPoint(iP)
                    new_p = trans.TransformPoint(temp_point[0], temp_point[1])
                    #print(new_p)
                    temp_new_ring.AddPoint(new_p[0], new_p[1])
                temp_new_part.AddGeometry(temp_new_ring)
            
            temp_new_polygon.AddGeometry(temp_new_part)
    else:
        print("geometry name:", temp_geom.GetGeometryName())
        temp_new_polygon = ogr.Geometry(ogr.wkbPolygon)

        temp_ring_count = temp_geom.GetGeometryCount() # Polygon有可能带岛
        #print("polygon's ring count:", temp_ring_count)
        for iRing in range(0, temp_ring_count):
            temp_ring = temp_geom.GetGeometryRef(iRing) # 遍历每一个Ring，默认第一个是外环
            
            # 第二种写法
            # new_points = trans.TransformPoints(temp_ring.GetPoints())
            # print(new_points)

            # 第三种写法
            import pyproj
            source_proj = pyproj.Proj(srs.ExportToProj4())
            target_proj = pyproj.Proj(4326)
            prjtrans = pyproj.Transformer.from_proj(source_proj, target_proj)
            # 注意以上四行应该写到循环外面
            temp_ring_point_count = temp_ring.GetPointCount()
            new_points = []
            for iP in range(0, temp_ring_point_count):
                temp_point = temp_ring.GetPoint(iP)
                new_p = prjtrans.transform(temp_point[0], temp_point[1])
                #print(new_p) #注意，转出来的经纬度是反的
                new_points.append((new_p[1], new_p[0]))

            temp_new_ring = ogr.Geometry(ogr.wkbLinearRing)
            for new_p in new_points:
                temp_new_ring.AddPoint(new_p[0], new_p[1])
            temp_new_polygon.AddGeometry(temp_new_ring)
    # end if-else geometry type

    if temp_new_polygon != None:
        tempNewFeature = ogr.Feature(layerjs_def)
        tempNewFeature.SetGeometry(temp_new_polygon)
        tempNewFeature.SetField("PAC",temp_feature.GetField("PAC"))
        tempNewFeature.SetField("NAME",temp_feature.GetField("NAME"))
        tempNewFeature.SetField("AREA",temp_feature.GetField("AREA"))

        layerjs_4326.CreateFeature(tempNewFeature)
        tempNewFeature.Destroy()

ds.FlushCache()
if ds != None: ds.Destroy()

shape_path = "E:\派森\期末\T3\county_popu.shp"
ds = ogr.Open(shape_path)
layer = ds.GetLayer(0)
srs = layer.GetSpatialRef()
layer_defn = layer.GetLayerDefn()
field_count = layer_defn.GetFieldCount()
filed_name_list = [] #暂存原始Shapefile的属性字段的名字
for iField in range(0, field_count):
    temp_field = layer_defn.GetFieldDefn(iField)
    temp_name = temp_field.GetName()
    filed_name_list.append(temp_name)
    print(temp_name)
#上海是310开头
layer.SetAttributeFilter('("PAC"/1)=310109')
feature_count = layer.GetFeatureCount()
# 注意此处不宜使用For循环直接遍历
# 如果要用，属性过滤器是不起作用的
# 还需要在循环内部进行If判断
# for i in range(0, feature_count): 
#     temp_feature = layer.GetFeature(i)
#     temp_field_pac = temp_feature.GetField('PAC')
#     if temp_field_pac/10000 != 32:
#         continue
layer.ResetReading()
feature_list = [] #暂存过滤后的Feature数据
temp_feature = layer.GetNextFeature()
while temp_feature:
    temp_geom = temp_feature.GetGeometryRef()
    temp_field_area = temp_feature.GetField('Shape_Area')
    temp_field_name = temp_feature.GetField('NAME')
    temp_calculatet_area = temp_geom.Area()
    print('Name:', temp_field_name,
          'Area:', temp_field_area, 
          'Cal_Area:', temp_calculatet_area)
    feature_list.append(temp_feature)
    temp_feature = layer.GetNextFeature()


'''
将过滤后的Feature保存到新的文件中
'''
gdal.SetConfigOption("SHAPE_ENCODING", "UTF-8") # IMPORTANT
new_shape_path = 'E:/派森/期末/T3/shanghai_虹口区.shp'

driverName = "ESRI Shapefile"
driver = ogr.GetDriverByName(driverName)
ds = driver.CreateDataSource(new_shape_path) #创建DataSource

geomType = ogr.wkbPolygon #指定几何类型
#创建图层，注意srs借用的是原来的
poLayer = ds.CreateLayer('shanghai_虹口区', srs, geomType)

#对原始数据的属性字段进行遍历
for iField in range(0, field_count):
    temp_field = layer_defn.GetFieldDefn(iField)
    poLayer.CreateField(temp_field, 1)
    
#创建完所有的属性字段之后，获取整个图层的定义
new_layerdef = poLayer.GetLayerDefn()

for iF in range(0, feature_count):
    temp_old_feature = feature_list[iF]
    temp_geom = temp_old_feature.GetGeometryRef()
    
    tempNewFeature = ogr.Feature(new_layerdef)
    tempNewFeature.SetGeometry(temp_geom)
    for temp_name in filed_name_list:
        tempNewFeature.SetField(temp_name,temp_old_feature.GetField(temp_name))

    poLayer.CreateFeature(tempNewFeature)
    del tempNewFeature

ds.FlushCache()
if ds != None: ds.Destroy()


'''
将过滤后的Feature保存到新的文件中, 并且做投影转换
'''
new_shape_path = "E:\派森\期末\T3\shanghai_wgs84_虹口区.shp"

driverName = "ESRI Shapefile"
driver = ogr.GetDriverByName(driverName)
ds = driver.CreateDataSource(new_shape_path)

geomType = ogr.wkbPolygon
srs_4326 = osr.SpatialReference(osr.SRS_WKT_WGS84_LAT_LONG) # 指定新的空间参考
srs_4326.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER) # 按照传统先X后Y的顺序进行坐标转换
#注意此处，指定了options=["ENCODING=UTF-8"], 会生成了以 *.cpg的文件, 里面给出了文字编码
layerjs_4326 = ds.CreateLayer('sh_虹口区', srs_4326, geomType, options=["ENCODING=UTF-8"])

#选用了某几个属性字段放到新的Shapefile中
field1 = ogr.FieldDefn("PAC", ogr.OFTInteger64)
layerjs_4326.CreateField(field1, 1)
field1.Destroy()

field2 = ogr.FieldDefn("NAME", ogr.OFTString)
layerjs_4326.CreateField(field2, 1)
field2.Destroy()

field3 = ogr.FieldDefn("AREA", ogr.OFTReal)
layerjs_4326.CreateField(field3, 1)
field3.Destroy()

#获取新数据的图层属性
layerjs_def = layerjs_4326.GetLayerDefn()

#根据原始坐标参考和新的坐标参考，构建一个投影转换器
trans = osr.CoordinateTransformation(srs, srs_4326)

for iF in range(0, feature_count):
    temp_feature = feature_list[iF]

    temp_geom = temp_feature.GetGeometryRef() # 拿到Feature的Geometry对象
    temp_geom_type = temp_geom.GetGeometryType() # 拿到Geometry的几何类型
    temp_geom_count = temp_geom.GetGeometryCount() # 有可能是Multi-Polygon
    
    temp_new_polygon = None
    if temp_geom_type == ogr.wkbMultiPolygon and temp_geom_count>1:
        print("geometry name:", temp_geom.GetGeometryName())
        #print(temp_geom.GetGeometryName())
        temp_new_polygon = ogr.Geometry(ogr.wkbMultiPolygon)
        for iGeo in range(0, temp_geom_count):
            temp_part = temp_geom.GetGeometryRef(iGeo) # 获取Multi中的每一个Part
            temp_part_ring_count = temp_part.GetGeometryCount() # 每个Polygon可能会有ExRing和InRing
            #print("polygon's ring count:", temp_part_ring_count)
            
            temp_new_part = ogr.Geometry(ogr.wkbPolygon)
            for iRing in range(0, temp_part_ring_count):
                temp_ring = temp_part.GetGeometryRef(iRing)

                temp_new_ring = ogr.Geometry(ogr.wkbLinearRing)
                
                # 第一种写法
                temp_ring_point_count = temp_ring.GetPointCount()
                for iP in range(0, temp_ring_point_count):
                    temp_point = temp_ring.GetPoint(iP)
                    new_p = trans.TransformPoint(temp_point[0], temp_point[1])
                    #print(new_p)
                    temp_new_ring.AddPoint(new_p[0], new_p[1])
                temp_new_part.AddGeometry(temp_new_ring)
            
            temp_new_polygon.AddGeometry(temp_new_part)
    else:
        print("geometry name:", temp_geom.GetGeometryName())
        temp_new_polygon = ogr.Geometry(ogr.wkbPolygon)

        temp_ring_count = temp_geom.GetGeometryCount() # Polygon有可能带岛
        #print("polygon's ring count:", temp_ring_count)
        for iRing in range(0, temp_ring_count):
            temp_ring = temp_geom.GetGeometryRef(iRing) # 遍历每一个Ring，默认第一个是外环
            
            # 第二种写法
            # new_points = trans.TransformPoints(temp_ring.GetPoints())
            # print(new_points)

            # 第三种写法
            import pyproj
            source_proj = pyproj.Proj(srs.ExportToProj4())
            target_proj = pyproj.Proj(4326)
            prjtrans = pyproj.Transformer.from_proj(source_proj, target_proj)
            # 注意以上四行应该写到循环外面
            temp_ring_point_count = temp_ring.GetPointCount()
            new_points = []
            for iP in range(0, temp_ring_point_count):
                temp_point = temp_ring.GetPoint(iP)
                new_p = prjtrans.transform(temp_point[0], temp_point[1])
                #print(new_p) #注意，转出来的经纬度是反的
                new_points.append((new_p[1], new_p[0]))

            temp_new_ring = ogr.Geometry(ogr.wkbLinearRing)
            for new_p in new_points:
                temp_new_ring.AddPoint(new_p[0], new_p[1])
            temp_new_polygon.AddGeometry(temp_new_ring)
    # end if-else geometry type

    if temp_new_polygon != None:
        tempNewFeature = ogr.Feature(layerjs_def)
        tempNewFeature.SetGeometry(temp_new_polygon)
        tempNewFeature.SetField("PAC",temp_feature.GetField("PAC"))
        tempNewFeature.SetField("NAME",temp_feature.GetField("NAME"))
        tempNewFeature.SetField("AREA",temp_feature.GetField("AREA"))

        layerjs_4326.CreateFeature(tempNewFeature)
        tempNewFeature.Destroy()

ds.FlushCache()
if ds != None: ds.Destroy()

shape_path = "E:\派森\期末\T3\county_popu.shp"
ds = ogr.Open(shape_path)
layer = ds.GetLayer(0)
srs = layer.GetSpatialRef()
layer_defn = layer.GetLayerDefn()
field_count = layer_defn.GetFieldCount()
filed_name_list = [] #暂存原始Shapefile的属性字段的名字
for iField in range(0, field_count):
    temp_field = layer_defn.GetFieldDefn(iField)
    temp_name = temp_field.GetName()
    filed_name_list.append(temp_name)
    print(temp_name)
#上海是310开头
layer.SetAttributeFilter('("PAC"/1)=310110')
feature_count = layer.GetFeatureCount()
# 注意此处不宜使用For循环直接遍历
# 如果要用，属性过滤器是不起作用的
# 还需要在循环内部进行If判断
# for i in range(0, feature_count): 
#     temp_feature = layer.GetFeature(i)
#     temp_field_pac = temp_feature.GetField('PAC')
#     if temp_field_pac/10000 != 32:
#         continue
layer.ResetReading()
feature_list = [] #暂存过滤后的Feature数据
temp_feature = layer.GetNextFeature()
while temp_feature:
    temp_geom = temp_feature.GetGeometryRef()
    temp_field_area = temp_feature.GetField('Shape_Area')
    temp_field_name = temp_feature.GetField('NAME')
    temp_calculatet_area = temp_geom.Area()
    print('Name:', temp_field_name,
          'Area:', temp_field_area, 
          'Cal_Area:', temp_calculatet_area)
    feature_list.append(temp_feature)
    temp_feature = layer.GetNextFeature()


'''
将过滤后的Feature保存到新的文件中
'''
gdal.SetConfigOption("SHAPE_ENCODING", "UTF-8") # IMPORTANT
new_shape_path = 'E:/派森/期末/T3/shanghai_杨浦区.shp'

driverName = "ESRI Shapefile"
driver = ogr.GetDriverByName(driverName)
ds = driver.CreateDataSource(new_shape_path) #创建DataSource

geomType = ogr.wkbPolygon #指定几何类型
#创建图层，注意srs借用的是原来的
poLayer = ds.CreateLayer('shanghai_杨浦区', srs, geomType)

#对原始数据的属性字段进行遍历
for iField in range(0, field_count):
    temp_field = layer_defn.GetFieldDefn(iField)
    poLayer.CreateField(temp_field, 1)
    
#创建完所有的属性字段之后，获取整个图层的定义
new_layerdef = poLayer.GetLayerDefn()

for iF in range(0, feature_count):
    temp_old_feature = feature_list[iF]
    temp_geom = temp_old_feature.GetGeometryRef()
    
    tempNewFeature = ogr.Feature(new_layerdef)
    tempNewFeature.SetGeometry(temp_geom)
    for temp_name in filed_name_list:
        tempNewFeature.SetField(temp_name,temp_old_feature.GetField(temp_name))

    poLayer.CreateFeature(tempNewFeature)
    del tempNewFeature

ds.FlushCache()
if ds != None: ds.Destroy()


'''
将过滤后的Feature保存到新的文件中, 并且做投影转换
'''
new_shape_path = "E:\派森\期末\T3\shanghai_wgs84_杨浦区.shp"

driverName = "ESRI Shapefile"
driver = ogr.GetDriverByName(driverName)
ds = driver.CreateDataSource(new_shape_path)

geomType = ogr.wkbPolygon
srs_4326 = osr.SpatialReference(osr.SRS_WKT_WGS84_LAT_LONG) # 指定新的空间参考
srs_4326.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER) # 按照传统先X后Y的顺序进行坐标转换
#注意此处，指定了options=["ENCODING=UTF-8"], 会生成了以 *.cpg的文件, 里面给出了文字编码
layerjs_4326 = ds.CreateLayer('sh_杨浦区', srs_4326, geomType, options=["ENCODING=UTF-8"])

#选用了某几个属性字段放到新的Shapefile中
field1 = ogr.FieldDefn("PAC", ogr.OFTInteger64)
layerjs_4326.CreateField(field1, 1)
field1.Destroy()

field2 = ogr.FieldDefn("NAME", ogr.OFTString)
layerjs_4326.CreateField(field2, 1)
field2.Destroy()

field3 = ogr.FieldDefn("AREA", ogr.OFTReal)
layerjs_4326.CreateField(field3, 1)
field3.Destroy()

#获取新数据的图层属性
layerjs_def = layerjs_4326.GetLayerDefn()

#根据原始坐标参考和新的坐标参考，构建一个投影转换器
trans = osr.CoordinateTransformation(srs, srs_4326)

for iF in range(0, feature_count):
    temp_feature = feature_list[iF]

    temp_geom = temp_feature.GetGeometryRef() # 拿到Feature的Geometry对象
    temp_geom_type = temp_geom.GetGeometryType() # 拿到Geometry的几何类型
    temp_geom_count = temp_geom.GetGeometryCount() # 有可能是Multi-Polygon
    
    temp_new_polygon = None
    if temp_geom_type == ogr.wkbMultiPolygon and temp_geom_count>1:
        print("geometry name:", temp_geom.GetGeometryName())
        #print(temp_geom.GetGeometryName())
        temp_new_polygon = ogr.Geometry(ogr.wkbMultiPolygon)
        for iGeo in range(0, temp_geom_count):
            temp_part = temp_geom.GetGeometryRef(iGeo) # 获取Multi中的每一个Part
            temp_part_ring_count = temp_part.GetGeometryCount() # 每个Polygon可能会有ExRing和InRing
            #print("polygon's ring count:", temp_part_ring_count)
            
            temp_new_part = ogr.Geometry(ogr.wkbPolygon)
            for iRing in range(0, temp_part_ring_count):
                temp_ring = temp_part.GetGeometryRef(iRing)

                temp_new_ring = ogr.Geometry(ogr.wkbLinearRing)
                
                # 第一种写法
                temp_ring_point_count = temp_ring.GetPointCount()
                for iP in range(0, temp_ring_point_count):
                    temp_point = temp_ring.GetPoint(iP)
                    new_p = trans.TransformPoint(temp_point[0], temp_point[1])
                    #print(new_p)
                    temp_new_ring.AddPoint(new_p[0], new_p[1])
                temp_new_part.AddGeometry(temp_new_ring)
            
            temp_new_polygon.AddGeometry(temp_new_part)
    else:
        print("geometry name:", temp_geom.GetGeometryName())
        temp_new_polygon = ogr.Geometry(ogr.wkbPolygon)

        temp_ring_count = temp_geom.GetGeometryCount() # Polygon有可能带岛
        #print("polygon's ring count:", temp_ring_count)
        for iRing in range(0, temp_ring_count):
            temp_ring = temp_geom.GetGeometryRef(iRing) # 遍历每一个Ring，默认第一个是外环
            
            # 第二种写法
            # new_points = trans.TransformPoints(temp_ring.GetPoints())
            # print(new_points)

            # 第三种写法
            import pyproj
            source_proj = pyproj.Proj(srs.ExportToProj4())
            target_proj = pyproj.Proj(4326)
            prjtrans = pyproj.Transformer.from_proj(source_proj, target_proj)
            # 注意以上四行应该写到循环外面
            temp_ring_point_count = temp_ring.GetPointCount()
            new_points = []
            for iP in range(0, temp_ring_point_count):
                temp_point = temp_ring.GetPoint(iP)
                new_p = prjtrans.transform(temp_point[0], temp_point[1])
                #print(new_p) #注意，转出来的经纬度是反的
                new_points.append((new_p[1], new_p[0]))

            temp_new_ring = ogr.Geometry(ogr.wkbLinearRing)
            for new_p in new_points:
                temp_new_ring.AddPoint(new_p[0], new_p[1])
            temp_new_polygon.AddGeometry(temp_new_ring)
    # end if-else geometry type

    if temp_new_polygon != None:
        tempNewFeature = ogr.Feature(layerjs_def)
        tempNewFeature.SetGeometry(temp_new_polygon)
        tempNewFeature.SetField("PAC",temp_feature.GetField("PAC"))
        tempNewFeature.SetField("NAME",temp_feature.GetField("NAME"))
        tempNewFeature.SetField("AREA",temp_feature.GetField("AREA"))

        layerjs_4326.CreateFeature(tempNewFeature)
        tempNewFeature.Destroy()

ds.FlushCache()
if ds != None: ds.Destroy()

shape_path = "E:\派森\期末\T3\county_popu.shp"
ds = ogr.Open(shape_path)
layer = ds.GetLayer(0)
srs = layer.GetSpatialRef()
layer_defn = layer.GetLayerDefn()
field_count = layer_defn.GetFieldCount()
filed_name_list = [] #暂存原始Shapefile的属性字段的名字
for iField in range(0, field_count):
    temp_field = layer_defn.GetFieldDefn(iField)
    temp_name = temp_field.GetName()
    filed_name_list.append(temp_name)
    print(temp_name)
#上海是310开头
layer.SetAttributeFilter('("PAC"/1)=310112')
feature_count = layer.GetFeatureCount()
# 注意此处不宜使用For循环直接遍历
# 如果要用，属性过滤器是不起作用的
# 还需要在循环内部进行If判断
# for i in range(0, feature_count): 
#     temp_feature = layer.GetFeature(i)
#     temp_field_pac = temp_feature.GetField('PAC')
#     if temp_field_pac/10000 != 32:
#         continue
layer.ResetReading()
feature_list = [] #暂存过滤后的Feature数据
temp_feature = layer.GetNextFeature()
while temp_feature:
    temp_geom = temp_feature.GetGeometryRef()
    temp_field_area = temp_feature.GetField('Shape_Area')
    temp_field_name = temp_feature.GetField('NAME')
    temp_calculatet_area = temp_geom.Area()
    print('Name:', temp_field_name,
          'Area:', temp_field_area, 
          'Cal_Area:', temp_calculatet_area)
    feature_list.append(temp_feature)
    temp_feature = layer.GetNextFeature()


'''
将过滤后的Feature保存到新的文件中
'''
gdal.SetConfigOption("SHAPE_ENCODING", "UTF-8") # IMPORTANT
new_shape_path = 'E:/派森/期末/T3/shanghai_闵行区.shp'

driverName = "ESRI Shapefile"
driver = ogr.GetDriverByName(driverName)
ds = driver.CreateDataSource(new_shape_path) #创建DataSource

geomType = ogr.wkbPolygon #指定几何类型
#创建图层，注意srs借用的是原来的
poLayer = ds.CreateLayer('shanghai_闵行区', srs, geomType)

#对原始数据的属性字段进行遍历
for iField in range(0, field_count):
    temp_field = layer_defn.GetFieldDefn(iField)
    poLayer.CreateField(temp_field, 1)
    
#创建完所有的属性字段之后，获取整个图层的定义
new_layerdef = poLayer.GetLayerDefn()

for iF in range(0, feature_count):
    temp_old_feature = feature_list[iF]
    temp_geom = temp_old_feature.GetGeometryRef()
    
    tempNewFeature = ogr.Feature(new_layerdef)
    tempNewFeature.SetGeometry(temp_geom)
    for temp_name in filed_name_list:
        tempNewFeature.SetField(temp_name,temp_old_feature.GetField(temp_name))

    poLayer.CreateFeature(tempNewFeature)
    del tempNewFeature

ds.FlushCache()
if ds != None: ds.Destroy()


'''
将过滤后的Feature保存到新的文件中, 并且做投影转换
'''
new_shape_path = "E:\派森\期末\T3\shanghai_wgs84_闵行区.shp"

driverName = "ESRI Shapefile"
driver = ogr.GetDriverByName(driverName)
ds = driver.CreateDataSource(new_shape_path)

geomType = ogr.wkbPolygon
srs_4326 = osr.SpatialReference(osr.SRS_WKT_WGS84_LAT_LONG) # 指定新的空间参考
srs_4326.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER) # 按照传统先X后Y的顺序进行坐标转换
#注意此处，指定了options=["ENCODING=UTF-8"], 会生成了以 *.cpg的文件, 里面给出了文字编码
layerjs_4326 = ds.CreateLayer('sh_闵行区', srs_4326, geomType, options=["ENCODING=UTF-8"])

#选用了某几个属性字段放到新的Shapefile中
field1 = ogr.FieldDefn("PAC", ogr.OFTInteger64)
layerjs_4326.CreateField(field1, 1)
field1.Destroy()

field2 = ogr.FieldDefn("NAME", ogr.OFTString)
layerjs_4326.CreateField(field2, 1)
field2.Destroy()

field3 = ogr.FieldDefn("AREA", ogr.OFTReal)
layerjs_4326.CreateField(field3, 1)
field3.Destroy()

#获取新数据的图层属性
layerjs_def = layerjs_4326.GetLayerDefn()

#根据原始坐标参考和新的坐标参考，构建一个投影转换器
trans = osr.CoordinateTransformation(srs, srs_4326)

for iF in range(0, feature_count):
    temp_feature = feature_list[iF]

    temp_geom = temp_feature.GetGeometryRef() # 拿到Feature的Geometry对象
    temp_geom_type = temp_geom.GetGeometryType() # 拿到Geometry的几何类型
    temp_geom_count = temp_geom.GetGeometryCount() # 有可能是Multi-Polygon
    
    temp_new_polygon = None
    if temp_geom_type == ogr.wkbMultiPolygon and temp_geom_count>1:
        print("geometry name:", temp_geom.GetGeometryName())
        #print(temp_geom.GetGeometryName())
        temp_new_polygon = ogr.Geometry(ogr.wkbMultiPolygon)
        for iGeo in range(0, temp_geom_count):
            temp_part = temp_geom.GetGeometryRef(iGeo) # 获取Multi中的每一个Part
            temp_part_ring_count = temp_part.GetGeometryCount() # 每个Polygon可能会有ExRing和InRing
            #print("polygon's ring count:", temp_part_ring_count)
            
            temp_new_part = ogr.Geometry(ogr.wkbPolygon)
            for iRing in range(0, temp_part_ring_count):
                temp_ring = temp_part.GetGeometryRef(iRing)

                temp_new_ring = ogr.Geometry(ogr.wkbLinearRing)
                
                # 第一种写法
                temp_ring_point_count = temp_ring.GetPointCount()
                for iP in range(0, temp_ring_point_count):
                    temp_point = temp_ring.GetPoint(iP)
                    new_p = trans.TransformPoint(temp_point[0], temp_point[1])
                    #print(new_p)
                    temp_new_ring.AddPoint(new_p[0], new_p[1])
                temp_new_part.AddGeometry(temp_new_ring)
            
            temp_new_polygon.AddGeometry(temp_new_part)
    else:
        print("geometry name:", temp_geom.GetGeometryName())
        temp_new_polygon = ogr.Geometry(ogr.wkbPolygon)

        temp_ring_count = temp_geom.GetGeometryCount() # Polygon有可能带岛
        #print("polygon's ring count:", temp_ring_count)
        for iRing in range(0, temp_ring_count):
            temp_ring = temp_geom.GetGeometryRef(iRing) # 遍历每一个Ring，默认第一个是外环
            
            # 第二种写法
            # new_points = trans.TransformPoints(temp_ring.GetPoints())
            # print(new_points)

            # 第三种写法
            import pyproj
            source_proj = pyproj.Proj(srs.ExportToProj4())
            target_proj = pyproj.Proj(4326)
            prjtrans = pyproj.Transformer.from_proj(source_proj, target_proj)
            # 注意以上四行应该写到循环外面
            temp_ring_point_count = temp_ring.GetPointCount()
            new_points = []
            for iP in range(0, temp_ring_point_count):
                temp_point = temp_ring.GetPoint(iP)
                new_p = prjtrans.transform(temp_point[0], temp_point[1])
                #print(new_p) #注意，转出来的经纬度是反的
                new_points.append((new_p[1], new_p[0]))

            temp_new_ring = ogr.Geometry(ogr.wkbLinearRing)
            for new_p in new_points:
                temp_new_ring.AddPoint(new_p[0], new_p[1])
            temp_new_polygon.AddGeometry(temp_new_ring)
    # end if-else geometry type

    if temp_new_polygon != None:
        tempNewFeature = ogr.Feature(layerjs_def)
        tempNewFeature.SetGeometry(temp_new_polygon)
        tempNewFeature.SetField("PAC",temp_feature.GetField("PAC"))
        tempNewFeature.SetField("NAME",temp_feature.GetField("NAME"))
        tempNewFeature.SetField("AREA",temp_feature.GetField("AREA"))

        layerjs_4326.CreateFeature(tempNewFeature)
        tempNewFeature.Destroy()

ds.FlushCache()
if ds != None: ds.Destroy()


shape_path = "E:\派森\期末\T3\county_popu.shp"
ds = ogr.Open(shape_path)
layer = ds.GetLayer(0)
srs = layer.GetSpatialRef()
layer_defn = layer.GetLayerDefn()
field_count = layer_defn.GetFieldCount()
filed_name_list = [] #暂存原始Shapefile的属性字段的名字
for iField in range(0, field_count):
    temp_field = layer_defn.GetFieldDefn(iField)
    temp_name = temp_field.GetName()
    filed_name_list.append(temp_name)
    print(temp_name)
#上海是310开头
layer.SetAttributeFilter('("PAC"/1)=310113')
feature_count = layer.GetFeatureCount()
# 注意此处不宜使用For循环直接遍历
# 如果要用，属性过滤器是不起作用的
# 还需要在循环内部进行If判断
# for i in range(0, feature_count): 
#     temp_feature = layer.GetFeature(i)
#     temp_field_pac = temp_feature.GetField('PAC')
#     if temp_field_pac/10000 != 32:
#         continue
layer.ResetReading()
feature_list = [] #暂存过滤后的Feature数据
temp_feature = layer.GetNextFeature()
while temp_feature:
    temp_geom = temp_feature.GetGeometryRef()
    temp_field_area = temp_feature.GetField('Shape_Area')
    temp_field_name = temp_feature.GetField('NAME')
    temp_calculatet_area = temp_geom.Area()
    print('Name:', temp_field_name,
          'Area:', temp_field_area, 
          'Cal_Area:', temp_calculatet_area)
    feature_list.append(temp_feature)
    temp_feature = layer.GetNextFeature()


'''
将过滤后的Feature保存到新的文件中
'''
gdal.SetConfigOption("SHAPE_ENCODING", "UTF-8") # IMPORTANT
new_shape_path = 'E:/派森/期末/T3/shanghai_宝山区.shp'

driverName = "ESRI Shapefile"
driver = ogr.GetDriverByName(driverName)
ds = driver.CreateDataSource(new_shape_path) #创建DataSource

geomType = ogr.wkbPolygon #指定几何类型
#创建图层，注意srs借用的是原来的
poLayer = ds.CreateLayer('shanghai_宝山区', srs, geomType)

#对原始数据的属性字段进行遍历
for iField in range(0, field_count):
    temp_field = layer_defn.GetFieldDefn(iField)
    poLayer.CreateField(temp_field, 1)
    
#创建完所有的属性字段之后，获取整个图层的定义
new_layerdef = poLayer.GetLayerDefn()

for iF in range(0, feature_count):
    temp_old_feature = feature_list[iF]
    temp_geom = temp_old_feature.GetGeometryRef()
    
    tempNewFeature = ogr.Feature(new_layerdef)
    tempNewFeature.SetGeometry(temp_geom)
    for temp_name in filed_name_list:
        tempNewFeature.SetField(temp_name,temp_old_feature.GetField(temp_name))

    poLayer.CreateFeature(tempNewFeature)
    del tempNewFeature

ds.FlushCache()
if ds != None: ds.Destroy()


'''
将过滤后的Feature保存到新的文件中, 并且做投影转换
'''
new_shape_path = "E:\派森\期末\T3\shanghai_wgs84_宝山区.shp"

driverName = "ESRI Shapefile"
driver = ogr.GetDriverByName(driverName)
ds = driver.CreateDataSource(new_shape_path)

geomType = ogr.wkbPolygon
srs_4326 = osr.SpatialReference(osr.SRS_WKT_WGS84_LAT_LONG) # 指定新的空间参考
srs_4326.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER) # 按照传统先X后Y的顺序进行坐标转换
#注意此处，指定了options=["ENCODING=UTF-8"], 会生成了以 *.cpg的文件, 里面给出了文字编码
layerjs_4326 = ds.CreateLayer('sh_宝山区', srs_4326, geomType, options=["ENCODING=UTF-8"])

#选用了某几个属性字段放到新的Shapefile中
field1 = ogr.FieldDefn("PAC", ogr.OFTInteger64)
layerjs_4326.CreateField(field1, 1)
field1.Destroy()

field2 = ogr.FieldDefn("NAME", ogr.OFTString)
layerjs_4326.CreateField(field2, 1)
field2.Destroy()

field3 = ogr.FieldDefn("AREA", ogr.OFTReal)
layerjs_4326.CreateField(field3, 1)
field3.Destroy()

#获取新数据的图层属性
layerjs_def = layerjs_4326.GetLayerDefn()

#根据原始坐标参考和新的坐标参考，构建一个投影转换器
trans = osr.CoordinateTransformation(srs, srs_4326)

for iF in range(0, feature_count):
    temp_feature = feature_list[iF]

    temp_geom = temp_feature.GetGeometryRef() # 拿到Feature的Geometry对象
    temp_geom_type = temp_geom.GetGeometryType() # 拿到Geometry的几何类型
    temp_geom_count = temp_geom.GetGeometryCount() # 有可能是Multi-Polygon
    
    temp_new_polygon = None
    if temp_geom_type == ogr.wkbMultiPolygon and temp_geom_count>1:
        print("geometry name:", temp_geom.GetGeometryName())
        #print(temp_geom.GetGeometryName())
        temp_new_polygon = ogr.Geometry(ogr.wkbMultiPolygon)
        for iGeo in range(0, temp_geom_count):
            temp_part = temp_geom.GetGeometryRef(iGeo) # 获取Multi中的每一个Part
            temp_part_ring_count = temp_part.GetGeometryCount() # 每个Polygon可能会有ExRing和InRing
            #print("polygon's ring count:", temp_part_ring_count)
            
            temp_new_part = ogr.Geometry(ogr.wkbPolygon)
            for iRing in range(0, temp_part_ring_count):
                temp_ring = temp_part.GetGeometryRef(iRing)

                temp_new_ring = ogr.Geometry(ogr.wkbLinearRing)
                
                # 第一种写法
                temp_ring_point_count = temp_ring.GetPointCount()
                for iP in range(0, temp_ring_point_count):
                    temp_point = temp_ring.GetPoint(iP)
                    new_p = trans.TransformPoint(temp_point[0], temp_point[1])
                    #print(new_p)
                    temp_new_ring.AddPoint(new_p[0], new_p[1])
                temp_new_part.AddGeometry(temp_new_ring)
            
            temp_new_polygon.AddGeometry(temp_new_part)
    else:
        print("geometry name:", temp_geom.GetGeometryName())
        temp_new_polygon = ogr.Geometry(ogr.wkbPolygon)

        temp_ring_count = temp_geom.GetGeometryCount() # Polygon有可能带岛
        #print("polygon's ring count:", temp_ring_count)
        for iRing in range(0, temp_ring_count):
            temp_ring = temp_geom.GetGeometryRef(iRing) # 遍历每一个Ring，默认第一个是外环
            
            # 第二种写法
            # new_points = trans.TransformPoints(temp_ring.GetPoints())
            # print(new_points)

            # 第三种写法
            import pyproj
            source_proj = pyproj.Proj(srs.ExportToProj4())
            target_proj = pyproj.Proj(4326)
            prjtrans = pyproj.Transformer.from_proj(source_proj, target_proj)
            # 注意以上四行应该写到循环外面
            temp_ring_point_count = temp_ring.GetPointCount()
            new_points = []
            for iP in range(0, temp_ring_point_count):
                temp_point = temp_ring.GetPoint(iP)
                new_p = prjtrans.transform(temp_point[0], temp_point[1])
                #print(new_p) #注意，转出来的经纬度是反的
                new_points.append((new_p[1], new_p[0]))

            temp_new_ring = ogr.Geometry(ogr.wkbLinearRing)
            for new_p in new_points:
                temp_new_ring.AddPoint(new_p[0], new_p[1])
            temp_new_polygon.AddGeometry(temp_new_ring)
    # end if-else geometry type

    if temp_new_polygon != None:
        tempNewFeature = ogr.Feature(layerjs_def)
        tempNewFeature.SetGeometry(temp_new_polygon)
        tempNewFeature.SetField("PAC",temp_feature.GetField("PAC"))
        tempNewFeature.SetField("NAME",temp_feature.GetField("NAME"))
        tempNewFeature.SetField("AREA",temp_feature.GetField("AREA"))

        layerjs_4326.CreateFeature(tempNewFeature)
        tempNewFeature.Destroy()

ds.FlushCache()
if ds != None: ds.Destroy()

shape_path = "E:\派森\期末\T3\county_popu.shp"
ds = ogr.Open(shape_path)
layer = ds.GetLayer(0)
srs = layer.GetSpatialRef()
layer_defn = layer.GetLayerDefn()
field_count = layer_defn.GetFieldCount()
filed_name_list = [] #暂存原始Shapefile的属性字段的名字
for iField in range(0, field_count):
    temp_field = layer_defn.GetFieldDefn(iField)
    temp_name = temp_field.GetName()
    filed_name_list.append(temp_name)
    print(temp_name)
#上海是310开头
layer.SetAttributeFilter('("PAC"/1)=310114')
feature_count = layer.GetFeatureCount()
# 注意此处不宜使用For循环直接遍历
# 如果要用，属性过滤器是不起作用的
# 还需要在循环内部进行If判断
# for i in range(0, feature_count): 
#     temp_feature = layer.GetFeature(i)
#     temp_field_pac = temp_feature.GetField('PAC')
#     if temp_field_pac/10000 != 32:
#         continue
layer.ResetReading()
feature_list = [] #暂存过滤后的Feature数据
temp_feature = layer.GetNextFeature()
while temp_feature:
    temp_geom = temp_feature.GetGeometryRef()
    temp_field_area = temp_feature.GetField('Shape_Area')
    temp_field_name = temp_feature.GetField('NAME')
    temp_calculatet_area = temp_geom.Area()
    print('Name:', temp_field_name,
          'Area:', temp_field_area, 
          'Cal_Area:', temp_calculatet_area)
    feature_list.append(temp_feature)
    temp_feature = layer.GetNextFeature()


'''
将过滤后的Feature保存到新的文件中
'''
gdal.SetConfigOption("SHAPE_ENCODING", "UTF-8") # IMPORTANT
new_shape_path = 'E:/派森/期末/T3/shanghai_嘉定区.shp'

driverName = "ESRI Shapefile"
driver = ogr.GetDriverByName(driverName)
ds = driver.CreateDataSource(new_shape_path) #创建DataSource

geomType = ogr.wkbPolygon #指定几何类型
#创建图层，注意srs借用的是原来的
poLayer = ds.CreateLayer('shanghai_嘉定区', srs, geomType)

#对原始数据的属性字段进行遍历
for iField in range(0, field_count):
    temp_field = layer_defn.GetFieldDefn(iField)
    poLayer.CreateField(temp_field, 1)
    
#创建完所有的属性字段之后，获取整个图层的定义
new_layerdef = poLayer.GetLayerDefn()

for iF in range(0, feature_count):
    temp_old_feature = feature_list[iF]
    temp_geom = temp_old_feature.GetGeometryRef()
    
    tempNewFeature = ogr.Feature(new_layerdef)
    tempNewFeature.SetGeometry(temp_geom)
    for temp_name in filed_name_list:
        tempNewFeature.SetField(temp_name,temp_old_feature.GetField(temp_name))

    poLayer.CreateFeature(tempNewFeature)
    del tempNewFeature

ds.FlushCache()
if ds != None: ds.Destroy()


'''
将过滤后的Feature保存到新的文件中, 并且做投影转换
'''
new_shape_path = "E:\派森\期末\T3\shanghai_wgs84_嘉定区.shp"

driverName = "ESRI Shapefile"
driver = ogr.GetDriverByName(driverName)
ds = driver.CreateDataSource(new_shape_path)

geomType = ogr.wkbPolygon
srs_4326 = osr.SpatialReference(osr.SRS_WKT_WGS84_LAT_LONG) # 指定新的空间参考
srs_4326.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER) # 按照传统先X后Y的顺序进行坐标转换
#注意此处，指定了options=["ENCODING=UTF-8"], 会生成了以 *.cpg的文件, 里面给出了文字编码
layerjs_4326 = ds.CreateLayer('sh_嘉定区', srs_4326, geomType, options=["ENCODING=UTF-8"])

#选用了某几个属性字段放到新的Shapefile中
field1 = ogr.FieldDefn("PAC", ogr.OFTInteger64)
layerjs_4326.CreateField(field1, 1)
field1.Destroy()

field2 = ogr.FieldDefn("NAME", ogr.OFTString)
layerjs_4326.CreateField(field2, 1)
field2.Destroy()

field3 = ogr.FieldDefn("AREA", ogr.OFTReal)
layerjs_4326.CreateField(field3, 1)
field3.Destroy()

#获取新数据的图层属性
layerjs_def = layerjs_4326.GetLayerDefn()

#根据原始坐标参考和新的坐标参考，构建一个投影转换器
trans = osr.CoordinateTransformation(srs, srs_4326)

for iF in range(0, feature_count):
    temp_feature = feature_list[iF]

    temp_geom = temp_feature.GetGeometryRef() # 拿到Feature的Geometry对象
    temp_geom_type = temp_geom.GetGeometryType() # 拿到Geometry的几何类型
    temp_geom_count = temp_geom.GetGeometryCount() # 有可能是Multi-Polygon
    
    temp_new_polygon = None
    if temp_geom_type == ogr.wkbMultiPolygon and temp_geom_count>1:
        print("geometry name:", temp_geom.GetGeometryName())
        #print(temp_geom.GetGeometryName())
        temp_new_polygon = ogr.Geometry(ogr.wkbMultiPolygon)
        for iGeo in range(0, temp_geom_count):
            temp_part = temp_geom.GetGeometryRef(iGeo) # 获取Multi中的每一个Part
            temp_part_ring_count = temp_part.GetGeometryCount() # 每个Polygon可能会有ExRing和InRing
            #print("polygon's ring count:", temp_part_ring_count)
            
            temp_new_part = ogr.Geometry(ogr.wkbPolygon)
            for iRing in range(0, temp_part_ring_count):
                temp_ring = temp_part.GetGeometryRef(iRing)

                temp_new_ring = ogr.Geometry(ogr.wkbLinearRing)
                
                # 第一种写法
                temp_ring_point_count = temp_ring.GetPointCount()
                for iP in range(0, temp_ring_point_count):
                    temp_point = temp_ring.GetPoint(iP)
                    new_p = trans.TransformPoint(temp_point[0], temp_point[1])
                    #print(new_p)
                    temp_new_ring.AddPoint(new_p[0], new_p[1])
                temp_new_part.AddGeometry(temp_new_ring)
            
            temp_new_polygon.AddGeometry(temp_new_part)
    else:
        print("geometry name:", temp_geom.GetGeometryName())
        temp_new_polygon = ogr.Geometry(ogr.wkbPolygon)

        temp_ring_count = temp_geom.GetGeometryCount() # Polygon有可能带岛
        #print("polygon's ring count:", temp_ring_count)
        for iRing in range(0, temp_ring_count):
            temp_ring = temp_geom.GetGeometryRef(iRing) # 遍历每一个Ring，默认第一个是外环
            
            # 第二种写法
            # new_points = trans.TransformPoints(temp_ring.GetPoints())
            # print(new_points)

            # 第三种写法
            import pyproj
            source_proj = pyproj.Proj(srs.ExportToProj4())
            target_proj = pyproj.Proj(4326)
            prjtrans = pyproj.Transformer.from_proj(source_proj, target_proj)
            # 注意以上四行应该写到循环外面
            temp_ring_point_count = temp_ring.GetPointCount()
            new_points = []
            for iP in range(0, temp_ring_point_count):
                temp_point = temp_ring.GetPoint(iP)
                new_p = prjtrans.transform(temp_point[0], temp_point[1])
                #print(new_p) #注意，转出来的经纬度是反的
                new_points.append((new_p[1], new_p[0]))

            temp_new_ring = ogr.Geometry(ogr.wkbLinearRing)
            for new_p in new_points:
                temp_new_ring.AddPoint(new_p[0], new_p[1])
            temp_new_polygon.AddGeometry(temp_new_ring)
    # end if-else geometry type

    if temp_new_polygon != None:
        tempNewFeature = ogr.Feature(layerjs_def)
        tempNewFeature.SetGeometry(temp_new_polygon)
        tempNewFeature.SetField("PAC",temp_feature.GetField("PAC"))
        tempNewFeature.SetField("NAME",temp_feature.GetField("NAME"))
        tempNewFeature.SetField("AREA",temp_feature.GetField("AREA"))

        layerjs_4326.CreateFeature(tempNewFeature)
        tempNewFeature.Destroy()

ds.FlushCache()
if ds != None: ds.Destroy()

shape_path = "E:\派森\期末\T3\county_popu.shp"
ds = ogr.Open(shape_path)
layer = ds.GetLayer(0)
srs = layer.GetSpatialRef()
layer_defn = layer.GetLayerDefn()
field_count = layer_defn.GetFieldCount()
filed_name_list = [] #暂存原始Shapefile的属性字段的名字
for iField in range(0, field_count):
    temp_field = layer_defn.GetFieldDefn(iField)
    temp_name = temp_field.GetName()
    filed_name_list.append(temp_name)
    print(temp_name)
#上海是310开头
layer.SetAttributeFilter('("PAC"/1)=310115')
feature_count = layer.GetFeatureCount()
# 注意此处不宜使用For循环直接遍历
# 如果要用，属性过滤器是不起作用的
# 还需要在循环内部进行If判断
# for i in range(0, feature_count): 
#     temp_feature = layer.GetFeature(i)
#     temp_field_pac = temp_feature.GetField('PAC')
#     if temp_field_pac/10000 != 32:
#         continue
layer.ResetReading()
feature_list = [] #暂存过滤后的Feature数据
temp_feature = layer.GetNextFeature()
while temp_feature:
    temp_geom = temp_feature.GetGeometryRef()
    temp_field_area = temp_feature.GetField('Shape_Area')
    temp_field_name = temp_feature.GetField('NAME')
    temp_calculatet_area = temp_geom.Area()
    print('Name:', temp_field_name,
          'Area:', temp_field_area, 
          'Cal_Area:', temp_calculatet_area)
    feature_list.append(temp_feature)
    temp_feature = layer.GetNextFeature()


'''
将过滤后的Feature保存到新的文件中
'''
gdal.SetConfigOption("SHAPE_ENCODING", "UTF-8") # IMPORTANT
new_shape_path = 'E:/派森/期末/T3/shanghai_浦东新区.shp'

driverName = "ESRI Shapefile"
driver = ogr.GetDriverByName(driverName)
ds = driver.CreateDataSource(new_shape_path) #创建DataSource

geomType = ogr.wkbPolygon #指定几何类型
#创建图层，注意srs借用的是原来的
poLayer = ds.CreateLayer('shanghai_浦东新区', srs, geomType)

#对原始数据的属性字段进行遍历
for iField in range(0, field_count):
    temp_field = layer_defn.GetFieldDefn(iField)
    poLayer.CreateField(temp_field, 1)
    
#创建完所有的属性字段之后，获取整个图层的定义
new_layerdef = poLayer.GetLayerDefn()

for iF in range(0, feature_count):
    temp_old_feature = feature_list[iF]
    temp_geom = temp_old_feature.GetGeometryRef()
    
    tempNewFeature = ogr.Feature(new_layerdef)
    tempNewFeature.SetGeometry(temp_geom)
    for temp_name in filed_name_list:
        tempNewFeature.SetField(temp_name,temp_old_feature.GetField(temp_name))

    poLayer.CreateFeature(tempNewFeature)
    del tempNewFeature

ds.FlushCache()
if ds != None: ds.Destroy()


'''
将过滤后的Feature保存到新的文件中, 并且做投影转换
'''
new_shape_path = "E:\派森\期末\T3\shanghai_wgs84_浦东新区.shp"

driverName = "ESRI Shapefile"
driver = ogr.GetDriverByName(driverName)
ds = driver.CreateDataSource(new_shape_path)

geomType = ogr.wkbPolygon
srs_4326 = osr.SpatialReference(osr.SRS_WKT_WGS84_LAT_LONG) # 指定新的空间参考
srs_4326.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER) # 按照传统先X后Y的顺序进行坐标转换
#注意此处，指定了options=["ENCODING=UTF-8"], 会生成了以 *.cpg的文件, 里面给出了文字编码
layerjs_4326 = ds.CreateLayer('sh_浦东新区', srs_4326, geomType, options=["ENCODING=UTF-8"])

#选用了某几个属性字段放到新的Shapefile中
field1 = ogr.FieldDefn("PAC", ogr.OFTInteger64)
layerjs_4326.CreateField(field1, 1)
field1.Destroy()

field2 = ogr.FieldDefn("NAME", ogr.OFTString)
layerjs_4326.CreateField(field2, 1)
field2.Destroy()

field3 = ogr.FieldDefn("AREA", ogr.OFTReal)
layerjs_4326.CreateField(field3, 1)
field3.Destroy()

#获取新数据的图层属性
layerjs_def = layerjs_4326.GetLayerDefn()

#根据原始坐标参考和新的坐标参考，构建一个投影转换器
trans = osr.CoordinateTransformation(srs, srs_4326)

for iF in range(0, feature_count):
    temp_feature = feature_list[iF]

    temp_geom = temp_feature.GetGeometryRef() # 拿到Feature的Geometry对象
    temp_geom_type = temp_geom.GetGeometryType() # 拿到Geometry的几何类型
    temp_geom_count = temp_geom.GetGeometryCount() # 有可能是Multi-Polygon
    
    temp_new_polygon = None
    if temp_geom_type == ogr.wkbMultiPolygon and temp_geom_count>1:
        print("geometry name:", temp_geom.GetGeometryName())
        #print(temp_geom.GetGeometryName())
        temp_new_polygon = ogr.Geometry(ogr.wkbMultiPolygon)
        for iGeo in range(0, temp_geom_count):
            temp_part = temp_geom.GetGeometryRef(iGeo) # 获取Multi中的每一个Part
            temp_part_ring_count = temp_part.GetGeometryCount() # 每个Polygon可能会有ExRing和InRing
            #print("polygon's ring count:", temp_part_ring_count)
            
            temp_new_part = ogr.Geometry(ogr.wkbPolygon)
            for iRing in range(0, temp_part_ring_count):
                temp_ring = temp_part.GetGeometryRef(iRing)

                temp_new_ring = ogr.Geometry(ogr.wkbLinearRing)
                
                # 第一种写法
                temp_ring_point_count = temp_ring.GetPointCount()
                for iP in range(0, temp_ring_point_count):
                    temp_point = temp_ring.GetPoint(iP)
                    new_p = trans.TransformPoint(temp_point[0], temp_point[1])
                    #print(new_p)
                    temp_new_ring.AddPoint(new_p[0], new_p[1])
                temp_new_part.AddGeometry(temp_new_ring)
            
            temp_new_polygon.AddGeometry(temp_new_part)
    else:
        print("geometry name:", temp_geom.GetGeometryName())
        temp_new_polygon = ogr.Geometry(ogr.wkbPolygon)

        temp_ring_count = temp_geom.GetGeometryCount() # Polygon有可能带岛
        #print("polygon's ring count:", temp_ring_count)
        for iRing in range(0, temp_ring_count):
            temp_ring = temp_geom.GetGeometryRef(iRing) # 遍历每一个Ring，默认第一个是外环
            
            # 第二种写法
            # new_points = trans.TransformPoints(temp_ring.GetPoints())
            # print(new_points)

            # 第三种写法
            import pyproj
            source_proj = pyproj.Proj(srs.ExportToProj4())
            target_proj = pyproj.Proj(4326)
            prjtrans = pyproj.Transformer.from_proj(source_proj, target_proj)
            # 注意以上四行应该写到循环外面
            temp_ring_point_count = temp_ring.GetPointCount()
            new_points = []
            for iP in range(0, temp_ring_point_count):
                temp_point = temp_ring.GetPoint(iP)
                new_p = prjtrans.transform(temp_point[0], temp_point[1])
                #print(new_p) #注意，转出来的经纬度是反的
                new_points.append((new_p[1], new_p[0]))

            temp_new_ring = ogr.Geometry(ogr.wkbLinearRing)
            for new_p in new_points:
                temp_new_ring.AddPoint(new_p[0], new_p[1])
            temp_new_polygon.AddGeometry(temp_new_ring)
    # end if-else geometry type

    if temp_new_polygon != None:
        tempNewFeature = ogr.Feature(layerjs_def)
        tempNewFeature.SetGeometry(temp_new_polygon)
        tempNewFeature.SetField("PAC",temp_feature.GetField("PAC"))
        tempNewFeature.SetField("NAME",temp_feature.GetField("NAME"))
        tempNewFeature.SetField("AREA",temp_feature.GetField("AREA"))

        layerjs_4326.CreateFeature(tempNewFeature)
        tempNewFeature.Destroy()

ds.FlushCache()
if ds != None: ds.Destroy()

shape_path = "E:\派森\期末\T3\county_popu.shp"
ds = ogr.Open(shape_path)
layer = ds.GetLayer(0)
srs = layer.GetSpatialRef()
layer_defn = layer.GetLayerDefn()
field_count = layer_defn.GetFieldCount()
filed_name_list = [] #暂存原始Shapefile的属性字段的名字
for iField in range(0, field_count):
    temp_field = layer_defn.GetFieldDefn(iField)
    temp_name = temp_field.GetName()
    filed_name_list.append(temp_name)
    print(temp_name)
#上海是310开头
layer.SetAttributeFilter('("PAC"/1)=310116')
feature_count = layer.GetFeatureCount()
# 注意此处不宜使用For循环直接遍历
# 如果要用，属性过滤器是不起作用的
# 还需要在循环内部进行If判断
# for i in range(0, feature_count): 
#     temp_feature = layer.GetFeature(i)
#     temp_field_pac = temp_feature.GetField('PAC')
#     if temp_field_pac/10000 != 32:
#         continue
layer.ResetReading()
feature_list = [] #暂存过滤后的Feature数据
temp_feature = layer.GetNextFeature()
while temp_feature:
    temp_geom = temp_feature.GetGeometryRef()
    temp_field_area = temp_feature.GetField('Shape_Area')
    temp_field_name = temp_feature.GetField('NAME')
    temp_calculatet_area = temp_geom.Area()
    print('Name:', temp_field_name,
          'Area:', temp_field_area, 
          'Cal_Area:', temp_calculatet_area)
    feature_list.append(temp_feature)
    temp_feature = layer.GetNextFeature()


'''
将过滤后的Feature保存到新的文件中
'''
gdal.SetConfigOption("SHAPE_ENCODING", "UTF-8") # IMPORTANT
new_shape_path = 'E:/派森/期末/T3/shanghai_金山区.shp'

driverName = "ESRI Shapefile"
driver = ogr.GetDriverByName(driverName)
ds = driver.CreateDataSource(new_shape_path) #创建DataSource

geomType = ogr.wkbPolygon #指定几何类型
#创建图层，注意srs借用的是原来的
poLayer = ds.CreateLayer('shanghai_金山区', srs, geomType)

#对原始数据的属性字段进行遍历
for iField in range(0, field_count):
    temp_field = layer_defn.GetFieldDefn(iField)
    poLayer.CreateField(temp_field, 1)
    
#创建完所有的属性字段之后，获取整个图层的定义
new_layerdef = poLayer.GetLayerDefn()

for iF in range(0, feature_count):
    temp_old_feature = feature_list[iF]
    temp_geom = temp_old_feature.GetGeometryRef()
    
    tempNewFeature = ogr.Feature(new_layerdef)
    tempNewFeature.SetGeometry(temp_geom)
    for temp_name in filed_name_list:
        tempNewFeature.SetField(temp_name,temp_old_feature.GetField(temp_name))

    poLayer.CreateFeature(tempNewFeature)
    del tempNewFeature

ds.FlushCache()
if ds != None: ds.Destroy()


'''
将过滤后的Feature保存到新的文件中, 并且做投影转换
'''
new_shape_path = "E:\派森\期末\T3\shanghai_wgs84_金山区.shp"

driverName = "ESRI Shapefile"
driver = ogr.GetDriverByName(driverName)
ds = driver.CreateDataSource(new_shape_path)

geomType = ogr.wkbPolygon
srs_4326 = osr.SpatialReference(osr.SRS_WKT_WGS84_LAT_LONG) # 指定新的空间参考
srs_4326.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER) # 按照传统先X后Y的顺序进行坐标转换
#注意此处，指定了options=["ENCODING=UTF-8"], 会生成了以 *.cpg的文件, 里面给出了文字编码
layerjs_4326 = ds.CreateLayer('sh_金山区', srs_4326, geomType, options=["ENCODING=UTF-8"])

#选用了某几个属性字段放到新的Shapefile中
field1 = ogr.FieldDefn("PAC", ogr.OFTInteger64)
layerjs_4326.CreateField(field1, 1)
field1.Destroy()

field2 = ogr.FieldDefn("NAME", ogr.OFTString)
layerjs_4326.CreateField(field2, 1)
field2.Destroy()

field3 = ogr.FieldDefn("AREA", ogr.OFTReal)
layerjs_4326.CreateField(field3, 1)
field3.Destroy()

#获取新数据的图层属性
layerjs_def = layerjs_4326.GetLayerDefn()

#根据原始坐标参考和新的坐标参考，构建一个投影转换器
trans = osr.CoordinateTransformation(srs, srs_4326)

for iF in range(0, feature_count):
    temp_feature = feature_list[iF]

    temp_geom = temp_feature.GetGeometryRef() # 拿到Feature的Geometry对象
    temp_geom_type = temp_geom.GetGeometryType() # 拿到Geometry的几何类型
    temp_geom_count = temp_geom.GetGeometryCount() # 有可能是Multi-Polygon
    
    temp_new_polygon = None
    if temp_geom_type == ogr.wkbMultiPolygon and temp_geom_count>1:
        print("geometry name:", temp_geom.GetGeometryName())
        #print(temp_geom.GetGeometryName())
        temp_new_polygon = ogr.Geometry(ogr.wkbMultiPolygon)
        for iGeo in range(0, temp_geom_count):
            temp_part = temp_geom.GetGeometryRef(iGeo) # 获取Multi中的每一个Part
            temp_part_ring_count = temp_part.GetGeometryCount() # 每个Polygon可能会有ExRing和InRing
            #print("polygon's ring count:", temp_part_ring_count)
            
            temp_new_part = ogr.Geometry(ogr.wkbPolygon)
            for iRing in range(0, temp_part_ring_count):
                temp_ring = temp_part.GetGeometryRef(iRing)

                temp_new_ring = ogr.Geometry(ogr.wkbLinearRing)
                
                # 第一种写法
                temp_ring_point_count = temp_ring.GetPointCount()
                for iP in range(0, temp_ring_point_count):
                    temp_point = temp_ring.GetPoint(iP)
                    new_p = trans.TransformPoint(temp_point[0], temp_point[1])
                    #print(new_p)
                    temp_new_ring.AddPoint(new_p[0], new_p[1])
                temp_new_part.AddGeometry(temp_new_ring)
            
            temp_new_polygon.AddGeometry(temp_new_part)
    else:
        print("geometry name:", temp_geom.GetGeometryName())
        temp_new_polygon = ogr.Geometry(ogr.wkbPolygon)

        temp_ring_count = temp_geom.GetGeometryCount() # Polygon有可能带岛
        #print("polygon's ring count:", temp_ring_count)
        for iRing in range(0, temp_ring_count):
            temp_ring = temp_geom.GetGeometryRef(iRing) # 遍历每一个Ring，默认第一个是外环
            
            # 第二种写法
            # new_points = trans.TransformPoints(temp_ring.GetPoints())
            # print(new_points)

            # 第三种写法
            import pyproj
            source_proj = pyproj.Proj(srs.ExportToProj4())
            target_proj = pyproj.Proj(4326)
            prjtrans = pyproj.Transformer.from_proj(source_proj, target_proj)
            # 注意以上四行应该写到循环外面
            temp_ring_point_count = temp_ring.GetPointCount()
            new_points = []
            for iP in range(0, temp_ring_point_count):
                temp_point = temp_ring.GetPoint(iP)
                new_p = prjtrans.transform(temp_point[0], temp_point[1])
                #print(new_p) #注意，转出来的经纬度是反的
                new_points.append((new_p[1], new_p[0]))

            temp_new_ring = ogr.Geometry(ogr.wkbLinearRing)
            for new_p in new_points:
                temp_new_ring.AddPoint(new_p[0], new_p[1])
            temp_new_polygon.AddGeometry(temp_new_ring)
    # end if-else geometry type

    if temp_new_polygon != None:
        tempNewFeature = ogr.Feature(layerjs_def)
        tempNewFeature.SetGeometry(temp_new_polygon)
        tempNewFeature.SetField("PAC",temp_feature.GetField("PAC"))
        tempNewFeature.SetField("NAME",temp_feature.GetField("NAME"))
        tempNewFeature.SetField("AREA",temp_feature.GetField("AREA"))

        layerjs_4326.CreateFeature(tempNewFeature)
        tempNewFeature.Destroy()

ds.FlushCache()
if ds != None: ds.Destroy()


shape_path = "E:\派森\期末\T3\county_popu.shp"
ds = ogr.Open(shape_path)
layer = ds.GetLayer(0)
srs = layer.GetSpatialRef()
layer_defn = layer.GetLayerDefn()
field_count = layer_defn.GetFieldCount()
filed_name_list = [] #暂存原始Shapefile的属性字段的名字
for iField in range(0, field_count):
    temp_field = layer_defn.GetFieldDefn(iField)
    temp_name = temp_field.GetName()
    filed_name_list.append(temp_name)
    print(temp_name)
#上海是310开头
layer.SetAttributeFilter('("PAC"/1)=310117')
feature_count = layer.GetFeatureCount()
# 注意此处不宜使用For循环直接遍历
# 如果要用，属性过滤器是不起作用的
# 还需要在循环内部进行If判断
# for i in range(0, feature_count): 
#     temp_feature = layer.GetFeature(i)
#     temp_field_pac = temp_feature.GetField('PAC')
#     if temp_field_pac/10000 != 32:
#         continue
layer.ResetReading()
feature_list = [] #暂存过滤后的Feature数据
temp_feature = layer.GetNextFeature()
while temp_feature:
    temp_geom = temp_feature.GetGeometryRef()
    temp_field_area = temp_feature.GetField('Shape_Area')
    temp_field_name = temp_feature.GetField('NAME')
    temp_calculatet_area = temp_geom.Area()
    print('Name:', temp_field_name,
          'Area:', temp_field_area, 
          'Cal_Area:', temp_calculatet_area)
    feature_list.append(temp_feature)
    temp_feature = layer.GetNextFeature()


'''
将过滤后的Feature保存到新的文件中
'''
gdal.SetConfigOption("SHAPE_ENCODING", "UTF-8") # IMPORTANT
new_shape_path = 'E:/派森/期末/T3/shanghai_松江区.shp'

driverName = "ESRI Shapefile"
driver = ogr.GetDriverByName(driverName)
ds = driver.CreateDataSource(new_shape_path) #创建DataSource

geomType = ogr.wkbPolygon #指定几何类型
#创建图层，注意srs借用的是原来的
poLayer = ds.CreateLayer('shanghai_松江区', srs, geomType)

#对原始数据的属性字段进行遍历
for iField in range(0, field_count):
    temp_field = layer_defn.GetFieldDefn(iField)
    poLayer.CreateField(temp_field, 1)
    
#创建完所有的属性字段之后，获取整个图层的定义
new_layerdef = poLayer.GetLayerDefn()

for iF in range(0, feature_count):
    temp_old_feature = feature_list[iF]
    temp_geom = temp_old_feature.GetGeometryRef()
    
    tempNewFeature = ogr.Feature(new_layerdef)
    tempNewFeature.SetGeometry(temp_geom)
    for temp_name in filed_name_list:
        tempNewFeature.SetField(temp_name,temp_old_feature.GetField(temp_name))

    poLayer.CreateFeature(tempNewFeature)
    del tempNewFeature

ds.FlushCache()
if ds != None: ds.Destroy()


'''
将过滤后的Feature保存到新的文件中, 并且做投影转换
'''
new_shape_path = "E:\派森\期末\T3\shanghai_wgs84_松江区.shp"

driverName = "ESRI Shapefile"
driver = ogr.GetDriverByName(driverName)
ds = driver.CreateDataSource(new_shape_path)

geomType = ogr.wkbPolygon
srs_4326 = osr.SpatialReference(osr.SRS_WKT_WGS84_LAT_LONG) # 指定新的空间参考
srs_4326.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER) # 按照传统先X后Y的顺序进行坐标转换
#注意此处，指定了options=["ENCODING=UTF-8"], 会生成了以 *.cpg的文件, 里面给出了文字编码
layerjs_4326 = ds.CreateLayer('sh_松江区', srs_4326, geomType, options=["ENCODING=UTF-8"])

#选用了某几个属性字段放到新的Shapefile中
field1 = ogr.FieldDefn("PAC", ogr.OFTInteger64)
layerjs_4326.CreateField(field1, 1)
field1.Destroy()

field2 = ogr.FieldDefn("NAME", ogr.OFTString)
layerjs_4326.CreateField(field2, 1)
field2.Destroy()

field3 = ogr.FieldDefn("AREA", ogr.OFTReal)
layerjs_4326.CreateField(field3, 1)
field3.Destroy()

#获取新数据的图层属性
layerjs_def = layerjs_4326.GetLayerDefn()

#根据原始坐标参考和新的坐标参考，构建一个投影转换器
trans = osr.CoordinateTransformation(srs, srs_4326)

for iF in range(0, feature_count):
    temp_feature = feature_list[iF]

    temp_geom = temp_feature.GetGeometryRef() # 拿到Feature的Geometry对象
    temp_geom_type = temp_geom.GetGeometryType() # 拿到Geometry的几何类型
    temp_geom_count = temp_geom.GetGeometryCount() # 有可能是Multi-Polygon
    
    temp_new_polygon = None
    if temp_geom_type == ogr.wkbMultiPolygon and temp_geom_count>1:
        print("geometry name:", temp_geom.GetGeometryName())
        #print(temp_geom.GetGeometryName())
        temp_new_polygon = ogr.Geometry(ogr.wkbMultiPolygon)
        for iGeo in range(0, temp_geom_count):
            temp_part = temp_geom.GetGeometryRef(iGeo) # 获取Multi中的每一个Part
            temp_part_ring_count = temp_part.GetGeometryCount() # 每个Polygon可能会有ExRing和InRing
            #print("polygon's ring count:", temp_part_ring_count)
            
            temp_new_part = ogr.Geometry(ogr.wkbPolygon)
            for iRing in range(0, temp_part_ring_count):
                temp_ring = temp_part.GetGeometryRef(iRing)

                temp_new_ring = ogr.Geometry(ogr.wkbLinearRing)
                
                # 第一种写法
                temp_ring_point_count = temp_ring.GetPointCount()
                for iP in range(0, temp_ring_point_count):
                    temp_point = temp_ring.GetPoint(iP)
                    new_p = trans.TransformPoint(temp_point[0], temp_point[1])
                    #print(new_p)
                    temp_new_ring.AddPoint(new_p[0], new_p[1])
                temp_new_part.AddGeometry(temp_new_ring)
            
            temp_new_polygon.AddGeometry(temp_new_part)
    else:
        print("geometry name:", temp_geom.GetGeometryName())
        temp_new_polygon = ogr.Geometry(ogr.wkbPolygon)

        temp_ring_count = temp_geom.GetGeometryCount() # Polygon有可能带岛
        #print("polygon's ring count:", temp_ring_count)
        for iRing in range(0, temp_ring_count):
            temp_ring = temp_geom.GetGeometryRef(iRing) # 遍历每一个Ring，默认第一个是外环
            
            # 第二种写法
            # new_points = trans.TransformPoints(temp_ring.GetPoints())
            # print(new_points)

            # 第三种写法
            import pyproj
            source_proj = pyproj.Proj(srs.ExportToProj4())
            target_proj = pyproj.Proj(4326)
            prjtrans = pyproj.Transformer.from_proj(source_proj, target_proj)
            # 注意以上四行应该写到循环外面
            temp_ring_point_count = temp_ring.GetPointCount()
            new_points = []
            for iP in range(0, temp_ring_point_count):
                temp_point = temp_ring.GetPoint(iP)
                new_p = prjtrans.transform(temp_point[0], temp_point[1])
                #print(new_p) #注意，转出来的经纬度是反的
                new_points.append((new_p[1], new_p[0]))

            temp_new_ring = ogr.Geometry(ogr.wkbLinearRing)
            for new_p in new_points:
                temp_new_ring.AddPoint(new_p[0], new_p[1])
            temp_new_polygon.AddGeometry(temp_new_ring)
    # end if-else geometry type

    if temp_new_polygon != None:
        tempNewFeature = ogr.Feature(layerjs_def)
        tempNewFeature.SetGeometry(temp_new_polygon)
        tempNewFeature.SetField("PAC",temp_feature.GetField("PAC"))
        tempNewFeature.SetField("NAME",temp_feature.GetField("NAME"))
        tempNewFeature.SetField("AREA",temp_feature.GetField("AREA"))

        layerjs_4326.CreateFeature(tempNewFeature)
        tempNewFeature.Destroy()

ds.FlushCache()
if ds != None: ds.Destroy()


shape_path = "E:\派森\期末\T3\county_popu.shp"
ds = ogr.Open(shape_path)
layer = ds.GetLayer(0)
srs = layer.GetSpatialRef()
layer_defn = layer.GetLayerDefn()
field_count = layer_defn.GetFieldCount()
filed_name_list = [] #暂存原始Shapefile的属性字段的名字
for iField in range(0, field_count):
    temp_field = layer_defn.GetFieldDefn(iField)
    temp_name = temp_field.GetName()
    filed_name_list.append(temp_name)
    print(temp_name)
#上海是310开头
layer.SetAttributeFilter('("PAC"/1)=310118')
feature_count = layer.GetFeatureCount()
# 注意此处不宜使用For循环直接遍历
# 如果要用，属性过滤器是不起作用的
# 还需要在循环内部进行If判断
# for i in range(0, feature_count): 
#     temp_feature = layer.GetFeature(i)
#     temp_field_pac = temp_feature.GetField('PAC')
#     if temp_field_pac/10000 != 32:
#         continue
layer.ResetReading()
feature_list = [] #暂存过滤后的Feature数据
temp_feature = layer.GetNextFeature()
while temp_feature:
    temp_geom = temp_feature.GetGeometryRef()
    temp_field_area = temp_feature.GetField('Shape_Area')
    temp_field_name = temp_feature.GetField('NAME')
    temp_calculatet_area = temp_geom.Area()
    print('Name:', temp_field_name,
          'Area:', temp_field_area, 
          'Cal_Area:', temp_calculatet_area)
    feature_list.append(temp_feature)
    temp_feature = layer.GetNextFeature()


'''
将过滤后的Feature保存到新的文件中
'''
gdal.SetConfigOption("SHAPE_ENCODING", "UTF-8") # IMPORTANT
new_shape_path = 'E:/派森/期末/T3/shanghai_青浦区.shp'

driverName = "ESRI Shapefile"
driver = ogr.GetDriverByName(driverName)
ds = driver.CreateDataSource(new_shape_path) #创建DataSource

geomType = ogr.wkbPolygon #指定几何类型
#创建图层，注意srs借用的是原来的
poLayer = ds.CreateLayer('shanghai_青浦区', srs, geomType)

#对原始数据的属性字段进行遍历
for iField in range(0, field_count):
    temp_field = layer_defn.GetFieldDefn(iField)
    poLayer.CreateField(temp_field, 1)
    
#创建完所有的属性字段之后，获取整个图层的定义
new_layerdef = poLayer.GetLayerDefn()

for iF in range(0, feature_count):
    temp_old_feature = feature_list[iF]
    temp_geom = temp_old_feature.GetGeometryRef()
    
    tempNewFeature = ogr.Feature(new_layerdef)
    tempNewFeature.SetGeometry(temp_geom)
    for temp_name in filed_name_list:
        tempNewFeature.SetField(temp_name,temp_old_feature.GetField(temp_name))

    poLayer.CreateFeature(tempNewFeature)
    del tempNewFeature

ds.FlushCache()
if ds != None: ds.Destroy()


'''
将过滤后的Feature保存到新的文件中, 并且做投影转换
'''
new_shape_path = "E:\派森\期末\T3\shanghai_wgs84_青浦区.shp"

driverName = "ESRI Shapefile"
driver = ogr.GetDriverByName(driverName)
ds = driver.CreateDataSource(new_shape_path)

geomType = ogr.wkbPolygon
srs_4326 = osr.SpatialReference(osr.SRS_WKT_WGS84_LAT_LONG) # 指定新的空间参考
srs_4326.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER) # 按照传统先X后Y的顺序进行坐标转换
#注意此处，指定了options=["ENCODING=UTF-8"], 会生成了以 *.cpg的文件, 里面给出了文字编码
layerjs_4326 = ds.CreateLayer('sh_青浦区', srs_4326, geomType, options=["ENCODING=UTF-8"])

#选用了某几个属性字段放到新的Shapefile中
field1 = ogr.FieldDefn("PAC", ogr.OFTInteger64)
layerjs_4326.CreateField(field1, 1)
field1.Destroy()

field2 = ogr.FieldDefn("NAME", ogr.OFTString)
layerjs_4326.CreateField(field2, 1)
field2.Destroy()

field3 = ogr.FieldDefn("AREA", ogr.OFTReal)
layerjs_4326.CreateField(field3, 1)
field3.Destroy()

#获取新数据的图层属性
layerjs_def = layerjs_4326.GetLayerDefn()

#根据原始坐标参考和新的坐标参考，构建一个投影转换器
trans = osr.CoordinateTransformation(srs, srs_4326)

for iF in range(0, feature_count):
    temp_feature = feature_list[iF]

    temp_geom = temp_feature.GetGeometryRef() # 拿到Feature的Geometry对象
    temp_geom_type = temp_geom.GetGeometryType() # 拿到Geometry的几何类型
    temp_geom_count = temp_geom.GetGeometryCount() # 有可能是Multi-Polygon
    
    temp_new_polygon = None
    if temp_geom_type == ogr.wkbMultiPolygon and temp_geom_count>1:
        print("geometry name:", temp_geom.GetGeometryName())
        #print(temp_geom.GetGeometryName())
        temp_new_polygon = ogr.Geometry(ogr.wkbMultiPolygon)
        for iGeo in range(0, temp_geom_count):
            temp_part = temp_geom.GetGeometryRef(iGeo) # 获取Multi中的每一个Part
            temp_part_ring_count = temp_part.GetGeometryCount() # 每个Polygon可能会有ExRing和InRing
            #print("polygon's ring count:", temp_part_ring_count)
            
            temp_new_part = ogr.Geometry(ogr.wkbPolygon)
            for iRing in range(0, temp_part_ring_count):
                temp_ring = temp_part.GetGeometryRef(iRing)

                temp_new_ring = ogr.Geometry(ogr.wkbLinearRing)
                
                # 第一种写法
                temp_ring_point_count = temp_ring.GetPointCount()
                for iP in range(0, temp_ring_point_count):
                    temp_point = temp_ring.GetPoint(iP)
                    new_p = trans.TransformPoint(temp_point[0], temp_point[1])
                    #print(new_p)
                    temp_new_ring.AddPoint(new_p[0], new_p[1])
                temp_new_part.AddGeometry(temp_new_ring)
            
            temp_new_polygon.AddGeometry(temp_new_part)
    else:
        print("geometry name:", temp_geom.GetGeometryName())
        temp_new_polygon = ogr.Geometry(ogr.wkbPolygon)

        temp_ring_count = temp_geom.GetGeometryCount() # Polygon有可能带岛
        #print("polygon's ring count:", temp_ring_count)
        for iRing in range(0, temp_ring_count):
            temp_ring = temp_geom.GetGeometryRef(iRing) # 遍历每一个Ring，默认第一个是外环
            
            # 第二种写法
            # new_points = trans.TransformPoints(temp_ring.GetPoints())
            # print(new_points)

            # 第三种写法
            import pyproj
            source_proj = pyproj.Proj(srs.ExportToProj4())
            target_proj = pyproj.Proj(4326)
            prjtrans = pyproj.Transformer.from_proj(source_proj, target_proj)
            # 注意以上四行应该写到循环外面
            temp_ring_point_count = temp_ring.GetPointCount()
            new_points = []
            for iP in range(0, temp_ring_point_count):
                temp_point = temp_ring.GetPoint(iP)
                new_p = prjtrans.transform(temp_point[0], temp_point[1])
                #print(new_p) #注意，转出来的经纬度是反的
                new_points.append((new_p[1], new_p[0]))

            temp_new_ring = ogr.Geometry(ogr.wkbLinearRing)
            for new_p in new_points:
                temp_new_ring.AddPoint(new_p[0], new_p[1])
            temp_new_polygon.AddGeometry(temp_new_ring)
    # end if-else geometry type

    if temp_new_polygon != None:
        tempNewFeature = ogr.Feature(layerjs_def)
        tempNewFeature.SetGeometry(temp_new_polygon)
        tempNewFeature.SetField("PAC",temp_feature.GetField("PAC"))
        tempNewFeature.SetField("NAME",temp_feature.GetField("NAME"))
        tempNewFeature.SetField("AREA",temp_feature.GetField("AREA"))

        layerjs_4326.CreateFeature(tempNewFeature)
        tempNewFeature.Destroy()

ds.FlushCache()
if ds != None: ds.Destroy()


shape_path = "E:\派森\期末\T3\county_popu.shp"
ds = ogr.Open(shape_path)
layer = ds.GetLayer(0)
srs = layer.GetSpatialRef()
layer_defn = layer.GetLayerDefn()
field_count = layer_defn.GetFieldCount()
filed_name_list = [] #暂存原始Shapefile的属性字段的名字
for iField in range(0, field_count):
    temp_field = layer_defn.GetFieldDefn(iField)
    temp_name = temp_field.GetName()
    filed_name_list.append(temp_name)
    print(temp_name)
#上海是310开头
layer.SetAttributeFilter('("PAC"/1)=310120')
feature_count = layer.GetFeatureCount()
# 注意此处不宜使用For循环直接遍历
# 如果要用，属性过滤器是不起作用的
# 还需要在循环内部进行If判断
# for i in range(0, feature_count): 
#     temp_feature = layer.GetFeature(i)
#     temp_field_pac = temp_feature.GetField('PAC')
#     if temp_field_pac/10000 != 32:
#         continue
layer.ResetReading()
feature_list = [] #暂存过滤后的Feature数据
temp_feature = layer.GetNextFeature()
while temp_feature:
    temp_geom = temp_feature.GetGeometryRef()
    temp_field_area = temp_feature.GetField('Shape_Area')
    temp_field_name = temp_feature.GetField('NAME')
    temp_calculatet_area = temp_geom.Area()
    print('Name:', temp_field_name,
          'Area:', temp_field_area, 
          'Cal_Area:', temp_calculatet_area)
    feature_list.append(temp_feature)
    temp_feature = layer.GetNextFeature()


'''
将过滤后的Feature保存到新的文件中
'''
gdal.SetConfigOption("SHAPE_ENCODING", "UTF-8") # IMPORTANT
new_shape_path = 'E:/派森/期末/T3/shanghai_奉贤区.shp'

driverName = "ESRI Shapefile"
driver = ogr.GetDriverByName(driverName)
ds = driver.CreateDataSource(new_shape_path) #创建DataSource

geomType = ogr.wkbPolygon #指定几何类型
#创建图层，注意srs借用的是原来的
poLayer = ds.CreateLayer('shanghai_奉贤区', srs, geomType)

#对原始数据的属性字段进行遍历
for iField in range(0, field_count):
    temp_field = layer_defn.GetFieldDefn(iField)
    poLayer.CreateField(temp_field, 1)
    
#创建完所有的属性字段之后，获取整个图层的定义
new_layerdef = poLayer.GetLayerDefn()

for iF in range(0, feature_count):
    temp_old_feature = feature_list[iF]
    temp_geom = temp_old_feature.GetGeometryRef()
    
    tempNewFeature = ogr.Feature(new_layerdef)
    tempNewFeature.SetGeometry(temp_geom)
    for temp_name in filed_name_list:
        tempNewFeature.SetField(temp_name,temp_old_feature.GetField(temp_name))

    poLayer.CreateFeature(tempNewFeature)
    del tempNewFeature

ds.FlushCache()
if ds != None: ds.Destroy()


'''
将过滤后的Feature保存到新的文件中, 并且做投影转换
'''
new_shape_path = "E:\派森\期末\T3\shanghai_wgs84_奉贤区.shp"

driverName = "ESRI Shapefile"
driver = ogr.GetDriverByName(driverName)
ds = driver.CreateDataSource(new_shape_path)

geomType = ogr.wkbPolygon
srs_4326 = osr.SpatialReference(osr.SRS_WKT_WGS84_LAT_LONG) # 指定新的空间参考
srs_4326.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER) # 按照传统先X后Y的顺序进行坐标转换
#注意此处，指定了options=["ENCODING=UTF-8"], 会生成了以 *.cpg的文件, 里面给出了文字编码
layerjs_4326 = ds.CreateLayer('sh_奉贤区', srs_4326, geomType, options=["ENCODING=UTF-8"])

#选用了某几个属性字段放到新的Shapefile中
field1 = ogr.FieldDefn("PAC", ogr.OFTInteger64)
layerjs_4326.CreateField(field1, 1)
field1.Destroy()

field2 = ogr.FieldDefn("NAME", ogr.OFTString)
layerjs_4326.CreateField(field2, 1)
field2.Destroy()

field3 = ogr.FieldDefn("AREA", ogr.OFTReal)
layerjs_4326.CreateField(field3, 1)
field3.Destroy()

#获取新数据的图层属性
layerjs_def = layerjs_4326.GetLayerDefn()

#根据原始坐标参考和新的坐标参考，构建一个投影转换器
trans = osr.CoordinateTransformation(srs, srs_4326)

for iF in range(0, feature_count):
    temp_feature = feature_list[iF]

    temp_geom = temp_feature.GetGeometryRef() # 拿到Feature的Geometry对象
    temp_geom_type = temp_geom.GetGeometryType() # 拿到Geometry的几何类型
    temp_geom_count = temp_geom.GetGeometryCount() # 有可能是Multi-Polygon
    
    temp_new_polygon = None
    if temp_geom_type == ogr.wkbMultiPolygon and temp_geom_count>1:
        print("geometry name:", temp_geom.GetGeometryName())
        #print(temp_geom.GetGeometryName())
        temp_new_polygon = ogr.Geometry(ogr.wkbMultiPolygon)
        for iGeo in range(0, temp_geom_count):
            temp_part = temp_geom.GetGeometryRef(iGeo) # 获取Multi中的每一个Part
            temp_part_ring_count = temp_part.GetGeometryCount() # 每个Polygon可能会有ExRing和InRing
            #print("polygon's ring count:", temp_part_ring_count)
            
            temp_new_part = ogr.Geometry(ogr.wkbPolygon)
            for iRing in range(0, temp_part_ring_count):
                temp_ring = temp_part.GetGeometryRef(iRing)

                temp_new_ring = ogr.Geometry(ogr.wkbLinearRing)
                
                # 第一种写法
                temp_ring_point_count = temp_ring.GetPointCount()
                for iP in range(0, temp_ring_point_count):
                    temp_point = temp_ring.GetPoint(iP)
                    new_p = trans.TransformPoint(temp_point[0], temp_point[1])
                    #print(new_p)
                    temp_new_ring.AddPoint(new_p[0], new_p[1])
                temp_new_part.AddGeometry(temp_new_ring)
            
            temp_new_polygon.AddGeometry(temp_new_part)
    else:
        print("geometry name:", temp_geom.GetGeometryName())
        temp_new_polygon = ogr.Geometry(ogr.wkbPolygon)

        temp_ring_count = temp_geom.GetGeometryCount() # Polygon有可能带岛
        #print("polygon's ring count:", temp_ring_count)
        for iRing in range(0, temp_ring_count):
            temp_ring = temp_geom.GetGeometryRef(iRing) # 遍历每一个Ring，默认第一个是外环
            
            # 第二种写法
            # new_points = trans.TransformPoints(temp_ring.GetPoints())
            # print(new_points)

            # 第三种写法
            import pyproj
            source_proj = pyproj.Proj(srs.ExportToProj4())
            target_proj = pyproj.Proj(4326)
            prjtrans = pyproj.Transformer.from_proj(source_proj, target_proj)
            # 注意以上四行应该写到循环外面
            temp_ring_point_count = temp_ring.GetPointCount()
            new_points = []
            for iP in range(0, temp_ring_point_count):
                temp_point = temp_ring.GetPoint(iP)
                new_p = prjtrans.transform(temp_point[0], temp_point[1])
                #print(new_p) #注意，转出来的经纬度是反的
                new_points.append((new_p[1], new_p[0]))

            temp_new_ring = ogr.Geometry(ogr.wkbLinearRing)
            for new_p in new_points:
                temp_new_ring.AddPoint(new_p[0], new_p[1])
            temp_new_polygon.AddGeometry(temp_new_ring)
    # end if-else geometry type

    if temp_new_polygon != None:
        tempNewFeature = ogr.Feature(layerjs_def)
        tempNewFeature.SetGeometry(temp_new_polygon)
        tempNewFeature.SetField("PAC",temp_feature.GetField("PAC"))
        tempNewFeature.SetField("NAME",temp_feature.GetField("NAME"))
        tempNewFeature.SetField("AREA",temp_feature.GetField("AREA"))

        layerjs_4326.CreateFeature(tempNewFeature)
        tempNewFeature.Destroy()

ds.FlushCache()
if ds != None: ds.Destroy()

shape_path = "E:\派森\期末\T3\county_popu.shp"
ds = ogr.Open(shape_path)
layer = ds.GetLayer(0)
srs = layer.GetSpatialRef()
layer_defn = layer.GetLayerDefn()
field_count = layer_defn.GetFieldCount()
filed_name_list = [] #暂存原始Shapefile的属性字段的名字
for iField in range(0, field_count):
    temp_field = layer_defn.GetFieldDefn(iField)
    temp_name = temp_field.GetName()
    filed_name_list.append(temp_name)
    print(temp_name)
#上海是310开头
layer.SetAttributeFilter('("PAC"/1)=310230')
feature_count = layer.GetFeatureCount()
# 注意此处不宜使用For循环直接遍历
# 如果要用，属性过滤器是不起作用的
# 还需要在循环内部进行If判断
# for i in range(0, feature_count): 
#     temp_feature = layer.GetFeature(i)
#     temp_field_pac = temp_feature.GetField('PAC')
#     if temp_field_pac/10000 != 32:
#         continue
layer.ResetReading()
feature_list = [] #暂存过滤后的Feature数据
temp_feature = layer.GetNextFeature()
while temp_feature:
    temp_geom = temp_feature.GetGeometryRef()
    temp_field_area = temp_feature.GetField('Shape_Area')
    temp_field_name = temp_feature.GetField('NAME')
    temp_calculatet_area = temp_geom.Area()
    print('Name:', temp_field_name,
          'Area:', temp_field_area, 
          'Cal_Area:', temp_calculatet_area)
    feature_list.append(temp_feature)
    temp_feature = layer.GetNextFeature()


'''
将过滤后的Feature保存到新的文件中
'''
gdal.SetConfigOption("SHAPE_ENCODING", "UTF-8") # IMPORTANT
new_shape_path = 'E:/派森/期末/T3/shanghai_崇明县.shp'

driverName = "ESRI Shapefile"
driver = ogr.GetDriverByName(driverName)
ds = driver.CreateDataSource(new_shape_path) #创建DataSource

geomType = ogr.wkbPolygon #指定几何类型
#创建图层，注意srs借用的是原来的
poLayer = ds.CreateLayer('shanghai_崇明县', srs, geomType)

#对原始数据的属性字段进行遍历
for iField in range(0, field_count):
    temp_field = layer_defn.GetFieldDefn(iField)
    poLayer.CreateField(temp_field, 1)
    
#创建完所有的属性字段之后，获取整个图层的定义
new_layerdef = poLayer.GetLayerDefn()

for iF in range(0, feature_count):
    temp_old_feature = feature_list[iF]
    temp_geom = temp_old_feature.GetGeometryRef()
    
    tempNewFeature = ogr.Feature(new_layerdef)
    tempNewFeature.SetGeometry(temp_geom)
    for temp_name in filed_name_list:
        tempNewFeature.SetField(temp_name,temp_old_feature.GetField(temp_name))

    poLayer.CreateFeature(tempNewFeature)
    del tempNewFeature

ds.FlushCache()
if ds != None: ds.Destroy()


'''
将过滤后的Feature保存到新的文件中, 并且做投影转换
'''
new_shape_path = "E:\派森\期末\T3\shanghai_wgs84_崇明县.shp"

driverName = "ESRI Shapefile"
driver = ogr.GetDriverByName(driverName)
ds = driver.CreateDataSource(new_shape_path)

geomType = ogr.wkbPolygon
srs_4326 = osr.SpatialReference(osr.SRS_WKT_WGS84_LAT_LONG) # 指定新的空间参考
srs_4326.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER) # 按照传统先X后Y的顺序进行坐标转换
#注意此处，指定了options=["ENCODING=UTF-8"], 会生成了以 *.cpg的文件, 里面给出了文字编码
layerjs_4326 = ds.CreateLayer('sh_崇明县', srs_4326, geomType, options=["ENCODING=UTF-8"])

#选用了某几个属性字段放到新的Shapefile中
field1 = ogr.FieldDefn("PAC", ogr.OFTInteger64)
layerjs_4326.CreateField(field1, 1)
field1.Destroy()

field2 = ogr.FieldDefn("NAME", ogr.OFTString)
layerjs_4326.CreateField(field2, 1)
field2.Destroy()

field3 = ogr.FieldDefn("AREA", ogr.OFTReal)
layerjs_4326.CreateField(field3, 1)
field3.Destroy()

#获取新数据的图层属性
layerjs_def = layerjs_4326.GetLayerDefn()

#根据原始坐标参考和新的坐标参考，构建一个投影转换器
trans = osr.CoordinateTransformation(srs, srs_4326)

for iF in range(0, feature_count):
    temp_feature = feature_list[iF]

    temp_geom = temp_feature.GetGeometryRef() # 拿到Feature的Geometry对象
    temp_geom_type = temp_geom.GetGeometryType() # 拿到Geometry的几何类型
    temp_geom_count = temp_geom.GetGeometryCount() # 有可能是Multi-Polygon
    
    temp_new_polygon = None
    if temp_geom_type == ogr.wkbMultiPolygon and temp_geom_count>1:
        print("geometry name:", temp_geom.GetGeometryName())
        #print(temp_geom.GetGeometryName())
        temp_new_polygon = ogr.Geometry(ogr.wkbMultiPolygon)
        for iGeo in range(0, temp_geom_count):
            temp_part = temp_geom.GetGeometryRef(iGeo) # 获取Multi中的每一个Part
            temp_part_ring_count = temp_part.GetGeometryCount() # 每个Polygon可能会有ExRing和InRing
            #print("polygon's ring count:", temp_part_ring_count)
            
            temp_new_part = ogr.Geometry(ogr.wkbPolygon)
            for iRing in range(0, temp_part_ring_count):
                temp_ring = temp_part.GetGeometryRef(iRing)

                temp_new_ring = ogr.Geometry(ogr.wkbLinearRing)
                
                # 第一种写法
                temp_ring_point_count = temp_ring.GetPointCount()
                for iP in range(0, temp_ring_point_count):
                    temp_point = temp_ring.GetPoint(iP)
                    new_p = trans.TransformPoint(temp_point[0], temp_point[1])
                    #print(new_p)
                    temp_new_ring.AddPoint(new_p[0], new_p[1])
                temp_new_part.AddGeometry(temp_new_ring)
            
            temp_new_polygon.AddGeometry(temp_new_part)
    else:
        print("geometry name:", temp_geom.GetGeometryName())
        temp_new_polygon = ogr.Geometry(ogr.wkbPolygon)

        temp_ring_count = temp_geom.GetGeometryCount() # Polygon有可能带岛
        #print("polygon's ring count:", temp_ring_count)
        for iRing in range(0, temp_ring_count):
            temp_ring = temp_geom.GetGeometryRef(iRing) # 遍历每一个Ring，默认第一个是外环
            
            # 第二种写法
            # new_points = trans.TransformPoints(temp_ring.GetPoints())
            # print(new_points)

            # 第三种写法
            import pyproj
            source_proj = pyproj.Proj(srs.ExportToProj4())
            target_proj = pyproj.Proj(4326)
            prjtrans = pyproj.Transformer.from_proj(source_proj, target_proj)
            # 注意以上四行应该写到循环外面
            temp_ring_point_count = temp_ring.GetPointCount()
            new_points = []
            for iP in range(0, temp_ring_point_count):
                temp_point = temp_ring.GetPoint(iP)
                new_p = prjtrans.transform(temp_point[0], temp_point[1])
                #print(new_p) #注意，转出来的经纬度是反的
                new_points.append((new_p[1], new_p[0]))

            temp_new_ring = ogr.Geometry(ogr.wkbLinearRing)
            for new_p in new_points:
                temp_new_ring.AddPoint(new_p[0], new_p[1])
            temp_new_polygon.AddGeometry(temp_new_ring)
    # end if-else geometry type

    if temp_new_polygon != None:
        tempNewFeature = ogr.Feature(layerjs_def)
        tempNewFeature.SetGeometry(temp_new_polygon)
        tempNewFeature.SetField("PAC",temp_feature.GetField("PAC"))
        tempNewFeature.SetField("NAME",temp_feature.GetField("NAME"))
        tempNewFeature.SetField("AREA",temp_feature.GetField("AREA"))

        layerjs_4326.CreateFeature(tempNewFeature)
        tempNewFeature.Destroy()

ds.FlushCache()
if ds != None: ds.Destroy()

