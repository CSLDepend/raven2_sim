clear;clc;close all;

% filenames = {'test_1.csv','test_2.csv','test_3.csv','test_4.csv'};
filenames = {'../../Tests/new_test_1.csv','../../Tests/new_test_2.csv','../../Tests/new_test_3.csv'};
file_num = 3;
D = readtable(filenames{file_num});
% Number of position variables
pos_n = 6;
% Number of orientation variables
ori_n = 18;
% Number of joint variables
joint_n = 16;

% Headers for position and orientation variables
% dac_headers = {'field_current_cmd0','field_current_cmd1','field_current_cmd2',...
%     'field_current_cmd3','field_current_cmd4','field_current_cmd5',...
%     'field_current_cmd6','field_current_cmd7','field_current_cmd8',...
%     'field_current_cmd9','field_current_cmd10','field_current_cmd11',...
%     'field_current_cmd12','field_current_cmd13','field_current_cmd14',...
%     'field_current_cmd15'};
tau_headers = {'field_tau0','field_tau1','field_tau2',...
    'field_tau3','field_tau4','field_tau5',...
    'field_tau6','field_tau7','field_tau8',...
    'field_tau9','field_tau10','field_tau11',...
    'field_tau12','field_tau13','field_tau14',...
    'field_tau15'};
mpos_headers = {'field_mpos0','field_mpos1','field_mpos2',...
    'field_mpos3','field_mpos4','field_mpos5',...
    'field_mpos6','field_mpos7','field_mpos8',...
    'field_mpos9','field_mpos10','field_mpos11',...
    'field_mpos12','field_mpos13','field_mpos14',...
    'field_mpos15'};
jpos_headers = {'field_jpos0','field_jpos1','field_jpos2',...
    'field_jpos3','field_jpos4','field_jpos5',...
    'field_jpos6','field_jpos7','field_jpos8',...
    'field_jpos9','field_jpos10','field_jpos11',...
    'field_jpos12','field_jpos13','field_jpos14',...
    'field_jpos15'};
mvel_headers = {'field_mvel0','field_mvel1','field_mvel2',...
    'field_mvel3','field_mvel4','field_mvel5',...
    'field_mvel6','field_mvel7','field_mvel8',...
    'field_mvel9','field_mvel10','field_mvel11',...
    'field_mvel12','field_mvel13','field_mvel14',...
    'field_mvel15'};
jvel_headers = {'field_jvel0','field_jvel1','field_jvel2',...
    'field_jvel3','field_jvel4','field_jvel5',...
    'field_jvel6','field_jvel7','field_jvel8',...
    'field_jvel9','field_jvel10','field_jvel11',...
    'field_jvel12','field_jvel13','field_jvel14',...
    'field_jvel15'};

% Extract dpos, pos, dori, ori, dacs, enc_vals arrays from table
tau = table2array(D(1:end,{tau_headers{1:joint_n}}));
mpos = table2array(D(1:end,{mpos_headers{1:joint_n}}));
mvel = table2array(D(1:end,{mvel_headers{1:joint_n}}));
jpos = table2array(D(1:end,{jpos_headers{1:joint_n}}));
jvel = table2array(D(1:end,{jvel_headers{1:joint_n}}));

% Robot states (runlevel and sublevel)
runlevel = table2array(D(1:size(D,1)-1,'field_runlevel'));
sublevel = table2array(D(1:size(D,1)-1,'field_sublevel'));
% Find the period where the robot goes to runlevel 3
start_time = find(runlevel == 3,1,'first')
end_time = find(runlevel == 3,1,'last')
size_time = end_time - start_time + 1;

% 1647 541 415 24852 22717
%start = 24852;
tau = tau(start_time:end_time,1:3);
mpos = mpos(start_time:end_time,1:3);
mvel = mvel(start_time:end_time,1:3);
jpos = jpos(start_time:end_time,1:3);
jvel = jvel(start_time:end_time,1:3);

save('test_joint123.mat','tau','mpos','mvel','jpos','jvel','size_time');

% % Robot states (runlevel and sublevel)
% runlevel = table2array(D(1:size(D,1)-1,'field_runlevel'));
% sublevel = table2array(D(1:size(D,1)-1,'field_sublevel'));
% % Find the period where the robot goes to runlevel 3
% start_time = find(runlevel == 1,1,'first')
% end_time = find(runlevel == 1,1,'last')
% size_time = end_time - start_time + 1;
% 
% % start_time = 1646; % 1648,542,383
% 
% % select motor number
% motor_num = 1;
% 
% tau = tau(start_time:end_time,motor_num);
% mpos = mpos(start_time:end_time,motor_num)*pi/180;
% mvel = mvel(start_time:end_time,motor_num)*pi/180;
% jpos = jpos(start_time:end_time,motor_num)*pi/180;
% jvel = jvel(start_time:end_time,motor_num)*pi/180;
% 
% 
% fileID = fopen('traj1_tau1.txt','w');
% fprintf(fileID,'%f\n',tau);
% fclose(fileID);
% 
% 
% fileID = fopen('traj1_mvel1.txt','w');
% fprintf(fileID,'%f\n',mvel);
% fclose(fileID);
% 
% fileID = fopen('traj1_mpos1.txt','w');
% fprintf(fileID,'%f\n',mpos);
% fclose(fileID);


% %% model parameters
% Im = 2.847*1e-4;
% tau_cm_all = [8.11e-2 4.11e-2 5.11e-2];
% tau_vm_all = [1.9e-4 1.8e-4 7.1e-4];
% tau_cm = tau_cm_all(motor_num);
% tau_vm = tau_vm_all(motor_num);
% 
% ke_all = [7200e3 15e3 9.25e3]; %[720e3 88e3 9.25e3]
% be_all = [400000 1380e3 400]; % [4000, 1380 400]
% ke = ke_all(motor_num);
% be = be_all(motor_num);
% 
% r_l_all = [63.095e-3 56.298e-3 8.445e-3];
% r_l = r_l_all(motor_num);
% 
% N = 12.25;
% 
% r_l1 = 63.095*1e-3;
% r_l2 = 56.298*1e-3;
% r_m1 = 5.675*1e-3;
% % r_m2 = 5.675*1e-3;
% % r_m3 = 5.675*1e-3;
% 
% % C_01 = 0.14545;
% % C_02 = 0.007797;
% % C_12 = 0.008077;
% 
% t_r1 = r_l1/r_m1*N;
% % t_r1 = 12.25;
% % t_r2 = r_l2/r_m2*N;
% % t_r3 = N;
% % A = [t_r1 0 0;C_01*t_r2 t_r2 0;C_02*t_r3 C_12*t_r3 t_r3];
% 
% % t_r = -t_r1;
% r_mc = 5.675e-3;
% 
% 
% 
% %% run simulation
% vol = dac*0.0003051804379;
% current = vol*1.14421;
% tau = current*0.0603*12.25;
% input = tau;
% 
% x1_ini = mpos(1);
% x2_ini = mvel(1);
% 
% time = 0:0.001:numel(dac)/1000-0.001;
% 
% input = timeseries(input,time);
% jpos = timeseries(jpos,time);
% jvel = timeseries(jvel,time);
% 
% TIME = 15%max(time);
% 
% model_name = 'motor1';
% StopTime = 13%max(time);
% open(model_name);
% set_param(model_name,'StopTime',num2str(StopTime));
% sim(model_name);
% 
% 
% %% plot
% figure(1);
% data = sim_mpos.Data;
% plot(sim_mpos.Time,data);
% hold on;
% plot(time,mpos);
% grid on;
% legend('sim mpos','actual mpos');
% 
% figure(2);
% data = sim_mvel.Data;
% plot(sim_mvel.Time,data);
% hold on;
% plot(time,mvel);
% grid on;
% legend('sim mvel','actual mvel');
% 
% 
% % figure(3);
% % plot(jpos.Data);
% % hold on;
% % plot(mpos/t_r1+1,'r');
% % grid on;
% % 
% % figure(4);
% % plot(jvel.Data);
% % hold on;
% % plot(mvel/t_r1,'r');
% % grid on;