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
from parse_plot import *

def eclud_dist(x1,y1,z1, x2,y2,z2):
	dist = math.sqrt(pow((x1-x2),2)+pow((y1-y2),2)+pow((z1-z2),2))
	return dist

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

	# Find dropped packets
	dropped = []
	for i in range(0, len(packets)-1):
		if not(int(packets[i]) == int(packets[i+1]) -1):
			for j in range(int(packets[i])+1,int(packets[i+1])):
				dropped.append(j)
	print 'Dropped Packets = '+str(dropped)
	
	output_line = ''
	
	# For faulty run, write Injection parameters First
	start = 0
	duration = 0
	csvfile5 = open(mfi2_param,'r')
	inj_param_reader = csv.reader(csvfile5)
	for line in inj_param_reader:
		#print line
		if (int(line[0]) == int(inj_num)):
			param_line = line
			print 'Inj Params = '+str(param_line)
			# Fix duration when dropped packets in the duration
			iduration = int(line[3])
			for d in dropped:
				if (int(line[2]) <= d and d < int(line[2]) + int(line[3])):
					iduration = iduration - 1 			
			# Fix iStart when Dropped packets
			if int(int(line[2])) in packets:
				istart = int(packets.index(int(line[2])))
				print "iStart verify = " + str(packets.index(int(line[2])))			
			# If injected packet is not in the packets
			else:
				# injection packet dropped
				if int(line[2]) <= max(packets):				
					istart = int(line[2]) 					
					for d in dropped:
						if (int(line[2]) >= d):
							istart = istart - 1
				# file corrupted: injection beyond packets in the file
				else:
					print 'ERROR: File probably corrupted. Injection beyond trajectory length\n'
					return '','',''
			# If the duration of attack is within the trajectory
			if istart+iduration < len(packets):
				for i in range(istart-3,istart+iduration):
					print str(i)+'='+str(packets[i])+':'+str(dac[0][i])			
			else:
				print 'ERROR: File probably corrupted. Injection beyond trajectory length\n'
				return '','',''
			# Write output
			if not(istart == int(line[2])):
				print 'Injection Start Fixed = '+str(istart)
			output_line = output_line + str(istart)+','	
			if not(iduration == int(line[3])):
				print 'Injection Duration Fixed = '+str(iduration)
			output_line = output_line + str(iduration)+','					
			break 
	csvfile5.close()
		
	# Write Len of Trajectory
	output_line = output_line + str(len(mpos[0])) + ','

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
                if err_pack_nums:
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
			if (abs(mpos_error[i][j]) > cf*float(mpos_lim[i][2])+sd*float(mpos_lim[i][3])) or (abs(mpos_error[i][j]) < cf*float(mpos_lim[i][2])-sd*float(mpos_lim[i][3])):
				error_line = error_line + str(j) + '-'
				#print 'mpos'+str(indices[i])
				#print j
				mpos_detect[i].append(1)
			else:
				mpos_detect[i].append(0)
		error_line = error_line + ','
		for j in range(0,len(mvel_error[i])):
			#if (abs(mvel_error[i][j]) > 1*float(mvel_lim[i][1])): 
			if (abs(mvel_error[i][j]) > cf*float(mvel_lim[i][2])+sd*float(mvel_lim[i][3])) or (abs(mvel_error[i][j]) < cf*float(mvel_lim[i][2])-sd*float(mvel_lim[i][3])):
				error_line = error_line + str(j) +  '-'
				#print 'mvel'+str(indices[i])
				#print j
				mvel_detect[i].append(1)
			else:
				mvel_detect[i].append(0)
		error_line = error_line + ','
		for j in range(0,len(jpos_error[i])):				
			#if (abs(jpos_error[i][j]) > 1*float(jpos_lim[i][1])): 
			if (abs(jpos_error[i][j]) > cf*float(jpos_lim[i][2])+sd*float(jpos_lim[i][3])) or (abs(jpos_error[i][j]) < cf*float(jpos_lim[i][2])-sd*float(jpos_lim[i][3])):
				error_line = error_line + str(j) + '-'
				#print 'jpos'+str(indices[i])+','+str(jpos_error[i][j])+','+str(jpos_lim[i][0])+'|'+str(jpos_lim[i][1])
				#print j 
				jpos_detect[i].append(1)
			else:
				jpos_detect[i].append(0)
		error_line = error_line + ','

	for i in range(0,3):
		for j in range(0,len(pos_error[i])):
			if (abs(pos_error[i][j]) > 1*float(pos_lim[i][1])):
			#if (abs(pos_error[i][j]) > cf*float(pos_lim[i][2])+sd*float(pos_lim[i][3])):
				error_line = error_line + str(j) + '-' 
				#print 'pos'+str(indices[i])
				#print j
				pos_detect[i].append(1)
			else:
				pos_detect[i].append(0)
		error_line = error_line + ','
	# Ecludian distance
	pos_ecludian = []
	for i in range(0,len(pos[0])-1):
		pos_ecludian.append(eclud_dist(pos[0][i],pos[1][i],pos[2][i], pos[0][i+1],pos[1][i+1],pos[2][i+1]))

	# Detector: mvel, mpos, jpos
	true_detect = [[],[],[],[]]
	false_detect = [[],[],[],[]]
	mpos_all_d = list(np.array(mpos_detect[0])|np.array(mpos_detect[1])|np.array(mpos_detect[2]))
	mvel_all_d = list(np.array(mvel_detect[0])|np.array(mvel_detect[1])|np.array(mvel_detect[2]))
	jpos_all_d = list(np.array(jpos_detect[0])|np.array(jpos_detect[1])|np.array(jpos_detect[2]))
	pos_all_d_pre = list(np.array(pos_detect[0])|np.array(pos_detect[1])|np.array(pos_detect[2]))
	# If Ecludian distance more than ?mm
	pos_threshold = 0.3
	pos_all_d = [0]*len(pos_ecludian)
	for i in range(0,len(pos_all_d)):
		if (pos_ecludian[i] > pos_threshold): # pos_all_d_pre[i]:
			pos_all_d[i] = 1
	'''if int(inj_num) == 531:
		print pos_ecludian[990:1010]
		print pos_ecludian[1000]
		print pos_ecludian[1001]
		print dac[0][990:1010]
		print gold_dac[0][990:1010]'''
			
	# MVEL Detect
	i = 0	
	while i < len(mvel_all_d):
		if mvel_all_d[i]:# and ((mpos_all_d[i-2] or mpos_all_d[i-1] or mpos_all_d[i])):
			if (istart <= i) and (i <= istart + iduration):
				true_detect[0].append(i)	
				i = istart+iduration+2
			else:
				false_detect[0].append(i)
				while i < len(mvel_all_d) and mvel_all_d[i]:	
					i = i + 1
		else:
			i = i + 1
	#MPOS Detect		
	i = 0
	while i < len(mpos_all_d):
		if mpos_all_d[i]:# and ((mvel_all_d[i-2] or mvel_all_d[i-1] or mvel_all_d[i])):
			if (istart <= i) and (i <= istart + iduration):
				true_detect[1].append(i)	
				i = istart+iduration+2
			else:
				false_detect[1].append(i)
				while i < len(mpos_all_d) and mpos_all_d[i]:		
					i = i + 1
		else:
			i = i + 1
	# JPOS Detect
	i = 0
	while i < len(jpos_all_d):
		if jpos_all_d[i]:# and ((mpos_all_d[i-2] or mpos_all_d[i-1] or mpos_all_d[i])):
			if (istart <= i) and (i <= istart + iduration):
				true_detect[2].append(i)	
				i = istart+iduration+2
			else:
				false_detect[2].append(i)
				while i < len(jpos_all_d) and jpos_all_d[i]:	
					i = i + 1			
		else:
			i = i + 1	
	# POS Detect is only true detection if it is within fault activation period and all others also detecte
	# Pos Detect		
	i = 0
	while i < len(pos_all_d):
		if (pos_all_d[i] == 1):# and ((jpos_all_d[i-2] or jpos_all_d[i-1] or jpos_all_d[i])):
			if (istart <= i) and (i <= istart + iduration):
				true_detect[3].append(i)	
				i = istart+iduration+2
			else:
				false_detect[3].append(i)
				while i < len(pos_all_d) and pos_all_d[i]:	
					i = i + 1			
		else:
			i = i + 1	
	
	'''if int(inj_num) == 531:
		print 'detected at'+str(true_detect[3])
		print 'detected: '+str(pos_ecludian[min(true_detect[3])])'''
		
	#print true_detect
	#print false_detect
	# Write Detections
	for i in range(0, 4):
		if true_detect[i]:
			output_line = output_line + str(min(true_detect[i]))+','
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
	for i in range(0, 4):
		if false_detect[i]:
			output_line = output_line + str('-'.join(map(str,false_detect[i])))+','
		else:
			output_line = output_line +','	
	
	# Update the graphs is they exist
	curr_folder = run_file.split(str(inj_num)+'.csv')[0]
	print run_file
	print str(inj_num)
	print curr_folder
	fig_folder = [curr_folder+f for f in os.listdir(curr_folder) if f.startswith('inj'+str(int(inj_num))+'_')]
	fig_folder = fig_folder[0]+'/'
	cmd = 'mkdir -p '+ fig_folder
	os.system(cmd)
	plot_dacs(gold_dac, dac, gold_t, t).savefig(fig_folder + 'dac.png')
	plot_mpos('1',gold_mpos, mpos, sim_mpos, gold_mvel, mvel, sim_mvel, gold_t, t,true_detect[1], true_detect[0]).savefig(fig_folder + 'mpos_mvel.png')
	plot_jpos(gold_jpos, jpos, sim_jpos, gold_t, t,true_detect[2]).savefig(fig_folder + 'jpos.png')
	plot_pos(gold_pos, pos, gold_t, t,true_detect[3]).savefig(fig_folder + 'pos.png')
	plot_dist(pos, pos_ecludian, true_detect[3]).savefig(fig_folder + 'pos_dist.png')
	plt.close("all")
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
        output_line = 'InjNum,Variable,Start,Duration,Value,FixedStart,FixedDuration,Num_Packets,Errors,'
        output_line = output_line + 'T1(mvel),T2(mpos),T3(jpos),T4(pos),T5(SW-Detect),T6(E-STOP),L1(mvel),L2(mpos),L3(jpos),L4(pos),L5(SW-Detect),L6(E-STOP),F1(mvel),F2(mpos),F3(jpos),F4(pos),'
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
            if f.endswith('csv') and not f.startswith('mfi2') and not f.startswith('traj') and not f.startswith('error_log') and (os.stat(os.path.join(root,f)).st_size > 0):
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
    	if param_line:
			# Write to CSV file	
			output_line = output_line.rstrip(',')
			writer4.writerow(param_line+output_line.split(',')+error_line.split(','))    
    csvfile4.close()
