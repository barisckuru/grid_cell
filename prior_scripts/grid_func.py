#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 22:25:59 2020

@author: bariskuru
"""


import time
import os 
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import skewnorm



def grid_maker(spacing, orientation, pos_peak, arr_size, sizexy, max_rate):
     # shiftxy for np.roll seems unnecessary
#    plt.close('all')
    
    #define the params from input here, scale the resulting array for maxrate and sperate the xy for size and shift
    
    arr_size = arr_size
    x, y = pos_peak
    pos_peak = np.array([x,y])
    max_rate = max_rate
    lambda_spacing = spacing*(arr_size/100) #100 required for conversion, they have probably used 100*100 matrix in 
    k = (4*np.pi)/(lambda_spacing*np.sqrt(3))
    degrees = orientation
    theta = np.pi*(degrees/180)
    meterx, metery = sizexy
    arrx = meterx*arr_size # *arr_size for defining the 2d array size
    arry = metery*arr_size
    
#    shiftx, shifty = shiftxy
    
    dims = np.array([arrx,arry])
    arr = np.ones(dims)
    
    
    k1 = ((k/np.sqrt(2))*np.array((np.cos(theta+(np.pi)/12) + np.sin(theta+(np.pi)/12),
          np.cos(theta+(np.pi)/12) - np.sin(theta+(np.pi)/12)))).reshape(2,)
    k2 = ((k/np.sqrt(2))*np.array((np.cos(theta+(5*np.pi)/12) + np.sin(theta+(5*np.pi)/12),
          np.cos(theta+(5*np.pi)/12) - np.sin(theta+(5*np.pi)/12)))).reshape(2,)
    k3 = ((k/np.sqrt(2))*np.array((np.cos(theta+(9*np.pi)/12) + np.sin(theta+(9*np.pi)/12),
          np.cos(theta+(9*np.pi)/12) - np.sin(theta+(9*np.pi)/12)))).reshape(2,)
    #.reshape is only need when function is in the loop(shape somehow becomes (2,1) otherwise normal shape is already (2,)
    
    for i in range(dims[0]):
        for j in range(dims[1]):
            curr_pos = np.array([i,j]-pos_peak)
            arr[i,j] = (np.cos(np.dot(k1, curr_pos))+
               np.cos(np.dot(k2, curr_pos))+ np.cos(np.dot(k3, curr_pos)))/3
    arr = max_rate*2/3*(arr+1/2)         
#    arr = (np.roll(arr, [shiftx, shifty], axis=(0,1)))       

    return arr



#arr = grid_maker(73, 0, [200,700],[1,1], 20)
#arr2 = grid_maker(44, 10, [490,490],[0,0],[1,1], 20)
#arr3 = grid_maker(55, 20, [510,510],[0,0],[1,1], 20)
#arr4 = grid_maker(73, 30, [520,480],[0,0],[1,1], 20)
#sum_arr = (arr+arr2+arr3+arr4)/4

start = time.time()
arr_size = 200
num_grids = 100

# grid_spc = np.random.randint(spacing_low, high=spacing_high, size=[num_grids,1]) # spacing_low = 28 #uniform dist
# skewed normal distribution for grid_spc
median_spc = 43
spc_max = 100
max_value = spc_max - 24 #24 is the apprx (median - np.median(random)) before locating median of dist 
skewness = 6  #Negative values are left skewed, positive values are right skewed.
grid_spc = skewnorm.rvs(a = skewness,loc=spc_max, size=num_grids)  #Skewnorm function
grid_spc = grid_spc - min(grid_spc)      #Shift the set so the minimum value is equal to zero.
grid_spc = grid_spc / max(grid_spc)      #Standadize all the vlues between 0 and 1. 
grid_spc = grid_spc * spc_max         #Multiply the standardized values by the maximum value.
grid_spc = grid_spc + (median_spc - np.median(grid_spc))

grid_ori = np.random.randint(0, high=60, size=[num_grids,1]) #uniform dist btw 0-60 degrees
grid_phase = np.random.randint(0, high=(arr_size-1), size=[num_grids,2]) #uniform dist grid phase
all_grids = np.zeros((arr_size, arr_size, num_grids))

for i in range(num_grids):
    x = grid_phase[i][0]
    y = grid_phase[i][1]
    arr = grid_maker(grid_spc[i], grid_ori[i], [x, y], arr_size, [1,1], 20)
    all_grids[:, :, i] = arr

stop = time.time()
time_min = (stop-start)/60
print(time_min)
print(stop-start)
mean_grid = np.mean(all_grids, axis=2)

count = 2
np.savez(os.path.join('/Users/bariskuru/Desktop/MasterThesis/grids', 
                      str(num_grids)+'_grids_'+str(arr_size)+'_arrsize_'+str(median_spc)+'_median_spc_'+str(count)), 
         all_grids=all_grids, 
         mean_grid=mean_grid, 
         grid_spc=grid_spc, 
         grid_ori=grid_ori, 
         grid_phase=grid_phase,
         count = count)

#plt.figure()
#plt.imshow(mean_grid, cmap='jet')
#plt.colorbar()
#plt.figure()
#plt.imshow(arr, cmap='jet')