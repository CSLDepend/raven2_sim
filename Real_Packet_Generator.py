import socket
import struct
import csv
import time
from collections import namedtuple

UDP_IP = "127.0.0.1"
UDP_PORT1 = 32000
UDP_PORT2 = 36001
format_ = "<IIIiiiiiiddddddddddddddddddiiiiii"

print "UDP target IP:", UDP_IP
print "UDP target port1:", UDP_PORT1
print "UDP target port2:", UDP_PORT2

u_struct = namedtuple("u_struct", "sequence pactyp version delx0 delx1 dely0 dely1 delz0 delz1 R_l00 R_l01 R_l02 R_l10 R_l11 R_l12 R_l20 R_l21 R_l22 R_r00 R_r01 R_r02 R_r10 R_r11 R_r12 R_r20 R_r21 R_r22 buttonstate0 buttonstate1 grasp0 grasp1 surgeon_mode checksum");

csvfile1 = open('/home/junjie/homa_wksp/teleop_data/data1.csv'); 
reader = csv.reader(csvfile1)
seq = 0;

sock = socket.socket(socket.AF_INET, # Internet
                      socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP,UDP_PORT1))
#Wait for a response from the robot
data = ''
while not data:
    print("Waiting for Raven to become ready...")
    data = sock.recvfrom(100)
    if data[0].find('Ready') < 0:
        data = ''
    else:
        print("Raven is ready...")   

line_no = 0
# Skip the first packets
for i in range(0,200):
   reader.next()
while (seq < 300): 
    line = reader.next();
    if ((line_no % 10) == 0):
        seq = seq + 1;   
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

        print "Packet No. ", seq
        print struct.unpack(format_,MESSAGE);
        print "\n"

        # Send the command to the robot
        sock.sendto(MESSAGE, (UDP_IP, UDP_PORT2))
        time.sleep(0.1)
        
    line_no = line_no + 1;


