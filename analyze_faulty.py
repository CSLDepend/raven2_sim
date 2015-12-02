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
import shelve
from statistics import mean, stdev
from operator import add, sub, mul, abs
from franges import frange

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

def plot_mpos(gold_mpos, mpos, sim_mpos, gold_mvel, mvel, sim_mvel, gold_t, t, mpos_detect, mvel_detect):
	indices = [0,1,2,4,5,6,7]	
	f1, axarr1 = plt.subplots(7, 2, sharex=True)
	plt.tight_layout()
	axarr1[0,0].set_title("Motor Positions (Gold Arm)")
	axarr1[0,1].set_title("Motor Velocities (Gold Arm)")
	for j in range(0,7):
		axarr1[j, 0].plot(gold_mpos[j], 'g')
		axarr1[j, 0].plot(mpos[j], 'r')
		if j < 3 and not(all(v == 0 for v in sim_mpos[j])):	
			axarr1[j, 0].plot(sim_mpos[j], 'b')	
		if j < 3 and mpos_detect: # and not(all(v == 0 for v in mpos_detect[j])):	
			mpos_vline = min(mpos_detect)# min([i for i, e in enumerate(mpos_detect[j]) if e != 0])
			axarr1[j, 0].axvline(x = mpos_vline, color = 'k', ls = 'dashed')
			#axarr1[j, 0].axvline(x = max(mpos_vlines[j]), color = 'k', ls = 'dashed')
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
  
def plot_dacs(gold_dac, dac, gold_t, t):
	indices = [0,1,2,4,5,6,7]
	f2, axarr2 = plt.subplots(7, 1, sharex=True)
	axarr2[0].set_title("DAC Values (Gold Arm)")
	for j in range(0,7):
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

def plot_jpos(gold_jpos, jpos, sim_jpos, gold_t, t, jpos_detect):
	indices = [0,1,2,4,5,6,7]
	f3, axarr3 = plt.subplots(7, 1, sharex=True)
	plt.tight_layout()
	axarr3[0].set_title("Joint Positions (Gold Arm)")
	for j in range(0,7):
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

def plot_pos(gold_pos, pos, gold_t, t,pos_detect):
	indices = [0,1,2,4,5,6,7]
	f4, axarr4 = plt.subplots(3, 1, sharex=True)
	axarr4[0].set_title("End-Effector Positions (Gold Arm)")
	pos_labels = ['X Pos(mm)','Y Pos(mm)','Z Pos(mm)']
	for j in range(0,3):
		axarr4[j].plot(gold_pos[j], 'g')
		axarr4[j].plot(pos[j], 'r')
		#if not(all(v == 0 for v in pos_detect[j])):	
		if pos_detect:
			pos_vline = min(pos_detect)
			#pos_vline = min([i for i, e in enumerate(pos_detect[j]) if e != 0]) 
			axarr4[j].axvline(x = pos_vline, color = 'k', ls = 'dashed')
		axarr4[j].set_ylabel(pos_labels[j])
		axarr4[j].tick_params(axis = 'both', labelsize=10)
	axarr4[j].set_xlabel('Packet No. (ms)')
	plt.tight_layout()	
	#plt.show()
	return f4


# Process each file
def parse_plot(golden_file, run_file, mfi2_param, inj_num): 
	print run_file
	# Open Log files
	csvfile2 = open(golden_file)
	reader2 = csv.reader(x.replace('\0', '') for x in csvfile2)

	# Parse the golden simulator run
	gold_mpos, gold_mvel, gold_dac, gold_jpos, gold_pos, gold_sim_mpos, gold_sim_mvel, gold_sim_jpos,gold_err, gold_packets, gold_t = parse_latest_run(reader2)
	#orig_mpos, orig_mvel, orig_dac, orig_jpos, orig_pos = parse_input_data(in_file)

	# Parse the latest run of simulator
	csvfile3 = open(run_file)
	reader3 = csv.reader(x.replace('\0', '') for x in csvfile3)
	mpos, mvel, dac, jpos, pos, sim_mpos, sim_mvel, sim_jpos, err, packets, t = parse_latest_run(reader3)

	# Close files
	csvfile2.close()
	csvfile3.close()

	# Log the results
	indices = [0,1,2,4,5,6,7]
	posi = ['X','Y','Z']

	# For faulty run, write Injection parameters First
	start = 0
	duration = 0
	csvfile5 = open(mfi2_param,'r')
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

	# Write Len of Trajectory
	output_line = str(len(mpos[0])) + ','

	# For faulty run, write error messages and see if a jump happened
	iSWDetect = ''
	iESTOP = ''
	# Error messages
	gold_msgs = [s for s in gold_err if s]
	err_msgs = [s for s in err if s]
	err_pack_nums = []
	# If there are any errors or different errors, print them all
	if err_msgs or not(err_msgs == gold_msgs):  
		# Find the first occurance of unique error messages
		for e in set(err_msgs):
			#print '#Packet ' + str(packets[err.index(e)]) +': ' + e	
			output_line = output_line + '#Packet ' + str(packets[err.index(e)]) +': ' + e
			err_pack_nums.append(packets[err.index(e)])
			if 'STOP' in e:
				iESTOP = str(packets[err.index(e)])	
		#print err_pack_nums
		#print iESTOP
		# First time software detected something
		iSWDetect = str(min(err_pack_nums))		
		#print iSWDetect
	output_line = output_line +  ','

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
	cf = 1      #coefficient
	sd = 2.58   #standard deviation
	for i in range(0,3):		
		for j in range(0,len(mpos_error[i])):
			#if (abs(mpos_error[i][j]) > 1*float(mpos_lim[i][1])):
			if (abs(mpos_error[i][j]) > cf*float(mpos_lim[i][2])+sd*float(mpos_lim[i][3])):
				error_line = error_line + str(j) + '-'
				#print 'mpos'+str(indices[i])
				#print j
				mpos_detect[i].append(1)
			else:
				mpos_detect[i].append(0)
		error_line = error_line + ','
		for j in range(0,len(mvel_error[i])):
			#if (abs(mvel_error[i][j]) > 1*float(mvel_lim[i][1])): 
			if (abs(mvel_error[i][j]) > cf*float(mvel_lim[i][2])+sd*float(mvel_lim[i][3])):
				error_line = error_line + str(j) +  '-'
				#print 'mvel'+str(indices[i])
				#print j
				mvel_detect[i].append(1)
			else:
				mvel_detect[i].append(0)
		error_line = error_line + ','
		for j in range(0,len(jpos_error[i])):				
			#if (abs(jpos_error[i][j]) > 1*float(jpos_lim[i][1])): 
			if (abs(jpos_error[i][j]) > cf*float(jpos_lim[i][2])+sd*float(jpos_lim[i][3])):
				error_line = error_line + str(j) + '-'
				#print 'jpos'+str(indices[i])+','+str(jpos_error[i][j])+','+str(jpos_lim[i][0])+'|'+str(jpos_lim[i][1])
				#print j 
				jpos_detect[i].append(1)
			else:
				jpos_detect[i].append(0)
		error_line = error_line + ','

	for i in range(0,3):
		for j in range(0,len(pos_error[i])):
			#if (abs(pos_error[i][j]) > 1*float(pos_lim[i][1])):
			if (abs(pos_error[i][j]) > cf*float(pos_lim[i][2])+sd*float(pos_lim[i][3])):
				error_line = error_line + str(j) + '-' 
				#print 'pos'+str(indices[i])
				#print j
				pos_detect[i].append(1)
			else:
				pos_detect[i].append(0)
		error_line = error_line + ','

	# Detector: mvel, mpos, jpos
	true_detect = [[],[],[],[]]
	false_detect = [[],[],[],[]]
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

	#print true_detect
	#print false_detect
	# Write Detections
	for i in range(0, 4):
		if true_detect[i]:
			output_line = output_line + str(true_detect[i])+','
		else:
			output_line = output_line +','

	# SW_Detect
	if (iSWDetect == ''):
		output_line = output_line +','
	else:
		output_line = output_line + str(iSWDetect) +','

	# E-STOP
	if (iESTOP == ''):
		output_line = output_line +','
	else:
		output_line = output_line + str(iESTOP) +','

	# Write Latency
	for i in range(0, 4):
		if true_detect[i]:
			output_line = output_line + str(int(min(true_detect[i]))-istart)+','
		else:
			output_line = output_line +','	

	# SW_Detect
	if (iSWDetect == ''):
		output_line = output_line +','
	else:
		output_line = output_line + str(int(iSWDetect)-istart) +','
		
	# E-STOP
	if (iESTOP == ''):
		output_line = output_line +','
	else:
		output_line = output_line + str(int(iESTOP)-istart) +','			

	# Write Miss Detections
	#print false_detect
	for i in range(0, 3):
		if false_detect[i]:
			output_line = output_line + str('-'.join(map(str,false_detect[i])))+','
		else:
			output_line = output_line +','	
	
        """
	# Update the graphs is they exist
	curr_folder = run_file.split(str(inj_num))[0]
	cmd = 'mkdir -p '+ curr_folder + inj_num + '_fig' 
	os.system(cmd)
	plot_dacs(gold_dac, dac, gold_t, t).savefig(curr_folder + inj_num + '_fig/dac.png')
	plot_mpos(gold_mpos, mpos, sim_mpos, gold_mvel, mvel, sim_mvel, gold_t, t,true_detect[1], true_detect[0]).savefig(curr_folder + inj_num +'_fig/mpos_mvel.png')
	plot_jpos(gold_jpos, jpos, sim_jpos, gold_t, t,true_detect[2]).savefig(curr_folder + inj_num +'_fig/jpos.png')
	plot_pos(gold_pos, pos, gold_t, t,true_detect[3]).savefig(curr_folder + inj_num +'_fig/pos.png')
	plt.close("all")
        """
	return param_line, output_line, error_line


# Main starts here
if __name__ == '__main__':

    usage = 'Usage: python ' + sys.argv[0] + ' <dir>' 
    
    if len(sys.argv) != 2:
        print(usage)
        sys.exit(0)

    # Log the results
    indices = [0,1,2,4,5,6,7]
    posi = ['X','Y','Z']
    output_file = './error_log.csv'

    # Write the headers for new file
    if not(os.path.isfile(output_file)):
        csvfile4 = open(output_file,'w')
        writer4 = csv.writer(csvfile4,delimiter=',') 
        output_line = 'Variable, Start, Duration, Value, Num_Packets, Errors, '
        output_line = output_line + 'T1(mvel), T2(mpos), T3(jpos), T4(pos), T5(SW-Detect), T6(E-STOP), L1(mvel), L2(mpos), L3(jpos), L4(pos), L5(SW-Detect),L6(E-STOP), F1(mvel), F2(mpos), F3(jpos), '
        for i in range(0,3):
            output_line = output_line + 'err_mpos' + str(indices[i]) + ','
            output_line = output_line + 'err_mvel' + str(indices[i]) + ','
            output_line = output_line + 'err_jpos' + str(indices[i]) + ','
        for i in range(0,3):
            if (i == 2):
                output_line = output_line + 'err_pos' + str(posi[i])
            else:
                output_line = output_line + 'err_pos' + str(posi[i]) + ','
        writer4.writerow(output_line.split(',')) 
        csvfile4.close()

    # Write the rows
    csvfile4 = open(output_file,'a')
    writer4 = csv.writer(csvfile4,delimiter=',') 

    #Get all csv files in current directory and subdirectories
    all_files = []
    golden_file = []
    param_file = []
    for root, dirs, files in os.walk(sys.argv[1]):
        for f in files:
            if f.endswith('csv') and not f.startswith('mfi2') and not f.startswith('traj') and os.stat(os.path.join(root,f)).st_size > 23000*1024:
                all_files.append(os.path.join(root,f))
            if f.endswith('trj'):
               golden_file.append(os.path.join(root,f))
            if f.endswith('param'):
               param_file.append(os.path.join(root,f))

    for f in all_files:
        bname = os.path.basename(f)
        inj_num = bname.split('.')[0]

        g_file = ''
        for g in golden_file:
            bname = os.path.basename(g)
            key = bname.split('.')[0]
            if key in f:
                g_file = g
                break
        if not g_file:
            print "Cannot find matching golden file"
            sys.exit(0)
        
        p_file = ''            
        for p in param_file:
            bname = os.path.basename(p)
            key = bname.split('.')[0]
            if key in f:
                p_file = p
                #print p_file
                break
        if not p_file:
            print "Cannot find matching param file"
            sys.exit(0)
        
        param_line, output_line, error_line = parse_plot(g_file, f, p_file, inj_num)
    
        # Write to CSV file	
        output_line = output_line.rstrip(',')
        writer4.writerow(param_line+output_line.split(',')+error_line.split(','))    
    csvfile4.close()
