import csv
import os
import sys
import matplotlib.pyplot as plt
import matplotlib as mpl
from franges import frange

def plot_hist(all_data):
    """Plot the histogram of each data."""
    skip = ['Injection_Info', 'Errors']
    bins = list(frange(-4, 4, 0.01))
    for key in all_data:
        if key not in skip:
            data = map(lambda t:float(t), all_data[key])
            fig = plt.figure()
            ax = fig.add_subplot(111, title=key)
            n, bins, patches = ax.hist(data, bins, normed=1, histtype='bar', rwidth=1)
            print(n)
            print(bins)
            print(patches)
            plt.show()

def parse_error_log():
    """ Analyze the xyz positions from the CSV files"""

    log_file = 'error_log.csv'
    header = []
    all_data = {}
    with open(log_file, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        for i, line in enumerate(reader):
            if i == 0:
                header = line
                all_data = {k: [] for k in header}
            else:
                for h, v in zip(header, line):
                    all_data[h].append(v)
    plot_hist(all_data)

# Main Code Starts Here
if __name__ == '__main__':
    usage = sys.argv[0]
    parse_error_log()
