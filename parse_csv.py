# parse_csv.py
# Find the Min and Max of tsp for all Rotation CSV file in current directory
# Created on 11/3/2015
# Author: Daniel Chen (dchen8@illinois.edu)

import csv
import sys
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os
from rotation_math import r_to_tsp

def diff_ort(orig, new):
    for o, n in zip(orig.split(','), new.split(';')):
        print float(n)-float(o)


def int_or_float(s):
    try:
        return int(s, 0)
    except ValueError:
        return float(s)

def find_min_max(data):
    x = map(lambda item:item[0], data)
    y = map(lambda item:item[1], data)
    z = map(lambda item:item[2], data)
    print("t[%f:%f], s[%f:%f], p[%f:%f]") % (max(x), min(x), max(y), min(y), max(z), min(z))
    return (max(x), min(x), max(y), min(y), max(z), min(z))

def plot_3D(data):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    x = map(lambda item:item[0], data)
    y = map(lambda item:item[1], data)
    z = map(lambda item:item[2], data)
    ax.scatter(x, y, z, c='r', marker='*')
    plt.show()

def result_min_max(data):
    x_max = max(map(lambda item:item[0], data))
    x_min = min(map(lambda item:item[1], data))
    y_max = max(map(lambda item:item[2], data))
    y_min = min(map(lambda item:item[3], data))
    z_max = max(map(lambda item:item[4], data))
    z_min = min(map(lambda item:item[5], data))
    print("All Result: t[%f:%f], s[%f:%f], p[%f:%f]") % (x_max, x_min, y_max, y_min, z_max, z_min)
    return (x_max, x_min, y_max, y_min, z_max, z_min)

# Main Code Starts Here
if __name__ == '__main__':

    outfile = open('result', 'w')

    # Get all files in current directory
    allfiles = os.listdir(os.getcwd())

    all_result = []
    for f in allfiles:
        if f.endswith('.csv') and os.stat(f).st_size > 0:
            print "Parsing File: %s" % f
            tsp = []
            with open(f, 'rb') as csvfile:
                reader = csv.reader(csvfile, delimiter=',')
                for i, line in enumerate(reader):
                    if i == 0:
                        if line[15] != 'field.ori0':
                            print "Error: Incorrect CSV format"
                            break
                    else:
                        orig = ','.join(line[15:24])
                        result = r_to_tsp(','.join(line[15:24]))
                        tsp.append(result)
                        #outfile.write(result + '\n')
            all_result.append(find_min_max(tsp))
            #plot_3D(tsp)
    result_min_max(all_result)
    outfile.close()
