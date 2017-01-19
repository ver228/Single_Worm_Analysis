# -*- coding: utf-8 -*-
"""
Created on Thu Dec 17 21:57:30 2015

@author: ajaver
"""
import matplotlib.pylab as plt
import h5py
import pandas as pd
import cv2
import numpy as np
from skimage.filters import threshold_otsu
from scipy.signal import medfilt
import time
import os

from MWTracker.trackWorms.getSkeletonsTables import getWormMask, binaryMask2Contour, getWormROI
from MWTracker.trackWorms.segWormPython.cleanWorm import cleanWorm
from MWTracker.trackWorms.segWormPython.linearSkeleton import linearSkeleton
from MWTracker.trackWorms.segWormPython.getHeadTail import getHeadTail, rollHead2FirstIndex, isHeadTailTouching
from MWTracker.trackWorms.segWormPython.cythonFiles.segWorm_cython import circComputeChainCodeLengths
from MWTracker.trackWorms.segWormPython.cleanWorm import circSmooth, extremaPeaksCircDist
from MWTracker.trackWorms.segWormPython.cythonFiles.circCurvature import circCurvature

#file_mask = '/Users/ajaver/Desktop/Videos/03-03-11/MaskedVideos/03-03-11/N2 swimming_2011_03_03__16_36___3___10.hdf5'
#file_mask = '/Volumes/behavgenom_archive$/MaskedVideos/nas207-3/Data/from pc207-15/laura/09-07-10/3/egl-17 (e1313)X on food R_2010_07_09__11_43_13___2___4.hdf5'
#file_mask = '/Users/ajaver/Desktop/Videos/single_worm/agar_1/MaskedVideos/431 JU298 on food L_2011_03_17__12_02_58___2___3.hdf5'
#file_mask = '/Users/ajaver/Desktop/Videos/single_worm/agar_2/MaskedVideos/798 JU258 on food L_2011_03_22__16_26_58___1___12.hdf5'
#file_mask = '/Users/ajaver/Desktop/Videos/single_worm/agar_1/MaskedVideos/unc-7 (cb5) on food R_2010_09_10__12_27_57__4.hdf5'
#file_mask = '/Users/ajaver/Desktop/Videos/single_worm/agar_1/MaskedVideos/gpa-11 (pk349)II on food L_2010_02_25__11_24_39___8___6.hdf5'



#file_mask = '/Users/ajaver/Desktop/Videos/single_worm/switched_sample/unc-104 (e1265)III on food L_2011_10_18__11_29_31__1.hdf5'
#file_skel = file_mask.replace('MaskedVideos', 'Results').replace('.hdf5', '_skeletons.hdf5')


file_skel = file_mask.replace('.hdf5', '_skeletons.hdf5')
assert(os.path.exists(file_mask))
assert(os.path.exists(file_skel))


with pd.HDFStore(file_skel, 'r') as fid:
    trajectories_data = fid['/trajectories_data']

#with pd.HDFStore(file_traj, 'r') as fid:
#    plate_worms = fid['/plate_worms']

current_frame = 9027#17277
with h5py.File(file_mask, 'r') as fid:
    img = fid['/mask'][current_frame]

row_data = trajectories_data[trajectories_data['frame_number'] == current_frame]
row_data = row_data.iloc[0]


worm_img, roi_corner = getWormROI(img, row_data['coord_x'], row_data['coord_y'], row_data['roi_size'])
min_mask_area = row_data['area']/2


worm_mask, contour, _ = getWormMask(worm_img, row_data['threshold'], 10, min_mask_area)


if contour.dtype != np.double:
    contour = contour.astype(np.double)

ske_worm_segments = 24.;
cnt_worm_segments = 2. * ske_worm_segments;

#this line does not really seem to be useful
#contour = cleanWorm(contour, cnt_worm_segments) 


#make sure the contours are in the counter-clockwise direction
#head tail indentification will not work otherwise
#x1y2 - x2y1(http://mathworld.wolfram.com/PolygonArea.html)
signed_area = np.sum(contour[:-1,0]*contour[1:,1]-contour[1:,0]*contour[:-1,1])/2
if signed_area>0:
    contour =  np.ascontiguousarray(contour[::-1,:])

#make sure the array is C_continguous. Several functions required this.
if not contour.flags['C_CONTIGUOUS']:
    contour = np.ascontiguousarray(contour)
    
    
    #% Compute the contour's local high/low-frequency curvature.
#% Note: worm body muscles are arranged and innervated as staggered pairs.
#% Therefore, 2 segments have one theoretical degree of freedom (i.e. one
#% approximation of a hinge). In the head, muscles are innervated
#% individually. Therefore, we sample the worm head's curvature at twice the
#% frequency of its body.
#% Note 2: we ignore Nyquist sampling theorem (sampling at twice the
#% frequency) since the worm's cuticle constrains its mobility and practical
#% degrees of freedom.

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

head_ind, tail_ind = \
getHeadTail(cnt_ang_low_freq, maxima_low_freq_ind, cnt_ang_hi_freq, maxima_hi_freq_ind, cnt_chain_code_len)

#one of the sides is too short so it might be touching itself (coiling)
err_msg = isHeadTailTouching(head_ind, tail_ind, cnt_chain_code_len); 

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
#%%
bend_low_freq_ind = minima_low_freq_ind[minima_low_freq < -30];
#if bend_low_freq_ind.size>0:
#    '''% Find concavities near the head. If there are any concavities
#    % near the tail, the head may be portruding from a coil; in
#    % which case, the width at the end of the head may be
#    % inaccurate.'''
#        if hlcBounds(1) < hrcBounds(2)
#            hBendI = lfCBendI(lfCBendI > hlcBounds(1) & ...
#                lfCBendI < hrcBounds(2));
#        else
#            hBendI = lfCBendI(lfCBendI > hlcBounds(1) | ...
#                lfCBendI < hrcBounds(2));
#        end
#        
#        % Does the worm more than double its width from the head?
#        % Note: if the worm coils, its width will grow to more than
#        % double that at the end of the head.
#        maxWidth = max(cWidths);
#        if isempty(hBendI)
#            if maxWidth / cWidths(hsBounds(2)) > 2 / bodyScale
#                errNum = 107;
#                errMsg = ['The worm more than doubles its width ' ...
#                    'from end of its head. Therefore, the worm is ' ...
#                    'coiled, laid an egg, and/or is significantly ' ...
#                    'obscured and cannot be segmented.'];
#                
#                % Organize the available worm information.
#                if verbose
#                    warning('segWorm:DoubleHeadWidth', ...
#                        ['Frame %d: ' errMsg], frame);
#                    vWorm = worm2struct(frame, contour, [], [], [], ...
#                        lfCAngles, headI, tailI, cCCLengths, [], [], ...
#                        [], [], [], [], [], [], [], [], [], [], [], [], ...
#                        [], [], [], [], [], [], [], [], [], [], [], [], ...
#                        [], [], [], [], [], [], [], [], [], 0, [], [], ...
#                        0, [], []);
#                else
#                    return;
#                end
#            end
#        end
#        
#        % Find concavities near the tail. If there are any concavities near
#        % the tail, the tail may be portruding from a coil; in which case,
#        % the width at the end of the tail may be inaccurate.
#        if trcBounds(1) < tlcBounds(2)
#            tBendI = lfCBendI(lfCBendI > trcBounds(1) & ...
#                lfCBendI < tlcBounds(2));
#        else
#            tBendI = lfCBendI(lfCBendI > trcBounds(1) | ...
#                lfCBendI < tlcBounds(2));
#        end
#        
#        % Does the worm more than double its width from the tail?
#        % If the worm coils, its width will grow to more than double
#        % that at the end of the tail.
#        if isempty(tBendI)
#            if maxWidth / cWidths(tsBounds(1)) > 2 / bodyScale
#                errNum = 108;
#                errMsg = ['The worm more than doubles its width ' ...
#                    'from end of its tail. Therefore, the worm is ' ...
#                    'coiled, laid an egg, and/or is significantly ' ...
#                    'obscured and cannot be segmented.'];
#                
#                % Organize the available worm information.
#                if verbose
#                    warning('segWorm:DoubleTailWidth', ...
#                        ['Frame %d: ' errMsg], frame);
#                    vWorm = worm2struct(frame, contour, [], [], [], ...
#                        lfCAngles, headI, tailI, cCCLengths, [], [], ...
#                        [], [], [], [], [], [], [], [], [], [], [], [], ...
#                        [], [], [], [], [], [], [], [], [], [], [], [], ...
#                        [], [], [], [], [], [], [], [], [], 0, [], [], ...
#                        0, [], []);
#                else
#                    return;
#                end
#            end
#        end
#        
#        % Use the most accurate estimate of head/tail width to
#        % determine whether the width of the body is more than double
#        % that at the end of the head/tail; in which case; the worm is
#        % coiled.
#        if ~(isempty(hBendI) && isempty(tBendI))
#            
#            % Find the distances of bends near the head.
#            hBendDist = abs(headI - hBendI);
#            hBendDist = min(hBendDist, abs(hBendDist - length(lfCAngles)));
#            
#            % Find the distances of bends near the tail.
#            tBendDist = abs(tailI - tBendI);
#            tBendDist = min(tBendDist, abs(tBendDist - length(lfCAngles)));
#            
#            % The bend near the head is furthest and, therefore, the
#            % width at the end of the head is our most accurate
#            % estimate of the worm's width.
#            if min(hBendDist) >= min(tBendDist)
#                if maxWidth / cWidths(hsBounds(2)) > 2 / bodyScale
#                    errNum = 107;
#                    errMsg = ['The worm more than doubles its width ' ...
#                        'from end of its head. Therefore, the worm is ' ...
#                        'coiled, laid an egg, and/or is significantly ' ...
#                        'obscured and cannot be segmented.'];
#                    
#                    % Organize the available worm information.
#                    if verbose
#                        warning('segWorm:DoubleHeadWidth', ...
#                            ['Frame %d: ' errMsg], frame);
#                        vWorm = worm2struct(frame, contour, [], [], [], ...
#                            lfCAngles, headI, tailI, cCCLengths, [], ...
#                            [], [], [], [], [], [], [], [], [], [], [], ...
#                            [], [], [], [], [], [], [], [], [], [], [], ...
#                            [], [], [], [], [], [], [], [], [], [], [], ...
#                            [], 0, [], [], 0, [], []);
#                    else
#                        return;
#                    end
#                end
#                
#            % The bend near the tail is furthest and, therefore, the
#            % width at the end of the tail is our most accurate
#            % estimate of the worm's width.
#            else
#                if maxWidth / cWidths(tsBounds(1)) > 2 / bodyScale
#                    errNum = 108;
#                    errMsg = ['The worm more than doubles its width ' ...
#                        'from end of its tail. Therefore, the worm is ' ...
#                        'coiled, laid an egg, and/or is significantly ' ...
#                        'obscured and cannot be segmented.'];
#                    
#                    % Organize the available worm information.
#                    if verbose
#                        warning('segWorm:DoubleTailWidth', ...
#                            ['Frame %d: ' errMsg], frame);
#                        vWorm = worm2struct(frame, contour, [], [], [], ...
#                            lfCAngles, headI, tailI, cCCLengths, [], ...
#                            [], [], [], [], [], [], [], [], [], [], [], ...
#                            [], [], [], [], [], [], [], [], [], [], [], ...
#                            [], [], [], [], [], [], [], [], [], [], [], ...
#                            [], 0, [], [], 0, [], []);
#                    else
#                        return;
#                    end
#                end
#            end
#        end
#    end
#
#



#%%
plt.figure()
plt.imshow(worm_mask, interpolation = 'none', cmap = 'gray')
plt.plot(contour[:,0], contour[:,1], 'r')
plt.xlim([0, worm_mask.shape[1]])
plt.ylim([0, worm_mask.shape[0]])
plt.grid('off')



