#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 23 18:23:36 2018

@author: ajaver
"""
import numpy as np
import pandas as pd
import matplotlib.pylab as plt



if __name__ == '__main__':
    
    #data_file = '../../compare_segworm/all_skeletons_comparisons.hdf5'
    data_file = './all_skeletons_comparisons.hdf5'
    #data_file = '/Users/ajaver/OneDrive - Imperial College London/paper_tierpsy_tracker/figures/skeleton_comparison/all_skeletons_comparisons.hdf5'
    
    #this is large, maybe i cannot load it in memory in as small machine
    with pd.HDFStore(data_file, 'r') as fid:
        errors_data = fid['/data']
    
    #%%
    errors_data['RMSE_N'] = errors_data['RMSE']/errors_data['length_tierpsy']
    errors_data['RMSE_BEST_N'] = errors_data[['RMSE', 'RMSE_switched']].min(axis=1)/errors_data['length_tierpsy']
    
    #%%
    #%%
    if True:
        ll = errors_data['RMSE'].dropna()
        rr = errors_data['RMSE_switched'].dropna()
        frac_th_switched = np.mean(ll>rr)
        print(frac_th_switched)
        del ll
        del rr
    #%%
    #tot = err_n.size
    counts, bins = np.histogram(errors_data['RMSE_N'].dropna(), bins=1000, range = (0, 1))
    
    counts = counts/np.sum(counts)
    
    counts_min, bins = np.histogram(errors_data['RMSE_BEST_N'].dropna(), bins=1000, range = (0, 1))
    counts_min = counts_min/np.sum(counts_min)
    
    #%%
    def _get_switch_error(dat):
        delS = dd - dd[:, ::-1]
        R_error = np.sum(delS**2, axis=0)
        _switch_error = np.sqrt(np.mean(R_error))
        return _switch_error
    
    L = 1;
    dd = np.linspace(0, L, 49)
    dd = np.vstack((dd,dd))
    
    assert (1 -np.sum(np.sqrt(np.sum(np.diff(dd, axis=1)**2, axis=0)))) < 1e3
    
    switch_error_lin = _get_switch_error(dd)
    
    theta = np.linspace(np.pi, -np.pi, 49)
    
    L = 2*np.pi #normalize by circle length
    dd = np.vstack((np.sin(theta), np.cos(theta)))/L 
    
    assert (1 -np.sum(np.sqrt(np.sum(np.diff(dd, axis=1)**2, axis=0)))) < 1e3
    
    switch_error_circ = _get_switch_error(dd)
    
    
    #%%
    seg_size = 1/48
    experiment_ids = errors_data['experiment_id'].unique()
    
    #%%
#    movie_fractions_d = np.zeros((np.max(experiment_ids),3), np.int32)
#    import tqdm
#    #dat = np.zeros(np.)
#    for ii in  tqdm.tqdm(range(errors_data.shape[0])):
#        row = errors_data.iloc[ii]
#        if ~np.isnan(row['RMSE_N']):
#            
#            exp_id = int(row['experiment_id'])
#            movie_fractions_d[exp_id, 0] += 1
#            if row['RMSE_N'] <= seg_size:
#                movie_fractions_d[exp_id, 1] += 1
#            if row['RMSE_BEST_N'] <= seg_size:
#                movie_fractions_d[exp_id, 2] += 1
#            
 
    #%%
    import tqdm
    switch_th = 0.6
    
    
    def slow_iterator():
        #i can run out of memory if i use groupby. Slow but sure
        for exp_id in tqdm.tqdm(experiment_ids):
            dat = errors_data[errors_data['experiment_id'] == exp_id].dropna()
            yield exp_id, dat
    
    #if True:
    
    movie_fractions = []
    
    err_g = errors_data.dropna().groupby('experiment_id')
    #err_g = slow_iterator()
    for exp_id, dat in err_g:
    
        print(exp_id)
        #print(exp_id)
        
        #using mean with nan present might give the wrong result... not really sure...
        
        tot_f = (~np.isnan(dat['RMSE_N'])).sum()
        
        frac_good = (dat['RMSE_N'] <= seg_size).sum()/tot_f
        frac_good_switched = (dat['RMSE_BEST_N'] <= seg_size).sum()/tot_f
        
        #frac_switched = ((rmse_n > seg_size) & (rmse_n <= switch_th)).mean()
        frac_terrible = (dat['RMSE_BEST_N'] > switch_th).sum()/tot_f
        
        movie_fractions.append((exp_id, frac_good, frac_good_switched, frac_terrible))
        
        
    
    
    exp_id, frac_good, frac_good_switched, frac_terrible = zip(*movie_fractions)
    dd = {'frac_good':frac_good, 'frac_good_switched':frac_good_switched, 'frac_terrible':frac_terrible}
    
    movie_fractions_df = pd.DataFrame(dd, index=exp_id)
    movie_fractions_df.to_csv('movie_good_fractions.csv', index=False)
    #%%
    import matplotlib.patches as patches
    
    plt.figure(figsize=(10, 3.5))
    
    ax_ = plt.subplot(1,2,1)
    xx = bins[:-1] + (bins[1]-bins[0])/2
    yy = np.cumsum(counts)
    yy_m = np.cumsum(counts_min)
    
    #plt.figure(figsize=(8, 6))
    plt.plot(xx, yy, lw=2, label = '$RMSE$')
    plt.plot(xx, yy_m, '--', lw=2, label = '$min\{ RMSE, RMSE_{switch}\}$')
    
    
    ini_x, fin_x = ax_.get_xlim()
    ini_x = -0.1
    ini_y, fin_y = ax_.get_ylim()
    
    fin_y = 1.12
    p = patches.Rectangle( (ini_x, ini_y), 
                                  seg_size- ini_x, 
                                  fin_y - ini_y,
                                  alpha=0.2, 
                                  color = 'steelblue')
    ax_.add_patch(p)
    #plt.rc('text', usetex=True)
    plt.text(-0.09, 1.05, r'99.2% of the frames', fontsize=10)
    #plt.rc('text', usetex=False)
    #plt.plot((seg_size, seg_size), (-0.1, 1.1), ':r')
    #plt.plot((switch_error_lin, switch_error_lin), (-0.1, 1.1), ':r')
    #plt.plot((switch_error_circ, switch_error_circ), (-0.1, 1.1), ':r')
    
    plt.xlabel('RMSE / L')
    plt.ylabel('Cumulative Distribution Fraction')
    plt.ylim((ini_y, fin_y))
    plt.xlim((ini_x, fin_x))
    
    
    plt.subplot(1,2,2)
    vv = movie_fractions_df['frac_good'].sort_values()
    #plt.plot(np.linspace(0,1, vv.size), vv.values)
    plt.plot(vv.values, lw=2, label = '$RMSE$')
    vv = movie_fractions_df['frac_good_switched'].sort_values()
    #plt.plot(np.linspace(0,1, vv.size), vv.values)
    plt.plot(vv.values, '--', lw=2, label = '$min\{ RMSE, RMSE_{switch}\}$')
    
    
    plt.legend(fontsize=12)
    
    plt.xlabel('Movie Number')
    plt.ylabel('Fraction of Skeletons (RMSE/L < 1/48)')
    dd = (movie_fractions_df[['frac_good', 'frac_good_switched']]>0.90).sum()
    
    plt.tight_layout()
    plt.savefig('db_skel_comparison.pdf')
    
    
    #at least 90% of the frames are (RMSE/L < 1/48)
    #8410 of 9343
    #9208 of 9343
    
    #RMSE_BEST_N %99.2008 of frames have less than 1/48  182646477/184117924
    #RMSE_N 96.193 of frames less than 1/48 177109279/184117924
    
    
    #at least 99% of the frames are (RMSE/L < 1/24)
    #'8313 of 9343'
    #'#9299 of 9343'
    
    #RMSE_BEST_N %99.874 of frames have less than 1/24 
    #RMSE_N %96.809 of frames less than 1/24
    #%3.08 frames switched
    #total skeletons 184117924
    
    
    
    #%%
    #%%
    if False:
        '''
        This analysis is to try to get the fraction of good frames in each of the analys. However,
        it is tricky since this include the NaN's due to stage motions
        '''
        bad_in_segworm = errors_data[['length_segworm']].isnull()
        bad_in_tierpsy = errors_data[['length_tierpsy']].isnull()
        
        frac_bad_segworm = bad_in_segworm.mean()
        frac_bad_tierpsy = bad_in_tierpsy.mean()
        
        frac_bad_only_tierpsy = (bad_in_tierpsy.values & ~bad_in_segworm.values).mean()
        frac_bad_only_segworm = (~bad_in_tierpsy.values & bad_in_segworm.values).mean()
        
        err_g = errors_data.groupby('experiment_id')
        all_bad_frac = []
        for exp_id, dat in err_g:
            #print(exp_id)
            bad_in_tierpsy = dat[['length_tierpsy']].isnull()
            bad_in_segworm = dat[['length_segworm']].isnull()
            
            frac_bad_only_tierpsy = (bad_in_tierpsy.values & ~bad_in_segworm.values).mean()
            frac_bad_only_segworm = (~bad_in_tierpsy.values & bad_in_segworm.values).mean()
            
            all_bad_frac.append((exp_id, frac_bad_only_tierpsy, frac_bad_only_segworm))
        
        exp_id, frac_bad_only_tierpsy, frac_bad_only_segworm = zip(*all_bad_frac)
        
        dd = {'frac_bad_only_tierpsy':frac_bad_only_tierpsy, 'frac_bad_only_segworm':frac_bad_only_segworm}
        bad_frac_df = pd.DataFrame(dd, index = exp_id)
    #%%
    #0.018500000000000003 %99 in min
    #0.53 %min
    
    ind = errors_data[errors_data['RMSE_BEST_N']>0.5]['experiment_id'].unique()#0.018500000000000003)
    #%%
    row  = errors_data.iloc[ind]
    #%%
    #%%
    import pymysql
    
    inds = (6, 1117,  4787,  5247,  8881,  9107,  9117,  9120, 10165, 11307, 11600)
    conn = pymysql.connect(host='localhost', db='single_worm_db')
    cur = conn.cursor()
    
    
    ss = ','.join(['"{}"'.format(x) for x in inds])
    sql = '''
    select e.id, CONCAT(results_dir, '/', base_name, '.hdf5'), segworm_file
    from experiments as e 
    join segworm_info as s on e.id = s.experiment_id
    where e.id in ({});
    '''.format(ss)
    cur.execute(sql)
    bad_exps = cur.fetchall()
    
    for exp_id, fname, segname in bad_exps:
        print(exp_id)
        print(fname)
        print(segname)
    
    #[4787, 5247, 8881, 9107, 9117, 11307, 11600]
    
    # (329, 3555, 3556, 4231, 5124, 5991, 8759, 10407, 11260) , 647, 11109