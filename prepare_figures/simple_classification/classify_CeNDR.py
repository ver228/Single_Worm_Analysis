#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 12:07:50 2018

@author: ajaver
"""
from trainer import TrainerSimpleNet

import os
import torch
from torch.autograd import Variable
import pandas as pd
from sklearn.model_selection import StratifiedKFold, StratifiedShuffleSplit

divergent_set = sorted(['CB4856', 'N2', 'DL238', 'CX11314', 'JU258', 'JT11398', 'LKC34',
       'EG4725', 'MY23', 'MY16', 'ED3017', 'JU775'])
    

save_clf_dir = './classifiers'
_is_save_models = True
_is_val = False

if not os.path.exists(save_clf_dir):
    os.makedirs(save_clf_dir)

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
    
    if _is_save_models:
        save_name = os.path.join(save_clf_dir, '{}_{}.pth.tar'.format(*fold_id))
        torch.save(trainer.model, save_name)
        
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
    
    motion_str = ['midbody_speed', 'midbody_motion_direction', 'midbody_crawling_', 'path_', 'turn']
    #motion_str = ['_speed', '_motion_direction', 'path_', 'turn']
    for m_part in motion_str:
        motion_cols += [x for x in all_feats_cols if m_part in x]
    
    #motion_cols = [x for x in motion_cols if 'foraging_speed' not in x]
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
    random_state = 777
    n_folds = 6
    batch_size =  50
    
    n_epochs = 500
    
    cuda_id = 0
    lr = 0.001
    momentum = 0.9
    
    all_data_in = []
    
    cols_types = {'all' : feats_cols_filt, 'motion' : motion_cols_filt}
    #, 'no_motion': list(set(feats_cols_filt)-set(motion_cols_filt))}
    
    s_g = StratifiedKFold(n_splits = n_folds,  random_state=random_state)
    folds_indexes = list(s_g.split(df_filt[cols_types['all']].values, df_filt['strain_id'].values))
    
    val_data = {}
    for set_type, cols in cols_types.items():
        Xd = df_filt[cols].values
        yd = df_filt['strain_id'].values
        #s_g = StratifiedShuffleSplit(n_splits = n_folds, test_size = 0.2, random_state=random_state)
       
        for i_fold, (train_index, test_index) in enumerate(folds_indexes):
            
            fold_param = (cuda_id, n_epochs, batch_size, lr, momentum)
            
            x_train, y_train  = Xd[train_index].copy(), yd[train_index].copy()
            x_test, y_test  = Xd[test_index].copy(), yd[test_index].copy()
            
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
        if m_type == 'loss':
            continue
        
        print(m_type, '**************')
        for set_type, dat in res_db.items():
            vv = dat[n]
            
            dd = '{} : {:.2f} {:.2f}'.format(set_type, np.mean(dat[n]), np.std(dat[n]))
            print(dd)
    #%%
    results = {}
    print('VAL acc:')
    for set_type, (x_val, y_val) in val_data.items():
        
        results[set_type] = []
        n_features = x_val.shape[1]
        n_classes = int(y_val.max() + 1)
        
        x_val = torch.from_numpy(x_val).float()
        y_val = torch.from_numpy(y_val).long() 
        
        input_v = Variable(x_val.cuda(cuda_id), requires_grad=False)
        target_v = Variable(y_val.cuda(cuda_id), requires_grad=False)
        
        trainer = TrainerSimpleNet(n_classes, n_features, n_epochs, batch_size, cuda_id, lr, momentum)
        for i_fold in range(n_folds):
            save_name = os.path.join(save_clf_dir, '{}_{}.pth.tar'.format(set_type, i_fold))
            dd = torch.load(save_name)
            trainer.model.load_state_dict(dd.state_dict())
            fold_res = trainer.evaluate(input_v, target_v)
            
            results[set_type].append(fold_res)
            
        dat = [x[1] for x in results[set_type]]
        dd = '{} : {:.2f} {:.2f}'.format(set_type, np.mean(dat), np.std(dat))
        print(dd)
        