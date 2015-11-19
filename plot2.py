'''/* Runs Raven 2 simulator by calling packet generator, Raven control software, and visualization code
 * Copyright (C) 2015 University of Illinois Board of Trustees, DEPEND Research Group, Creators: Homa Alemzadeh and Daniel Chen
 *
 * This file is part of Raven 2 Surgical Simulator.
 * Plots the results of the latest run vs. the golden run 
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
from parse_plot import *
from sys import argv


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
    print 'python plot2.py plot|log'
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


if mode == "log":
	indices = [0,1,2,4,5,6,7]
	posi = ['X','Y','Z']
	if not(os.path.isfile(raven_home+'/fault_free_log.csv')):
		csvfile4 = open(raven_home+'/fault_free_log.csv','w')
		writer4 = csv.writer(csvfile4,delimiter=',') 
		# For rt_process_preempt:
		output_line = ''
		for i in range(0,len(mpos)):
			output_line = output_line + 'err_mpos' + str(indices[i]) + ','
			output_line = output_line + 'err_mvel' + str(indices[i]) + ','
			output_line = output_line + 'err_jpos' + str(indices[i]) + ','
		for i in range(0,len(pos)):
			if (i == len(pos)-1):
				output_line = output_line + 'err_pos' + str(posi[i])
			else:
				output_line = output_line + 'err_pos' + str(posi[i]) + ','
		writer4.writerow(output_line.split(',')) 
		csvfile4.close()
		
	csvfile4 = open(raven_home+'/fault_free_log.csv','a')
	writer4 = csv.writer(csvfile4,delimiter=',') 

	output_line = ''
	# Trajectory errors 
	mpos_error = [];
	mvel_error = [];
	jpos_error = [];
	pos_error = [];
	for i in range(0,len(mpos)):
		traj_len = min(len(mpos[0]),len(gold_mpos[0]))
		mpos_error.append(float(sum(abs(np.array(mpos[i][1:traj_len])-np.array(gold_mpos[i][1:traj_len]))))/traj_len)
		mvel_error.append(float(sum(abs(np.array(mvel[i][1:traj_len])-np.array(gold_mvel[i][1:traj_len]))))/traj_len)
		jpos_error.append(float(sum(abs(np.array(jpos[i][1:traj_len])-np.array(gold_jpos[i][1:traj_len]))))/traj_len)
		output_line = output_line + str(mpos_error[i]) + ', '+ str(mvel_error[i]) +', '+ str(jpos_error[i])+',' 
	for i in range(0,len(pos)):    
		traj_len = min(len(pos[0]),len(gold_pos[0]))
		pos_error.append(float(sum(abs(np.array(pos[i][1:traj_len])-np.array(gold_pos[i][1:traj_len]))))/traj_len)
		if (i == len(pos)-1):
			output_line = output_line + str(pos_error[i])
		else:
			output_line = output_line + str(pos_error[i])+','
	writer4.writerow(output_line.split(','))    
	csvfile4.close()


