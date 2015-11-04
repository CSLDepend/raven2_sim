'''/* Surgeon Packet Generator - Works with Control software for the Raven II robot
  Input arguments simulator
 * Copyright (C) 2015 University of Illinois Board of Trustees, DEPEND Research Group, Creator: Homa Alemzadeh
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

import socket
import struct
import csv
import time
from collections import namedtuple
import threading
import sys
import signal
import time
import math
from sys import argv

UDP_IP = "127.0.0.1"
UDP_PORT1 = 32000
UDP_PORT2 = 36001

# Not_Ready: state = 0, Operating: state = 1, Stopped: state = 2  
robot_state = 0;

script, mode = argv
simulator = 0
if mode == "sim" or mode == "dyn_sim":
    simulator = 1
    print "Packet Generator for Simulation"
elif mode == "rob": 
    simulator = 0
    print "Packet Generator for Robot Replay"
else:
    print "Usage: python Real_Packet_Generator_Surgoen <sim|rob>"
    sys.exit(2)

SKIP = 1
fast_surgeon = 1
if fast_surgeon:
   MAX_LINES = 15000
   FREQ = 0.001
else: 
   MAX_LINES = 3000
   FREQ = 0.01

# When only running simulator with no robot, we need to send jpos values
if (simulator):
   format_ = "<IIIiiiiiiddddddddddddddddddddddddddddddddddiiiiii"
   u_struct = namedtuple("u_struct", "sequence pactyp version delx0 delx1 dely0 dely1 delz0 delz1 R_l00 R_l01 R_l02 R_l10 R_l11 R_l12 R_l20 R_l21 R_l22 R_r00 R_r01 R_r02 R_r10 R_r11 R_r12 R_r20 R_r21 R_r22 jpos0 jpos1 jpos2 jpos3 jpos4 jpos5 jpos6 jpos7 jpos8 jpos9 jpos10 jpos11 jpos12 jpos13 jpos14 jpos15 buttonstate0 buttonstate1 grasp0 grasp1 surgeon_mode checksum");
else:
   format_ = "<IIIiiiiiiddddddddddddddddddiiiiii"
   u_struct = namedtuple("u_struct", "sequence pactyp version delx0 delx1 dely0 dely1 delz0 delz1 R_l00 R_l01 R_l02 R_l10 R_l11 R_l12 R_l20 R_l21 R_l22 R_r00 R_r01 R_r02 R_r10 R_r11 R_r12 R_r20 R_r21 R_r22 buttonstate0 buttonstate1 grasp0 grasp1 surgeon_mode checksum");


line_no = 0;
sock1 = socket.socket(socket.AF_INET, # Internet
	              socket.SOCK_DGRAM) # UDP
sock1.bind((UDP_IP,UDP_PORT1))
sock2 = socket.socket(socket.AF_INET, # Internet
	              socket.SOCK_DGRAM) # UDP
def readSignals():
    global robot_state
    while(1):
	data = sock1.recvfrom(100)       
	if (robot_state == 0):
	    if (data[0].find('Ready') > -1):
	        robot_state = 1;
	    else:
	        robot_state = 0;

	elif (robot_state == 1):
	    print "\rRaven is ready...",
	    if (data[0].find('Stopped') > -1):
	        robot_state = 2;
	    else:
	        robot_state = 1;

	elif (robot_state == 2): 
	    print "\rRaven is stopped...", 
	    if (data[0].find('Ready') > -1):
	        robot_state = 1;
	    else:
	        robot_state = 2;    

def sendPackets():
    global line_no
    seq = 0;
    line = [];
    #csvfile1 = open('./teleop_data/traj1.csv'); 
    csvfile1 = open('/home/raven/homa_wksp/Tests/test2.csv');   
    reader = csv.reader(csvfile1)
    headers = reader.next()
    # Find the indices for the variables in the datasheet
    runlevel_index = headers.index('field.runlevel');
    dori_index = headers.index('field.ori_d0');
    dpos_index = headers.index('field.pos_d0');
    djpos_index = headers.index('field.jpos_d0');
    mpos_index = headers.index('field.mpos0');
    mvel_index = headers.index('field.mvel0');
    enc_index = headers.index('field.encVals0');

    # Skip the packets until runlevel 3
    runlevel = 0;	
    while not(runlevel == 3):
        line = reader.next()
        runlevel = int(line[runlevel_index])
   
    #for i in range(0,SKIP):
    #   line = reader.next()
    
    global robot_state
    while (robot_state == 0):
		print "\rWaiting for Raven...",  
  
    # Send trajectory packets until the operation is done (e.g. 300 steps) 
    # Skip every SKIP-1 packets in the trajectory  
    while (line_no < MAX_LINES):#(runlevel == 3)
		# If robot is ready, update the packet to be sent
		if (robot_state == 1):
			for i in range(0,SKIP):
				line = reader.next();
				runlevel = int(line[runlevel_index])
				line_no = line_no + 1;    
           
			seq = seq + 1;
			print "\nSending Packet #"+str(seq) 
			print_line = '\nmpos = '
			for i in range(0,16):
				print_line = print_line + (str(float(line[mpos_index+i])*(math.pi/180))+',')
			print print_line
			print_line = '\nmvel = '
			for i in range(0,16):
				print_line = print_line + (str(float(line[mvel_index+i])*(math.pi/180))+',')
			print print_line
			print_line = '\nencVals = '
			for i in range(0,16):
				print_line = print_line + (str(float(line[enc_index+i])*(math.pi/180))+',')
			print print_line  
			# Construct the packet to send
			if (simulator):  
			    tuple_to_send = u_struct(sequence = seq, 
			        pactyp = 0, 
			        version = 0, 
			        delx0 = int(float(line[dpos_index])),
			        delx1 = int(float(line[dpos_index+3])),
			        dely0 = int(float(line[dpos_index+1])),
			        dely1 = int(float(line[dpos_index+4])),
			        delz0 = int(float(line[dpos_index+2])),
			        delz1 = int(float(line[dpos_index+5])),
			        R_l00 = float(line[dori_index]),
			        R_l01 = float(line[dori_index+1]),
			        R_l02 = float(line[dori_index+2]),
			        R_l10 = float(line[dori_index+3]),
			        R_l11 = float(line[dori_index+4]), 
			        R_l12 = float(line[dori_index+5]),
			        R_l20 = float(line[dori_index+6]),
			        R_l21 = float(line[dori_index+7]),
			        R_l22 = float(line[dori_index+8]),
			        R_r00 = float(line[dori_index+9]),
			        R_r01 = float(line[dori_index+10]), 
			        R_r02 = float(line[dori_index+11]),
			        R_r10 = float(line[dori_index+12]),
			        R_r11 = float(line[dori_index+13]), 
			        R_r12 = float(line[dori_index+14]),
			        R_r20 = float(line[dori_index+15]),
			        R_r21 = float(line[dori_index+16]),
			        R_r22 = float(line[dori_index+17]),
			        jpos0 = float(line[djpos_index]),
					jpos1 = float(line[djpos_index+1]),
					jpos2 = float(line[djpos_index+2]),
					jpos3 = float(line[djpos_index+3]),
					jpos4 = float(line[djpos_index+4]),
					jpos5 = float(line[djpos_index+5]),
					jpos6 = float(line[djpos_index+6]),
					jpos7 = float(line[djpos_index+7]),
					jpos8 = float(line[djpos_index+8]),
					jpos9 = float(line[djpos_index+9]),
					jpos10 = float(line[djpos_index+10]),
					jpos11 = float(line[djpos_index+11]),
					jpos12 = float(line[djpos_index+12]),
					jpos13 = float(line[djpos_index+13]),
					jpos14 = float(line[djpos_index+14]),
					jpos15 = float(line[djpos_index+15]),
			        buttonstate1 = 0,
			        buttonstate0 = 0, 
			        grasp0 = float((float(line[djpos_index+7])+float(line[djpos_index+6]))*1000),
			        grasp1 = float((float(line[djpos_index+15])+float(line[djpos_index+14]))*1000), 
			        surgeon_mode = 1, 
			        checksum=0);
			else:
			    tuple_to_send = u_struct(sequence = seq, 
			        pactyp = 0, 
			        version = 0, 
			        delx0 = int(float(line[dpos_index])),
			        delx1 = int(float(line[dpos_index+3])),
			        dely0 = int(float(line[dpos_index+1])),
			        dely1 = int(float(line[dpos_index+4])),
			        delz0 = int(float(line[dpos_index+2])),
			        delz1 = int(float(line[dpos_index+5])),
			        R_l00 = float(line[dori_index]),
			        R_l01 = float(line[dori_index+1]),
			        R_l02 = float(line[dori_index+2]),
			        R_l10 = float(line[dori_index+3]),
			        R_l11 = float(line[dori_index+4]),
			        R_l12 = float(line[dori_index+5]),
			        R_l20 = float(line[dori_index+6]),
			        R_l21 = float(line[dori_index+7]),
			        R_l22 = float(line[dori_index+8]),
			        R_r00 = float(line[dori_index+9]),
			        R_r01 = float(line[dori_index+10]),
			        R_r02 = float(line[dori_index+11]),
			        R_r10 = float(line[dori_index+12]),
			        R_r11 = float(line[dori_index+13]),
			        R_r12 = float(line[dori_index+14]),
			        R_r20 = float(line[dori_index+15]),
			        R_r21 = float(line[dori_index+16]),
			        R_r22 = float(line[dori_index+17]),
			        buttonstate0 = 0,
			        buttonstate1 = 0, 
			        grasp0 = float((float(line[djpos_index+7])+float(line[djpos_index+6]))*1000),
			        grasp1 = float((float(line[djpos_index+15])+float(line[djpos_index+14]))*1000), 
			        surgeon_mode = 1, 
			        checksum=0);                
			MESSAGE = struct.pack(format_,*tuple_to_send._asdict().values());
			if (robot_state == 1):
			    print struct.unpack(format_,MESSAGE);
			    print "\n"
			# Send the command to the robot
			sock2.sendto(MESSAGE, (UDP_IP, UDP_PORT2))
			time.sleep(FREQ)
		# If in robot_s stay with the same packet but with new seq number
		elif (robot_state == 2):
			print "\rWaiting for the robot to be restarted",
			sys.stdout.flush();
    
def signal_handler(signal, frame):
    sock1.close()
    sock2.close()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

t1 = threading.Thread(target=readSignals);
t2 = threading.Thread(target=sendPackets);
t1.daemon = True;
t2.daemon = True;
t1.start();
t2.start();

while(line_no < MAX_LINES):
   time.sleep(1)

sock1.close()
sock2.close()
sys.exit(0)


 



