import socket
import struct
import csv
import time
from collections import namedtuple
import threading
import sys
import signal
import time

UDP_IP = "127.0.0.1"
UDP_PORT1 = 32001
UDP_PORT2 = 34001
format_ = "<IIIiiiiiiddddddddddddddddddiiiiii"

u_struct = namedtuple("u_struct", "sequence pactyp version delx0 delx1 dely0 dely1 delz0 delz1 R_l00 R_l01 R_l02 R_l10 R_l11 R_l12 R_l20 R_l21 R_l22 R_r00 R_r01 R_r02 R_r10 R_r11 R_r12 R_r20 R_r21 R_r22 buttonstate0 buttonstate1 grasp0 grasp1 surgeon_mode checksum");

# Not_Ready: state = 0, Operating: state = 1, Stopped: state = 2  
PLC_state = 0;

sock1 = socket.socket(socket.AF_INET, # Internet
                      socket.SOCK_DGRAM) # UDP
sock1.bind((UDP_IP,UDP_PORT1))
sock2 = socket.socket(socket.AF_INET, # Internet
                      socket.SOCK_DGRAM) # UDP
def readSignals():
    global robot_state
    while(line_no < MAX_LINES):
        data = sock1.recvfrom(100)       
        if (robot_state == 0):
            if (data[0].find('Ready') > -1):
                robot_state = 1;
            else:
                robot_state = 0;

        elif (robot_state == 1):
            print "\rRaven is ready...",
            if (data[0].find('Stopped') > -1):
                robot_state = 2;
            else:
                robot_state = 1;

        elif (robot_state == 2): 
            print "\rRaven is stopped...", 
            if (data[0].find('Ready') > -1):
                robot_state = 1;
            else:
                robot_state = 2;    

def sendPackets():
    seq = 0;
    line = [];
    csvfile1 = open('/home/alemzad1/homa_wksp/teleop_data/data1.csv'); 
    reader = csv.reader(csvfile1)
    
    # Skip the first packets
    for i in range(0,200):
       line = reader.next()
    
    global robot_state

    print ("here")
    while (robot_state == 0):
        print "\rWaiting for Raven...",  
  
    # Send trajectory packets until the operation is done (e.g. 300 steps) 
    # Skip every 10 packets in the trajectory  
    while (line_no < MAX_LINES):    
        # If robot is ready, update the packet to be sent
        if (robot_state == 1):
            for i in range(0,1):
                line = reader.next();
                line_no = line_no + 1;           
            print "Sending New Packet" 
            seq = seq + 1;
            # Construct the packet to send
            # Later should look at the runlevel and sublevel to set the surgeon_mode
            tuple_to_send = u_struct(sequence = seq, 
                    pactyp = 0, 
                    version = 0, 
                    delx0 = int(float(line[9])),
                    delx1 = int(float(line[12])),
                    dely0 = int(float(line[10])),
                    dely1 = int(float(line[13])),
                    delz0 = int(float(line[11])),
                    delz1 = int(float(line[14])),
                    R_l00 = float(line[15]),
                    R_l01 = float(line[16]),
                    R_l02 = float(line[17]),
                    R_l10 = float(line[18]),
                    R_l11 = float(line[19]), 
                    R_l12 = float(line[20]),
                    R_l20 = float(line[21]),
                    R_l21 = float(line[22]),
                    R_l22 = float(line[23]),
                    R_r00 = float(line[24]),
                    R_r01 = float(line[25]), 
                    R_r02 = float(line[26]),
                    R_r10 = float(line[27]),
                    R_r11 = float(line[28]), 
                    R_r12 = float(line[29]),
                    R_r20 = float(line[30]),
                    R_r21 = float(line[31]),
                    R_r22 = float(line[32]),
                    buttonstate0 = 0,
                    buttonstate1 = 0, 
                    grasp0 = float((float(line[112])-float(line[113]))/2),
                    grasp1 = float((float(line[120])-float(line[121]))/2), 
                    surgeon_mode = 1, 
                    checksum=0);
            MESSAGE = struct.pack(format_,*tuple_to_send._asdict().values());
            if (robot_state == 1):
                print struct.unpack(format_,MESSAGE);
                print "\n"
            # Send the command to the robot
            sock2.sendto(MESSAGE, (UDP_IP, UDP_PORT2))
            time.sleep(FREQ)
        # If in robot_s stay with the same packet but with new seq number
        elif (robot_state == 2):
            print "\rWaiting for the robot to be restarted",
            sys.stdout.flush();
   
def signal_handler(signal, frame):
    sock1.close()
    sock2.close()
    sys.exit()

signal.signal(signal.SIGINT, signal_handler)

t1 = threading.Thread(target=readSignals);
t2 = threading.Thread(target=sendPackets);
t1.daemon = True;
t2.daemon = True;
t1.start();
t2.start();

while(line_no < MAX_LINES):
   time.sleep(1)

t1.exit()
t2.exit()
sock1.close()
sock2.close()
sys.exit()




 



