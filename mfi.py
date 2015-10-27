"""
File: mfi.py
Authors: Daniel Chen and Homa Alemzadeh
Created: 2015/2/3

Overall Idea
1. copy entire folder from backup to origion
2. Read the target file and determine what to insert
3. Insert to the source code file
4. Compile the source code file

Modified: 2015/2/5
1. Now checks if make was successful, if not restores and quits
2. Added a quit function to be called on Ctrl+C and compilation errors
3. Fixed the R matrix value assignment
4. Added different assignment scenarios for position, rotation, and joint variables
"""

import random
from math import cos, sin, sqrt, acos, asin, pow as pow_f


def str_to_nums(out_str):
    out_num = [];
    param = out_str.split(',')
    for p in param:
        out_num.append(int_or_float(p))
    return out_num

# Convert rotation matrix to yaw (rz), pitch (ry), roll (rx) 
def to_ypr(R_str):
    param = R_str.split(',')
    R00 = float(param[0]);
    R02 = float(param[2]);
    R22 = float(param[8]);

    ry = asin(min(1,max(R02,-1)));
    rx = acos(min(1,max(R22/cos(ry),-1)));
    rz = acos(min(1,max(R00/cos(ry),-1)));

    ypr_str = str(rz)+', '+str(ry)+', '+str(rx);

    return ypr_str

# Convert yaw (rz), pitch (ry), roll (rx) to rotation matrix
def generate_rotation(a, b):
    rx = random.uniform(a, b)
    ry = random.uniform(a, b)
    rz = random.uniform(a, b)

    R00 = cos(ry)*cos(rz)
    R01 = -cos(ry)*sin(rz)
    R02 = sin(ry)

    R10 = cos(rx)*sin(rz)+cos(rz)*sin(rx)*sin(ry)
    R11 = cos(rx)*cos(rz)-sin(rx)*sin(ry)*sin(rz)
    R12 = -cos(ry)*sin(rx)

    R20 = sin(rx)*sin(rz)-cos(rx)*cos(rz)*sin(ry)
    R21 = cos(rz)*sin(rx)+cos(rx)*sin(ry)*sin(rz)
    R22 = cos(rx)*cos(ry)
    R = '%5f;%5f;%5f;%5f;%5f;%5f;%5f;%5f;%5f' % \
            (R00, R01, R02, R10, R11, R12, R20, R21, R22)

    return R

def int_or_float(s):
    try:
        return int(s, 0)
    except ValueError:
        return float(s)

# generate_target_r(param)
# Format of param:
#   <type> <min> <max>

def generate_target_r(param):
    for item in param:
        p = item.lstrip()
        param2 = p.split(' ')
        newline = ''
        if param2[1] == 'rand_float':
            new_val = random.uniform(int_or_float(param2[2]), int_or_float(param2[3]))
            newline = "%s %5f" % (param2[0], new_val)
        elif param2[1] == 'rand_int':
            new_val = random.randint(int(param2[2]), int(param2[3]))
            newline = "%s %d" % (param2[0], new_val)
        elif param2[1] == 'rand_rotation':
            new_val = generate_rotation(int_or_float(param2[2]), int_or_float(param2[3]))
            newline = "%s %s" % (param2[0], new_val)
        else:
            newline = item
    return newline;

# generate_target_r(param)
# Format of param:
#   <type> <min> <max>
# Example: generate_target_r_stratified(['sequence rand_float 0.1 10.5'], 10, 9)

def generate_target_r_stratified(param, num_of_bin, current_bin):
    for item in param:
        p = item.lstrip()
        param2 = p.split(' ')
        print param2[0]
        print param2[1]
        print param2[2]
        print param2[3]
        newline = ''
        if param2[1] == 'rand_float':
            min_val = int_or_float(param2[2])
            max_val = int_or_float(param2[3])
            total_range = max_val - min_val
            increment = total_range / num_of_bin
            lower_bound = min_val + current_bin * increment
            upper_bound = min_val + (current_bin+1) * increment
            if upper_bound > max_val:
                upper_bound = max_val
            new_val = random.uniform(lower_bound, upper_bound)
            newline = "%s %5f" % (param2[0], new_val)
        elif param2[1] == 'rand_int':
            min_val = int(param2[2])
            max_val = int(param2[3])
            total_range = max_val - min_val
            increment = total_range / num_of_bin
            lower_bound = min_val + current_bin * increment
            upper_bound = min_val + (current_bin+1) * increment
            if upper_bound > max_val:
                upper_bound = max_val
            new_val = random.randint(lower_bound, upper_bound)
            newline = "%s %d" % (param2[0], new_val)
        elif param2[1] == 'rand_rotation':
            new_val = generate_rotation(int_or_float(param2[2]), int_or_float(param2[3]))
            newline = "%s %s" % (param2[0], new_val)
        else:
            newline = item
        print "debug: " + newline
    return newline;

