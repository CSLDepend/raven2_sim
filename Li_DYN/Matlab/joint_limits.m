% set up joint limits

% right arm joint limits
global j1_r_min j1_r_max j2_r_min j2_r_max j3_r_min j3_r_max ...
    j4_r_min j4_r_max j5_r_min j5_r_max j6_r_min j6_r_max j7_r_min j7_r_max

j1_r_min = 10/180*pi;
j1_r_max = 115/180*pi;

j2_r_min = pi/4;
j2_r_max = 3*pi/4;

j3_r_min = 260/1000;
j3_r_max = 520/1000;

j4_r_min = -5*pi/6;
j4_r_max = 5*pi/6;

j5_r_min = -pi;
j5_r_max = 0;

j6_r_min = -pi/2;
j6_r_max = pi/2;

j7_r_min = -pi/2;
j7_r_max = pi/2;


% left arm joint limits
global j1_l_min j1_l_max j2_l_min j2_l_max j3_l_min j3_l_max ...
    j4_l_min j4_l_max j5_l_min j5_l_max j6_l_min j6_l_max j7_l_min j7_l_max

j1_l_min = -170*pi/180;
j1_l_max = -65*pi/180;

j2_l_min = -3*pi/4;
j2_l_max = -pi/4;

j3_l_min = 260/1000;
j3_l_max = 520/1000;

j4_l_min = -5*pi/6;
j4_l_max = 5*pi/6;

j5_l_min = -pi;
j5_l_max = 0;

j6_l_min = -pi/2;
j6_l_max = pi/2;

j7_l_min = -pi/2;
j7_l_max = pi/2;

