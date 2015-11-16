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
	plt.show()
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
	plt.show()
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
	plt.show()
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
	plt.show()
	return f4
