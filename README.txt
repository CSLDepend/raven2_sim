======================================
Summary and licensing information
======================================
This code is for RAVEN II surgical simulator. It is based on the open-source RAVEN II control software, developed by the University of Washington Biorobotics lab at: https://github.com/uw-biorobotics/raven2/tree/indigo. It enables running RAVEN control software with no robotic hardware attached.

A Python script (Real_Packet_Generator_Surgeon.py) mimicks the network packets sent from the surgeon console based on a previously collected data from the trajectory of a basic surgical task. A 3D visualization tool for ROS (rviz package) is used for 3D animation of the robotic motions. 
For more information, please see: http://web.engr.illinois.edu/~alemzad1/papers/MedicalCPS_2015.pdf
http://arxiv.org/abs/1504.07135v1

Copyright (C) 2015 University of Illinois Board of Trustees, DEPEND Research Group
Homa Alemzadeh, Daniel Chen, Abishek Krishnamoorthy (rviz), and Xiao Li (dynamic models) 

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

======================================
How to run
======================================
1. After downloading the repository, rename the folder to "raven_2"
2. Change the ROS_PACKAGE_PATH environment variable to the location of raven_2 folder
3. Unzip the "new_test_3.csv" datafile in the ./teleop_data folder
