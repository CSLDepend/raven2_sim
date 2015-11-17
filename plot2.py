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

print "\nPlotting the results.."
# Get raven_home directory
env = os.environ.copy()
splits = env['ROS_PACKAGE_PATH'].split(':')
raven_home = splits[0]

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

plot_mpos(gold_mpos, orig_mpos, mpos, gold_mvel, orig_mvel, mvel, gold_t, orig_t, t).savefig(raven_home+'/mpos.png')
plot_dacs(gold_dac, orig_dac, dac, gold_t, orig_t, t)
plot_jpos(gold_jpos, orig_jpos, jpos, gold_t, orig_t, t)
plot_pos(gold_pos, orig_pos, pos, gold_t, orig_t, t)
 

# Close files
csvfile1.close()
csvfile2.close()
csvfile3.close()
