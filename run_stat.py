# run_stat.py

#Usage: run_stat.py <data>

from sys import argv
import numpy as np
import matplotlib.pyplot as plt





def print_min_max_mean(all_names, all_data):
    for name,data in zip(all_names,all_data):
        print("%s" % name)
        print("max = %f" % max(data))
        print("min = %f" % min(data))
        print("mean = %f" % np.mean(data))
        print("std = %f" % np.std(data, ddof=1))
        print "\n"

def plot_hist(all_names, all_data):
    fig = plt.figure()
    bins = list(range(0,30))

    for i,(name,data) in enumerate(zip(all_names, all_data),1):
        subplot = fig.add_subplot(len(all_names), 1, i, title=name)
        n, bins, patches = subplot.hist(data, bins, normed=1, histtype='bar', rwidth=1)
        subplot.set_xlim(0,30)
        text=("Min = %.2f\nMax = %.2f\nAvg = %.2f" % (min(data), max(data), np.mean(data)))
        subplot.text(25,0,text)
        print(name)
        print(n)
        print(sum(n[11:]))
    plt.show()

# Main code starts here

file_names_l=[]
file_data_l=[]

for arg in argv[1:]:
    with open(arg, 'rb') as f:
        line = f.readlines()
        file_data_l.append([float(i) for i in line if float(i) >= 0])
        file_names_l.append(arg)

print_min_max_mean(file_names_l, file_data_l)
plot_hist(file_names_l, file_data_l)
