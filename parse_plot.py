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
		sim_index = headers.index('field.sim_mpos0');
	except:
		sim_index = -1
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
	sim_mpos = [[],[],[]]
	sim_mvel = [[],[],[]]
	sim_jpos = [[],[],[]]
	
	i = 0
	past_line = ''
	for l in reader:
	# We are going to compare estimated ones, so shift one sample ahead
		if (i > 1) and (int(l[runlevel_index]) == 3):  
			if not(packet_no == int(l[packet_index])):	
				packet_nums.append(packet_no)
				time.append(float(line[0])-t0)
				for j in range(0,7):			
					est_dmpos[j].append(float(line[dmpos_index+indices[j]]))#*math.pi/180)
					est_mpos[j].append(float(line[mpos_index+indices[j]]))#*math.pi/180)
					est_mvel[j].append(float(line[mvel_index+indices[j]]))#*math.pi/180)
				for j in range(0,7):
					est_dac[j].append(float(line[dac_index+indices[j]]))
				for j in range(0,7):
					if j == 2:
						est_djpos[j].append(float(line[djpos_index+indices[j]])*(math.pi/180)*1000)
						est_jpos[j].append(float(line[jpos_index+indices[j]])*(math.pi/180)*1000)
					else:
						est_djpos[j].append(float(line[djpos_index+indices[j]]))#*math.pi/180)
						est_jpos[j].append(float(line[jpos_index+indices[j]]))#*math.pi/180)
				for j in range(0,3):
					est_dpos[j].append(float(line[dpos_index+indices[j]])/1000)#*math.pi/180)
					est_pos[j].append(float(line[pos_index+indices[j]])/1000)#*math.pi/180)
				try:			
					for j in range(0,3):
						sim_mpos[j].append(float(line[sim_index+indices[j]]))
						sim_mvel[j].append(float(line[sim_index+3+indices[j]]))
						sim_jpos[j].append(float(line[sim_index+6+indices[j]]))
				except:
					pass
				try:			
					err_msg.append(str(line[err_index]))
				except:
					pass
			line = l
			packet_no = int(line[packet_index])
		else:
			t0 = float(line[0])
		i = i + 1;
	
	for j in range(0,3):
		if not(all(v == 0 for v in sim_jpos[j])):
			init_diff = float(est_jpos[j][0]) - float(sim_jpos[j][0])
			sim_jpos[j] = [x+init_diff for x in sim_jpos[j]]
	print len(est_mvel[0])
	print len(est_mpos[0])
	return est_mpos, est_mvel, est_dac, est_jpos, est_pos, sim_mpos, sim_mvel, sim_jpos, err_msg, packet_nums, time 	

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

def plot_mpos(m, gold_mpos, orig_mpos, mpos, sim_mpos, gold_mvel, orig_mvel, mvel, sim_mvel, gold_t, orig_t, t, mpos_detect, mvel_detect):
	indices = [0,1,2,4,5,6,7]	
	f1, axarr1 = plt.subplots(7, 2, sharex=True)
	plt.tight_layout()
	axarr1[0,0].set_title("Motor Positions (Gold Arm)")
	axarr1[0,1].set_title("Motor Velocities (Gold Arm)")
	for j in range(0,7):
		axarr1[j, 0].plot(orig_mpos[j], 'k')
		axarr1[j, 0].plot(gold_mpos[j], 'g')
		axarr1[j, 0].plot(mpos[j], 'r')
		if j < 3 and not(all(v == 0 for v in sim_mpos[j])):	
			axarr1[j, 0].plot(sim_mpos[j], 'b')	
		if j < 3 and mpos_detect: # and not(all(v == 0 for v in mpos_detect[j])):	
			mpos_vline = min(mpos_detect)# min([i for i, e in enumerate(mpos_detect[j]) if e != 0])
			axarr1[j, 0].axvline(x = mpos_vline, color = 'k', ls = 'dashed')
			#axarr1[j, 0].axvline(x = max(mpos_vlines[j]), color = 'k', ls = 'dashed')
		axarr1[j, 1].plot(orig_mvel[j], 'k')
		axarr1[j, 1].plot(gold_mvel[j], 'g')
		axarr1[j, 1].plot(mvel[j], 'r')
		if j < 3 and not(all(v == 0 for v in sim_mvel[j])):	
			axarr1[j, 1].plot(sim_mvel[j], 'b')
		if j < 3 and mvel_detect: #and not(all(v == 0 for v in mvel_detect[j])):	
			mvel_vline = min(mvel_detect)#min([i for i, e in enumerate(mvel_detect[j]) if e != 0]) 
			axarr1[j, 1].axvline(x = mvel_vline, color = 'k', ls = 'dashed')
			#axarr1[j, 1].axvline(x = max(mvel_vlines[j]), color = 'k', ls = 'dashed')			
		# Set the row labels
		axarr1[j, 0].set_ylabel('Motor '+str(indices[j]))
		# Set the Y ticks
		axarr1[j, 0].locator_params(axis = 'y', nbins = 3)
		axarr1[j, 0].tick_params(axis = 'both', labelsize=10)
		# Set the Y ticks
		axarr1[j, 1].locator_params(axis = 'y', nbins = 3)
		axarr1[j, 1].tick_params(axis = 'both', labelsize=10)		
	# Set the column labels
	axarr1[j, 0].set_xlabel('Packet No. (ms)')
	axarr1[j, 1].set_xlabel('Packet No. (ms)')
	plt.tight_layout()	
	#plt.show()
	return f1
  
def plot_dacs(gold_dac, orig_dac, dac, gold_t, orig_t, t):
	indices = [0,1,2,4,5,6,7]
	f2, axarr2 = plt.subplots(7, 1, sharex=True)
	axarr2[0].set_title("DAC Values (Gold Arm)")
	for j in range(0,7):
		axarr2[j].plot(orig_dac[j], 'k')
		axarr2[j].plot(gold_dac[j], 'g')
		axarr2[j].plot(dac[j], 'r')
		axarr2[j].set_ylabel('Joint '+str(indices[j]))
		# Set the Y ticks
		axarr2[j].locator_params(axis = 'y', nbins = 3)
		axarr2[j].tick_params(axis = 'both', labelsize=10)
	axarr2[j].set_xlabel('Packet No. (ms)')
	plt.tight_layout()
	#plt.show()
	return f2

def plot_jpos(gold_jpos, orig_jpos, jpos, sim_jpos, gold_t, orig_t, t, jpos_detect):
	indices = [0,1,2,4,5,6,7]
	f3, axarr3 = plt.subplots(7, 1, sharex=True)
	plt.tight_layout()
	axarr3[0].set_title("Joint Positions (Gold Arm)")
	for j in range(0,7):
		axarr3[j].plot(orig_jpos[j], 'k')
		axarr3[j].plot(gold_jpos[j], 'g')
		axarr3[j].plot(jpos[j], 'r')
		if j < 3 and not(all(v == 0 for v in sim_jpos[j])):	
			axarr3[j].plot(sim_jpos[j], 'b')			
		if j < 3 and jpos_detect: #and not(all(v == 0 for v in jpos_detect[j])):	
			jpos_vline = min(jpos_detect)#min([i for i, e in enumerate(jpos_detect[j]) if e != 0]) 
			axarr3[j].axvline(x = jpos_vline, color = 'k', ls = 'dashed')
			#axarr3[j].axvline(x = max(jpos_vlines[j]), color = 'k', ls = 'dashed')		
		axarr3[j].set_ylabel('Joint '+str(indices[j]))
		# Set the Y ticks
		axarr3[j].locator_params(axis = 'y', nbins = 3)
		axarr3[j].tick_params(axis = 'both', labelsize=10)
	axarr3[j].set_xlabel('Packet No. (ms)')		
	plt.tight_layout()	
	#plt.show()
	return f3

def plot_pos(gold_pos, orig_pos, pos, gold_t, orig_t, t,pos_detect):
	indices = [0,1,2,4,5,6,7]
	f4, axarr4 = plt.subplots(3, 1, sharex=True)
	axarr4[0].set_title("End-Effector Positions (Gold Arm)")
	pos_labels = ['X Pos(mm)','Y Pos(mm)','Z Pos(mm)']
	for j in range(0,3):
		axarr4[j].plot(orig_pos[j], 'k')
		axarr4[j].plot(gold_pos[j], 'g')
		axarr4[j].plot(pos[j], 'r')
		#if not(all(v == 0 for v in pos_detect[j])):	
		if pos_detect:
			pos_vline = min(pos_detect)#pos_vline = min([i for i, e in enumerate(pos_detect[j]) if e != 0]) 
			axarr4[j].axvline(x = pos_vline, color = 'k', ls = 'dashed')
		axarr4[j].set_ylabel(pos_labels[j])
		axarr4[j].tick_params(axis = 'both', labelsize=10)
	axarr4[j].set_xlabel('Packet No. (ms)')
	plt.tight_layout()	
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
    script, pmode, inj_num, traj  = argv
except:
    print "Error: missing parameters"
    print 'python plot2.py 0|1 inj_num traj_name'
    sys.exit(2)
    
print 'Mode = '+str(pmode)

# Open Log files
csvfile1 = open(raven_home+'/robot_run.csv')
reader1 = csv.reader(x.replace('\0', '') for x in csvfile1)
csvfile2 = open(raven_home+'/golden_run/'+traj+'.csv')
reader2 = csv.reader(x.replace('\0', '') for x in csvfile2)

# Parse the robot run
orig_mpos, orig_mvel, orig_dac, orig_jpos, orig_pos, orig_sim_mpos, orig_sim_mvel, orig_sim_jpos,orig_err, orig_packets, orig_t = parse_latest_run(reader1)
# Parse the golden simulator run
gold_mpos, gold_mvel, gold_dac, gold_jpos, gold_pos, gold_sim_mpos, gold_sim_mvel, gold_sim_jpos,gold_err, gold_packets, gold_t = parse_latest_run(reader2)
#orig_mpos, orig_mvel, orig_dac, orig_jpos, orig_pos = parse_input_data(in_file)

# Parse the latest run of simulator
csvfile3 = open(raven_home+'/latest_run.csv')
reader3 = csv.reader(x.replace('\0', '') for x in csvfile3)
mpos, mvel, dac, jpos, pos, sim_mpos, sim_mvel, sim_jpos, err, packets, t = parse_latest_run(reader3)

# Close files
csvfile1.close()
csvfile2.close()
csvfile3.close()

# Log the results
indices = [0,1,2,4,5,6,7]
posi = ['X','Y','Z']

'''# For faulty run, write Injection parameters First
if str(pmode) == '1':
	start = 0
	duration = 0
	csvfile5 = open('./mfi2_params.csv','r')
	inj_param_reader = csv.reader(csvfile5)
	for line in inj_param_reader:
		#print line
		if (int(line[0]) == int(inj_num)):
			param_line = line[1:]
			print param_line
			istart = int(line[2])
			iduration = int(line[3])
			break 
	csvfile5.close()
	

mpos_detect = [[],[],[]]
mvel_detect = [[],[],[]]
jpos_detect = [[],[],[]]
pos_detect = [[],[],[]]

# Get the bounds to see if a jump happened
csvfile6 = open('./stats','rU')
range_reader = csv.reader(csvfile6)
mpos_lim = []
mvel_lim = []
jpos_lim = []
pos_lim = []
mpos_dist = []
mvel_dist = []
jpos_dist = []
pos_dist = []	
for line in range_reader:
	if 'mpos_delta' in line[0]:
		mpos_lim.append(line[1:])
	elif 'mvel_delta' in line[0]:
		mvel_lim.append(line[1:])
	elif 'jpos_delta' in line[0]:
		jpos_lim.append(line[1:])
	elif 'pos_delta' in line[0]:
		pos_lim.append(line[1:])
	elif 'mpos_dist' in line[0]:
		mpos_dist.append(line[1:])
	elif 'mvel_dist' in line[0]:
		mvel_dist.append(line[1:])
	elif 'jpos_dist' in line[0]:
		jpos_dist.append(line[1:])
	elif 'pos_dist' in line[0]:
		pos_dist.append(line[1:])			
csvfile6.close()	

# Step Errors
mpos_error = [[],[],[]];
mvel_error = [[],[],[]];
jpos_error = [[],[],[]];
pos_error = [[],[],[]];
for i in range(0,len(mpos_error)):		
	mpos_error[i]=(list(np.array(mpos[i][1:])-np.array(mpos[i][:-1])))
	mvel_error[i]=(list(np.array(mvel[i][1:] )-np.array(mvel[i][:-1])))
	jpos_error[i]=(list(np.array(jpos[i][1:])-np.array(jpos[i][:-1])))
for i in range(0,len(pos_error)):    
	pos_error[i]=(list(np.array(pos[i][1:])-np.array(pos[i][:-1])))	

# Find jumps in delta
error_line = ''
for i in range(0,3):		
	for j in range(0,len(mpos_error[i])):
		if (abs(mpos_error[i][j]) > 1*float(mpos_lim[i][2])+2.58*float(mpos_lim[i][3])):
			error_line = error_line + str(j) + '-'
			#print 'mpos'+str(indices[i])
			#print j
			mpos_detect[i].append(1)
		else:
			mpos_detect[i].append(0)
	for j in range(0,len(mvel_error[i])):
		if (abs(mvel_error[i][j]) > 1*float(mvel_lim[i][2])+2.58*float(mvel_lim[i][3])): 
			error_line = error_line + str(j) +  '-'
			#print 'mvel'+str(indices[i])
			#print j
			mvel_detect[i].append(1)
		else:
			mvel_detect[i].append(0)
	for j in range(0,len(jpos_error[i])):				
		if (abs(jpos_error[i][j]) > 1*float(jpos_lim[i][2])+2.58*float(jpos_lim[i][3])): 
			error_line = error_line + str(j) + '-'
			#print 'jpos'+str(indices[i])+','+str(jpos_error[i][j])+','+str(jpos_lim[i][0])+'|'+str(jpos_lim[i][1])
			#print j 
			jpos_detect[i].append(1)
		else:
			jpos_detect[i].append(0)

for i in range(0,3):
	for j in range(0,len(pos_error[i])):
		if (abs(pos_error[i][j]) > 1*float(pos_lim[i][2])+2.58*float(pos_lim[i][3])):
			error_line = error_line + str(j) + '-' 
			#print 'pos'+str(indices[i])
			#print j
			pos_detect[i].append(1)
		else:
			pos_detect[i].append(0)'''

# Detector: mvel, mpos, jpos
true_detect = [[],[],[],[]]
false_detect = [[],[],[],[]]
'''
if str(pmode) == '1':
	mpos_all_d = list(np.array(mpos_detect[0])|np.array(mpos_detect[1])|np.array(mpos_detect[2]))
	mvel_all_d = list(np.array(mvel_detect[0])|np.array(mvel_detect[1])|np.array(mvel_detect[2]))
	jpos_all_d = list(np.array(jpos_detect[0])|np.array(jpos_detect[1])|np.array(jpos_detect[2]))
	pos_all_d = list(np.array(pos_detect[0])|np.array(pos_detect[1])|np.array(pos_detect[2]))
	# MVEL Detect
	i = 0	
	while i < len(mvel_all_d):
		if mvel_all_d[i]:
			if (istart <= i) and (i <= istart + iduration + 1):
				true_detect[0].append(i)	
				i = istart+iduration+2
			else:
				false_detect[0].append(i)
				while mvel_all_d[i]:	
					i = i + 1	
		else:
			i = i + 1
	#MPOS Detect		
	i = 0
	while i < len(mpos_all_d):
		if mpos_all_d[i]:
			if (istart <= i) and (i <= istart + iduration + 1):
				true_detect[1].append(i)	
				i = istart+iduration+2
			else:
				false_detect[1].append(i)
				while mpos_all_d[i]:		
					i = i + 1
		else:
			i = i + 1
	# JPOS Detect
	i = 0
	while i < len(jpos_all_d):
		if jpos_all_d[i]:
			if (istart <= i) and (i <= istart + iduration + 1):
				true_detect[2].append(i)	
				i = istart+iduration+2
			else:
				false_detect[2].append(i)
				while jpos_all_d[i]:	
					i = i + 1			
		else:
			i = i + 1	
	# Pos Detect		
	i = 0
	while i < len(pos_all_d):
		if pos_all_d[i]:
			if (istart <= i) and (i <= istart + iduration + 1):
				true_detect[3].append(i)	
				i = istart+iduration+2
			else:
				false_detect[3].append(i)
				while pos_all_d[i]:	
					i = i + 1			
		else:
			i = i + 1	
			
	print true_detect
	print false_detect'''

# Plot the graphs
cmd = 'mkdir -p ' + raven_home+'/figures'
os.system(cmd)
plot_dacs(gold_dac, orig_dac, dac, gold_t, orig_t, t).savefig(raven_home+'/figures/dac.png')
plot_mpos(pmode,gold_mpos, orig_mpos, mpos, sim_mpos, gold_mvel, orig_mvel, mvel, sim_mvel, gold_t, orig_t, t,true_detect[1], true_detect[0]).savefig(raven_home+'/figures/mpos_mvel.png')
plot_jpos(gold_jpos, orig_jpos, jpos, sim_jpos, gold_t, orig_t, t,true_detect[2]).savefig(raven_home+'/figures/jpos.png')
plot_pos(gold_pos, orig_pos, pos, gold_t, orig_t, t,true_detect[3]).savefig(raven_home+'/figures/pos.png')

if str(pmode) == '0':
	# Difference between robot and model
	# Write the rows
	if not(os.path.isfile('./sim_robot_results.csv')):
		csvfile7 = open('./sim_robot_results.csv','w')
		writer7 = csv.writer(csvfile7,delimiter=',') 
		writer7.writerow(['mpos_err0','mvel_err0','jpos_err0','mpos_err1','mvel_err1','jpos_err1','mpos_err2','mvel_err2','jpos_err2'])  
		csvfile7.close()

	mpos_rob_err = [[],[],[]]
	mvel_rob_err = [[],[],[]]
	jpos_rob_err = [[],[],[]]
	outline = []
	for j in range(0,3):
		if not(all(v == 0 for v in sim_mpos[j])):	
			traj_len = min(len(mpos[j]),len(sim_mpos[j]))
			mpos_rob_err[j].append(sum(list(abs(np.array(mpos[j][1:traj_len])-np.array(sim_mpos[j][1:traj_len]))))/traj_len)
		if not(all(v == 0 for v in sim_mvel[j])):
			traj_len = min(len(mvel[j]),len(sim_mvel[j]))
			mvel_rob_err[j].append(sum(list(abs(np.array(mvel[j][1:traj_len])-np.array(sim_mvel[j][1:traj_len]))))/traj_len)
		if not(all(v == 0 for v in sim_jpos[j])):
			traj_len = min(len(jpos[j]),len(sim_jpos[j]))
			jpos_rob_err[j].append(sum(list(abs(np.array(jpos[j][1:traj_len])-np.array(sim_jpos[j][1:traj_len]))))/traj_len)
	for j in range(0,3):
		for i in range(0,len(mpos_rob_err[j])):
			outline.extend([mpos_rob_err[j][i],mvel_rob_err[j][i],jpos_rob_err[j][i]])    
	if len(outline) > 0:
		csvfile7 = open('./sim_robot_results.csv','a')
		writer7 = csv.writer(csvfile7,delimiter=',') 
		writer7.writerow(outline)
		csvfile7.close()
