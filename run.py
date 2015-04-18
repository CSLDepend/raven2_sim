"""
File: insert_code.py
Authors: Daniel Chen and Homa Alemzadeh
Created: 2015/2/3

Overall Idea
1. copy entire folder from backup to origion
2. Read the target file and determine what to insert
3. Insert to the source code file
4. Compile the source code file

Modified: 2015/2/5
1. Now checks if make was successful, if not restores and quits
2. Added a quit function to be called on Ctrl+C and compilation errors
3. Fixed the R matrix value assignment
4. Added different assignment scenarios for position, rotation, and joint variables
"""

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

src = '/home/alemzad1/homa_wksp/raven_2/src/raven'
raven_home = '/home/alemzad1/homa_wksp/raven_2'
root_dir = '/home/alemzad1/homa_wksp'
cur_inj = -1
saved_param = []
surgeon_simulator = 1;
UDP_IP = "127.0.0.1"
UDP_PORT = 34000

sock = socket.socket(socket.AF_INET, # Internet
                      socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP,UDP_PORT))

# Find my own IP
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("gmail.com", 80))
my_ip = s.getsockname()[0]
print my_ip
s.close()

env = os.environ.copy()
'''splits = env['ROS_PACKAGE_PATH'].split(':')
splits[-1] = '/home/alemzad1/homa_wksp/raven_2'
os.environ['ROS_PACKAGE_PATH']=':'.join(splits)
print os.environ['ROS_PACKAGE_PATH'] '''

goldenRavenTask= 'xterm -e roslaunch raven_2 raven_2.launch'
ravenTask = 'xterm -hold -e roslaunch raven_2 raven_2.launch'
visTask = 'xterm -hold -e roslaunch raven_visualization raven_visualization.launch'
if (surgeon_simulator == 1):
    packetTask = 'xterm -hold -e python '+raven_home+'/Real_Packet_Generator_Surgeon.py'
else:
    packetTask = 'xterm -e python '+raven_home+'/Packet_Generator.py'


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

    os.system("killall xterm")
    #os.system("killall python")
    os.system("killall roslaunch")
    os.system("killall r2_control")

vis_proc = subprocess.Popen(visTask, env=env, shell=True, preexec_fn=os.setsid)
time.sleep(3.5)  
packet_proc = subprocess.Popen(packetTask, shell=True, preexec_fn=os.setsid)
raven_proc = subprocess.Popen(ravenTask, env=env, shell=True, preexec_fn=os.setsid)

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

