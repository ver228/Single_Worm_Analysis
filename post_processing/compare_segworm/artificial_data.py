#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  3 11:38:26 2017

@author: ajaver
"""
import numpy as np
import matplotlib.pylab as plt
import open_worm_analysis_toolbox as mv

def _rotate_points(theta):
    c = np.cos(theta)
    s = np.sin(theta)
    rot_mat = np.array(((c, -s), (s, c)))
    return rot_mat
    
def _make_ellipse(major_axis, minor_axis, npoints = 49):
    ang = np.linspace(0, 2*np.pi, npoints)
    xx = major_axis*np.sin(ang)
    yy = minor_axis*np.cos(ang)
    
    points = np.vstack((xx,yy))
    return points

def _make_circle(radius, npoints=49):
    return _make_ellipse(radius, radius, npoints)

def _split_cnt(cnt, npoints):
    cnt1 = cnt[:, :npoints]
    cnt2 = np.append(cnt[:, npoints-1:], cnt[:, 0][:, np.newaxis], axis=1)
    cnt2 = cnt2[:, ::-1]
    
    assert np.all(cnt1[:,0] == cnt2[:,0]) and np.all(cnt1[:,-1] == cnt2[:,-1])
    assert cnt1.shape[1] == npoints and cnt2.shape[1] == npoints
    return cnt1, cnt2

def _add_rotations(points, n_angles):
    angles_to_rotate = np.linspace(0, 2*np.pi, n_angles)
    points_rot = [np.dot(points.T, _rotate_points(theta)).T for theta in angles_to_rotate]
    
    return points_rot

def _make_wave(wavelength, npoints=49, major_axis_l=1, minor_axis_l=0.25):
    xx = np.linspace(0, major_axis_l, npoints)
    kk = np.pi*wavelength
    yy = minor_axis_l*np.sin(kk*xx)
    return np.vstack((xx,yy))
#%%

def _make_eccentricty_test(npoints=49, n_angles=8, n_minor_axis=10):
    
    points = []
    for minor_axis in np.linspace(0.1, 1, n_minor_axis):
        ellipse_p= _make_ellipse(1, minor_axis, npoints = npoints)
        ellipse_rot = _add_rotations(ellipse_p, n_angles)
        
        points += ellipse_rot

    return points

def _make_eccentricty_test_skels(npoints=49):
    #let's remove the last contour. The algorithm will not work if there are redundant points
    skels = [x[:, :-1] for x in _make_eccentricty_test(npoints+1)]
    return skels


def _make_eccentricty_test_cnt(npoints=49):
    n_cnt_points = npoints*2 - 2
    cnt_points = _make_eccentricty_test(n_cnt_points)
    
    cnt_ventral, cnt_dorsal = zip(*[_split_cnt(cnt, npoints) for cnt in cnt_points])
    return cnt_ventral, cnt_dorsal
    
def eccentricity_test():
    #%%
    skels = _make_eccentricty_test_skels()
    bw = mv.BasicWorm.from_skeleton_factory(skels);
    nw = mv.NormalizedWorm.from_BasicWorm_factory(bw)
    wf = mv.WormFeatures(nw)
    
    
    
    cnt_ventral, cnt_dorsal = _make_eccentricty_test_cnt(npoints=49)
    bw_cnt = mv.BasicWorm.from_contour_factory(cnt_ventral, cnt_dorsal);
    nw_cnt = mv.NormalizedWorm.from_BasicWorm_factory(bw_cnt)
    wf_cnt = mv.WormFeatures(nw_cnt)
    
    
    plt.figure()
    plt.subplot(2,1,1)
    plt.plot(wf._features['posture.eccentricity'].value)
    plt.subplot(2,1,2)
    plt.plot(wf_cnt._features['posture.eccentricity'].value)

#%%
#n_angles = 8
#for ff in range(n_angles):
#    plt.subplot(2,4, ff+1)
#    plt.plot(nw_cnt.skeleton_x[:, ff], nw_cnt.skeleton_y[:, ff], '.-')
#    plt.plot(nw_cnt.ventral_contour_x[:, ff], nw_cnt.ventral_contour_y[:, ff], '.-')
#    plt.plot(nw_cnt.dorsal_contour_x[:, ff], nw_cnt.dorsal_contour_y[:, ff], '.-')
#    plt.axis('equal')
#%%
def make_wave_test_skels(wavelength_range=8):
    wave1_range = range(1, 8)
    skels_w1 = [_make_wave(wl) for wl in wave1_range]
    skels_w2 = [_make_wave(wl+2) + skels_w1[ii] for ii, wl in enumerate(wave1_range)]
    skels = skels_w1 + skels_w2
    return skels

#%%
skels = make_wave_test_skels()
bw = mv.BasicWorm.from_skeleton_factory(skels);
nw = mv.NormalizedWorm.from_BasicWorm_factory(bw)
wf = mv.WormFeatures(nw)


plt.plot(wf.get_features('posture.primary_wavelength').value)
    
    
eccentricity_test()
#%%


#    skel = np.vstack((xx,yy))
#    
#    for theta in np.linspace(0, np.pi, 4):
#        skel_rot = np.dot(skel.T, _rotate(theta)).T
#        #plt.plot(skel_rot[0,:], skel_rot[1,:])
#        
#        skels.append(skel_rot)
    
#%%
#for aa in [0.1, 0.25, 0.5, 1]:
#    ang = np.linspace(0, 2*np.pi, 49)
#    xx = np.sin(ang)
#    yy = aa*np.cos(ang)
#    skels.append(np.vstack((xx,yy)))
    
#bw = mv.BasicWorm.from_skeleton_factory(skels);
#nw = mv.NormalizedWorm.from_BasicWorm_factory(bw)
#wf = mv.WormFeatures(nw)
#
#
##%%
#plt.figure()
#for ii, skel in enumerate(skels):
#    plt.subplot(6,6,ii+1)
#    plt.plot(skel[1,:], skel[0,:])


#%%
#xx = np.linspace(0, 1, 49)
#for ii in range(nw.skeleton.shape[-1]):
#    plt.figure()
#    plt.subplot(2,1,1)
#    plt.plot(xx, nw.angles[:, ii])
#    plt.xlim((0,1))
#    
#    plt.subplot(2,1,2)
#    plt.plot(nw.skeleton_x[:,ii], nw.skeleton_y[:,ii], 'r')
#    #plt.xlim((0,1))
##%%
#bends_feats = ['posture.bends.head.mean', 
#               'posture.bends.neck.mean', 
#               'posture.bends.midbody.mean', 
#               'posture.bends.hips.mean', 
#               'posture.bends.tail.mean']
#
#worm_partitions = {'head': (0, 8),
#                'neck': (8, 16),
#                'midbody': (16, 33),
#                'old_midbody_velocity': (20, 29),
#                'hips': (33, 41),
#                'tail': (41, 49),
#                # refinements of ['head']
#                'head_tip': (0, 4),
#                'head_base': (4, 8),    # ""
#                # refinements of ['tail']
#                'tail_base': (40, 45),
#                'tail_tip': (45, 49),   # ""
#                'all': (0, 49),
#                # neck, midbody, and hips
#                'body': (8, 41)}
#
#
#for key in bends_feats:
#    part = key.split('.')[2]
#    dd = worm_partitions[part]
#    
#    mbend = np.nanmean(nw.angles[dd[0]:dd[1], :], axis=0)
#    plt.figure()
#    plt.plot(mbend)
#    plt.plot(wf._features[key].value, 'r')
#    plt.title(key)
#
##%%
#
##
##for key in wf._features:
##    if all(x in key for x in ['bend', 'mean']):
##        try:
##            xx = wf._features[key].value
##            plt.figure()
##            plt.plot(xx)
##            plt.title(key)
##            print(key)
##            
##        except:
##            pass
##        