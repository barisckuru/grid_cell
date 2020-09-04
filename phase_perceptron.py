#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  1 12:04:12 2020

@author: bariskuru
"""

import torch
from torch.autograd import Variable
import torch.nn as nn
from torch import optim

import seaborn as sns, numpy as np
import matplotlib.pyplot as plt
from poiss_inp_gen_short_traj import inhom_poiss
import os
from rate_n_phase_perceptron import phase_code

#BUILD THE NETWORK

class Net(nn.Module):
    def __init__(self, n_inp, n_out):
        super(Net, self).__init__()
        self.fc1 = nn.Linear(n_inp, n_out)
    def forward(self, x):
        y = torch.relu(self.fc1(x))
        return y

#TRAIN THE NETWORK

def train_net(net, train_data, train_labels, n_iter=1000, lr=1e-4):
    optimizer = optim.SGD(net.parameters(), lr=lr)
    track_loss = []
    loss_fn = nn.MSELoss()
    # loss_fn = nn.L1Loss()
    for i in range(n_iter):
        out = net(train_data)
        loss = torch.sqrt(loss_fn(out, labels))
        # Compute gradients
        optimizer.zero_grad()
        loss.backward()
    
        # Update weights
        optimizer.step()
    
        # Store current value of loss
        track_loss.append(loss.item())  # .item() needed to transform the tensor output of loss_fn to a scalar
        
        # Track progress
        if (i + 1) % (n_iter // 5) == 0:
          print(f'iteration {i + 1}/{n_iter} | loss: {loss.item():.3f}')

    return track_loss, out

#Count the number of spikes in bins 

def binned_ct(arr, bin_size_ms, dt_ms=25, time_ms=5000):
    n_bins = int(time_ms/bin_size_ms)
    n_cells = arr.shape[0] 
    n_traj = arr.shape[1]
    counts = np.empty((n_bins, n_cells, n_traj))
    for i in range(n_bins):
        for index, value in np.ndenumerate(arr):
            counts[i][index] = ((bin_size_ms*(i) < value) & (value < bin_size_ms*(i+1))).sum()
            #search and count the number of spikes in the each bin range
    return counts

#Parametersfor the grid cell poisson input generation
savedir = os.getcwd()
n_grid = 200 
max_rate = 20
seed = 100
dur_ms = 2000
bin_size = 100
n_bin = int(dur_ms/bin_size)
dur_s = int(dur_ms/1000)
speed_cm = 20
field_size_cm = 100
traj_size_cm = dur_s*speed_cm



def spike_ct(trajs_pf):

    seed_2s = np.arange(200,205,1)
    n_traj = 2
    poiss_spikes = []
    counts_1 = np.empty((len(seed_2s), n_bin*n_grid))
    counts_2 = np.empty((len(seed_2s), n_bin*n_grid))
    for idx, seed_2 in enumerate(seed_2s):
        curr_spikes = inhom_poiss(trajs_pf, n_traj, seed=seed_2, dt_s=dt_s, traj_size_cm=traj_size_cm)
        poiss_spikes.append(curr_spikes)
        counts_1[idx, :] = binned_ct(curr_spikes, bin_size, time_ms=dur_ms)[:,:,0].flatten()
        counts_2[idx,:] = binned_ct(curr_spikes, bin_size, time_ms=dur_ms)[:,:,1].flatten()
    counts = np.vstack((counts_1, counts_2))
    return counts





phases_sim, spikes_sim = phase_code([75, 74.5])
phases_diff, spikes_diff = phase_code([75, 60])




lr = 1e-8
n_iter = 500
seed_4s = [0,1,2,3,4,5,6,7,8,9]
plt.figure()
plt.title('Perceptron Learning Phase Code for Similar Trajectories\n multip torch seeds, learning rate = '+str(lr))
plt.xlabel('Epochs')
plt.ylabel('RMSE Loss')


seed_1s = np.arange(100,110,1)

th_cross_sim = []
th_cross_diff = []
for idx, seed_4 in enumerate(seed_4s):

    data_sim = torch.FloatTensor(phases_sim)

    labels = torch.FloatTensor([75,74.5]) 
    torch.manual_seed(seed_4)
    net_sim = Net(4000,1)
    train_loss_sim, out_sim = train_net(net_sim, data_sim, labels, n_iter=n_iter, lr=lr)
    th_cross_sim.append(np.argmax(np.array(train_loss_sim) < 0.2))
    if seed_4 == seed_4s[0]:
        plt.plot(train_loss_sim, 'b-', label='75cm vs 74.5cm')
    else:
        plt.plot(train_loss_sim, 'b-')
    if seed_4 == seed_4s[7]:
        print(out_sim)

plt.legend()

plt.annotate(str(th_cross_sim)+'\n'+str(th_cross_diff), (0,0), (0, -40), xycoords='axes fraction', textcoords='offset points', va='top', fontsize=9)

