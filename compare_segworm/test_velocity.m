%addpath(genpath('/Users/ajaver/Downloads/06-09-2012/'))
main_dir = '/Users/ajaver/OneDrive - Imperial College London/tests/single_worm/RawVideos/';
%main_dir = '.';

fname_new_openworm = fullfile(main_dir, 'N2 on food R_2011_09_13__11_59___3___3_features.hdf5');
features_ts = h5read(fname_new_openworm, '/features_timeseries');

fname_old_server = strrep(fname_new_openworm, '.hdf5', '.mat');
load(fname_old_server)
%%
skeletons = h5read(fname_new_openworm, '/coordinates/skeletons');
x = squeeze(skeletons(1,:,:));
y = squeeze(skeletons(2,:,:));

dx= diff(x, 1, 1);
dy= diff(y, 1, 1);
r2 = dx.*dx + dy.*dy;
lengths = sqrt(sum(r2, 1));
velocity_code = wormVelocity(x, y, 30, lengths, 0);
%%
figure
subplot(1,2,1)
plot(velocity_code.midbody.direction(1:26994), worm.locomotion.velocity.midbody.direction, '.')
xlabel('Calculated from new skeletons')
ylabel('Stored in schafer server')

subplot(1,2,2)
plot( velocity_code.midbody.direction, features_ts.midbody_motion_direction, '.')
xlabel('Calculated from new skeletons')
ylabel('Calculated using openworm')