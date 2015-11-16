%% set up initial configuration
% left arm
AA = eye(3);
AAA=diag(A);
AA(1,1)=AAA(1);
AA(2,2)=AAA(2);
AA(3,3)=AAA(3);
temp = inv(AA)*[mpos1(1) mpos2(1) mpos3(1)]';

theta1_0_l = temp(1)-pi;% between -170 and -65 degree, convert to radian
theta2_0_l = temp(2)-pi;      % between -135 and -45 degree, convert to radian
theta3_0_l = temp(3);     % between 260 and 520 milimeter, convert to meter
theta4_0_l = 0;          % between -150 and 150 degree, convert to radian
theta5_0_l = -pi/2;      % between -180 and 0 degree, convert to radian
theta6_0_l = 0;          % between -90 and 90 degree, convert to radian
theta7_0_l = 0;          % between -90 and 90 degree, convert to radian

theta1_d_0_l = jvel1(1);
theta2_d_0_l = jvel2(1);
theta3_d_0_l = jvel3(1);
theta4_d_0_l = 0;
theta5_d_0_l = 0;
theta6_d_0_l = 0;
theta7_d_0_l = 0;

% right arm
theta1_0_r = pi/3;       % between 10 and 115 degree, convert to radian
theta2_0_r = pi/2;       % between 45 and 135 degree, convert to radian
theta3_0_r = 500/1000;     % between 260 and 520 milimeter, convert to meter
theta4_0_r = 0;          % between -150 and 150 degree, convert to radian
theta5_0_r = -pi/2;      % between -180 and 0 degree, convert to radian
theta6_0_r = 0;          % between -90 and 90 degree, convert to radian
theta7_0_r = 0;          % between -90 and 90 degree, convert to radian

theta1_d_0_r = 0;
theta2_d_0_r = 0;
theta3_d_0_r = 0;
theta4_d_0_r = 0;
theta5_d_0_r = 0;
theta6_d_0_r = 0;
theta7_d_0_r = 0;



% motor initial states
m1_vel_ini = mvel1(1);
m1_pos_ini = mpos1(1);

m2_vel_ini = mvel2(1);
m2_pos_ini = mpos2(1);

m3_vel_ini = mvel3(1);
m3_pos_ini = mpos3(1);


%% write initial condition to file
% diary ('ini_cond.txt');
% theta1_0_l
% theta2_0_l
% theta3_0_l
% theta1_d_0_l
% theta2_d_0_l
% theta3_d_0_l
% m1_pos_ini
% m2_pos_ini
% m3_pos_ini
% m1_vel_ini
% m2_vel_ini
% m3_vel_ini
% diary off