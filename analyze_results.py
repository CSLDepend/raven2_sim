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
import pandas as pd


results_file = './error_log.csv'

df = pd.read_csv()
print df.head()
Start_1000 = df.ix[df['Start']==1000]
print Start_1000
# Read the rows
csvfile = open(results_file,'r')
reader = csv.reader(csvfile,delimiter=',') 
headers = reader.next()
print headers
#fields = [InjNum, Variable, Start, Duration, Value, Num_Packets, Errors, T1(mvel), T2(mpos), T3(jpos), T4(pos), T5(SW-Detect), T6(E-STOP), L1(mvel), L2(mpos), L3(jpos), L4(pos), L5(SW-Detect),L6(E-STOP), F1(mvel), F2(mpos), F3(jpos)]
variable_index = headers.index('Variable')
start_index = headers.index('Start')
duration_index = headers.index('Duration')
value_index = headers.index('Value')
num_packets_index = headers.index('Num_Packets')
T_index = headers.index('T1(mvel)')
L_index = headers.index('L1(mvel)')

Variables = [] 
Starts = []
Durations = []
Values = []
Time = [[],[],[],[],[],[]]
Latency = [[],[],[],[],[],[]]

experiment_hash = []
fig1 = plt.figure()
ax = fig1.add_subplot(111)
for line in reader:
	data_vec = []
	exp_str  = str(','.join(line[0:5]))
	print exp_str
		
	Durations.append(int(line[duration_index]))
	Values.append(int(line[value_index]))
	for i in range(0,6):	
		if line[T_index+i]:
			print line[T_index + i]			
			Time[i].append(int(line[T_index+i]))	
			Latency[i].append(int(line[L_index+i]))

		else:
			Time[i].append(None)	
			Latency[i].append(None)	
			data_vec.append(None)
	val_vec = [Values[-1]]*6
	print data_vec
	ax.plot(Durations, data_vec)
	'''cmap = plt.get_cmap('gnuplot')
	colors = [cmap(i) for i in np.linspace(0,1,7)]
	for i in range(0,6):		
		ax.plot(Values, Latency[i],label = str(headers[L_index+i]),color = colors[i])'''
	
fig1.savefig('./results.png')
csvfile.close()
