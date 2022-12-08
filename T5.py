# -*- coding: utf-8 -*-
"""
Created on Sun Jun 26 16:56:55 2022

@author: Hello
"""
import csv
import urllib.request as request
import json
# cartopy：用来获取地图
import cartopy.crs as ccrs
import cartopy.feature as cfeature
# matplotlib：用来绘制图表
import matplotlib.pyplot as plt
# shapely：用来处理点线数据
import shapely.geometry as sgeom
import warnings
#import re
import numpy as np
import pandas as pd
warnings.filterwarnings('ignore')
plt.rcParams['font.sans-serif'] = [u'SimHei']
plt.rcParams['axes.unicode_minus'] = False
# 通过cartopy获取底图
fig = plt.figure(figsize=(10,10))
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

# 用经纬度对地图区域进行截取，这里只展示我国沿海区域
ax.set_extent([85,170,-20,60], crs=ccrs.PlateCarree())

# 设置名称
ax.set_title('2021年台风路径图',fontsize=16)

# 设置地图属性，比如加载河流、海洋
ax.add_feature(cfeature.LAND)
ax.add_feature(cfeature.OCEAN)
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.RIVERS)
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.LAKES, alpha=0.5)

# 展示地图
plt.show()
#获取数据的网站在此：
#https://typhoon.slt.zj.gov.cn/default.aspx

# 获取一年的台风列表
url='https://typhoon.slt.zj.gov.cn/Api/TyphoonList/2021?callback=jQuery18307669471823366587_1654483413702&_=1654483442956'
list_info = request.urlopen(url).read().decode('utf-8')

# 处理网络请求得到的字符串
list_info = list_info[list_info.find('['):]
list_info = list_info[:-2]

# 按照JSON进行解析
obj_list = json.loads(list_info)

# 指定一个台风对象，再次请求网络数据
idx = 5
instance_id = obj_list[idx]['tfid']
url_inst='https://typhoon.slt.zj.gov.cn/Api/TyphoonInfo/'+instance_id+'?callback=jQuery18307669471823366587_1654483413702&_=1654483464147'
instance_info = request.urlopen(url_inst).read().decode('utf-8')

# 对单个台风的请求结果进行字符串处理
instance_info = instance_info[instance_info.find('['):]
instance_info = instance_info[:-2]

# 获取单个台风的JSON对象
obj_inst = json.loads(instance_info)

# 获取台风的路径
point_count = len(obj_inst[0]['points'])
x = []
y = []
move_speed=[]
power=[]
level=[]
data=[]
time=[]
data.append(['lon','lat','move_speed','power','level','time'])
for iP in range(0, point_count):
    #这边只取了位置lng,lat信息，json中还有其他信息，如pressure，power，strong，speed等
    temp_lng = obj_inst[0]['points'][iP]['lng'] 
    temp_lat = obj_inst[0]['points'][iP]['lat']
    temp_speed=obj_inst[0]['points'][iP]['movespeed']
    temp_power=obj_inst[0]['points'][iP]['power']
    temp_strong=obj_inst[0]['points'][iP]['strong']
    temp_time=obj_inst[0]['points'][iP]['time']
    x.append(float(temp_lng))
    y.append(float(temp_lat))
    move_speed.append(temp_speed)
    power.append(temp_power)
    level.append(temp_strong)
    time.append(temp_time)
    data.append([float(temp_lng),float(temp_lat),temp_speed,temp_power,temp_strong,temp_time])
    print(float(temp_lng),float(temp_lat)) 
   
    
   
#temp_speed=obj_inst[0]['points'][iP]['movespeed']
#temp_power=obj_inst[0]['points'][iP]['power']
#temp_strong=obj_inst[0]['points'][iP]['strong']



with open('E:\派森\期末\T5\data1.csv', 'w',newline='') as csvfile:
   
    writer  = csv.writer(csvfile)
    for row in data:
       
           writer.writerow(row)

    csvfile.close()

# 直接绘制路径
import matplotlib.pyplot as plt

ax.plot(x, y)


# 使用Shapely，生成LineString对象
from shapely.geometry import *
line = LineString(zip(x, y))

# 生成一个0.2度的缓冲区
from descartes.patch import *
buffer = line.buffer(0.2)
patch = PolygonPatch(buffer, fc='#00FF00')

# 通过cartopy获取底图
fig = plt.figure(figsize=(10,10))
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
ax.add_patch(patch)
# 用经纬度对地图区域进行截取，这里只展示我国沿海区域
ax.set_extent([85,170,-20,60], crs=ccrs.PlateCarree())

# 设置名称
ax.set_title('2021年某台风路径图',fontsize=16)

# 设置地图属性，比如加载河流、海洋
ax.add_feature(cfeature.LAND)
ax.add_feature(cfeature.OCEAN)
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.RIVERS)
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.LAKES, alpha=0.5)
#ax.add_geometries([buffer],ccrs.PlateCarree(),facecolor='#F9009F', edgecolor='none')
#ax.add_geometries([line],ccrs.PlateCarree(),facecolor='none', edgecolor='#9F0000')

plt.show()

#data1=[x,y]

#data=pd.DataFrame(columns='lon',data=x)
import os, glob
import pandas as pd
import numpy as np
import shapely.geometry as sgeom
import matplotlib.pyplot as plt
from matplotlib.image import imread
from matplotlib.animation import FuncAnimation
import matplotlib.lines as mlines
import cartopy.crs as ccrs
import cartopy.feature as cfeat
from cartopy.mpl.ticker import LongitudeFormatter,LatitudeFormatter
import cartopy.io.shapereader as shpreader
import cartopy.io.img_tiles as cimgt
from PIL import Image
import warnings 
warnings.filterwarnings('ignore')
df = pd.read_csv('E:\派森\期末\data1.csv')

def create_map(title, extent):
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
  #  url = 'http://map1c.vis.earthdata.nasa.gov/wmts-geo/wmts.cgi'
  #  layer = 'BlueMarble_ShadedRelief'
   # ax.add_wmts(url, layer)
   # ax.set_extent(extent,crs=ccrs.PlateCarree())
   # 用经纬度对地图区域进行截取，这里只展示我国沿海区域
    ax.set_extent([85,170,-20,60], crs=ccrs.PlateCarree())

# 设置名称
    #ax.set_title('2021年台风路径图',fontsize=16)
    ax.add_feature(cfeature.LAND)
    ax.add_feature(cfeature.OCEAN)
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.RIVERS)
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.LAKES, alpha=0.2)
    #ax.add_geometries([buffer],ccrs.PlateCarree(),facecolor='#F9009F', edgecolor='none')
   #ax.add_geometries([line],ccrs.PlateCarree(),facecolor='none', edgecolor='#9F0000')
    gl = ax.gridlines(draw_labels=False, linewidth=1, color='k', alpha=0.5, linestyle='--')
    gl.xlabels_top = gl.ylabels_right = False  
    ax.set_xticks(np.arange(extent[0], extent[1]+5, 5))
    ax.set_yticks(np.arange(extent[2], extent[3]+5, 5))
    ax.xaxis.set_major_formatter(LongitudeFormatter())
    ax.xaxis.set_minor_locator(plt.MultipleLocator(1))
    ax.yaxis.set_major_formatter(LatitudeFormatter())
    ax.yaxis.set_minor_locator(plt.MultipleLocator(1))
    ax.tick_params(axis='both', labelsize=10, direction='out')

    a = mlines.Line2D([],[],color='#FFFF00',marker='o',markersize=7, label='热带低压',ls='')
    b = mlines.Line2D([],[],color='#6495ED', marker='o',markersize=7, label='热带风暴',ls='')
    c = mlines.Line2D([],[],color='#3CB371', marker='o',markersize=7, label='强热带风暴',ls='')
    d = mlines.Line2D([],[],color='#FFA500', marker='o',markersize=7, label='台风',ls='')
    e = mlines.Line2D([],[],color='#FF00FF', marker='o',markersize=7, label='强台风',ls='')
    f = mlines.Line2D([],[],color='#DC143C', marker='o',markersize=7, label='超强台风',ls='')
    ax.legend(handles=[a,b,c,d,e,f], numpoints=1, handletextpad=0, loc='upper left', shadow=True)
   # plt.title(f'{title} Typhoon Track', fontsize=15)
    plt.title(f'{title}', fontsize=15)
    return ax


def get_color(lever):
    global color
    if level == '热带低压' or level == '热带扰动':
        color='#FFFF00'
    elif level == '热带风暴':
        color='#6495ED'
    elif level == '强热带风暴':
        color='#3CB371'
    elif level == '台风':
        color='#FFA500'
    elif level == '强台风':
        color='#FF00FF'
    elif level == '超强台风':
        color='#DC143C'
        return color

def get_color1(power):
    global color
    if power == 7:
        color='#FFFF00'
    elif power == 8:
        color='#6495ED'
    elif power == 9:
        color='#3CB371'
    elif power == 10:
        color='#FFA500'
    elif power == 11:
        color='#FF00FF'
    elif power == 12:
        color='#DC143C'
    elif power ==13:
        color='#FFFFE0'
    elif power== 14:
        color='#D8BFD8'
    return color
    

def draw_single(df):
    ax = create_map('2021台风路径',extent=[110, 135, 20, 45])
    for i in range(len(df)):
        ax.scatter(list(df['lon'])[i], list(df['lat'])[i], marker='o', s=20, color=get_color(list(df['level'])[i]))

    for i in range(len(df)-1):
        pointA = list(df['lon'])[i],list(df['lat'])[i]
        pointB = list(df['lon'])[i+1],list(df['lat'])[i+1]
        ax.add_geometries([sgeom.LineString([pointA, pointB])], color=get_color(list(df['level'])[i+1]),crs=ccrs.PlateCarree())
    plt.savefig('./typhoon_one.png')
    
    
draw_single(df)

def draw_multi(df):
   z=0
   for state in range(len(df.index))[:]:
        ax = create_map(f'2021台风路径 {df["time"].iloc[state]}', [110, 135, 20, 45])
        for i in range(len(df[:state])):
            z=z+1
            ax.plot(df['lon'].iloc[i], df['lat'].iloc[i], linestyle='-', lw=1,color=get_color1(z))
                    
draw_multi(df)

def draw_single_gif(df):
    for state in range(len(df.index))[:]:
        ax = create_map(f'2021台风路径 {df["time"].iloc[state]}', [110, 135, 20, 45])
        for i in range(len(df[:state])):
            ax.plot(df['lon'].iloc[i], df['lat'].iloc[i], linestyle='-', lw=1,marker='o',color=get_color(df['level'].iloc[i]))
        for i in range(len(df[:state])-1):
            pointA = df['lon'].iloc[i],df['lat'].iloc[i]
            pointB = df['lon'].iloc[i+1],df['lat'].iloc[i+1]
            ax.add_geometries([sgeom.LineString([pointA, pointB])], color=get_color(df['level'].iloc[i+1]),crs=ccrs.PlateCarree())
        print(f'正在绘制第{state}张轨迹图')
        plt.savefig(f'E:\派森\期末\T5/{str(state).zfill(3)}.png', bbox_inches='tight')
    #import matplotlib.pyplot as plt
    import imageio,os
    images = []
    filenames=sorted((fn for fn in os.listdir('.') if fn.endswith('.png')))
    for filename in filenames:
       images.append(imageio.imread(filename))
       imageio.mimsave('E:\派森\期末\T5\gif.gif', images,duration=1)
    #将图片拼接成动画
    imgFiles = list(glob.glob(f'台风.png'))
    images = [Image.open(fn) for fn in imgFiles]
    im = images[0]
    filename = f'台风.gif'
    im.save(fp=filename, format='gif', save_all=True, append_images=images[1:], duration=500)
draw_single_gif(df)



def zhuanti(df):
    #ax = create_map('2021台风路径',extent=[110, 135, 20, 45])
    
    #for i in range(len(df)):
       #ax.plot(list(df['lon'])[i], list(df['lat'])[i],'--',lw=1)


    peight=0
    pnine=0
    pten=0
    peleven=0
    ptwel=0
    pthir=0
    pfort=0
    pseven=0
    
    for item in range(0,len(df)-1):
        z=df['power'].iloc[item]
        if(z==8):
          peight+=1
        if(z==9):
          pnine=pnine+1
        if(z==10):
          pten+=1
        if(z==11):
          peleven+=1
        if(z==12):
          ptwel+=1
        if(z==13):
          pthir+=1
        if(z==14):
          pfort+=1
        if(z==7):
          pseven+=1
    fig,ax=plt.subplots()     

    index=np.arange(8)
    width=0.4
    data11=(pseven,peight,pnine,
    pten,
    peleven,
    ptwel,
    pthir,pfort)
    ax.bar=(index,data11,width)
    ax.set_xticks(index+width/2)
    labels=('七级','八级','九级','十级','十一级','十二级','十三级','十四级')
    ax.set_xticklabels(labels)
    ax.legend()
    plt.show()
    
zhuanti(df)




    