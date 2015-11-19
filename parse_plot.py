'''/* Runs Raven 2 simulator by calling packet generator, Raven control software, and visualization code
 * Copyright (C) 2015 University of Illinois Board of Trustees, DEPEND Research Group, Creators: Homa Alemzadeh and Daniel Chen
 *
 * This file is part of Raven 2 Surgical Simulator.
 * Provides functions for parsing CSV results files and plotting data
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

import csv
import time
import os
import subprocess
import sys
import matplotlib.pyplot as plt
import math
import numpy as np 
from sys import argv

def parse_latest_run(reader):
	indices = [0,1,2,4,5,6,7]
	runlevel = 0
	packet_no = 111
	line_no = 0
	headers = reader.next()
	#print headers
	# Find the indices for the variables in the datashee
	runlevel_index = headers.index('field.runlevel'); 
	packet_index = headers.index('field.last_seq'); 
	mpos_index = headers.index('field.mpos0');
	dmpos_index = headers.index('field.mpos_d0');
	mvel_index = headers.index('field.mvel0');
	dmvel_index = headers.index('field.mvel_d0');
	dac_index = headers.index('field.current_cmd0');
	jpos_index = headers.index('field.jpos0');
	djpos_index = headers.index('field.jpos_d0');
	dpos_index = headers.index('field.pos_d0');
	pos_index = headers.index('field.pos0');
	try:
		err_index = headers.index('field.err_msg');
	except:
		err_index = -1

	# Skip the datasheet lines until runlevel = 3 and packet number is 1
	while (runlevel < 3) or (packet_no == 111) or (packet_no == 0):
		line = reader.next()
		runlevel = int(line[runlevel_index])
		packet_no = int(line[packet_index])
		#print runlevel
		line_no = line_no + 1
	print '\rStarted at Line = '+ str(line_no)+ ', Packet = '+str(packet_no)+', Run Level = '+str(runlevel)

	# Get the estimated desired and actual trajectories from the last run 
	est_dmpos = [[],[],[],[],[],[],[]] 
	est_mpos = [[],[],[],[],[],[],[]]
	est_mvel = [[],[],[],[],[],[],[]]
	est_dac = [[],[],[],[],[],[],[]]
	est_djpos = [[],[],[],[],[],[],[]]
	est_jpos = [[],[],[],[],[],[],[]]
	est_dpos = [[],[],[]]
	est_pos = [[],[],[]]
	err_msg = []
	packet_nums = []
	time = []

	i = 0
	past_line = ''
	for l in reader:
	# We are going to compare estimated ones, so shift one sample ahead
		if (i > 1) and (int(l[runlevel_index]) == 3):  
			if not(packet_no == int(l[packet_index])):	
				packet_nums.append(packet_no)
				time.append(float(line[0])-t0)
				for j in range(0,7):			
					est_dmpos[j].append(float(line[dmpos_index+indices[j]])*math.pi/180)
					est_mpos[j].append(float(line[mpos_index+indices[j]])*math.pi/180)
					est_mvel[j].append(float(line[mvel_index+indices[j]])*math.pi/180)
				for j in range(0,7):
					est_dac[j].append(float(line[dac_index+indices[j]]))
				for j in range(0,7):
					est_djpos[j].append(float(line[djpos_index+indices[j]])*math.pi/180)
					est_jpos[j].append(float(line[jpos_index+indices[j]])*math.pi/180)
				for j in range(0,3):
					est_dpos[j].append(float(line[dpos_index+indices[j]])*math.pi/180)
					est_pos[j].append(float(line[pos_index+indices[j]])*math.pi/180)
				try:			
					err_msg.append(str(line[err_index]))
				except:
					pass
			line = l
			packet_no = int(line[packet_index])
		else:
			t0 = float(line[0])
		i = i + 1;
	print len(est_mvel[0])
	print len(est_mpos[0])
	return est_mpos, est_mvel, est_dac, est_jpos, est_pos, err_msg, packet_nums, time 	

#Obselete
def parse_input_data(in_file):
	indices = [0,1,2,4,5,6,7]
	# Get the desired and actural trajectories from the input data
	dmpos = [[],[],[]]
	mpos = [[],[],[]]
	mvel = [[],[],[]]
	dac = [[],[],[],[],[]]
	djpos = [[],[],[],[],[],[],[]]
	jpos = [[],[],[],[],[],[],[]]
	dpos = [[],[],[]]
	pos = [[],[],[]]
	for line in in_file:
		results = line.strip().split(',')
		for j in range(0,7):
			dmpos[j].append(float(results[j*6]))		
			mpos[j].append(float(results[j*6+1]))
			mvel[j].append(float(results[j*6+2]))
		for j in range(0,7):
			dac[j].append(float(results[indices[j]*6+3]))
		for j in range(0,7):
			djpos[j].append(float(results[indices[j]*6+4]))
			jpos[j].append(float(results[indices[j]*6+5]))
		for j in range(0,3):
			dpos[j].append(float(results[48+j*2]))
			pos[j].append(float(results[48+j*2+1]))
	
	return mpos,mvel,dac,jpos,pos

def plot_mpos(gold_mpos, orig_mpos, mpos, gold_mvel, orig_mvel, mvel, gold_t, orig_t, t):
	indices = [0,1,2,4,5,6,7]	
	f1, axarr1 = plt.subplots(7, 2, sharex=True)
	axarr1[0,0].set_title("Motor Positions (Gold Arm)")
	axarr1[0,1].set_title("Motor Velocities (Gold Arm)")
	for j in range(0,7):
		axarr1[j, 0].plot(orig_mpos[j], 'k')
		axarr1[j, 0].plot(gold_mpos[j], 'g')
		axarr1[j, 0].plot(mpos[j], 'r')
		axarr1[j, 1].plot(orig_mvel[j], 'k')
		axarr1[j, 1].plot(gold_mvel[j], 'g')
		axarr1[j, 1].plot(mvel[j], 'r')
		axarr1[j, 0].set_ylabel('Motor '+str(indices[j]))
	#plt.show()
	return f1
  
def plot_dacs(gold_dac, orig_dac, dac, gold_t, orig_t, t):
	indices = [0,1,2,4,5,6,7]
	f2, axarr2 = plt.subplots(7, 1, sharex=True)
	axarr2[0].set_title("DAC Values (Gold Arm)")
	for j in range(0,7):
		axarr2[j].plot(gold_dac[j], 'g')
		axarr2[j].plot(orig_dac[j], 'k')
		axarr2[j].plot(dac[j], 'r')
		axarr2[j].set_ylabel('Joint '+str(indices[j]))
	#plt.show()
	return f2

def plot_jpos(gold_jpos, orig_jpos, jpos, gold_t, orig_t, t):
	indices = [0,1,2,4,5,6,7]
	f3, axarr3 = plt.subplots(7, 1, sharex=True)
	axarr3[0].set_title("Joint Positions (Gold Arm)")
	for j in range(0,7):
		axarr3[j].plot(gold_jpos[j], 'g')
		axarr3[j].plot(orig_jpos[j], 'k')
		axarr3[j].plot(jpos[j], 'r')
		axarr3[j].set_ylabel('Joint '+str(indices[j]))
	#plt.show()
	return f3

def plot_pos(gold_pos, orig_pos, pos, gold_t, orig_t, t):
	indices = [0,1,2,4,5,6,7]
	f4, axarr4 = plt.subplots(3, 1, sharex=True)
	axarr4[0].set_title("End-Effector Positions (Gold Arm)")
	pos_labels = ['X','Y','Z']
	for j in range(0,3):
		axarr4[j].plot(gold_pos[j], 'g')
		axarr4[j].plot(orig_pos[j], 'k')
		axarr4[j].plot(pos[j], 'r')
		axarr4[j].set_ylabel(pos_labels[j])
	#plt.show()
	return f4

# Main Code Starts Here
print "\nPlotting the results.."
# Get raven_home directory
env = os.environ.copy()
splits = env['ROS_PACKAGE_PATH'].split(':')
raven_home = splits[0]

# Parse the arguments
try:
    script, mode  = argv
except:
    print "Error: missing parameters"
    print 'python plot2.py 0|1'
    sys.exit(2)

# Open Log files
csvfile1 = open(raven_home+'/robot_run.csv')
reader1 = csv.reader(x.replace('\0', '') for x in csvfile1)
csvfile2 = open(raven_home+'/golden_run/latest_run.csv')
reader2 = csv.reader(x.replace('\0', '') for x in csvfile2)

# Parse the robot run
orig_mpos, orig_mvel, orig_dac, orig_jpos, orig_pos, orig_err, orig_packets, orig_t = parse_latest_run(reader1)
# Parse the golden simulator run
gold_mpos, gold_mvel, gold_dac, gold_jpos, gold_pos, gold_err, gold_packets, gold_t = parse_latest_run(reader2)
#orig_mpos, orig_mvel, orig_dac, orig_jpos, orig_pos = parse_input_data(in_file)

# Parse the latest run of simulator
csvfile3 = open(raven_home+'/latest_run.csv')
reader3 = csv.reader(x.replace('\0', '') for x in csvfile3)
mpos, mvel, dac, jpos, pos, err, packet_nums, t = parse_latest_run(reader3)

# Close files
csvfile1.close()
csvfile2.close()
csvfile3.close()


plot_mpos(gold_mpos, orig_mpos, mpos, gold_mvel, orig_mvel, mvel, gold_t, orig_t, t).savefig(raven_home+'/figures/mpos_mvel.png')
plot_dacs(gold_dac, orig_dac, dac, gold_t, orig_t, t).savefig(raven_home+'/figures/dac.png')
plot_jpos(gold_jpos, orig_jpos, jpos, gold_t, orig_t, t).savefig(raven_home+'/figures/jpos.png')
plot_pos(gold_pos, orig_pos, pos, gold_t, orig_t, t).savefig(raven_home+'/figures/pos.png')

# Log the results
indices = [0,1,2,4,5,6,7]
posi = ['X','Y','Z']
if mode == '0':
	output_file = raven_home+'/fault_free_log.csv'
if mode == '1':
	output_file = raven_home+'/error_log.csv'
	
# Write the headers for new file
if not(os.path.isfile(output_file)):
	csvfile4 = open(output_file,'w')
	writer4 = csv.writer(csvfile4,delimiter=',') 
	if mode == '0':
		output_line = 'Num_Packets'+','
	if mode == '1':
	    output_line = 'Variable, Start, Duration, Value, Num_Packets, Errors, '
	for i in range(0,len(mpos)):
		output_line = output_line + 'err_mpos' + str(indices[i]) + ','
		output_line = output_line + 'err_mvel' + str(indices[i]) + ','
		output_line = output_line + 'err_jpos' + str(indices[i]) + ','
	for i in range(0,len(pos)):
		if (i == len(pos)-1):
			output_line = output_line + 'err_pos' + str(posi[i])
		else:
			output_line = output_line + 'err_pos' + str(posi[i]) + ','
	if mode == '1':
		output_line = output_line + ', Jump?'
	writer4.writerow(output_line.split(',')) 
	csvfile4.close()

# Write the rows
csvfile4 = open(output_file,'a')
writer4 = csv.writer(csvfile4,delimiter=',') 

# For faulty run, write Injection parameters
if mode == '1':
	csvfile5 = open('./mfi2_params.csv','r')
	inj_param_reader = csv.reader(csvfile5)
	for line in inj_param_reader:
		#print line
		if (int(line[0]) == self.curr_inj):
			param_line = line[1:]
			break 
	csvfile5.close()
	print param_line

# Write Len of Trajectory
output_line = str(len(mpos[0])) + ','

# For faulty run, write error messages and see if a jump happened
if mode == '1':
	# Error messages
	gold_msgs = [s for s in gold_err if s]
	err_msgs = [s for s in err if s]
	# If there are any errors or different errors, print them all
	if err_msgs or not(err_msgs == gold_msgs):  
		for e in set(err_msgs):
			output_line = output_line + '#Packet ' + str(packets[err.index(e)]) +': ' + e
	output_line = output_line +  ','


# Trajectory errors 
mpos_error = [];
mvel_error = [];
jpos_error = [];
pos_error = [];
traj_len = min(len(mpos[0]),len(gold_mpos[0]))
for i in range(0,len(mpos)):		
	mpos_error.append(float(sum(abs(np.array(mpos[i][1:traj_len])-np.array(gold_mpos[i][1:traj_len]))))/traj_len)
	mvel_error.append(float(sum(abs(np.array(mvel[i][1:traj_len])-np.array(gold_mvel[i][1:traj_len]))))/traj_len)
	jpos_error.append(float(sum(abs(np.array(jpos[i][1:traj_len])-np.array(gold_jpos[i][1:traj_len]))))/traj_len)
	output_line = output_line + str(mpos_error[i]) + ', '+ str(mvel_error[i]) +', '+ str(jpos_error[i])+',' 
for i in range(0,len(pos)):    
	pos_error.append(float(sum(abs(np.array(pos[i][1:traj_len])-np.array(gold_pos[i][1:traj_len]))))/traj_len)
	if (i == len(pos)-1):
		output_line = output_line + str(pos_error[i])
	else:
		output_line = output_line + str(pos_error[i])+','

# For faulty run, see if a jump happened
if mode == '1':
	output_line = output_line + ', '+ ''

writer4.writerow(output_line.split(','))    
csvfile4.close()
