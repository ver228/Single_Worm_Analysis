# -*- coding: utf-8 -*-
"""
Created on Fri Oct 23 02:42:19 2015

@author: ajaver
"""

import pandas as pd
import matplotlib.pylab as plt
import csv
import numpy as np
from scipy.signal import savgol_filter

#filename = '/Users/ajaver/Desktop/SingleWormData/Results/03-03-11/247 JU438 swimming_2011_03_03__11_37___3___2_trajectories.hdf5'
filename = '/Users/ajaver/Desktop/Videos/SingleWormData/Results/03-03-11/764 ED3049 on food L_2011_03_03__15_44___3___7_trajectories.hdf5' 
motor_log = '/Users/ajaver/Desktop/Videos/SingleWormData/Worm_Videos/03-03-11/764 ED3049 on food L_2011_03_03__15_44___3___7.log.csv'


#%% WORM DATA FROM TRAJECTORIES FILE
fps = 30
with pd.HDFStore(filename, 'r') as fid:
    traj_data = fid['/plate_worms']
    
    valid_index = traj_data['worm_index_joined'].value_counts().argmax()
    traj_data = traj_data[traj_data['worm_index_joined']==valid_index]
    
    #change this to deal with missing numbers
    worm_x = traj_data['coord_x'].values
    worm_y = traj_data['coord_y'].values
    worm_time = traj_data['frame_number'].values/fps

#%% READ MOTOR DATA FROM CSV
with open(motor_log) as fid:
    reader = csv.reader(fid)
    data = []
    for line in reader:
        data.append(line)
header = data.pop(0)

motor_data = {}
for col in header:
    motor_data[col] = []
for line in data:
    for ii, col in enumerate(header):
        motor_data[col].append(line[ii])
        
ff = 'Centroid/Stage/Speed X (microns[/second])'
motor_x = np.array([float(d) for d in motor_data[ff]])
ff = 'Centroid/Stage/Speed Y (microns[/second])'
motor_y = np.array([float(d) for d in motor_data[ff]])

motor_time = []
for timestr in motor_data['Media Time']:
    time_parts = [float(x) for x in timestr.split(':')]
    time = sum((60**ii)*part for ii,part in enumerate(time_parts))
    
    motor_time.append(time)
motor_time = np.array(motor_time)
#%%

motor_time_frames = np.round(motor_time*30);
motor_time_frames = np.round(motor_time*30);


#%%

plt.figure()
plt.plot(worm_time[:1000], worm_x[:1000])

plt.xlabel('Seconds')
plt.ylabel('Worm position')



plt.figure()
good = motor_time<=35
plt.plot(motor_time[good], motor_x[good], '-o')

plt.xlabel('Seconds')
plt.ylabel('Stage position')

#%%
plt.figure()
xx = worm_x#savgol_filter(worm_x,3,2)
delta = 3
dx = xx[delta:] - xx[:-delta]
dt = worm_time[delta:] - worm_time[:-delta]
speed_x = dx/dt
speed_x = np.hstack((0, speed_x))

plt.plot(worm_time[:1000], speed_x[:1000], label = 'worm speed')


dx = np.diff(motor_x)
dt = np.diff(motor_time)
m_speed = dx/dt
m_speed = np.hstack((0, m_speed))

good = motor_time<=35
plt.plot(motor_time[good], m_speed[good], '-o')
#%%
plt.figure()
plt.plot(speed_x[:1000], label = 'worm speed')