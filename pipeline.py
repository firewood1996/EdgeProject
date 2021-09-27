#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Aug 1 20:09:19 2021
Last updated on Sept 13, 2021
@author: Sophie 

#Pipeline for processing DEBS 2015 data to create input for EdgeCloudSim (Sections A-E)
as well as produce plots (Section F)
"""
import pandas as pd

#--------------------------------------------------------
#--------------------------------------------------------
# SET THIS BEFORE RUNNING THE CODE:
output_folder='abs_path_to_output_folder' #all sections 
file_original='abs_path_to_DEBS2015_dataset' #secion B
#--------------------------------------------------------
#--------------------------------------------------------
#%% -------SECTION A----------------------------
#Create a 1kmx1km grid 
#DEBS 2015: start at init_lat and init_long and expand the grid 150 km south and 150 km west

import geopy.distance
init_lat=41.474937
init_long=-74.913585

outer_lat=0
outer_long=0


grid=''
grid='grid_latitude,grid_longitude\n'
grid+=str(init_lat) +','+str(init_long)+'\n'

for i_south in range(1, 151):
    for i_east in range(1, 150):
        if outer_lat==0 and outer_long==0:
            outer_lat=init_lat
            outer_long=init_long
        a=geopy.distance.distance(kilometers=1).destination((init_lat, init_long), bearing=90)
        grid+=str(a.latitude) +','+str(a.longitude)+'\n'
        init_lat=a.latitude
        init_long=a.longitude
    b=geopy.distance.distance(kilometers=1).destination((outer_lat, outer_long), bearing=180)
    if i_south!=150:   
        grid+=str(b.latitude) +','+str(b.longitude)+'\n'
    outer_lat=0 
    outer_long=0
    init_lat=b.latitude
    init_long=b.longitude


file_grid=output_folder+'1_km_grid.csv'
file_p = open(file_grid, 'w')
file_p.writelines(grid)
file_p.close()
grid=pd.read_csv(file_grid)


#%% -------SECTION B----------------------------
#Read in 5K data samples from the DEBS2015
#Note: file_original must be pre-defined

file_p1 = open(file_original, 'r')
count = 0
line_write='';

file_extractN_minutes=output_folder+'extract.csv'
file_p2 = open(file_extractN_minutes, 'w')
columns_names='medallion,hack_license,pickup_datetime,dropoff_datetime, trip_time_in_secs,'+\
    'trip_distance,pickup_longitude,pickup_latitude,dropoff_longitude,dropoff_latitude,'+\
        'payment_type,fare_amount,surcharge,mta_tax,tip_amount,tolls_amount,total_amount\n'
file_p2.writelines(columns_names)


while True:
    line = file_p1.readline()
    file_p2.writelines(line)

    if count==5000:
        break
    line_write='';
    count += 1
 
    
file_p1.close() 
file_p2.close()
df = pd.read_csv(file_extractN_minutes)


#%%#%% -------SECTION C----------------------------
import geopy.distance
grid_step=1  #define it in km
grid_inside=1.1*grid_step/2  #0.1 margin

grid_id = pd.Series([])
grid_id_dropOFF = pd.Series([])
test=pd.Series([])

#init 
for ind in df.index:
    grid_id[ind]=''
    grid_id_dropOFF[ind]=''

for ind in df.index:
    coords_1 = (df['pickup_latitude'][ind], df['pickup_longitude'][ind]) #latitude, longitude of the PIC UP location
    coords_3 = (df['dropoff_latitude'][ind], df['dropoff_longitude'][ind]) #latitude, longitude of the PIC UP location

    if df['pickup_latitude'][ind]!=0.0 and df['pickup_longitude'][ind]!=0.0 and df['dropoff_latitude'][ind]!=0.0 and df['dropoff_longitude'][ind]!=0.0:
        
        for inner_ind in range(grid.index.start, grid.index.stop):
        
            coords_2 = (grid['grid_latitude'][inner_ind], grid['grid_longitude'][inner_ind]) #traverse the points in the grid
            distance=geopy.distance.distance(coords_1, coords_2).km
            
            if distance <=grid_inside:
                grid_id[ind]+=str(inner_ind)+','
                
            distance=geopy.distance.distance(coords_2, coords_3).km
                
            if distance <=grid_inside:
                grid_id_dropOFF[ind]+=str(inner_ind)+','    

df['pickup_grid_id'] = grid_id
df['dropoff_grid_id'] = grid_id_dropOFF
df_updated=output_folder+'excerpt_1kmGridID.csv'
df.to_csv(df_updated)


#%% -------SECTION D----------------------------
#drop rows that are missing either pick-up and/or drop-off grid IDs 
import math
df_copy = pd.Series([])
df_copy=df

for ind in df.index:
    if df['pickup_grid_id'][ind]=='' or df['dropoff_grid_id'][ind]=='':
        df_copy=df_copy.drop([ind])
        
df_copy = df_copy.reset_index() #reset the index after the drops

pickup_X = pd.Series([])
pickup_Y = pd.Series([])
dropoff_X = pd.Series([])
dropoff_Y = pd.Series([])

for ind in df_copy.index:
    pickup_X[ind]=int(df_copy['pickup_grid_id'][ind].split(',')[0])%150 #remainder
    pickup_Y[ind]=math.floor(int(df_copy['pickup_grid_id'][ind].split(',')[0])/150) #div
    dropoff_X[ind]=int(df_copy['dropoff_grid_id'][ind].split(',')[0])%150 #remainder
    dropoff_Y[ind]=math.floor(int(df_copy['dropoff_grid_id'][ind].split(',')[0])/150) #div

df_copy['pickup_X']=pickup_X
df_copy['pickup_Y']=pickup_Y
df_copy['dropoff_X']=dropoff_X
df_copy['dropoff_Y']=dropoff_Y

file_2=output_folder+'extract_XY.csv'
df_copy.to_csv(file_2)

#%% -------SECTION E----------------------------
# Repeat() is from https://www.geeksforgeeks.org/python-program-print-duplicates-list-integers/
def Repeat(x):
    _size = len(x)
    repeated = []
    for i in range(_size):
        k = i + 1
        for j in range(k, _size):
            if x[i] == x[j] and x[i] not in repeated:
                repeated.append(x[i]) #returns the item

    return repeated

hack_repeat= (Repeat(df_copy['hack_license'])) #repeating taxi tags

path=[] 
for index in hack_repeat:
    path.append('')
count=0

for hack_item in hack_repeat:
    for index in range (df_copy.index.start, df_copy.index.stop):
        if hack_item==df_copy['hack_license'][index]:
            path[count]+=df_copy['pickup_datetime'][index]+','+df_copy['dropoff_datetime'][index]+ ','+str(df_copy['pickup_X'][index])+','+str(df_copy['pickup_Y'][index])+ ','+str(df_copy['dropoff_X'][index])+','+str(df_copy['dropoff_Y'][index])+';'
    count+=1    


#%%-------SECTION E----------------------------
import numpy as np
number_minutes=26 #for on the 5K data sample
timeline=np.linspace(0, number_minutes*60, num=number_minutes*10, endpoint=False)                 
a=np.zeros(( len(timeline), df_copy.shape[0]*2))    #initialize "a"

x_index=0
y_index=1
hack_done = [] 

for index in range (df_copy.index.start, df_copy.index.stop):
        
    #check if there is a match in the taxi tag:
        if df_copy['hack_license'][index] not in hack_repeat: 
            time1=pd.Timestamp(df_copy['pickup_datetime'][index].split(",")[0]).minute*60+pd.Timestamp(df_copy['pickup_datetime'][index].split(",")[0]).second
            time2=pd.Timestamp(df_copy['dropoff_datetime'][index].split(",")[0]).minute*60+pd.Timestamp(df_copy['dropoff_datetime'][index].split(",")[0]).second
            j=0
            while j<len(timeline):
                if timeline[j]<time1: 
                    a[j][x_index]=(df_copy['pickup_X'][index])
                    a[j][y_index]=(df_copy['pickup_Y'][index])
                    j+=1
                    continue
                if timeline[j]>time2: 
                    a[j][x_index]=(df_copy['dropoff_X'][index])
                    a[j][y_index]=(df_copy['dropoff_Y'][index])
                    j+=1
                    continue
                if timeline[j]<=time2 and  timeline[j]>=time1: 
                    x1=(df_copy['pickup_X'][index])
                    y1=(df_copy['pickup_Y'][index])
                    x2=(df_copy['dropoff_X'][index])
                    y2=(df_copy['dropoff_Y'][index])
                    xx= np.around(np.linspace(x1, x2, num=int((time2-time1)/6+1), endpoint=True))
                    yy= np.around(np.linspace(y1, y2, num=int((time2-time1)/6+1), endpoint=True))
                    
                    if time2>timeline[-1]-5 and  j+int((time2-time1)/6+1)>timeline.shape[0]:
                        delta=j+int((time2-time1)/6+1)-timeline.shape[0]
                        xx=xx[:-delta]
                        yy=yy[:-delta]
                        a[j:j+int((time2-time1)/6+1),x_index:x_index+1]=np.reshape(xx, (len(xx),1))
                        a[j:j+int((time2-time1)/6+1),y_index:y_index+1]=np.reshape(yy, (len(yy),1))
                    else:
                        a[j:j+int((time2-time1)/6+1),x_index:x_index+1]=np.reshape(xx, (len(xx),1))
                        a[j:j+int((time2-time1)/6+1),y_index:y_index+1]=np.reshape(yy, (len(yy),1))
                    j+=int((time2-time1)/6+1)
                    continue

        if df_copy['hack_license'][index] in hack_repeat and df_copy['hack_license'][index] not in hack_done: 
            hack_done.append(df_copy['hack_license'][index]) 
            
            test=path[hack_repeat.index(df_copy['hack_license'][index])]
            t1_1=test.split(';')[0].split(",")[0]
            time1=pd.Timestamp(t1_1).second+pd.Timestamp(t1_1).minute*60+pd.Timestamp(t1_1).hour*3660
            t1_2=test.split(';')[0].split(",")[1]
            time2=pd.Timestamp(t1_2).second+pd.Timestamp(t1_2).minute*60+pd.Timestamp(t1_2).hour*3660
            x1=test.split(';')[0].split(",")[2]
            y1=test.split(';')[0].split(",")[3]
            x2=test.split(';')[0].split(",")[4]
            y2=test.split(';')[0].split(",")[5]
            
        
            t1_1=test.split(';')[1].split(",")[0]
            time3=pd.Timestamp(t1_1).second+pd.Timestamp(t1_1).minute*60+pd.Timestamp(t1_1).hour*3660
            t1_2=test.split(';')[1].split(",")[1]
            time4=pd.Timestamp(t1_2).second+pd.Timestamp(t1_2).minute*60+pd.Timestamp(t1_2).hour*3660
            x3=test.split(';')[1].split(",")[2]
            y3=test.split(';')[1].split(",")[3]
            x4=test.split(';')[1].split(",")[4]
            y4=test.split(';')[1].split(",")[5] 
            
            j=0
            while j<len(timeline):
          
                if timeline[j]<time1: 
                    a[j][x_index]=x1
                    a[j][y_index]=y1
                    j+=1
                    continue
                if timeline[j]>time4: 
                    a[j][x_index]=x4
                    a[j][y_index]=y4
                    j+=1
                    continue
                if timeline[j]<=time2 and  timeline[j]>=time1: 
                    if index==3: 
                        print(3)
                    xx= np.around(np.linspace(int(x1), int(x2), num=int((time2-time1)/6+1), endpoint=True))
                    yy= np.around(np.linspace(int(y1), int(y2), num=int((time2-time1)/6+1), endpoint=True))
                    a[j:j+int((time2-time1)/6+1),x_index:x_index+1]=np.reshape(xx, (len(xx),1))
                    a[j:j+int((time2-time1)/6+1),y_index:y_index+1]=np.reshape(yy, (len(yy),1))            
                    j+=int((time2-time1)/6+1)
                    continue

                if timeline[j]<=time4 and  timeline[j]>=time3: 
                    xx= np.around(np.linspace(int(x3),int(x4), num=int((time4-time3)/6+1), endpoint=True))
                    yy= np.around(np.linspace(int(y3), int(y4), num=int((time4-time3)/6+1), endpoint=True))
                    
                    if time4>timeline[-1]-5 and  j+int((time4-time3)/6+1)>timeline.shape[0]:
                        delta=j+int((time4-time3)/6+1)-timeline.shape[0]
                        xx=xx[:-delta]
                        yy=yy[:-delta]
                        a[j:j+int((time4-time3)/6+1),x_index:x_index+1]=np.reshape(xx, (len(xx),1))
                        a[j:j+int((time4-time3)/6+1),y_index:y_index+1]=np.reshape(yy, (len(yy),1))
                    else:
                        a[j:j+int((time4-time3)/6+1),x_index:x_index+1]=np.reshape(xx, (len(xx),1))
                        a[j:j+int((time4-time3)/6+1),y_index:y_index+1]=np.reshape(yy, (len(yy),1))
                    j+=int((time4-time3)/6+1)
                    continue

                if timeline[j]<=time3 and  timeline[j]>=time2: 
                    xx=np.around (np.linspace(int(x2), int(x3), num=int((time3-time2)/6+1), endpoint=True))
                    yy= np.around(np.linspace(int(y2), int(y3), num=int((time3-time2)/6+1), endpoint=True))
                    a[j:j+int((time3-time2)/6+1),x_index:x_index+1]=np.reshape(xx, (len(xx),1))
                    a[j:j+int((time3-time2)/6+1),y_index:y_index+1]=np.reshape(yy, (len(yy),1))
                    j+=int((time3-time2)/6+1)
                    continue


        x_index+=2
        y_index+=2
        

ex = pd.DataFrame(a)
ex=ex.astype(int)    #cast to int   
ex = ex.loc[:, (ex != 0).any(axis=0)]
#drop the 0 columns
ex_copy=ex
for ii in range(1, 6866):
    if ex.iloc[:, ii].min()==0:
        ex_copy=ex_copy.drop(ii, axis = 1)
ex=ex_copy 

file_latest=output_folder+'spatial_seriesEdgeCLoudSimInput_REF2.csv' #to be inputted into the simulation
ex.to_csv(file_latest, index_label=None, header=False, columns=None, index=False)

        
#%%-------SECTION F----------------------------
#Statistics for x,y positions/plotting
import matplotlib.pyplot as plt
import time

X_min=min( df_copy["dropoff_X"].min(), df_copy["pickup_X"].min() )
X_max=max(df_copy["dropoff_X"].max() ,  df_copy["pickup_X"].max() )
Y_min=min( df_copy["dropoff_Y"].min(), df_copy["pickup_Y"].min() )
Y_max=max(df_copy["dropoff_Y"].max() ,  df_copy["pickup_Y"].max() )
print('x belongs to [' + str( X_min) + ',' + str(X_max) +  '] y belongs to [' + str(Y_min)+ ','+ str(Y_max)+  ']')
#x belongs to [66,96]; y belongs to [65,95]
listA=[]
for x in range(66, 97):
    for y in range(65,96):
        listA.append(str(x)+','+str(y))

plotting = pd.DataFrame(columns = listA)
plotting['time']=timeline
plotting=plotting.fillna(0)

for row in range(0,  ex.shape[0]):
    # time. sleep(2)
    x_index=0
    y_index=1
    for column in range(0,  int(ex.shape[1]/2)-2) :
        x=ex.iloc[row,x_index]
        y=ex.iloc[row,y_index]
        temp=plotting[str(x)+","+str(y)][row]+1
        plotting[str(x)+","+str(y)][row]=temp
        x_index+=2
        y_index+=2

file_plot=output_folder+'plotting.csv'
plotting.to_csv(file_plot)



#check the values of devices across one row (except for the last column which refrects the timeline)
#these should be consistent
# plotting.iloc[0,:-1].sum() = 3431.0, thus  device count is 3431
for row in range(0,  plotting.shape[0]):
    if plotting.iloc[row,:-1].sum()!=plotting.iloc[0,:-1].sum():
        print(plotting.iloc[row,:-1].sum())


#plot
fig, ax = plt.subplots()
#edge nodes:
edgeX=[66,81,96,66,81,96,66,81,96]
edgeY=[65,65,65	,80	,80	,80	,95,95,95]


num_dev=int(plotting.iloc[0,:-1].sum())
for row in range(0,  ex.shape[0]):
    plt.close() #close the previous figure
    fig, ax = plt.subplots()
    fig.set_size_inches(8, 6)

    for j in range (0, len(listA) ):
        if plotting[listA[j]][row]!=0:
            x=int(listA[j].split(',')[0])
            y=int(listA[j].split(',')[1])
            plt.scatter(x, y, color='c')
            ax.annotate(plotting[listA[j]][row], xy=(x, y), fontsize=6)

    plt.ylabel('Y')
    plt.xlabel('X')
    plt.title(str(num_dev)+' devices @ time=' + str(plotting['time'][row]) + ' sec.')
    plt.scatter(edgeX, edgeY, color='r')
    
    ax.text(67, 90, "Devices", bbox=dict(facecolor='cyan', alpha=0.5))
    ax.text(67, 92.5, "Edge Nodes", bbox=dict(facecolor='red', alpha=0.5))

    
    plt.grid(True)
    plt.show()

    fig_name='/Users/sophie/Desktop/project/Sept7/Plot/'+str(row)
    plt.savefig(fig_name, dpi=150) #high resolution images
    time. sleep(0.5)

