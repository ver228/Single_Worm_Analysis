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
    xx = major_axis*np.cos(ang)
    yy = minor_axis*np.sin(ang)
    
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
class Eccentricity_Test():
    def __init__(self, n_points=49, n_angles=8, n_eccentricities=10):
        self.n_points = n_points
        self.n_angles = n_angles
        self.eccentricity_range = np.linspace(0.1, 1, n_eccentricities)
        
        
        #create circular/elliptical skeletons
        #we remove the last point so the skeletons does not overlaps
        skels = [x[:, :-1] for x in self._make_eccentricty_test(self.n_points+1)]
        bw = mv.BasicWorm.from_skeleton_factory(skels);
        nw = mv.NormalizedWorm.from_BasicWorm_factory(bw)
        self.wf_skel = mv.WormFeatures(nw)
        
        #create circular/elliptical contours
        n_cnt_points = self.n_points*2 - 2
        cnt_points = self._make_eccentricty_test(n_cnt_points)
        
        cnt_ventral, cnt_dorsal = zip(*[split_cnt(cnt, self.n_points) for cnt in cnt_points])
        bw_cnt = mv.BasicWorm.from_contour_factory(cnt_ventral, cnt_dorsal);
        nw_cnt = mv.NormalizedWorm.from_BasicWorm_factory(bw_cnt)
        self.wf_cnt = mv.WormFeatures(nw_cnt)
        
    
    def _make_eccentricty_test(self, n_points):
        points = []
        for ecc in self.eccentricity_range:
            minor_axis = 1-ecc**2
            ellipse_p= make_ellipse(1, minor_axis, n_points)
            ellipse_rot = add_rotations(ellipse_p, self.n_angles)
            
            points += ellipse_rot
    
        return points
        
        
        
    
    
    def plot(self):
        real_eccentricities = [[x]*self.n_angles for x in self.eccentricity_range]
        real_eccentricities = sum(real_eccentricities, [])
        
        plt.figure()
        plt.subplot(2,1,1)
        plt.plot(self.wf_skel._features['posture.eccentricity'].value, 'x-')
        plt.plot(real_eccentricities, '.-')
#        skel_angs = self.wf_skel._get_and_log_feature('posture.eccentricity_and_orientation', internal_request=True).orientation
#        plt.subplot(2,2,2)
#        plt.plot(skel_angs, 's-')
        
        
        plt.subplot(2,1,2)
        plt.plot(self.wf_cnt._features['posture.eccentricity'].value, 'x-')
        plt.plot(real_eccentricities, '.-')
#        cnt_angs = self.wf_cnt._get_and_log_feature('posture.eccentricity_and_orientation', internal_request=True).orientation
#        plt.subplot(2,2,4)
#        plt.plot(cnt_angs, 's-')
#%%
test_ecc = Eccentricity_Test()
test_ecc.plot()
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
#angles = nw.angles
#for set_n in range(0, angles.shape[1], 8):
#    plt.figure()
#    
#    for ii in range(set_n, set_n+8):
#        plt.subplot(1,2,1)
#        plt.plot(angles[:, ii])
#        
#        plt.subplot(1,2,2)
#        plt.plot(nw.skeleton_x[:,ii], nw.skeleton_y[:,ii])
#        plt.xlim((-1, 1))
#        plt.ylim((-1, 1))
#        plt.axis('equal')
    

#%%
#eccentricity_test()
#wavelength_test()
#posture.bends.head
#posture.bends.neck
#posture.bends.midbody
#posture.bends.hips
#posture.bends.tail
#posture.bends.head.mean
#posture.bends.neck.mean
#posture.bends.midbody.mean
#posture.bends.hips.mean
#posture.bends.tail.mean
#posture.bends.head.std_dev
#posture.bends.neck.std_dev
#posture.bends.midbody.std_dev
#posture.bends.hips.std_dev
#posture.bends.tail.std_dev
#%%

#wp = mv.prefeatures.basic_worm.WormPartition()
#worm_parts = wp.worm_partitions
#worm_parts_f = ['head', 'neck', 'midbody', 'hips', 'tail']
#
##make_circle(radius, npoints=49,  max_ang = 2*np.pi)
#
#all_x = [np.zeros(1)]
#all_y = [np.zeros(1)]
#
#A = 1
#for field in worm_parts_f:
#    ini, fin = worm_parts[field]
#    n_points = (fin - ini)
#    radius = (n_points)/2
#    center = (fin+ini)/2
#    
#    x, y = make_circle(radius, npoints = n_points, max_ang = np.pi)
#    x += center
#    y *= A*y
#    
#    A *= -1
#    all_x.append(x[:1:-1])
#    all_y.append(y[:1:-1])
#
#xx = np.hstack(all_x)
#yy = np.hstack(all_y)
#
#skels = [np.vstack((xx,yy)), np.vstack((xx,-yy))]
##%%
#bw = mv.BasicWorm.from_skeleton_factory(skels);
#nw = mv.NormalizedWorm.from_BasicWorm_factory(bw)
#wf = mv.WormFeatures(nw)

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