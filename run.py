'''/* Runs Raven 2 simulator by calling packet generator, Raven control software, and visualization code
 * Copyright (C) 2015 University of Illinois Board of Trustees, DEPEND Research Group, Creators: Homa Alemzadeh and Daniel Chen
 *
 * This file is part of Raven 2 Surgical Simulator.
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

import os
import subprocess
import random
import sys
from math import cos, sin, sqrt, acos, asin, pow as pow_f
import socket
import sys
import numpy as np
import struct
import time
import signal
from sys import argv
import mfi

def rsp_func():
	rsp = str(raw_input("Is the Raven Home found correctly (Yes/No)? "))
	if rsp.lower() == 'yes' or rsp.lower() == 'y':
		print 'Found Raven Home Directory.. Starting..\n'
	elif rsp.lower() == 'no' or rsp.lower() == 'n':
		print 'Please change the ROS_PACKAGE_PATH environment variable.\n'
		sys.exit(2)
	else:
		rsp_func()
class Raven():
    def __init__(self, raven_home, mode, packet_gen, injection):
        self.mode = mode
        self.packet_gen = packet_gen
        self.raven_home = raven_home
        self.surgeon_simulator = 1
        self.defines_changed = 0
        self.mfi_changed = 0
        self.defines_src_file = raven_home + "/include/raven/defines.h"
        self.defines_bkup_file = raven_home + "/include/raven/defines_back.h"
        self.defines_chk_file = raven_home + "/include/raven/defines_last_run"
        self.master_file = './selected_injection.txt'
        inj = injection.split(':')
        self.injection = inj[0]
        if len(inj) > 1:
            self.starting_inj_num = int(inj[1])
        else:
            self.starting_inj_num = 0

    def __change_defines_h(self):
        # Change define macros
        cmd = 'cp ' + self.defines_src_file + ' ' + self.defines_bkup_file
        os.system(cmd)
        #open files
        src_fp = open(self.defines_src_file,'w')
        bkup_fp = open(self.defines_bkup_file,'r')

        for line in bkup_fp:
            if line.startswith('//#define simulator'):
                if self.mode == 'sim':
                    line = line.lstrip('//')
            elif line.startswith('//#define dyn_simulator'):
                if self.mode == 'dyn_sim':
                    line = line.lstrip('//')
            elif line.startswith('//#define packetgen'):
                if self.packet_gen == '1':
                    line = line.lstrip('//')
            elif line.startswith('//#define mfi'):
                if self.injection == 'mfi':
                    line = line.lstrip('//')
            src_fp.write(line)
        src_fp.close()
        bkup_fp.close()
        #save a check file
        cmd = 'cp ' + self.defines_src_file + ' ' + self.defines_chk_file
        os.system(cmd)
        self.defines_changed = 1

    def __restore_defines_h(self):
        #restore file
        cmd = 'chmod 777 ' + self.defines_bkup_file;
        os.system(cmd);
        cmd = 'cp ' + self.defines_bkup_file + ' ' + self.defines_src_file
        # delete backup
        if (os.system(cmd) == 0): 
            cmd = 'rm ' + self.defines_bkup_file;
            os.system(cmd);   
        self.defines_changed = 0

    def __mfi_insert_code(self, file_name, line_num, trigger, target):
        """
        Example: if (x > 3 && x < 5) {x = 40}
        """
        # Compute all the variable
        self.mfi_src_file = self.raven_home + "/src/raven/" + file_name
        self.mfi_bkup_file = self.raven_home + "/src/raven/" + file_name + '.bkup'
        self.mfi_chk_file = self.raven_home + "/src/raven/" + file_name + '.chk'
        trigger_line = ' && '.join(trigger)
        # target[0] variable name, target[1] value

        # For R matrices injected values are based on absolute values of yaw, roll, pitch
        if ((target[0] == 'u.R_l') or (target[0] == 'u.R_r')):
            code = 'if (' + trigger_line + ') { '; 
            elems = target[1].split(';');
            for i in range(0,3):
                for j in range(0,3):
                    code =code+target[0]+'['+str(i)+']['+str(j)+']='+ elems[i*3+j]+'; '; 
            code = code + '}\n';  
            print code
        # For thetas and USBs the injected value is absolute 
        elif (target[0].find('jpos') > -1) or (file_name.find('USB') > -1):
            code = 'if (' + trigger_line + ') { ' + target[0] + ' = ' + target[1] + ';}\n'
        # For position the injected value is incremental
        else:
            code = 'if (' + trigger_line + ') { ' + target[0] + '+= ' + target[1] + ';}\n'
        print file_name + ':' + line_num + '\n' + code

        #save a backup file
        cmd = 'cp ' + self.mfi_src_file + ' ' + self.mfi_bkup_file
        os.system(cmd)
        self.mfi_changed = 1

        #open files
        src_fp = open(self.mfi_src_file, 'w')
        bkup_fp = open(self.mfi_bkup_file, 'r')
        
        for i, line in enumerate(bkup_fp):
            if i == int(line_num)-1:
                src_fp.write(code)
            src_fp.write(line)
        src_fp.close()
        bkup_fp.close()

        #save a check file
        cmd = 'cp ' + self.mfi_src_file + ' ' + self.mfi_chk_file
        os.system(cmd)

    def __restore_mfi(self):
        #restore file
        cmd = 'chmod 777 '+self.mfi_bkup_file;
        os.system(cmd);
        cmd = 'cp ' + self.mfi_bkup_file + ' ' + self.mfi_src_file

        # delete backup
        if (os.system(cmd) == 0): 
            cmd = 'rm ' + self.mfi_bkup_file;
            os.system(cmd);   
        self.mfi_changed = 0

    def __quit(self): 
        try:
            r2_control_pid = subprocess.check_output("pgrep r2_control", 
                    shell=True)
            os.killpg(int(r2_control_pid), signal.SIGINT)
            time.sleep(1)
        except:
            pass
        try:
            roslaunch_pid = subprocess.check_output("pgrep roslaunch", 
                    shell=True)
            os.killpg(int(roslaunch_pid), signal.SIGINT)
            time.sleep(1)
        except:
            pass
        try:
            os.killpg(self.raven_proc.pid, signal.SIGINT)
            time.sleep(1)
        except:
            pass
        try:
            os.killpg(self.packet_proc.pid, signal.SIGINT)
            time.sleep(1)
        except:
            pass
        try:
            os.killpg(self.rostopic_proc.pid, signal.SIGINT)
            time.sleep(1)
        except:
            pass
        try:
            os.killpg(self.dynSim_proc.pid, signal.SIGINT)
            time.sleep(1)
        except:
            pass
        os.system("rm /tmp/dac_fifo")
        os.system("rm /tmp/mpos_vel_fifo")
        os.system("killall roslaunch")
        os.system("killall rostopic")    
        os.system("killall r2_control")
        os.system("killall rviz")
        os.system("killall xterm")
        os.system("killall two_arm_dyn")
        #os.system("killall python") # Don't work with run_mfi_experiment()

    def _compile_raven(self):

        self.__change_defines_h()

        # Make the file
        cmd = 'cd ' + self.raven_home + ';make -j > compile.output'
        make_ret = os.system(cmd)

        if self.defines_changed:
            self.__restore_defines_h()
        if self.mfi_changed:
            self.__restore_mfi()

        if (make_ret != 0):
           print "Make Error: Compilation Failed..\n"
           self.__quit()
           sys.exit(0)

    def _run_experiment(self):
        # Open Sockets
        UDP_IP = "127.0.0.1"
        UDP_PORT = 34000
        os.system("killall xterm")
        sock = socket.socket(socket.AF_INET, # Internet
                              socket.SOCK_DGRAM) # UDP
        sock.bind((UDP_IP,UDP_PORT))

        # Setup Variables
        goldenRavenTask= 'xterm -e roslaunch raven_2 raven_2.launch'
        ravenTask = 'xterm -hold -e roslaunch raven_2 raven_2.launch'
        visTask = 'xterm -hold -e roslaunch raven_visualization raven_visualization.launch'
        dynSimTask = 'xterm -hold -e "cd ../Li_DYN && make && ./two_arm_dyn"'
        rostopicTask = 'rostopic echo -p ravenstate >'+self.raven_home+'/latest_run.csv'
        if (self.surgeon_simulator == 1):
            packetTask = 'xterm -hold -e python '+self.raven_home+'/Real_Packet_Generator_Surgeon.py '+ self.mode
            #print(packetTask)
        else:
            packetTask = 'xterm -e python '+self.raven_home+'/Packet_Generator.py'

        # Call visualization, packet generator, and Raven II software
        vis_proc = subprocess.Popen(visTask, env=env, shell=True, preexec_fn=os.setsid)
        time.sleep(4)  
        if self.packet_gen == "1":
                self.packet_proc = subprocess.Popen(packetTask, shell=True, preexec_fn=os.setsid)
                print "Using the packet generator.."
        elif self.packet_gen == "0":
                print "Waiting for the GUI packets.."
        else:
            print usage
            sys.exit(2)
        self.raven_proc = subprocess.Popen(ravenTask, env=env, shell=True, preexec_fn=os.setsid)
        self.rostopic_proc = subprocess.Popen(rostopicTask, env=env, shell=True, preexec_fn=os.setsid)
        time.sleep(0.5);


        # Call Dynamic Simulator
        if self.mode == "dyn_sim":
                #self.dynSim_proc = subprocess.Popen(dynSimTask, env=env, shell=True, preexec_fn=os.setsid)
                #os.system("cd ../Li_DYN && ./two_arm_dyn")
                print "Started the dynamic simulator.."

        print("Press Ctrl+C to exit.")

        #Wait for a response from the robot
        data = ''
        while not data:
            print("Waiting for Raven to be done...")
            data = sock.recvfrom(100)
            if data[0].find('Done!') > -1:
                print("Raven is done, shutdown everything...")  
            elif data[0].find('Stopped') > -1:
                print("Raven is stopped, shutdown everything...")  
            else:
                data = ''
        self.__quit()
    
    def _run_mfi_experiment(self):
        cur_inj = -1
        saved_param = []

        with open(self.master_file) as fp:
            target_file = ''
            line_num = 0
            trigger = []
            target = []

            for line in fp:
                # Strip '\n' from each line then split by ','
                line = line.strip('\n')
                param = line.split(',')

                # Skip lines begin with # or empty line
                if param[0] == '' or param[0] == '#':
                    continue
               
                # Read location info
                elif param[0] == 'location':
                    location_info = param[1].split(':')
                    target_file = location_info[0].lstrip()
                    line_num = location_info[1]

                # Read trigger info
                elif param[0] == 'trigger':
                    param.pop(0)
                    trigger = [item.strip() for item in param]

                elif param[0] == 'target_r':
                    param.pop(0)
                    saved_param = param
                    target = (mfi.generate_target_r(saved_param)).split(' ')

                elif param[0] == 'injection':
                    if cur_inj != int(param[1]):
                        cur_inj = int(param[1])
                        print("setup param for %d" % cur_inj)
                    else:
                        # Injection starts at argv[1]
                        # Example starting_inj_num is 3.2
                        if int(param[1]) >= self.starting_inj_num:
                            # If param == 3, indicate do random injection param[2] times.
                            if len(param) == 3:
                                for x in xrange(int(param[2])):
                                    #target = (mfi.generate_target_r(saved_param)).split(' ')
                                    target = (mfi.generate_target_r_stratified(saved_param, int(param[2]), x)).split(' ')
                                    self.__mfi_insert_code(target_file, line_num, trigger, target)
                                    self._compile_raven()
                                    print("injecting to %d.%d" % (cur_inj, x))
                                    self._run_experiment()
                            else:
                                print("injecting to %d" % (cur_inj))
                                self.__mfi_insert_code(target_file, line, trigger, target)
                                self._compile_raven()
                                self._run_experiment()
                print line

   
    def signal_handler(self, signal, frame):
        print "Ctrl+C Pressed!"
        self.__quit()
        sys.exit(0)

    def run(self):
        if self.injection == 'mfi':
            self._run_mfi_experiment()
        else:
            self._compile_raven()
            self._run_experiment()


# Main code starts here

# Get raven_home directory
env = os.environ.copy()
splits = env['ROS_PACKAGE_PATH'].split(':')
raven_home = splits[0]
print '\nRaven Home Found to be: '+ raven_home
rsp_func()
usage = "Usage: python run.py <sim|dyn_sim|rob> <1:packet_gen|0:gui> <none|mfi:start#>"
# Parse the arguments
try:
    script, mode, packet_gen, injection = argv
except:
    print "Error: missing parameters"
    print usage
    sys.exit(2)

if mode == "sim":
    print "Run the Simulation"
elif mode == "dyn_sim":
    print "Run the Dynamic Simulation"
elif mode == "rob": 
    print "Run the Real Robot"
else:
    print usage
    sys.exit(2)

# Init Raven
raven = Raven(raven_home, mode, packet_gen, injection)
signal.signal(signal.SIGINT, raven.signal_handler)

# Run Raven
raven.run()

