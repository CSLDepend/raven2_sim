import csv
import time
import os
import subprocess
import sys
import matplotlib.pyplot as plt
import math
import numpy as np

print "\nPlotting the results.."
# Get raven_home directory
env = os.environ.copy()
splits = env['ROS_PACKAGE_PATH'].split(':')
raven_home = splits[0]

csvfile1 = open(raven_home+'/latest_run.csv')
reader = csv.reader(csvfile1)
reader = csv.reader(x.replace('\0', '') for x in csvfile1)
in_file = open(raven_home+'/input_data.txt','r')

runlevel = 0
packet_no = 111
line_no = 0
headers = reader.next()
#print headers
# Find the indices for the variables in the datasheet
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

# Skip the datasheet lines until runlevel = 3 and packet number is 1
while (runlevel < 3) or (packet_no == 111) or (packet_no == 0):
	line = reader.next()
	runlevel = int(line[runlevel_index])
	packet_no = int(line[packet_index])
	#print runlevel
	line_no = line_no + 1
print '\rStarted at Line = '+ str(line_no)+ ' and Packet = '+str(packet_no)

# Get the estimated desired and actual trajectories from the last run 
est_dmpos = [[],[],[]] 
est_mpos = [[],[],[]]
est_mvel = [[],[],[]]
est_dac = [[],[],[],[],[]]
est_djpos = [[],[],[],[],[],[],[]]
est_jpos = [[],[],[],[],[],[],[]]
est_dpos = [[],[],[]]
est_pos = [[],[],[]]
indices = [0,1,2,4,5,6,7]
i = 0;
for line in reader:
	# We are going to compare estimated ones, so shift one sample ahead
	if (i > 1):
		for j in range(0,3):			
			est_dmpos[j].append(float(line[dmpos_index+indices[j]])*math.pi/180)
			est_mpos[j].append(float(line[mpos_index+indices[j]])*math.pi/180)
			est_mvel[j].append(float(line[mvel_index+indices[j]])*math.pi/180)
		for j in range(0,5):
			est_dac[j].append(float(line[dac_index+indices[j]]))
		for j in range(0,7):
			est_djpos[j].append(float(line[djpos_index+indices[j]])*math.pi/180)
			est_jpos[j].append(float(line[jpos_index+indices[j]])*math.pi/180)
		for j in range(0,3):
			est_dpos[j].append(float(line[dpos_index+indices[j]])*math.pi/180)
			est_pos[j].append(float(line[pos_index+indices[j]])*math.pi/180)
	i = i + 1;
csvfile1.close()

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
	for j in range(0,3):
		dmpos[j].append(float(results[j*6]))		
		mpos[j].append(float(results[j*6+1]))
 		mvel[j].append(float(results[j*6+2]))
	for j in range(0,5):
		dac[j].append(float(results[indices[j]*6+3]))
	for j in range(0,7):
		djpos[j].append(float(results[indices[j]*6+4]))
		jpos[j].append(float(results[indices[j]*6+5]))
	for j in range(0,3):
		dpos[j].append(float(results[48+j*2]))
		pos[j].append(float(results[48+j*2+1]))
in_file.close()

f1, axarr1 = plt.subplots(3, 2, sharex=True)
axarr1[0,0].set_title("Motor Positions (Gold Arm)")
axarr1[0,1].set_title("Motor Velocities (Gold Arm)")
for j in range(0,3):
	axarr1[j, 0].plot(dmpos[j], '+g')
	axarr1[j, 0].plot(est_dmpos[j], '+k')
	axarr1[j, 0].plot(mpos[j], 'b')
	axarr1[j, 0].plot(est_mpos[j], 'r')
	axarr1[j, 1].plot(mvel[j], 'b')
	axarr1[j, 1].plot(est_mvel[j], 'r')
	axarr1[j, 0].set_ylabel('Joint '+str(indices[j]))

f2, axarr2 = plt.subplots(3, 1, sharex=True)
axarr2[0].set_title("DAC Values (Gold Arm)")
for j in range(0,3):
	axarr2[j].plot(dac[j], 'b')
	axarr2[j].plot(est_dac[j], 'r')
	axarr2[j].set_ylabel('Joint '+str(indices[j]))

f3, axarr3 = plt.subplots(7, 1, sharex=True)
axarr3[0].set_title("Joint Positions (Gold Arm)")
for j in range(0,7):
	axarr3[j].plot(djpos[j], '+g')
	axarr3[j].plot(est_djpos[j], '+k')
	axarr3[j].plot(jpos[j], 'b')
	axarr3[j].plot(est_jpos[j], 'r')
	axarr3[j].set_ylabel('Joint '+str(indices[j]))

f4, axarr4 = plt.subplots(3, 1, sharex=True)
axarr4[0].set_title("End-Effector Positions (Gold Arm)")
pos_labels = ['X','Y','Z']
for j in range(0,3):
	axarr4[j].plot(dpos[j], '+g')
	axarr4[j].plot(est_dpos[j], '+k')
	axarr4[j].plot(pos[j], 'b')
	axarr4[j].plot(est_pos[j], 'r')
	axarr4[j].set_ylabel(pos_labels[j])
plt.show()
