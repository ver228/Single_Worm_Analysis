#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 26 12:08:20 2017

@author: ajaver
"""
import os
import open_worm_analysis_toolbox as mv
import numpy as np
import tables
import json
import zipfile
from scipy.interpolate import interp1d

def _h_signed_area(cnt_side1, cnt_side2):
    '''calculate the contour area using the shoelace method, the sign indicate the contour orientation.'''
    assert cnt_side1.shape == cnt_side2.shape
    if cnt_side1.ndim == 2:
        # if it is only two dimenssion (as if in a single skeleton).
        # Add an extra dimension to be compatible with the rest of the code
        cnt_side1 = cnt_side1[:, :, np.newaxis]
        cnt_side2 = cnt_side2[:, :, np.newaxis]

    contour = np.vstack((cnt_side1, cnt_side2[::-1, :, :]))
    signed_area = np.sum(
        contour[:-1,0, :] * contour[1:,1, :] -
        contour[1:,0, :] * contour[:-1,1, :],
        axis=0)/ 2
    
    assert signed_area.size == cnt_side1.shape[-1]
    return signed_area

def _h_get_angle(x, y, segment_size):
    '''
    Get the skeleton angles from its x, y coordinates
    '''
    assert(x.ndim == 1)
    assert(y.ndim == 1)

    dx = x[segment_size:] - x[:-segment_size]
    dy = y[segment_size:] - y[:-segment_size]

    pad_down = int(np.floor(segment_size / 2))
    pad_up = int(np.ceil(segment_size / 2))

    # pad the rest of the array with delta of one segment
    #dx = np.hstack((np.diff(x[0:pad_down]), dx, np.diff(x[-pad_up:])))
    #dy = np.hstack((np.diff(y[0:pad_down]), dy, np.diff(y[-pad_up:])))

    #dx = np.diff(x);
    #dy = np.diff(y);

    angles = np.arctan2(dx, dy)
    dAngles = np.diff(angles)

    #    % need to deal with cases where angle changes discontinuously from -pi
    #    % to pi and pi to -pi.  In these cases, subtract 2pi and add 2pi
    #    % respectively to all remaining points.  This effectively extends the
    #    % range outside the -pi to pi range.  Everything is re-centred later
    #    % when we subtract off the mean.
    #
    #    % find discontinuities larger than pi (skeleton cannot change direction
    #    % more than pi from one segment to the next)
    # %+1 to cancel shift of diff
    positiveJumps = np.where(dAngles > np.pi)[0] + 1
    negativeJumps = np.where(dAngles < -np.pi)[0] + 1
    
    
    #% subtract 2pi from remainging data after positive jumps
    for jump in positiveJumps:
        angles[jump:] = angles[jump:] - 2 * np.pi

    #% add 2pi to remaining data after negative jumps
    for jump in negativeJumps:
        angles[jump:] = angles[jump:] + 2 * np.pi

    #% rotate skeleton angles so that mean orientation is zero
    meanAngle = np.mean(angles)
    angles = angles - meanAngle

    pad_left = np.full(pad_down, np.nan)
    pad_right = np.full(pad_up, np.nan)
    angles = np.hstack((pad_left, angles, pad_right))
    return (angles, meanAngle)

def _get_resampled_curve(curve, resampling_n):
    dx = np.diff(curve[:, 0])
    dy = np.diff(curve[:, 1])
    dr = np.sqrt(dx * dx + dy * dy)
    
    lengths = np.cumsum(dr)
    lengths = np.hstack((0, lengths))  # add the first point
    tot_length = lengths[-1]
    
    fx = interp1d(lengths, curve[:, 0])
    fy = interp1d(lengths, curve[:, 1])
    subLengths = np.linspace(0 + np.finfo(float).eps, tot_length, resampling_n)
    resampled_curve = np.zeros((resampling_n, 2))
    resampled_curve[:, 0] = fx(subLengths)
    resampled_curve[:, 1] = fy(subLengths)
    return resampled_curve

def _h_width(
        skeleton,
        contour_side1,
        contour_side2,
        resampling_n):
    '''Find the contour width from each skeleton point.
    The method search closer contour points to a perpendicular line to the each
    of the skeleton points. 
    
   '''
    #TODO optimize this code!!! It should be to decrease time by limiting the search space to 
    #neighboring points.
    
    n_segments = skeleton.shape[0]
    cnt_width = np.zeros(n_segments)
    
    #import matplotlib.pylab as plt
    #plt.plot(contour_side1[:,0], contour_side1[:,1], '.')
    #plt.plot(contour_side2[:,0], contour_side2[:,1], '.')
    #plt.plot(skeleton[:,0], skeleton[:,1], '.')
    
    for skel_ind in range(1, n_segments-1):
        # get the slop of a line perpendicular to the keleton
        dR = skeleton[skel_ind + 1] - skeleton[skel_ind - 1]
        #m = dR[1]/dR[0]; M = -1/m
        a = -dR[0]
        b = +dR[1]
        c = b * skeleton[skel_ind, 1] - a * skeleton[skel_ind, 0]
        
        # modified from https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line
        #a = M, b = -1
        
        
        dist2cnt1 = np.sum((contour_side1 - skeleton[skel_ind])**2, axis=1)
        dist2cnt2 = np.sum((contour_side2 - skeleton[skel_ind])**2, axis=1)
        
        #get a threshold otherwise it might get a faraway point that it is closer to the parallel line
        width_th = 4*max(np.min(dist2cnt1), np.min(dist2cnt2))
        
        d1 = np.abs(a * contour_side1[:, 0] - b * contour_side1[:, 1] + c)
        d1[dist2cnt1 > width_th] = np.nan
        
        d2 = np.abs(a * contour_side2[:, 0] - b * contour_side2[:, 1] + c)
        d2[dist2cnt2 > width_th] = np.nan
        
        
        try:
            cnt1_ind = np.nanargmin(d1)
            cnt2_ind = np.nanargmin(d2)
            cnt_width[skel_ind] = dist2cnt1[cnt1_ind] + dist2cnt2[cnt2_ind]
            
            #xx = (contour_side1[cnt1_ind,0], skeleton[skel_ind,0], contour_side2[cnt2_ind,0])
            #yy = (contour_side1[cnt1_ind,1], skeleton[skel_ind,1], contour_side2[cnt2_ind,1])
            #plt.plot(xx, yy, 'o-')
            
        except ValueError:
            cnt1_ind = np.nan
            cnt2_ind = np.nan
            cnt_width[skel_ind] = np.nan
    
    return cnt_width

def _get_skels_segworm(segworm_feat_file):
    #load segworm data
    with tables.File(segworm_feat_file, 'r') as fid:
        segworm_x = -fid.get_node('/worm/posture/skeleton/x')[:]
        segworm_y = -fid.get_node('/worm/posture/skeleton/y')[:]
        skels_segworm = np.stack((segworm_x,segworm_y), axis=2)
    
    return skels_segworm



class WormFromWCON(mv.NormalizedWorm):
    """
    Encapsulates the notion of a worm's elementary measurements, scaled
    (i.e. "normalized") to 49 points along the length of the worm.
    In the future it might become a method of NormalizedWorm,
    but for the moment let's test it as a separate identity
    """

    def __init__(self, wcon_file):
        # Populates an empty normalized worm.
        mv.NormalizedWorm.__init__(self)
        
        try:
            with zipfile.ZipFile(wcon_file, mode='r') as zf:
                fname = os.path.basename(wcon_file).replace('.zip', '')
                wcon_txt = zf.read(fname).decode("utf-8")
        except:
            #if it is not a .zip file
            with open(wcon_file, 'r') as fid:
                wcon_txt = fid.read()
        
        self._wcon_feats = json.loads(wcon_txt)
        
        _data = self._wcon_feats['data'][0]
        def _read_repack(field_x):
            field_y = field_x.replace('x', 'y')
            dat =  np.stack((_data[field_x], _data[field_y]), axis=2).astype(np.float)
            
            #the openworm toolbox requires 49x2xn
            # roll axis to have it as 49x2xn
            dat = np.rollaxis(dat, 0, dat.ndim)
            # change the memory order so the last dimension changes slowly
            dat = np.asfortranarray(dat)
            
            return dat

        
        #fields requiered by NormalizedWorm (will be filled in readSkeletonsData)
        #self.skeleton_id = None
        self.timestamp = np.array(_data['t']).astype(np.float)
        self.skeleton = _read_repack('x')
        self.ventral_contour = _read_repack('@OMG x_ventral_contour')
        self.dorsal_contour = _read_repack('@OMG x_dorsal_contour')
        
        # video info, for the moment we intialize it with the fps
        #self.video_info = mv.VideoInfo('', self.fps)
        self.video_info.frame_code = np.isnan(self.skeleton[0,0,:])

        
        self.time_axis = 2
        self.coord_axis = 1
        self.segment_axis = 0
        
        
    @property
    def length(self):
        try:
            return self._length
        except:
            #calculate length
            dR = np.diff(self.skeleton, axis=0)**2
            self._length = np.sqrt(np.sum(dR, axis=(0, 1)))
            return self._length
    
    @property
    def n_segments(self):
        return self.skeleton.shape[self.segment_axis]

    
    @property
    def num_frames(self):
        return self.skeleton.shape[self.time_axis]
    
    
    @property
    def angles(self):
        '''calculate the angles of each of the skeletons'''
        try:
            return self._angles
        except:
            
            self._angles = np.full((self.n_segments, self.num_frames), np.nan)
            #meanAngles_all = np.zeros(tot)
            
            for ss in range(self.num_frames):
                if np.isnan(self.skeleton[0, 0, ss]):
                    continue  # skip if skeleton is invalid
                
                self._angles[:, ss], _ = \
                _h_get_angle(self.skeleton_x[:, ss], 
                           self.skeleton_y[:, ss], 
                           segment_size=5)
            return self._angles
        
    @property
    def widths(self):
        '''calculate the widths from the skeleton and contours'''
        try:
            return self._widths
        except:
            self._widths = np.zeros((self.n_segments, self.num_frames))
            resampling_n = self.n_segments*4
            for ss in range(self.num_frames):
                if np.isnan(self.skeleton[0, 0, ss]):
                    continue  # skip if skeleton is invalid
                
                skeleton = self.skeleton[:, :, ss]
                contour_side1 = _get_resampled_curve(self.dorsal_contour[:, :, ss], resampling_n)
                contour_side2 = _get_resampled_curve(self.ventral_contour[:, :, ss], resampling_n)
                
                self._widths[:,ss] = _h_width(skeleton, 
                                      contour_side1, 
                                      contour_side2, 
                                      resampling_n)
                if ss % 1000 == 0:
                    print('Calculating contour widths {} of {}'.format(ss, self.num_frames))
            return self._widths
    
    @property
    def area(self):
        try:
            return self._area
        except:
            signed_area = _h_signed_area(self.dorsal_contour, self.ventral_contour)
            self._area = np.abs(signed_area)
            return self._area

if __name__ == '__main__':
    main_dir = '/Users/ajaver/OneDrive - Imperial College London/Local_Videos/single_worm/global_sample_v3/'
    base_name = 'N2 on food L_2010_08_03__10_17_54___7___1'
    
    feat_file = os.path.join(main_dir, base_name + '_features.hdf5')
    wcon_file = os.path.join(main_dir, base_name + '.wcon.zip')
    wcon_file = os.path.join(main_dir, base_name + '.wcon')
    
    
    nw = WormFromWCON(wcon_file)
    #print(nw.area.shape)
    wf = mv.WormFeatures(nw)


    #wp = mv.NormalizedWormPlottable(nw, interactive=False)
    #wp.show()
    


