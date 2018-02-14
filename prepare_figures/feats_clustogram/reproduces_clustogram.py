#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 17:27:52 2018

@author: ajaver
"""

import pymysql
import pandas as pd
import numpy as np
from scipy.stats import ranksums
if __name__ == '__main__':
    conn = pymysql.connect(host='localhost', database='single_worm_db')
            
    sql = '''
    SELECT e.date, s.name AS strain, s.description AS strain_description, g.name AS gene, fm.* 
    FROM features_means AS fm
    JOIN experiments AS e ON e.id = fm.experiment_id
    JOIN strains AS s ON e.strain_id = s.id
    JOIN genes AS g ON s.gene_id = g.id
    '''
    df = pd.read_sql(sql, con=conn)
    #%%
    paper_feats = ['eccentricity', 'bend_count', 'midbody_width', 'primary_wavelength', 'length',
                   'backward_frequency', 'backward_time_ratio', 'omega_turns_frequency', 
                   'forward_time_ratio', 'midbody_speed_forward', 'path_range',
                   'midbody_crawling_frequency_abs', 'foraging_speed_abs', 
                   'midbody_crawling_amplitude_forward_abs', 'midbody_crawling_amplitude_backward_abs',
                   'midbody_crawling_amplitude_abs', 'head_bend_mean_abs', 
                   'foraging_amplitude_abs', 'foraging_amplitude_paused_abs',
                   'foraging_amplitude_backward_abs', 'max_amplitude', 
                   'midbody_bend_mean_abs', 'tail_bend_mean_abs']
    
    good = df['gene'].str.contains('unc') | df['gene'].str.contains('egl') | (df['strain'] == 'N2')
    good = good & ~df['strain_description'].str.contains('GFP') 
    df_g = df[good].groupby('strain')
    N2_data = df_g.get_group('N2')
    
    time_offset_allowed = 10
    
    
    col2ignore_r = ['date', 'strain', 'strain_description', 'gene', 'experiment_id',
       'worm_index', 'n_frames', 'n_valid_skel', 'first_frame']
    
    valid_feats = [x for x in df if x not in col2ignore_r]
    
    #only select features that have less than 0.05 of nan
    mm = df[valid_feats].isnull().mean()
    valid_feats = mm[mm<=0.05].index.tolist()
    paper_feats = [x for x in paper_feats if x in valid_feats]
    
    ctr_sizes = []
    all_pvalues = []
    for ss, s_data in df_g:
        print(ss)
        if ss == 'N2':
            continue
        
        offset = pd.to_timedelta(time_offset_allowed, unit='day')
        #ini_date = s_data['date'].min() - offset
        #fin_date = s_data['date'].max() + offset
        
        udates = s_data['date'].map(lambda t: t.date()).unique()
        udates = [pd.to_datetime(x) for x in udates]
        
        good = (N2_data['date'] > udates[0] - offset) & (N2_data['date'] < udates[0] + offset)
        for ud in udates:
            good |= (N2_data['date'] > ud - offset) & (N2_data['date'] < ud + offset)
        ctrl_data = N2_data[good]
        
        ctr_sizes.append((ss, len(ctrl_data)))
        
        ss_description = s_data['strain_description'].values[0]
        for ff in valid_feats:
            ctr = ctrl_data[ff].values
            atr = s_data[ff].values
            
            #_, p = ttest_ind(ctr, atr)
            _, p = ranksums(ctr, atr)
            assert isinstance(p, float)
            
            
            all_pvalues.append((ss, ss_description, ff, p, np.mean(ctr), np.mean(atr)))
    
    df_pvalues = pd.DataFrame(all_pvalues, columns = ['strain', 'strain_description', 'feature', 'pvalue', 'ctr_avg', 'strain_avg'])
    
    tot_comp = df_pvalues.shape[0]*df_pvalues.shape[1]
    
    df_pvalues_c = df_pvalues.pivot('strain_description', 'feature', 'pvalue')
    #%%
    import matplotlib.pylab as plt
    import seaborn as sns
    import statsmodels.stats.multitest as smm
    #%%
    df_s = df_pvalues.pivot('strain_description', 'feature', 'pvalue')
    rej, pval_corr = smm.multipletests(df_pvalues['pvalue'], method = 'fdr_tsbky' )[:2]
    df_pvalues['pval_corr'] = pval_corr
    
    pval_ind = np.zeros_like(df_pvalues['pval_corr'])
    for kk, pp in enumerate([0.05, 0.01, 0.001, 0.0001]):
        pval_ind[df_pvalues['pval_corr'] < pp] = kk + 1
    pval_ind[df_pvalues['strain_avg'] < df_pvalues['ctr_avg']] *= -1
    df_pvalues['pval_ind'] = pval_ind.astype(np.int)
    
    cc = sns.color_palette("RdBu_r", 9)
    c_levels = np.sort(df_pvalues['pval_ind'].unique())
    c_lut = {k:v for k,v in zip(c_levels, cc)}
    
    df_s = df_pvalues.pivot('strain_description', 'feature', 'pval_ind')
    df_s = df_s[paper_feats]
    
    cbar_kws={
            "ticks":[-4, -3, -2, -1, 0, 1, 2, 3, 4],
            #"label" : ['<0.0001', '<0.001', '<0.01', '<0.05', '>0.05', '<0.05', '<0.01', '<0.001', '<0.0001']
    }
    ff = sns.clustermap(df_s, figsize=(5,12), cmap="RdBu_r", method='average', cbar_kws=cbar_kws)
    plt.savefig('clustermap.pdf', bbox_inches='tight')
    plt.savefig('clustermap.png', bbox_inches='tight')