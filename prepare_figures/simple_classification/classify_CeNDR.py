#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 12:07:50 2018

@author: ajaver
"""
from trainer import TrainerSimpleNet

import torch
from torch.autograd import Variable
import pandas as pd
from sklearn.model_selection import StratifiedShuffleSplit

divergent_set = sorted(['CB4856', 'N2', 'DL238', 'CX11314', 'JU258', 'JT11398', 'LKC34',
       'EG4725', 'MY23', 'MY16', 'ED3017', 'JU775'])
    

def softmax_clf(data_in):
    
    fold_id, fold_data, fold_param = data_in
    
    (db_name, i_fold) = fold_id
    (x_train, y_train), (x_test, y_test) = fold_data
    (cuda_id, n_epochs, batch_size, lr, momentum) = fold_param
    
    
    n_classes = int(y_train.max() + 1)
    
    x_train = torch.from_numpy(x_train).float()
    y_train = torch.from_numpy(y_train).long()
    
    x_test = torch.from_numpy(x_test).float()
    y_test = torch.from_numpy(y_test).long() 
    
    input_v = Variable(x_test.cuda(cuda_id), requires_grad=False)
    target_v = Variable(y_test.cuda(cuda_id), requires_grad=False)
    
    input_train = x_train
    target_train = y_train
    
    
    n_features = x_train.shape[1]
    trainer = TrainerSimpleNet(n_classes, n_features, n_epochs, batch_size, cuda_id, lr, momentum)
    trainer.fit(input_train, target_train)
    fold_res = trainer.evaluate(input_v, target_v)
    
    print('Test: loss={:.4}, acc={:.2f}%, f1={:.4}'.format(*fold_res))
    
    return (fold_id, fold_res)
    
if __name__ == '__main__':
    fname = './data/ow_features_full_CeNDR.csv'
    
    strain_dict = {ss:ii+1 for ii, ss in enumerate(divergent_set)}
    
    
    df = pd.read_csv(fname)
    df['strain'] = df['strain'].str.strip()
    
    #select only divergent set
    df = df[df['strain'].isin(divergent_set)]
    df['strain_id'] = df['strain'].map(strain_dict)
    
    
    
    bad_cols = ['id', 'id.1', 'strain', 'directory', 'base_name', 
                'exp_name' , 'experiment_id', 'strain_id']
    all_feats_cols = [x for x in df.columns if x not in bad_cols]
    #remove orientation this feature is wrong and should not be used
    all_feats_cols = [x for x in all_feats_cols if not '_orientation_' in x]
    
    motion_cols = [
     'forward_time',
     'forward_distance',
     'inter_forward_time',
     'inter_forward_distance',
     'forward_frequency',
     'forward_time_ratio',
     'forward_distance_ratio',
     'paused_time',
     'paused_distance',
     'inter_paused_time',
     'inter_paused_distance',
     'paused_frequency',
     'paused_time_ratio',
     'paused_distance_ratio',
     'backward_time',
     'backward_distance',
     'inter_backward_time',
     'inter_backward_distance',
     'backward_frequency',
     'backward_time_ratio',
     'backward_distance_ratio'
     ]
    
    motion_str = ['midbody_speed', 'midbody_motion_direction', 'path_', 'turn']
    for m_part in motion_str:
        motion_cols += [x for x in all_feats_cols if m_part in x]
    #%%
    MAX_FRAC_NAN = 0.05
    MIN_N_VIDEOS = 3
    
    frac_bad = df[all_feats_cols].isnull().mean()
    cols2remove =  frac_bad.index[(frac_bad>MAX_FRAC_NAN).values].tolist()
    df_filt = df[[x for x in df if x not in cols2remove]].copy()
    
    feats_cols_filt = [x for x in all_feats_cols if x not in cols2remove]
    motion_cols_filt = [x for x in motion_cols if x not in cols2remove]
    
    #imputate missing data with the global median
    med_vals = df_filt[feats_cols_filt].median()
    
    for feat in feats_cols_filt:
        bad = df_filt[feat].isnull()
        if bad.any():
            
            df_filt.loc[bad, feat] = med_vals[feat]
    #%%
    # scale data (z-transform)
    dd = df_filt[feats_cols_filt]
    z = (dd-dd.mean())/(dd.std())
    df_filt[feats_cols_filt] = z
    
    #%%
    
    n_folds = 10
    batch_size =  100
    
    n_epochs = 500
    
    cuda_id = 0
    lr = 0.001
    momentum = 0.9
    
    fold_param = (cuda_id, n_epochs, batch_size, lr, momentum)
    
    all_data_in = []
    
    
    cols_types = {'all' : feats_cols_filt, 'motion' : motion_cols_filt}
    
    for set_type, cols in cols_types.items():
    
        X = df_filt[cols].values
        y = df_filt['strain_id'].values
        
        s_g = StratifiedShuffleSplit(n_splits = n_folds, test_size = 0.2, random_state=777)
        for i_fold, (train_index, test_index) in enumerate(s_g.split(X, y)):
            x_train, y_train  = X[train_index], y[train_index]
            x_test, y_test  = X[test_index], y[test_index]
            
            fold_data = (x_train, y_train), (x_test, y_test)
            fold_id = (set_type, i_fold)
            
            all_data_in.append((fold_id, fold_data, fold_param))
    #%%
    import numpy as np
    import multiprocessing as mp
    import pickle
    
    p = mp.Pool(1)
    results = p.map(softmax_clf, all_data_in)
    
    with open('model_results.pkl', "wb" ) as fid:
        pickle.dump(results, fid)
    #%%
    res_db = {}
    for (set_type, i_fold), dat in results:
        if set_type not in res_db:
            res_db[set_type] = []
        res_db[set_type].append(dat)
    
    for set_type, dat in res_db.items():
        res_db[set_type] = list(zip(*dat))
        
    for n, m_type in enumerate(['loss', 'acc', 'f1']):
        print(m_type)
        for set_type, dat in res_db.items():
            vv = dat[n]
            
            dd = '{} : {:.2f} {:.2f}'.format(set_type, np.mean(dat[n]), np.std(dat[n]))
            print(dd)
    #%%
    
    