# -*- coding: utf-8 -*-
"""
Created on Mon Jun 27 23:30:02 2022

@author: Hello
"""
import gdal
import matplotlib.pyplot as plt
import numpy as np
def slope_x_y(grid,xcellsize,ycellsize):
    ycount=grid.shape[0]
    xcount=grid.shape[1]
    dx=1.0/(xcellsize*2)
    dy=1.0/(ycellsize*2)
    
    slopex=np.zeros(grid.shape,dtype=np.float64)
    slopey=np.zeros(grid.shape,dtype=np.float64)
    for iy in range(1,ycount-1):
        for ix in range(1,xcount-1):
            slopex[iy,ix]=(grid[iy,ix+1]-grid[iy,ix-1])*dx
            slopey[iy,ix]=(grid[iy+1,ix]-grid[iy-1,ix])*dy
    slopex[:,0]=slopex[:,1]
    slopex[:,-1]=slopex[:,-2]
    slopey[0,:] = slopey[1,:]
    slopey[-1,:]=slopey[-2,:]
    return slopex,slopey     

                    
demDS=gdal.Open("E:\派森\期末\T4\clip1.tifa.tif")
gt=(118.2, 0.00027777777777778173, 0.0, 32.1, 0.0, -0.00027777777777778173)
xcellsize=gt[1]
ycellsize=gt[5]
grid=demDS.ReadAsArray(0,0).astype(np.float64)
slopex,slopey=slope_x_y(grid,xcellsize,ycellsize)
slope=np.sqrt(slopex*slopex+slopey*slopey)
slope=np.arctan(slope)*180/np.pi
aspect=np.arctan2(slopex,slopey)*180/np.pi

ax,fig=plt.subplots()

plt.title('slope*aspect')
#plt.xticks([])
plt.contour(grid)
plt.colorbar()


plt.imshow(slope*aspect,cmap='gray')
plt.savefig("E:\派森\期末\T4/as.png")

from PIL import Image
img=Image.open("E:\派森\期末\T4/as.png")
png=Image.open("E:\派森\期末\T4/flag-x.png")
png=png.resize((80,52),Image.ANTIALIAS)
r,g,b,a=png.split()
png_x=img.width-png.width-20000
png_y=img.width-png.height-700
img.paste(png,(png_x,png_y),mask=a)

