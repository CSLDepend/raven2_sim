'''/* Runs Raven 2 simulator by calling packet generator, Raven control software, and visualization code
 * Copyright (C) 2015 University of Illinois Board of Trustees, DEPEND Research Group, Creators: Homa Alemzadeh and Daniel Chen
 *
 * This file is part of Raven 2 Surgical Simulator.
 *
 * Raven 2 Surgical Simulator is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * Raven 2 Surgical Simulator is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with Raven 2 Control.  If not, see <http://www.gnu.org/licenses/>.
 */'''

import os
import subprocess
import random
import sys
from math import cos, sin, sqrt, acos, asin, pow as pow_f
import socket
import sys
from collections import OrderedDict
import numpy as np
import struct
import time
import signal
from sys import argv

def rsp_func():
	rsp = str(raw_input("Is the Raven Home found correctly (Yes/No)? "))
	if rsp.lower() == 'yes' or rsp.lower() == 'y':
		print 'Found Raven Home Directory.. Starting..\n'
	elif rsp.lower() == 'no' or rsp.lower() == 'n':
		print 'Please change the ROS_PACKAGE_PATH environment variable.\n'
		sys.exit(2)
	else:
		rsp_func()

# Change define macros
def change_defines_h(mode, packet_gen, injection):
    cmd = 'cp ' + src_file + ' ' + bkup_file
    os.system(cmd)
    #open files
    src_fp = open(src_file,'w')
    bkup_fp = open(bkup_file,'r')

    for line in bkup_fp:
        if line.startswith('//#define simulator'):
            if mode == 'sim':
                line = line.lstrip('//')
        elif line.startswith('//#define dyn_simulator'):
            if mode == 'dyn_sim':
                line = line.lstrip('//')
        elif line.startswith('//#define packetgen'):
            if packet_gen == '1':
                line = line.lstrip('//')
        elif line.startswith('//#define mfi'):
            if injection == 'mfi':
                line = line.lstrip('//')
        src_fp.write(line)
    src_fp.close()
    bkup_fp.close()
    #save a check file
    cmd = 'cp ' + src_file + ' ' + chk_file
    os.system(cmd)

def restore_defines_h():
    #restore file
    cmd = 'chmod 777 '+bkup_file;
    os.system(cmd);
    cmd = 'cp ' + bkup_file + ' ' + src_file
    # delete backup
    if (os.system(cmd) == 0): 
        cmd = 'rm ' + bkup_file;
        os.system(cmd);   

def compile_raven():
    # Make the file
    cmd = 'cd ' + raven_home + ';make -j > compile.output'
    return os.system(cmd)

def quit(): 
    try:
        r2_control_pid = subprocess.check_output("pgrep r2_control", 
                shell=True)
        os.killpg(int(r2_control_pid), signal.SIGINT)
        time.sleep(1)
    except:
        pass
    try:
        roslaunch_pid = subprocess.check_output("pgrep roslaunch", 
                shell=True)
        os.killpg(int(roslaunch_pid), signal.SIGINT)
        time.sleep(1)
    except:
        pass
    try:
        os.killpg(raven_proc.pid, signal.SIGINT)
        time.sleep(1)
    except:
        pass
    try:
        os.killpg(packet_proc.pid, signal.SIGINT)
        time.sleep(1)
    except:
        pass
    try:
        os.killpg(rostopic_proc.pid, signal.SIGINT)
        time.sleep(1)
    except:
        pass
    try:
        os.killpg(dynSim_proc.pid, signal.SIGINT)
        time.sleep(1)
    except:
        pass
    os.system("rm /tmp/dac_fifo")
    os.system("rm /tmp/mpos_vel_fifo")
    os.system("killall roslaunch")
    os.system("killall rostopic")    
    os.system("killall r2_control")
    os.system("killall rviz")
    os.system("killall xterm")
    os.system("killall two_arm_dyn")
    os.system("killall python")

def signal_handler(signal, frame):
    print "Ctrl+C Pressed!"
    quit()
    sys.exit(0)

def run_experiment(raven_home, mode, packet_gen):
    # Open Sockets
    os.system("killall xterm")
    sock = socket.socket(socket.AF_INET, # Internet
                          socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP,UDP_PORT))

    # Setup Variables
    goldenRavenTask= 'xterm -e roslaunch raven_2 raven_2.launch'
    ravenTask = 'xterm -hold -e roslaunch raven_2 raven_2.launch'
    visTask = 'xterm -hold -e roslaunch raven_visualization raven_visualization.launch'
    dynSimTask = 'xterm -hold -e "cd ../Li_DYN && make && ./two_arm_dyn"'
    rostopicTask = 'rostopic echo -p ravenstate >'+raven_home+'/latest_run.csv'
    if (surgeon_simulator == 1):
        packetTask = 'xterm -hold -e python '+raven_home+'/Real_Packet_Generator_Surgeon.py '+ mode
        #print(packetTask)
    else:
        packetTask = 'xterm -e python '+raven_home+'/Packet_Generator.py'

    # Call visualization, packet generator, and Raven II software
    vis_proc = subprocess.Popen(visTask, env=env, shell=True, preexec_fn=os.setsid)
    time.sleep(4)  
    if packet_gen == "1":
            packet_proc = subprocess.Popen(packetTask, shell=True, preexec_fn=os.setsid)
            print "Using the packet generator.."
    elif packet_gen == "0":
            print "Waiting for the GUI packets.."
    else:
        print "Usage: python run.py <sim|dyn_sim|rob> <1:packet_gen|0:gui>"
        sys.exit(2)
    raven_proc = subprocess.Popen(ravenTask, env=env, shell=True, preexec_fn=os.setsid)
    rostopic_proc = subprocess.Popen(rostopicTask, env=env, shell=True, preexec_fn=os.setsid)
    time.sleep(0.5);


    # Call Dynamic Simulator
    if mode == "dyn_sim":
            #dynSim_proc = subprocess.Popen(dynSimTask, env=env, shell=True, preexec_fn=os.setsid)
            #os.system("cd ../Li_DYN && ./two_arm_dyn")
            print "Started the dynamic simulator.."

    print("Press Ctrl+C to exit.")

    #Wait for a response from the robot
    data = ''
    while not data:
        print("Waiting for Raven to be done...")
        data = sock.recvfrom(100)
        if data[0].find('Done!') > -1:
            print("Raven is done, shutdown everything...")  
        elif data[0].find('Stopped') > -1:
            print("Raven is stopped, shutdown everything...")  
        else:
            data = ''
    quit()
"""
def run_mfi(raven_home, mode, packet_gen):
    cur_inj = -1
    saved_param = []

    with open(master_file) as fp:
        target_file = ''
        line_num = 0
        trigger = []
        target = []

        for line in fp:
            # Strip '\n' from each line then split by ','
            line = line.strip('\n')
            param = line.split(',')

            # Skip lines begin with # or empty line
            if param[0] == '' or param[0] == '#':
                continue
           
            # Read location info
            elif param[0] == 'location':
                location_info = param[1].split(':')
                target_file = location_info[0].lstrip()
                line_num = location_info[1]

            # Read trigger info
            elif param[0] == 'trigger':
                param.pop(0)
                trigger = [item.strip() for item in param]

            elif param[0] == 'target_r':
                param.pop(0)
                saved_param = param
                target = (mfi.generate_target_r(saved_param)).split(' ')

            elif param[0] == 'injection':
                if cur_inj != int(param[1]):
                    cur_inj = int(param[1])
                    print("setup param for %d" % cur_inj)
                else:
                    # Injection starts at argv[1]
                    # Example starting_inj_num is 3.2
                    starting_inj_num = (sys.argv[1]).split('.')
                    if int(param[1]) >= int(starting_inj_num[0]):
                        # If param == 3, indicate do random injection param[2] times.
                        if len(param) == 3:
                            for x in xrange(int(param[2])):
                                if len(starting_inj_num) > 1:
                                    if x < int(starting_inj_num):
                                        next
                                #target = (mfi.generate_target_r(saved_param)).split(' ')
                                target = (mfi.generate_target_r_stratified(saved_param, int(param[2]), x)).split(' ')
                                mfi.insert_code(raven_home, target_file, line_num, trigger, target)

                                print("injecting to %d.%d" % (cur_inj, x))
                                run_experiment(raven_home, mode, packet_gen)
                        else:
                            print("injecting to %d" % (cur_inj))
                            mfi.insert_code(raven_home, target_file, line, trigger, target)
                            run_experiment(raven_home, mode, packet_gen)

"""

env = os.environ.copy()
#print env['ROS_PACKAGE_PATH']
splits = env['ROS_PACKAGE_PATH'].split(':')
raven_home = splits[0]
print '\nRaven Home Found to be: '+ raven_home
rsp_func()
src_file = raven_home + "/include/raven/defines.h"
bkup_file = raven_home + "/include/raven/defines_back.h"
chk_file = raven_home + "/include/raven/defines_last_run"
master_file = './selected_injection.txt'

surgeon_simulator = 1;
UDP_IP = "127.0.0.1"
UDP_PORT = 34000

signal.signal(signal.SIGINT, signal_handler)

# Parse the arguments
try:
    script, mode, packet_gen, injection = argv
except Exception as e:
    print "Error: missing parameters"
    print "Usage: python run.py <sim|dyn_sim|rob> <1:packet_gen|0:gui> <none|mfi>"
    sys.exit(2)

if mode == "sim":
    print "Run the Simulation"
elif mode == "dyn_sim":
    print "Run the Dynamic Simulation"
elif mode == "rob": 
    print "Run the Real Robot"
else:
    print "Usage: python run.py <sim|dyn_sim|rob> <1:packet_gen|0:gui> <none|mfi>"
    sys.exit(2)

# Change Source
change_defines_h(mode, packet_gen, injection)

# Compile Raven
make_ret = compile_raven()

# Restore Source
restore_defines_h()

if (make_ret != 0):
   print "Make Error: Compilation Failed..\n"
   quit()
   sys.exit(0)

run_experiment(raven_home, mode, packet_gen)

