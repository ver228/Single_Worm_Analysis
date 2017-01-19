# -*- coding: utf-8 -*-
"""
Created on Thu May 12 16:14:10 2016

@author: ajaver
"""
import tables
from scipy.io import loadmat

import pandas as pd
import matplotlib.pylab as plt
import numpy as np
import seaborn as sns
import shutil
import os

from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

engine_v2 = create_engine(r'mysql+pymysql://ajaver:@localhost/single_worm_db_v2')
Base = automap_base()

Base.prepare(engine_v2, reflect=True)
Experiment = Base.classes.experiments;
Strain = Base.classes.strains;
SegwormFeature = Base.classes.segworm_features;
ProgressTrack = Base.classes.progress_tracks;
SegWormComparison = Base.classes.segworm_comparisons;
ProgressMask = Base.classes.progress_masks;
session_v2 = Session(engine_v2)

#%%
bad_frames_global = {
'247 JU438 on food L_2011_04_12__15_06_54___1___7.hdf5': [(24666,24666), (24676,24678)],
'acr-3 (ok2049)X on food R_2010_02_19__10_45_18___8___5.hdf5': 
    [(17148,17157), (17163,17168), (17189,17189), (17192,17193), (17213,17213),
     (17148,17148), (17157,17157), (17163,17163), (17165,17168)],
'acr-11 (ok1345) on food L_2010_02_24__10_46_05___8___5.hdf5': 
    [(14332,14332), (14334,14334), (19497,19498), (19501,19501), (19503,19503),
     (19515,19518), (19520,19520), (19524,19524), (19527,19527)],
'N2 on food L_2009_11_19__12_47_15___2___7.hdf5':[(13933,13946)],
'QT309 (nRH01) on food L_2011_10_04__12_15___3___1.hdf5':
    [(19495,19543), (19588,19637), (19644,19661), (19722,19750), (21246,21257)],
'unc-32 (e189) on food R_2009_12_09__15_57_03___1___13.hdf5':[(328,508)],
'unc-69 (e587) on food R_2010_04_14__14_38_28___2___11.hdf5':[(4003,4156)]
}

good_files_global = ['135 CB4852 on food L_2011_03_29__15_53_00___1___10.hdf5', '247 JU438 on food L_2011_03_03__11_18___3___1.hdf5', '300 LSJ1 on food R_2011_03_22__15_53___3___10.hdf5', '399 CB4856 on food R_2011_02_17__11_39_10___8___3.hdf5', '431 JU298 on food L_2011_02_17__10_59_34___2___1.hdf5', '431 JU298 on food R_2010_11_25__16_38_28___7___7.hdf5', '431 JU298 on food R_2011_03_10__11_31_41___7___3.hdf5', '507 ED3054 on food R_2011_03_03__12_32_06__5.hdf5', '575 JU440 on food R_2011_03_04__12_18_25___6___5.hdf5', '814 JU393 on food L_2011_04_12__12_30___3___5.hdf5', '972 JU345 on food R_2011_03_30__12_52_07__5.hdf5', 'acr-15 (ok1412) on food R_2011_06_14__12_29_12___1___6.hdf5', 'C45A6.2 (ok1187) on food L_2010_03_25__12_55_52__8.hdf5', 'daf-3 (e1376)X on food R_2010_07_27__11_06_33___7___3.hdf5', 'daf-7 (m62)III on food R_2010_07_27__12_36_42___2___6.hdf5', 'daf-7 (m62)III on food R_2010_07_29__12_57_15___8___7.hdf5', 'del-1 (ok150) on food L_2010_07_06__12_07_15___2___7.hdf5', 'del-1 (ok150)X on food R_2012_03_08__15_44_54___2___8.hdf5', 'egl-12 (n602)V on food R_2010_07_09__15_02_02___2___7.hdf5', 'egl-12 (n602)V on food R_2010_07_16__12_08_27___7___6.hdf5', 'egl-14 (n549)X on food L_2010_07_15__16_22_45__14.hdf5', 'egl-21 (n476)IV on food L_2010_07_20__12_03_29___1___6.hdf5', 'egl-27 (ok151)II on food L_2010_07_23__15_33_07___1___12.hdf5', 'egl-33 (n151)I on food L_2010_05_14__15_34___3___14.hdf5', 'egl-43 (n1079)II on food L_2010_08_05__13_04___3___8.hdf5', 'egl-47 (n1081)V on food R_2010_05_11__12_02_49___1___4.hdf5', 'egl-49 (n1107) on food R_2010_05_11__11_24___3___2.hdf5', 'egl-49 (n1107) on food R_2010_05_13__11_36_01__5.hdf5', 'egl-50 (n1086) on food R_2009_12_10__10_45_23___7___2.hdf5', 'flp-1 (yn2) on food L_2010_01_15__10_21_15___2___1.hdf5', 'flp-18 (dp99)X on food R_2010_01_21__13_07_56___8___8.hdf5', 'gpa-6 (ph480)X on food L_2010_03_04__12_04_20___4___10.hdf5', 'gpa-7 (pk610)IV on food L_2010_03_11__12_25_19___2___7.hdf5', 'gpa-16 (ok2349) on food L_2010_12_14__15_13_59___1___5.hdf5', 'gpb-2 (sa603)I on food L_2010_03_05__12_33_07___1___10.hdf5', 'ins-4 (ok3534) on food L_2011_05_17__12_55_01___8___7.hdf5', 'ins-4 (ok3534)II on food R_2011_05_12__10_43_01___8___1.hdf5', 'M05B5.6 (tm3092) on food L_2010_07_08__12_29_36___7___7.hdf5', 'M124 on food L_2010_05_14__16_36_33__15.hdf5', 'M0585.6 (tm3085) on food L_2010_04_08__14_55_21___1___8.hdf5', 'mec-4 (u253) on food L_2010_10_28__15_53_09___7___10.hdf5', 'mec-7 (v448) on food R_2010_10_28__10_58_31___7___1.hdf5', 'mec-18 (e228) on food R_2010_10_21__12_04_55___2___4.hdf5', 'mod-5 (n822)I on food L_2009_11_19__13_09_20___1___7.hdf5', 'N2 male on food R_2012_02_22__10_17_38___2___1.hdf5', 'N2 on food L_2010_01_12__10_40_17___4___1.hdf5', 'N2 on food L_2010_01_19__15_46_31___2___11.hdf5', 'N2 on food L_2010_10_15__11_25_26___2___2.hdf5', 'N2 on food L_2010_11_26__15_07_04___8___9.hdf5', 'N2 on food L_2011_03_29__11_08_53___2___1.hdf5', 'N2 on food R_2010_10_21__14_47_42__8.hdf5', 'N2 on food R_2010_11_26__11_18_47__3.hdf5', 'N2 on food R_2010_12_14__15_38___3___7.hdf5', 'nlp-14 (tm1880)X on food R_2010_03_12__13_05_00___4___9.hdf5', 'npr-8 (tm1553) on food  R_2010_01_26__15_37_57___2___11.hdf5', 'npr-9 (tm1652) on food R_2010_01_28__12_15___3___6.hdf5', 'npr-11 (ok594)X  on food L_2010_01_28__11_13_53___2___3.hdf5', 'npr-12 (tm1498)IV on food L_2010_12_16__15_47_51__7.hdf5', 'npr-12 (tm1498)IV on food L_2011_02_04__11_49_01___8___4.hdf5', 'ocr-3 (a1537) on food R_2010_04_23__12_19___3___8.hdf5', 'ocr-4 (vs137); ocr-2 (9447); ocr-1 (ok134) on food R_2010_07_06__12_28_59___8___8.hdf5', 'osm-9 (ky10) on food L_2010_06_15__14_55___3___8.hdf5', 'pgn-66 (ok1507) on food R_2010_04_29__11_29_06___4___3.hdf5', 'pmk-1 (km25) on food R_2010_04_21__11_28_07___2___4.hdf5', 'ric-19 (ok883) on food L_2011_08_24__10_02_51__1.hdf5', 'ser-1 (ok345) on food L_2009_12_15__15_08___3___11.hdf5', 'ser-2 (pk1357)X on food R_2009_12_17__11_44_32___1___3.hdf5', 'ser-7 (tm1325) on food L_2009_12_14__12_44_16___7___7.hdf5', 'sma-2 (e502) on food L_2011_10_13__11_55_19__2.hdf5', 'sma-2 (e502)III on food L_2011_10_06__12_56_12___7___7.hdf5', 'snf-11 (ok156)V on food R_2009_11_19__16_35_11___1___11.hdf5', 'spe-41 (sy693); him-5 (e1490) on food R_2010_04_09__12_24_35___2___7.hdf5', 'spe-41 (sy693); him-5 (e1490) on food R_2010_04_09__15_35_37___8___13.hdf5', 'tom-1 (ok1285) on food R_2010_08_03__11_56_54___8___6.hdf5', 'unc-2 (gk3206)X on food L_2012_03_15__10_54_42___3___5.hdf5', 'unc-7 (cb5) on food L_2010_09_09__11_47_49___7___6.hdf5', 'unc-26 (m2)IV on food L_2010_04_16__11_00_22__3.hdf5', 'unc-40 (n324)I on food L_2010_04_13__13_05_36___7___9.hdf5', 'unc-43 (e755)IV on food R_2010_08_19__15_46_50___4___10.hdf5', 'unc-60 (e723)V on food L_2010_04_13__15_58_27___4___15.hdf5', 'unc-75 (e950)I on food R_2010_09_23__11_57_14___8___4.hdf5', 'unc-79 (e1068)III on food R_2010_04_14__15_40_04___7___15.hdf5', 'unc-80 (e1069) nRHO-1 G14Von food R_2012_02_09__12_13___3___5.hdf5', 'unc-86 (e1416)III on food R_2010_08_06__12_15___3___5.hdf5', 'unc-103 (e1597)V on food R_2010_08_20__13_14_33___2___10.hdf5', 'vab-7 (e1562)III on food R_2011_10_04__13_22_20__4.hdf5', 'acr-11 (ok1345) on food L_2010_02_24__10_47_34___7___5.hdf5', 'daf-3 (e1376)X on food R_2010_07_29__15_16_26___2___9.hdf5', 'N2 on food L_2011_08_31__13_15_04___1___6.hdf5', 'N2 on food R_2010_02_26__08_45_25__1.hdf5', 'N2 on food R_2010_01_11__11_37_05___4___1.hdf5', 'nca-1 (gk9) nRHO-1 QT309 on food L_2011_11_10__10_15_15___2___1.hdf5', 'N2 on food R_2010_05_14__10_08___3___1.hdf5']

for fname in good_files_global:
    bad_frames_global[fname] = []

#%%
bad_frames_p = {
'f-5 (e1386) on food R_2010_07_22__14_45_57___8___8.hdf5':
    [(2458,2471),(2481,2502),(4754,4790),(15103,15107)], 
'syg-1 (ok3640) on food R_2010_07_27__14_46_42___7___9.hdf5':
    [(25836,25841),(25860,25862),(25871,25877),(25887,25887),(25897,25897)], 
'egl-43 (n1079)II on food L_2010_09_16__13_03_18___1___6.hdf5':
    [(1065,1157), (5310,5315)], 
'egl-43 (n1079)II on food L_2010_08_06__12_33_42___1___6.hdf5':
    [(24976, 25051), (25698, 25713), (25764, 25775), (25784, 25785), (25834, 25847), (26885, 26997)],
'gpa-5 (pk376)X on food L_2010_02_25__13_06_02___8___11.hdf5':
    [(13132, 13177), (13192, 13366), (13376, 13378), (13409, 13492)],
'N2 on food R_2010_02_19__09_23_46___8___1.hdf5':
    [(16413, 16413), (16419, 16419), (16425, 16426), (16434, 16434), (16440, 16440), (16449, 16474)],
'acr-11 (ok1345) on food L_2010_02_24__10_46_05___8___5.hdf5':
    [(14332, 14334), (19497, 19503), (19515, 19527)],
'egl-43 (n1079)II on food L_2010_08_05__13_06_06___8___8.hdf5':
    [(8735,8758)],
'unc-26 (m2)IV on food L_2010_04_16__11_57___3___6.hdf5':
    [(4986, 4989), (5052, 5673), (5891, 6410), (6421, 6422), (6492, 6556), (6559, 6689), (6692, 6692), (6925, 6947)],
'unc-101 (e1265) on food R_2010_09_24__11_37_44___7___2.hdf5':
    [(22375,24220)],
'unc-26 (m2)IV on food L_2010_04_16__15_10_08___4___11.hdf5':
    [(1442, 1873), (2086, 2321), (2327, 2334), (2358, 2358), (2374, 2387), (2393, 2416), (2460, 2608), (2623, 2640), (2651, 2654), (2666, 2666), (2675, 2687), (2697, 2720), (2728, 8206), (8220, 8222), (8309, 8903), (8912, 8923), (8930, 8969), (8977, 9075), (9123, 9123), (9171, 9171), (9179, 9179), (9188, 9190), (9196, 9198), (9330, 9330), (9348, 9348), (9355, 9369), (9396, 9398), (9411, 9413), (9783, 9783), (9793, 9793), (9898, 9898), (9969, 9969), (9990, 9992), (10014, 10014), (10021, 10130), (10185, 10191), (10230, 10230), (10332, 10333), (18528, 18528), (18534, 18556), (18580, 19408)], 
'unc-69 (e587) on food L_2010_04_14__14_37_33___1___11.hdf5':
    [(6266, 6443), (16188, 16270), (16276, 16300), (16306, 16313), (16321, 16321), (16332, 16341), (16356, 16356), (16380, 18024), (18030, 18196)],
}

badly_segmented = {
'unc-3 (e151)X on food L_2011_11_04__10_25_14___2___3.hdf5':[(3939, 3940), (3954, 3994), (4049, 4057), (4088, 4156), (4265, 4277), (4321, 4354), (4486, 4489), (4497, 4609), (5377, 5456), (5475, 5481), (5490, 5504), (5510, 5510), (5524, 5526), (5811, 6319), (6472, 6475), (6484, 6901), (6922, 6922), (6946, 6946), (6954, 6961), (7234, 7235), (18068, 18072), (18079, 18188), (18205, 18205), (18313, 18373), (19717, 19779), (19788, 19788), (25740, 25778), (25786, 25786), (25794, 25844), (25850, 25853), (25971, 25971), (25979, 26086), (26117, 26131), (26158, 26317), (26423, 26441), (26453, 26530), (26595, 26595), (26607, 26701)],
'unc-104 (e1265)III on food L_2011_10_18__11_29_31__1.hdf5':-1, 
'unc-37 (e2126)I on food L_2010_04_13__15_00_57__12.hdf5':-1
}

bad_oriented = ['egl-31 (n472)I on food R_2010_07_15__14_36_47___8___9.hdf5 ', 'egl-31 (n472)I on food R_2010_07_15__14_38_02__9.hdf5', 'egl-47 (n1081)V on food L_2010_12_16__15_25___3___6.hdf5', 'sem-4 (ga82)I on food R_2010_07_27__16_24_15___2___13.hdf5', 'unc-115 (mn481)X on food R_2010_08_20__15_03_37___1___11.hdf5']
good_files_p = ['acr-10 (OK3064) on food R_2010_02_23__12_15_15___8___10.hdf5', 'daf-5 (e1386)II on food L_2010_07_22__14_46_33__8.hdf5', 'egl-6 (n592)X on food R_2010_05_13__15_47___3___13.hdf5', 'egl-10 (md176) on food L_2010_05_19__11_44_37___4___2.hdf5', 'egl-11 (n587)V on food R_2010_05_14__13_07___3___10.hdf5', 'egl-12 (n602)V on food R_2010_07_09__15_02_02___2___7.hdf5', 'egl-18 (ok290)IV on food R_2010_07_16__12_27_43___8___7.hdf5', 'egl-21 (n611)V on food L_2010_05_13__12_36_32___7___8.hdf5', 'egl-27 (ok151)II on food L_2010_08_05__14_44___3___10.hdf5', 'egl-28 (n570)II on food R_2010_07_20__15_56_51___1___12.hdf5', 'egl-43 (n1079)II on food L_2010_07_15__15_52_44___1___13.hdf5', 'gpa-6 (ph480)X on food L_2010_02_26__09_24_28___8___3.hdf5', 'gpa-8 (pk345)V on food R_2010_03_05__11_15_21___7___6.hdf5', 'gpc-1 (pk298) on food R_2010_03_09__15_13_17___2___10.hdf5', 'mec-7 (v448) on food L_2010_10_14__16_36_54___1___5.hdf5', 'mec-7 (v448) on food L_2010_10_21__11_28_13___7___2.hdf5', 'mec-7 (v448) on food R_2010_09_30__12_43_53___1___9.hdf5', 'mec-7 (v448) on food R_2010_11_11__16_19_04___7___10.hdf5', 'N2 on food L_2011_03_30__15_12_28___7___7.hdf5', 'nlp-1 (ok1469)X on food R_2010_03_12__11_23_33___2___5.hdf5', 'nlp-8 (ok1799)I on food L_2010_12_16__16_05_45___1___8.hdf5', 'nlp-14 (tm1880)X on food R_2010_03_18__13_14_07___8___10.hdf5', 'npr-8 (tm1553) on food L_2010_01_22__12_32___3___8.hdf5', 'spe-41 (sy693); him-5 (e1490) on food L_2010_04_09__15_35_58___7___13.hdf5', 'T28F2.7 (ok2657) on food L_2010_03_19__09_33_34___1___3.hdf5', 'T28F2.7 (ok2657) on food R_2010_03_31__11_16_21__1.hdf5', 'T28F7.2 (ok2657) on food L_2010_03_31__11_14_39___4___2.hdf5', 'tph-1 superoutcrossed on food R_2009_12_17__16_35_29__12.hdf5', 'unc-1 (e94)X on food R_2011_10_04__13_18_41___2___4.hdf5', 'unc-1 (e1598)X on food L_2010_04_14__11_59_55___8___7.hdf5', 'unc-2 (ox106) on food R_2010_04_14__15_57_53___8___15.hdf5', 'unc-8 rev on food L_2010_04_08__15_16_18__10.hdf5', 'unc-38 (e264)I on food R_2010_08_19__12_37_26___8___7.hdf5', 'unc-69 (e587) on food L_2010_04_15__12_46_32___1___9.hdf5', 'unc-86 (e1416)III on food R_2010_09_24__11_54_11___1___3.hdf5', 'unc-89 (e1460)I on food L_2010_04_13__12_06_36___8___6.hdf5', 'unc-103 (e1597)II on food L_2010_08_06__15_39_31___2___11.hdf5', 'egl-8 (v488) on food R_2011_09_20__13_33_10___7___7.hdf5', 'acr-9 (ok933)X on food R_2010_02_23__11_15_40___8___7.hdf5', 'egl-14 (n549)X on food L_2010_07_09__12_02_12___1___5.hdf5', 'egl-33 (n151)I on food R_2010_05_14__15_37_04__12.hdf5', 'unc-18 (e81)X on food R_2011_08_24__13_01___3___10.hdf5', 'unc-63 (ok1075) on food L_2010_04_16__12_57_13___8___8.hdf5', 'N2 on food R_2011_05_24__13_03_48___7___6.hdf5', 'egl-23 (n601)IV on food L_2010_07_15__15_15_46___4___11.hdf5', 'unc-16 (e109) on food L_2009_12_11__12_21___3___2.hdf5', 'flp-25 (gk1016)III on food L_2010_01_12__13_07_15___4___8.hdf5', 'gpa-6 (ph480)X on food L_2010_03_04__12_05_09___8___10.hdf5.', 'mec-7 (v448) on food L_2010_11_11__11_47_32___2___3.hdf5', 'ins-4 (ok3534)II on food L_2011_05_19__16_02___3___10.hdf5', 'unc-79 (e1068)III on food L_2010_04_13__15_39_23___8___14.hdf5', 'egl-21 (n476)IV on food L_2010_07_23__15_16_04___8___11.hdf5', 'egl-21 (n611)V on food R_2010_05_13__12_36_51__8.hdf5', 'unc-116 (e2310)III on food L_2010_07_29__14_56___3___8.hdf5', 'N2 on food R_2011_08_31__15_08_38___2___7.hdf5']

for fname in good_files_p:
    bad_frames_p[fname] = []
for fname in bad_oriented:
    bad_frames_p[fname] = -1
#%%
def getSkelError(feat_file, segworm_feat_file):
    with tables.File(feat_file, 'r') as fid:
        if '/features_means' in fid and \
        fid.get_node('/features_means').attrs['has_finished'] and \
        fid.get_node('/features_timeseries').shape[0]>0:
            skeletons = fid.get_node('/skeletons')[:]
            frame_range = fid.get_node('/features_events/worm_1')._v_attrs['frame_range']

    skeletons = np.pad(skeletons, [(frame_range[0],0), (0,0), (0,0)], 
                   'constant', constant_values = np.nan)
    
    #load segworm data
    fvars = loadmat(segworm_feat_file, struct_as_record=False, squeeze_me=True)
    segworm_x = -fvars['worm'].posture.skeleton.x.T
    segworm_y = -fvars['worm'].posture.skeleton.y.T
    
    #correct in case the data has different size shape
    max_n_skel = min(segworm_x.shape[0], skeletons.shape[0])
    segworm_x = segworm_x[:max_n_skel]
    segworm_y = segworm_y[:max_n_skel]
    skeletons = skeletons[:max_n_skel]
    
    #calculate the square root of the mean squared error
    dX = skeletons[:,:,0] - segworm_x
    dY = skeletons[:,:,1] - segworm_y
    R_error = dX*dX + dY*dY
    skel_error = np.sqrt(np.mean(R_error, axis=1))

    dX_switched = skeletons[:,::-1,0] - segworm_x
    dY_switched = skeletons[:,::-1,1] - segworm_y
    switched_error = np.sqrt(np.mean(dX_switched**2 + dY_switched**2, axis=1))

    return skel_error, switched_error, skeletons


#%%
main_dir = '/Users/ajaver/Desktop/Videos/single_worm/global_sample/'

#for base_name in bad_frames_global:

base_name = 'acr-11 (ok1345) on food L_2010_02_24__10_46_05___8___5.hdf5'

skeletons_file =os.path.join(main_dir, base_name.replace('.hdf5', '_skeletons.hdf5'))
feat_file = os.path.join(main_dir, base_name.replace('.hdf5', '_features.hdf5'))
segworm_feat_file = os.path.join(main_dir, base_name.replace('.hdf5', '_features.mat'))

skel_error, switched_error, skeletons = getSkelError(feat_file, segworm_feat_file)

bad_orient = np.zeros(skel_error.shape, np.bool)
with tables.File(skeletons_file, 'r') as fid:
    timestamp_ind = fid.get_node('/timestamp/raw')[:].astype(np.int)

for bf in bad_frames_global[base_name]:
    bad_orient[timestamp_ind[bf[0]:bf[1]+1]] = True


mismatch_orient = skel_error>switched_error

tot_valid_skel = np.sum(~np.isnan(skeletons[:,0,0]))
tot_mutual_skel = np.sum(~np.isnan(skel_error))
tot_mismatch = np.sum(mismatch_orient)
tot_good_skel = np.sum(~np.isnan(skeletons[:,0,0]) & ~bad_orient)
