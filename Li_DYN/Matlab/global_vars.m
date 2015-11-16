global gravity
gravity = 1*[0 -9.81 0];

%% motor parameters
global ke1 be1 r_mc1 r_l1 N Im1 tau_cm1 tau_vm1 F_cl1 F_vl1
ke1 = 720e3;
be1 = 1000*1;
tau_cm1 = 8.11e-2*0.9;
tau_vm1 = 1.9e-4*2;
Im1 = 2.847e-4*1.0;
N = 12.25;
r_mc1 = 5.675e-3;
r_l1 = 63.095e-3;
F_cl1 = 0.505*1;
F_vl1 = 0.00505*1.0;
tr_1 = r_l1/r_mc1*N;

global com1
com1 = [-0.215224 0.00717636 0.104721];

global ke2 be2 r_mc2 r_l2 Im2 tau_cm2 tau_vm2 F_cl2 F_vl2
ke2 = 3*88e3;
be2 = 3*1380;
tau_cm2 = 4.11e-2*1.2; % 0.95 1.2
tau_vm2 = 1.8e-4*12; %15 4
Im2 = 2.847e-4;
r_mc2 = 5.675e-3;
r_l2 = 56.298e-3;
F_cl2 = 0.49*1; % 5
F_vl2 = 0.0049*1; % 2
tr_2 = r_l2/r_mc2*N;

global ke3 be3 r_mc3 r_l3 Im3 tau_cm3 tau_vm3 F_cl3 F_vl3
ke3 = 1*9.25e3;
be3 = 1.0*400;
tau_cm3 = 5.11e-2*2; %1.1 1.2
tau_vm3 = 7.1e-4*2;  %1.3, 1.17
Im3 = 2.847e-4;
r_mc3 = 5.675e-3;
r_l3 = 1;
F_cl3 = 0.53*10;
F_vl3 = 0.0053*10;
tr_3 = 1/r_mc3*N;

C01 = 0.14545;
C02 = 0.007797;
C12 = 0.008077;
A = [tr_1 0 0;C01*tr_2 tr_2 0;C02*tr_3 C12*tr_3 tr_3];



%% link properties
global I1 I2 I3 m1 m2 m3
m1 = 0.503;
m2 = 0.753;
m3 = 0.407;
R1 = [0 0 -1;0 1 0;1 0 0];
% R1 = eye(3);
dxyz = [-215.22-(-82.8) 7.18 104.72]'/1000;
dI = (dxyz'*dxyz*eye(3)-dxyz*dxyz')*m1;
I1 = R1*[17.376 0.291 -0.374;0.291 11 -5.483;-0.374 -5.483 6.499]*1e-3*R1'+dI;
R2 = [0 0 1;0 -1 0;1 0 0];
I2 = R2*[81.579 0.773 0.762;0.773 44.329 37.973;0.762 37.973 37.686]*1e-3*R2';
R3 = [0 0 1;1 0 0;0 1 0];
I3 = R3*[2.908 -0.001 -0.066;-0.001 3.009 -0.009;-0.066 -0.009 0.355]*1e-3*R3';

%% integration initialization
global last_step_time_r last_step_time_l
last_step_time_r = 0;
last_step_time_l = 0;

%% joint control, using P and PID
global kp_arm1 ki_arm1 kd_arm1 err1_r err1_l
% kp_arm1 = 0.3;
% ki_arm1 = 0;
% kd_arm1 = 0.008;
kp_arm1 = 0.3*tr_1;
% ki_arm1 = 10;
ki_arm1 = 0;
kd_arm1 = 0.008*tr_1;
err1_r = 0;
err1_l = 0;

global kp_arm2 ki_arm2 kd_arm2 err2_r err2_l
% kp_arm2 = 0.3;
% ki_arm2 = 0;
% kd_arm2 = 0.008;
kp_arm2 = 500;
% ki_arm2 = 10;
ki_arm2 = 0;
kd_arm2 = 20;
err2_r = 0;
err2_l = 0;

global kp_arm3 ki_arm3 kd_arm3 err3_r err3_l
% kp_arm3 = 0.15;
% ki_arm3 = 0;
% kd_arm3 = 0.1;
kp_arm3 = 500;
% ki_arm3 = 20;
ki_arm3 = 0;
kd_arm3 = 200;
err3_r = 0;
err3_l = 0;

global kp_arm4 kp_arm5 kp_grasping
kp_arm4 = 0.09;
kp_arm5 = 0.05;
kp_grasping = 0.05;


%% set joint limit PD controller gains
global jl_kp jl_kd jl_kd_2 jl_kd_3
jl_kp = 0;
jl_kd = 0.0;
jl_kd_2 = 0.0001;
jl_kd_3 = 0.00001;
joint_limits;