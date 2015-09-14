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

script, mode = argv
if mode == "sim":
    print "Run the Simulation"
elif mode == "rob": 
    print "Run the Real Robot"
else:
    print "Usage: python run.py <sim|rob>"
    sys.exit(2)

src = '~/test_wksp/raven_2/src/raven'
raven_home = '~/test_wksp/raven_2'
root_dir = '~/test_wksp'
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
#print my_ip
s.close()

env = os.environ.copy()
'''splits = env['ROS_PACKAGE_PATH'].split(':')
splits[-1] = '/home/alemzad1/test_wksp/raven_2'
os.environ['ROS_PACKAGE_PATH']=':'.join(splits)
print os.environ['ROS_PACKAGE_PATH'] '''

goldenRavenTask= 'xterm -e roslaunch raven_2 raven_2.launch'
ravenTask = 'xterm -hold -e roslaunch raven_2 raven_2.launch'
visTask = 'xterm -hold -e roslaunch raven_visualization raven_visualization.launch'
if (surgeon_simulator == 1):
    packetTask = 'xterm -hold -e python '+raven_home+'/Real_Packet_Generator_Surgeon.py '+ mode
    #print(packetTask)
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

    os.system("killall python")
    os.system("killall roslaunch")
    os.system("killall r2_control")
    os.system("killall xterm")
    os.system("killall xterm")

def signal_handler(signal, frame):
    print "Ctrl+C Pressed!"
    quit()
    sys.exit(0)

# Main code starts here
signal.signal(signal.SIGINT, signal_handler)

# Call visualization, packet generator, and Raven II software
vis_proc = subprocess.Popen(visTask, env=env, shell=True, preexec_fn=os.setsid)
time.sleep(4)  
packet_proc = subprocess.Popen(packetTask, shell=True, preexec_fn=os.setsid)
raven_proc = subprocess.Popen(ravenTask, env=env, shell=True, preexec_fn=os.setsid)

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

