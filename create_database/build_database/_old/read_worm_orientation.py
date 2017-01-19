# -*- coding: utf-8 -*-
"""
Created on Mon Apr 18 14:53:13 2016

@author: ajaver
"""

import glob
import os
import h5py
import numpy as np
import matplotlib.pylab as plt

from sqlalchemy import create_engine, MetaData
from sqlalchemy.schema import Table
from sqlalchemy.orm import Session
from sklearn.decomposition import IncrementalPCA#RandomizedPCA
from sklearn import preprocessing

#from sqlalchemy.orm import mapper, sessionmaker

myengine = create_engine(r'mysql+pymysql://ajaver:@localhost/single_worm_old')

meta = MetaData()
meta.reflect(bind=myengine, views=True)
experiments_full =Table('exp_annotation_full', meta, autoload=True)

session = Session(myengine)

main_dir = '/Users/ajaver/Desktop/Videos/single_worm/agar_3/MaskedVideos/'

files = glob.glob(os.path.join(main_dir, '*.hdf5' ))

I_all = np.zeros(0)
label_side = np.zeros(0)
label_worm = np.zeros(0)

ipca = IncrementalPCA()
for ii_mask, masked_image_file in enumerate(files):
    _, fname = os.path.split(masked_image_file)
    base_name = os.path.splitext(fname)[0]
    
    exp_row = session.query(experiments_full).\
    filter(experiments_full.c.file_name==base_name).one_or_none()
    
    if exp_row is not None:
        print('%i) %s | %s' % (ii_mask, exp_row[9],  base_name))
    else:
        print(exp_row, base_name)
        continue
    
    intensity_file = masked_image_file.replace('MaskedVideos', 'Results').replace('.hdf5', '_intensities.hdf5')
    
    if not os.path.exists(intensity_file):
        continue
    #%%
    with h5py.File(intensity_file, 'r') as fid:
        II = fid['/straighten_worm_intensity'][:, 30:-30, 3:-3].astype(np.float)
        #II = II - np.median(II, axis= (1,2))[:,np.newaxis, np.newaxis]
    
    n_samples, h, w = II.shape
    X = np.reshape(II, (n_samples, h*w))
    X_normalized = preprocessing.normalize(X, norm='l2')
    ipca.partial_fit(X_normalized)
#    #%%
    I_int_d = np.percentile(II, [0.5, 99.5], axis=0)
    plt.figure()
    plt.subplot(1,2,1)
    I_int = np.squeeze(I_int_d[1,:,:])
    plt.imshow(I_int, interpolation='none', cmap='gray')
    plt.title('%i) %s' % (ii_mask, exp_row[9]))
    plt.subplot(1,2,2)
    I_int = np.squeeze(I_int_d[-1,:,:]-I_int_d[0,:,:])
    plt.imshow(I_int, interpolation='none', cmap='gray')
    plt.title('%i) %s' % (ii_mask, exp_row[9]))
    
#%%
n_components = 10

eigenints = ipca.components_.reshape((-1, h, w))
plt.figure()
for ii in range(n_components):
    ax = plt.subplot(1, n_components, ii+1)
    plt.imshow(eigenints[ii], interpolation='none', cmap='gray')
    ax.set_xticks([])
    ax.set_yticks([])

#ipca.explained_variance_ratio_