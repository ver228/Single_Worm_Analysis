#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  3 11:38:26 2017

@author: ajaver
"""
import numpy as np
import matplotlib.pylab as plt
import open_worm_analysis_toolbox as mv

def rotate_points(theta):
    c = np.cos(theta)
    s = np.sin(theta)
    rot_mat = np.array(((c, -s), (s, c)))
    return rot_mat
    
def make_ellipse(major_axis, minor_axis, npoints = 49, max_ang = 2*np.pi):
    ang = np.linspace(0, max_ang, npoints)
    xx = major_axis*np.sin(ang)
    yy = minor_axis*np.cos(ang)
    
    points = np.vstack((xx,yy))
    return points

def make_circle(radius, npoints=49,  max_ang = 2*np.pi):
    return make_ellipse(radius, radius, npoints, max_ang)

def split_cnt(cnt, npoints):
    cnt1 = cnt[:, :npoints]
    cnt2 = np.append(cnt[:, npoints-1:], cnt[:, 0][:, np.newaxis], axis=1)
    cnt2 = cnt2[:, ::-1]
    
    assert np.all(cnt1[:,0] == cnt2[:,0]) and np.all(cnt1[:,-1] == cnt2[:,-1])
    assert cnt1.shape[1] == npoints and cnt2.shape[1] == npoints
    return cnt1, cnt2

def add_rotations(points, n_angles, ang_shift=0):
    angles_to_rotate = np.linspace(0, 2*np.pi, n_angles) + ang_shift
    points_rot = [np.dot(points.T, rotate_points(theta)).T for theta in angles_to_rotate]
    
    return points_rot

#%%

def _make_eccentricty_test(npoints=49, n_angles=8, n_minor_axis=10):
    
    points = []
    for minor_axis in np.linspace(0.1, 1, n_minor_axis):
        ellipse_p= make_ellipse(1, minor_axis, npoints = npoints)
        ellipse_rot = add_rotations(ellipse_p, n_angles)
        
        points += ellipse_rot

    return points

def _make_eccentricty_test_skels(npoints=49):
    #let's remove the last contour. The algorithm will not work if there are redundant points
    skels = [x[:, :-1] for x in _make_eccentricty_test(npoints+1)]
    return skels


def _make_eccentricty_test_cnt(npoints=49):
    n_cnt_points = npoints*2 - 2
    cnt_points = _make_eccentricty_test(n_cnt_points)
    
    cnt_ventral, cnt_dorsal = zip(*[split_cnt(cnt, npoints) for cnt in cnt_points])
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
    
    #%%
    plt.figure()
    plt.subplot(2,2,1)
    plt.plot(wf._features['posture.eccentricity'].value, '.-')
    skel_angs = wf._get_and_log_feature('posture.eccentricity_and_orientation', internal_request=True).orientation
    plt.subplot(2,2,2)
    plt.plot(skel_angs, '.-')
    
    
    plt.subplot(2,2,3)
    plt.plot(wf_cnt._features['posture.eccentricity'].value, '.-')
    cnt_angs = wf_cnt._get_and_log_feature('posture.eccentricity_and_orientation', internal_request=True).orientation
    plt.subplot(2,2,4)
    plt.plot(cnt_angs, '.-')
    #%%
#    for ff in range(n_angles):
#        #ang_t = angles_to_rotate[ff]*180/np.pi
#        sx = nw.skeleton_x[:, ff]
#        sy = nw.skeleton_y[:, ff]
#        plt.subplot(2,4, ff+1)
#        plt.plot(sx, sy, '.-')
#        
#        theta_d = skel_angs[ff]
#        theta_r = theta_d * (np.pi / 180)
#        wwx = sx * np.cos(theta_r) + sy * np.sin(theta_r)
#        wwy = sx * -np.sin(theta_r) + sy * np.cos(theta_r)
#        #wwx = wwx - np.mean(wwx, axis=0)
#        #wwy = wwy - np.mean(wwy, axis=0)
#        
#        plt.plot(wwx, wwy, '.-')
#        #plt.title('{} {}'.format(ang_t, skel_angs[ff]))
#        plt.axis('equal')
#%%
def make_wave(wavelength, npoints=49, major_axis_l=1, minor_axis_l=0.1, ang_shift=0):
    xx = np.linspace(0, major_axis_l, npoints)
    kk = np.pi*wavelength
    yy = minor_axis_l*np.sin(kk*xx + ang_shift)
    return np.vstack((xx,yy))

def _make_wave_test_skels(wavelength_range=8, n_angles=8):
    
    wave1_range = range(1, 8)
    skels_w1 = [make_wave(wl, minor_axis_l=0.15) for wl in wave1_range]
    skels_w2 = [make_wave(wl+2, minor_axis_l=0.15, ang_shift=np.pi/2) for wl in wave1_range]
    for kk in range(len(skels_w1)):
        skels_w2[kk][1,:] += skels_w1[kk][1,:]
    
    skels_w = skels_w1 + skels_w2
    
    return skels_w
    skels_w_rot = [add_rotations(x, n_angles) for x in skels_w]
    skels_w_rot = sum(skels_w_rot, [])
    return skels_w_rot

#%%
def wavelength_test():
    N_ANGLES = 25
    skels = _make_wave_test_skels(n_angles=N_ANGLES)
    bw = mv.BasicWorm.from_skeleton_factory(skels);
    nw = mv.NormalizedWorm.from_BasicWorm_factory(bw)
    wf = mv.WormFeatures(nw)
    #%%
    w1 = wf.get_features('posture.primary_wavelength').value
    w2 = wf.get_features('posture.secondary_wavelength').value
    
    plt.figure()
    plt.plot(w1, 's-')
    plt.plot(w2, 'o-')
        
    #%%
    
    for field in ['posture.amplitude_max',
                  'posture.amplitude_ratio',
                  'posture.track_length']:
        plt.figure()
        xx = wf.get_features(field).value
        plt.plot(xx, 'o-')
        plt.title(field)
    
    #%%
    sx = nw.skeleton_x
    sy = nw.skeleton_y
    
    theta_d = wf._get_and_log_feature('posture.eccentricity_and_orientation', internal_request=True).orientation
    theta_r = theta_d * (np.pi / 180)
    wwx = sx * np.cos(theta_r) + sy * np.sin(theta_r)
    wwy = sx * -np.sin(theta_r) + sy * np.cos(theta_r)
    wwx = wwx - np.mean(wwx, axis=0)
    wwy = wwy - np.mean(wwy, axis=0)
    #%%
    #dx = sx[-1, :] - sx[0, :]
    #dy = sy[-1, :] - sy[0, :]
    #theta_d = -np.arctan2(dy, dx)*180/np.pi
    
    #%%
    nn = 0
    ran = ((N_ANGLES*nn), (N_ANGLES*(nn+1)))
    #ang_s = np.linspace(0, 360, N_ANGLES)
    ##
    ###ang_s[ang_s>180] -= 360
    ###ang_s[ang_s<-180] += 360
    ###
    ###bad = np.abs(ang_s) >90
    ###ang_s[bad] = (180-np.abs(ang_s[bad]))*np.sign(ang_s[bad])*-1
    ##
    #plt.figure()
    #plt.plot(theta_d[ran[0]:ran[1]], 'o')
    #plt.plot(ang_s, '.')
    
    plt.figure()
    for ff in range(ran[0], ran[1]):
        #plt.plot(sx[:, ff], sy[:, ff])
        plt.subplot(4,4, ff+1)
        plt.plot(wwx[:, ff], wwy[:, ff], '.-')
        
        #plt.title('{} {}'.format(ang_t, skel_angs[ff]))
        plt.axis('equal')

#%%
#eccentricity_test()
#wavelength_test()

#%%

wp = mv.prefeatures.basic_worm.WormPartition()
worm_parts = wp.worm_partitions
worm_parts_f = ['head', 'neck', 'midbody', 'hips', 'tail']

#make_circle(radius, npoints=49,  max_ang = 2*np.pi)


ini, fin = worm_parts['head']
rad = (fin - ini)/49
center = (fin+ini)/2


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