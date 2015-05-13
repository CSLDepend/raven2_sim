#!/bin/sh

# Write target PID and FD to a file
#pidof r2_control > target

pid=`pidof r2_control`
fd=`ls -l /proc/$pid/fd | awk '{if ($11 == "/home/homa/.ros/err_network.log") print $9;}'`

echo $pid $fd > /tmp/target
