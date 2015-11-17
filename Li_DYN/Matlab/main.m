% Created by Xiao Li, PhD at UIUC, Mechanical Science and Engineering
% main file for running RAVEN-II simulation

clear;close all;clc;
addpath graphics;

traj =4;

if traj == 1
    load('joint1.mat');
elseif traj == 2
    load('joint2.mat');
elseif traj == 3 
    load('joint3.mat');
else
    load('test_joint123.mat');
end

%
global_vars;
global int_st_sz sim_time % ODE solver's integration step size
int_st_sz = 0.0001;
% sim_time = 2;

global tau1 input2 input3 time
start_time = 1;
end_time = size_time;

jpos1 = jpos(start_time:end_time,1)*pi/180;
jvel1 = jvel(start_time:end_time,1)*pi/180;
mpos1 = mpos(start_time:end_time,1)*pi/180;
mvel1 = mvel(start_time:end_time,1)*pi/180;
tau1 = tau(start_time:end_time,1);
dac1 = tau1*1.353775*2730;

jpos2 = jpos(start_time:end_time,2)*pi/180;
jvel2 = jvel(start_time:end_time,2)*pi/180;
mpos2 = mpos(start_time:end_time,2)*pi/180;
mvel2 = mvel(start_time:end_time,2)*pi/180;
tau2 = tau(start_time:end_time,2);
dac2 = tau2*1.353775*2730;

jpos3 = jpos(start_time:end_time,3)*pi/180;
jvel3 = jvel(start_time:end_time,3)*pi/180;
mpos3 = mpos(start_time:end_time,3)*pi/180;
mvel3 = mvel(start_time:end_time,3)*pi/180;
tau3 = tau(start_time:end_time,3);
dac3 = tau3*1.353775*2730;

vol1 = -10+(dac1+32768)*0.0003051804379;
current1 = vol1*1.1442+0.0027;
tau1_tmp = current1*0.0640*12.25; % 0.0603 -> 0.0640
tau1 = (tau1_tmp+1.27*0.0311)*1;
% tau1 = tau1_tmp;
i2.737629663234212e-04*nput1 = tau1;

vol2 = -10+(dac2+32768)*0.0003051804379;
current2 = vol2*1.1442+0.0027;
tau2_tmp = current2*0.0640*12.25;
tau2 = (tau2_tmp+1.035*0.0653)*0.85;
% tau2 = tau2_tmp;
% tau2 = tau2_tmp;
input2 = tau2;

vol3 = -10+(dac3+32768)*0.0003051804379;
current3 = vol3*1.1442+0.0027;
tau3_tmp = current3*0.0640*12.25;
tau3 = (tau3_tmp-0.97*0.0425)*1.0;
% tau3 = current3*0.0603*12.25;
input3 = tau3;


time = 0:0.001:numel(dac1)/1000-0.001;
input1 = timeseries(input1,time);
input2 = timeseries(input2,time);
input3 = timeseries(input3,time);

sim_time = max(time);

% DACs = [dac1 dac2 dac3];
% fid = fopen('DACs.txt', 'w');
% fprintf(fid,'%f  %f  %f\n',DACs');
% fclose(fid);


fprintf(' initializing ... ');
initial_config;
random1 = 105*rand(1)+10;
random1_d = 105*rand(1)+10;
random1_d = random1;

random2 = 90*rand(1)+45;
random2_d = 90*rand(1)+45;
random2_d = random2;

random3 = 260*rand(1)+260;
random3_d = 260*rand(1)+260;
random3_d = random3;


theta1_0_r = 30*pi/180;       % between 10 and 115 degree, convert to radian
theta2_0_r = 30*pi/180;       % between 45 and 135 degree, convert to radian
theta3_0_r = 300/1000;     % between 260 and 520 milimeter, convert to meter


theta1_0_r = random1*pi/180;       % between 10 and 115 degree, convert to radian
theta2_0_r =random2*pi/180;       % between 45 and 135 degree, convert to radian
theta3_0_r = random3/1000;     % between 260 and 520 milimeter, convert to meter


%% set up desired configuration
% left arm
theta1_d_l = -60*pi/180;
theta2_d_l = -60*pi/180;
theta3_d_l = 300/1000;

theta1_d_r = 60*pi/180;
theta2_d_r = 60*pi/180;
theta3_d_r = 400/1000;

run_simulink;


%%
close all;
figure(1);
subplot(2,1,1);
plot(time,mvel1);
hold on;
plot(sim_mvel1.Time,sim_mvel1.Data);
grid on;
title('motor 1 velocity');

subplot(2,1,2);
plot(time,mpos1+sim_mpos1.Data(1)-mpos1(1));
hold on;
plot(sim_mpos1.Time,sim_mpos1.Data);
grid on;
title('motor 1 position');


figure(2);
subplot(2,1,1);
plot(time,mvel2);
hold on;
plot(sim_mvel2.Time,sim_mvel2.Data);
grid on;
title('motor 2 velocity');

subplot(2,1,2);
plot(time,mpos2+sim_mpos2.Data(1)-mpos2(1));
hold on;
plot(sim_mpos2.Time,sim_mpos2.Data);
grid on;
title('motor2 position');


figure(3);
subplot(2,1,1);
plot(time,mvel3);
hold on;
plot(sim_mvel3.Time,sim_mvel3.Data);
grid on;
title('motor 3 velocity');

subplot(2,1,2);
plot(time,mpos3+sim_mpos3.Data(1)-mpos3(1));
hold on;
plot(sim_mpos3.Time,sim_mpos3.Data);
grid on;
title('motor3 position');

% %%
% % close all
% figure(4)
% subplot(2,1,1)
% plot(time,jpos1-pi);
% hold on;
% plot(time,joint1_states.Data(:,1));
% 
% subplot(2,1,2)
% plot(time,jvel1);
% hold on;
% plot(time,joint1_states.Data(:,2));
% 
% figure(5)
% subplot(2,1,1)
% plot(time,jpos2-pi);
% hold on;
% plot(time,joint2_states.Data(:,1));
% 
% subplot(2,1,2)
% plot(time,jvel2);
% hold on;
% plot(time,joint2_states.Data(:,2));
% 
% figure(6)
% subplot(2,1,1)
% plot(time,jpos3);
% hold on;
% plot(time,joint3_states.Data(:,1));
% 
% subplot(2,1,2)
% plot(time,jvel3);
% hold on;
% plot(time,joint3_states.Data(:,2));


%%
% close all;
% cpp = textread('cpp_sim_result.txt');
% % figure(7);
% % plot(time,cpp(:,4));
% % hold on;
% % plot(sim_mvel1.Time,sim_mvel1.Data);
% 
% 
% figure(8);
% plot(time,cpp(:,10));
% hold on;
% plot(sim_mvel1.Time,sim_mvel1.Data);