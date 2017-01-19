# -*- coding: utf-8 -*-
"""
@author: ajaver
"""


import os
import xlrd
import numpy as np
import tifffile
import cv2
import matplotlib.pylab as plt
import tables
import csv

import glob
#%%
from MWTracker.trackWorms.segWormPython.linearSkeleton import linearSkeleton
from MWTracker.trackWorms.segWormPython.getHeadTail import rollHead2FirstIndex
from MWTracker.trackWorms.segWormPython.cythonFiles.segWorm_cython import circComputeChainCodeLengths
from MWTracker.trackWorms.segWormPython.cleanWorm import circSmooth, extremaPeaksCircDist
from MWTracker.trackWorms.segWormPython.cythonFiles.circCurvature import circCurvature
from MWTracker.trackWorms.segWormPython.mainSegworm import resampleAll

from MWTracker.trackWorms.segWormPython.mainSegworm import getSkeleton
from MWTracker.trackWorms.getSkeletonsTables import binaryMask2Contour


def getSkeletonHT(contour, head_ind, tail_ind):
    ske_worm_segments = 24.;
    cnt_worm_segments = 2. * ske_worm_segments;
    
    
    cnt_chain_code_len = circComputeChainCodeLengths(contour);
    worm_seg_length = (cnt_chain_code_len[0] + cnt_chain_code_len[-1]) / cnt_worm_segments;
    
    edge_len_hi_freq = worm_seg_length;
    cnt_ang_hi_freq = circCurvature(contour, edge_len_hi_freq, cnt_chain_code_len);
    
    edge_len_low_freq = 2 * edge_len_hi_freq;
    cnt_ang_low_freq = circCurvature(contour, edge_len_low_freq, cnt_chain_code_len);
    
    #% Blur the contour's local high-frequency curvature.
    #% Note: on a small scale, noise causes contour imperfections that shift an
    #% angle from its correct location. Therefore, blurring angles by averaging
    #% them with their neighbors can localize them better.
    worm_seg_size = contour.shape[0] / cnt_worm_segments;
    blur_size_hi_freq = np.ceil(worm_seg_size / 2);
    cnt_ang_hi_freq = circSmooth(cnt_ang_hi_freq, blur_size_hi_freq)
        
    #% Compute the contour's local high/low-frequency curvature maxima.
    maxima_hi_freq, maxima_hi_freq_ind = \
    extremaPeaksCircDist(1, cnt_ang_hi_freq, edge_len_hi_freq, cnt_chain_code_len)
    
    maxima_low_freq, maxima_low_freq_ind = \
    extremaPeaksCircDist(1, cnt_ang_low_freq, edge_len_low_freq, cnt_chain_code_len)
    
    #change arrays so the head correspond to the first position
    head_ind, tail_ind, contour, cnt_chain_code_len, cnt_ang_low_freq, maxima_low_freq_ind = \
    rollHead2FirstIndex(head_ind, tail_ind, contour, cnt_chain_code_len, cnt_ang_low_freq, maxima_low_freq_ind)
    
    #% Compute the contour's local low-frequency curvature minima.
    minima_low_freq, minima_low_freq_ind = \
    extremaPeaksCircDist(-1, cnt_ang_low_freq, edge_len_low_freq, cnt_chain_code_len);
    
    #% Compute the worm's skeleton.
    skeleton, cnt_widths = linearSkeleton(head_ind, tail_ind, minima_low_freq, minima_low_freq_ind, \
        maxima_low_freq, maxima_low_freq_ind, contour.copy(), worm_seg_length, cnt_chain_code_len);
    
    #The head must be in position 0    
    assert head_ind == 0
    
    # Get the contour for each side.
    cnt_side1 = contour[:tail_ind+1, :].copy()
    cnt_side2 = np.vstack([contour[0,:], contour[:tail_ind-1:-1,:]])
    
    
    skeleton, _, cnt_side1, cnt_side2, cnt_widths = \
    resampleAll(skeleton, cnt_side1, cnt_side2, cnt_widths, resampling_N)
    
    return skeleton, cnt_side1, cnt_side2, cnt_widths

#%%
if __name__ == '__main__':
    #save_dir = '/Volumes/behavgenom$/Kezhi/DataSet/AllFiles/OutSource_files/All_Label/contours_from_manual/'
    save_dir = '/Volumes/behavgenom$/Kezhi/DataSet/AllFiles/OutSource_files/All_Label/Tif/skeleton_Ave/'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    average_width_file = os.path.join(save_dir, 'average_width.csv')
    bad_files = os.path.join(save_dir, 'bad_files.txt')
    #delete old data
    with open(average_width_file, 'w') as fid1, open(bad_files, 'w') as fid2:
        pass
    
    resampling_N = 49
    tif_dir = '/Volumes/behavgenom$/Kezhi/DataSet/AllFiles/OutSource_files/All_Label/Tif/'
    xls_dir = '/Volumes/behavgenom$/Kezhi/DataSet/AllFiles/OutSource_files/All_Label/xlsx/'
    
    all_tif = glob.glob(tif_dir + '*.tif')
    all_xls = glob.glob(xls_dir + '*.xls*')
    #with open('manual_xls.txt', 'r') as fid:
    #    dat = fid.read()
    #    dat = [x for x in dat.split('\n') if x]
    
    #with open('manual_tif.txt', 'r') as fid:
    #    all_tif = fid.read().split('\n')
    
    
    
    #%%
    all_coords = {}
    tif_dict = {}
    
    for ii, fname in enumerate(all_xls):
        
        print(ii, len(all_xls))
        base_name = os.path.splitext(os.path.split(fname)[1])[0]
        base_name = base_name.rpartition(')')[0] + ')'
        try:
            wb = xlrd.open_workbook(fname)
            wb_data =[]
            #%%
            for s in wb.sheets():
                sheet_dat = []
                for row in range(s.nrows):
                    row_dat = []
                    for col in range(s.ncols):
                        value  = (s.cell(row,col).value)
                        row_dat.append(value)
                    sheet_dat.append(row_dat)
                
                wb_data.append(sheet_dat)
            
            wb_data = [x for x in wb_data if x]
            assert len(wb_data) == 1
            wb_data = wb_data[0]
        except xlrd.XLRDError:
            #%%
            wb_data = []
            with open(fname, 'r') as fid:
                for row in fid.read().split('\n'):
                    if row:
                        wb_data.append(row.split('\t'))
        assert not base_name in all_coords
        all_coords[base_name] = wb_data
    
        valid_f = [x for x in all_tif if base_name in x]
        assert len(valid_f) == 1
        tif_dict[base_name] = valid_f[0]
        
        
        #%% read head tail coordinates
        print(len(all_coords[base_name]), base_name)
        header = all_coords[base_name].pop(0)
        assert header[5] == 'X'
        assert header[6] == 'Y'
        
        dat = np.array([(float(x[5]), float(x[6])) for x in all_coords[base_name]])
        head_coords = dat[::2]
        tail_coords = dat[1::2]
    
    #%% read images
        images = tifffile.imread(tif_dict[base_name]);
        
        img_shape = images.shape if images.ndim == 3 else images.shape[:-1]
        all_masks = np.zeros(img_shape, np.uint8)
        for ii, img in enumerate(images):
            if img.ndim == 3:
                img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            all_masks[ii] = img>0
        
        all_masks = all_masks.astype(np.uint8)*255
    #%%
        tot_rows = all_masks.shape[0]
        skeletons = np.full((tot_rows, resampling_N, 2), np.nan)
        cnt_side1s = np.full((tot_rows, resampling_N, 2), np.nan)
        cnt_side2s = np.full((tot_rows, resampling_N, 2), np.nan)
        cnt_widths = np.full((tot_rows, resampling_N), np.nan)
        
        #try:
        for tt in range(tot_rows):
            worm_mask = all_masks[tt]
            #head_coord = head_coords[tt]
            #tail_coord = tail_coords[tt]
            
            #%%
            _, contours, hierarchies = cv2.findContours(worm_mask.copy(), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
            
            IM_LIMX = worm_mask.shape[0]-2
            IM_LIMY = worm_mask.shape[1]-2
            contour = []
            hierarchy = []
            for cnt, hier in zip(contours, hierarchies[0]):
                if not np.any(cnt == 1) and \
                    not np.any(cnt[:,:,0] ==  IM_LIMY)\
                    and not np.any(cnt[:,:,1] == IM_LIMX):
                        contour.append(cnt)
                        hierarchy.append(hier)
            
            if len(contour) > 0:
                #select the largest area if there are more than one objects
                cnt_areas = [cv2.contourArea(cnt) for cnt in contour]
                valid_ind = np.argmax(cnt_areas)
                
                contour = contour[valid_ind]
            elif len(contour) == 1:
                contour = contour[0]
    
            contour = np.squeeze(contour).astype(np.float)
            if contour.size > 0:
                #head_ind = np.argmin(np.sum((contour - head_coord)**2, axis=1))
                #tail_ind = np.argmin(np.sum((contour - tail_coord)**2, axis=1))
                #skeleton, cnt_side1, cnt_side2, cnt_widths = getSkeletonHT(contour, head_ind, tail_ind)
                skeleton, ske_len, cnt_side1, cnt_side2, cnt_width, cnt_area = \
                getSkeleton(contour, resampling_N=49)
                if skeleton.size>0:
                    skeletons[tt] = skeleton
                    cnt_side1s[tt] = cnt_side1
                    cnt_side2s[tt] = cnt_side2
                    cnt_widths[tt] = cnt_width
        #except (IndexError, AssertionError, ZeroDivisionError):
        #    with open(bad_files, 'a') as fid:
        #        fid.write(fname + '/n')
                    
                    
        #%%
        table_filters = tables.Filters(complevel=5, complib='zlib', shuffle=True, fletcher32=True)
        
        save_file = os.path.join(save_dir, base_name + '_contours.hdf5')
        with tables.File(save_file, 'w') as fid:
            fid.create_carray('/', 'mask', obj = all_masks, filters = table_filters,
                              chunkshape = (1, all_masks.shape[1],all_masks.shape[2]));
            fid.create_carray('/', 'skeleton', obj = skeletons, filters = table_filters,
                              chunkshape = (1, resampling_N,2));
            fid.create_carray('/', 'contour_side1', obj = cnt_side1s, filters = table_filters,
                              chunkshape = (1, resampling_N,2));
            fid.create_carray('/', 'contour_side2', obj = cnt_side2s, filters = table_filters,
                              chunkshape = (1, resampling_N,2));
            fid.create_carray('/', 'contour_width', obj = cnt_widths, filters = table_filters,
                              chunkshape = (1, resampling_N));
            fid.create_carray('/', 'head_coord', obj = head_coords)
            fid.create_carray('/', 'tail_coord', obj = tail_coords)
            
        #%%
        with open(average_width_file, 'a') as fid:
            csvwriter = csv.writer(fid)
            csvwriter.writerow([base_name, np.nanmedian(cnt_widths[:,17:33])])
            
#%%
#plt.figure()
#plt.imshow(worm_mask, interpolation='none', cmap='gray')
#plt.plot(head_coord[0], head_coord[1], 'og')
#plt.plot(tail_coord[0], tail_coord[1], 'sr')
