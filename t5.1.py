# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 01:51:47 2022

@author: Hello
"""
import numpy as np
import matplotlib.pyplot as plt
fig,ax=plt.subplots()
index=np.arange(8)
width=0.4
data11=(21, 34, 8, 11, 7, 19, 46, 56)
color='c'
label='power'
ax.plot=(index,data11,width,color,label)
ax.set_xticks(index+width/2)
labels=('七级','八级','九级','十级','十一级','十二级','十三级','十四级')
ax.set_xticklabels(labels)
ax.legend()
plt.show()
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
color='c'
label='power'
ax.bar=(index,data11,width,color,label)
ax.set_xticks(index+width/2)
labels=('七级','八级','九级','十级','十一级','十二级','十三级','十四级')
#ax.set_xticklabels(labels)
#ax.legend()
plt.show()