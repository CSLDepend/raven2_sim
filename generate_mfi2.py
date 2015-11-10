from pprint import pprint
import sys
import os
from math import pi
from rotation_math import tsp_to_r
from franges import frange
from random import randint

def _generate_all_r():
    """ Generate all combinations of rotation matrix. """
    inc = 0.1 # Can change the increment
    result = []
    for t in frange(-pi/2, pi/2+inc, inc):
        for s in frange(-pi, pi+inc, inc):
            for p in frange(-pi, pi+inc, inc):
                r = tsp_to_r((t,s,p))
                result.append(r)
    return result

def _generate_all_delta():
    """ Generate all combinations of delta. """
    inc = 5 # Can change the increment
    delta_min = -100
    delta_max = 100

    result = []
    for x in range(delta_min, delta_max+inc, inc):
        for y in range(delta_min, delta_max+inc, inc):
            for z in range(delta_min, delta_max+inc, inc):
                result.append((x,y,z))
    return result
    

def _generate_ow_code(pre_trig, trigger, t1, t2, variable, stuck_value):
    """ Example 
		pre_trig = 'device0.runlevel == 0 &&'
        trigger = 'u.sequence'
        t1 = '1000'
        t2 = '1100'
        variable = ['u.delay[0]', 'u.delay[1]']
        stuck_value = ['100','110']

        if(device0.runlevel == 3 && u.sequence > 1000 && u.sequqnce < 1100) {
            u.delay[0] = 100;
            u.delay[1] = 110;
        }
    """
    assert(len(variable) == len(stuck_value))
    #code = 'if(device0.runlevel == 3 && %s>%s && %s<%s) {' % \
    code = 'if(%s %s>=%s && %s<%s) {' % \
            (pre_trig, trigger, t1, trigger, t2)
    for v, s in zip(variable, stuck_value):
        l = '%s=%s;' % (v,s)
        code = code + l
    code = code + '}'
    return code

def _generate_add_code(trigger, t1, t2, variable, stuck_value):
    """ Example 
        trigger = 'u.sequence'
        t1 = '1000'
        t2 = '1100'
        variable = ['u.delay[0]', 'u.delay[1]']
        stuck_value = ['100','110']

        if(device0.runlevel == 3 && u.sequence >= 1000 && u.sequqnce < 1100) {
            u.delay[0] += 100;
            u.delay[1] += 110;
        }
    """
    assert(len(variable) == len(stuck_value))
    code = 'if(device0.runlevel == 3 && %s>=%s && %s<%s) {' % \
            (trigger, t1, trigger, t2)
    for v, s in zip(variable, stuck_value):
        l = '%s+=%s;' % (v,s)
        code = code + l
    code = code + '}'
    return code

def _generate_delay_code(trigger, t1, t2, usec):
    """ Example: assumes the source code includes unistd.h
        trigger = 'u.sequence'
        t1 = '1000'
        t2 = '1100'
        length = '100' in usec

        if(device0.runlevel == 3 && u.sequence >= 1000 && u.sequqnce < 1100) {
            usleep(100)
        }
    """
    code = 'if(device0.runlevel == 3 && %s>=%s && %s<%s) {usleep(%s);}' % \
            (trigger, t1, trigger, t2, usec)
    return code

def generate_stuck_fault_list():
    pre_trig = 'device0.runlevel == 3 &&'
    trigger = 'u.sequence'
    t_range = ['10', '110']
    code = []
    variable = [ \
            ['u.delay[0]', 'u.delay[1]'], \
            ['u.grasp[0]','u.grasp[1]'] \
            ]
    stuck_val = [ \
            ['100','110'], \
            ['20','30']
            ]
    for v, s in zip(variable, stuck_val):
        code.append(_generate_ow_code(pre_trig, trigger, \
                t_range[0], t_range[1], v, s))
    return code

def generate_u_delta_faults():
    trigger = 'u.sequence'
    t_range = ['10', '110']
    code = []
    variable = ['u.delx[0]', 'u.dely[0]','u.delz[0]']
    val = _generate_all_delta()
    for v in val:
        code.append(_generate_ow_code(trigger, \
                t_range[0], t_range[1], variable, v))
    #pprint(code)
    with open('mfi2_u_delta_faults.txt', 'w') as outfile:
        for line in code:
            outfile.write(line + '\n')
    return code


def generate_u_R_l_faults():
    trigger = 'u.sequence'
    t_range = ['10', '110']
    code = []
    variable = ['u.R_l[0][0]', \
            'u.R_l[0][1]', \
            'u.R_l[0][2]', \
            'u.R_l[1][0]', \
            'u.R_l[1][1]', \
            'u.R_l[1][2]', \
            'u.R_l[2][0]', \
            'u.R_l[2][1]', \
            'u.R_l[2][2]']
    val = _generate_all_r()
    for v in val:
        code.append(_generate_ow_code(trigger, \
                t_range[0], t_range[1], variable, v))
    #pprint(code)
    with open('mfi2_u_R_l_faults.txt', 'w') as outfile:
        for line in code:
            outfile.write(line + '\n')
    return code

def generate_network_layer_skip():
    """ Generate code to skip packet for various number of packets.
        This is done by changing the packet to reflective packet.
    """
    trigger = 'u.sequence'
    variable = ['u.sequence']
    stuck_value = ['0']
    t1 = '1000' # Modify to change the start packet
    t2 = 100    # Modify to change the range
    code = []
    for t in range(1, t2): # Modify to change the end packet
        code.append(_generate_ow_code(trigger, t1, str(int(t1)+t2), \
                variable, stuck_value))

    # Write code to file
    with open('mfi2_network_skip.txt', 'w') as outfile:
        outfile.writelines('location:network_layer.cpp://MFI_HOOK\n')
        for i, line in enumerate(code):
            outfile.writelines('injection %d:%s\n' % (i,line))

def generate_network_layer_delay():
    # Generate code
    trigger = 'u.sequence'
    t_range = ['1000', '1100'] #free to modify
    usec = range(1, 1000) #free to modify
    code = []
    for u in usec:
        code.append(_generate_delay_code(trigger, t_range[0], t_range[1], u))
    # Write code to file
    with open('mfi2_network_delay.txt', 'w') as outfile:
        outfile.writelines('location:network_layer.cpp://MFI_HOOK\n')
        for i, line in enumerate(code):
            outfile.writelines('injection %d:%s\n' % (i,line))

def write_to_file(code, out_file, target_file_and_hook):
    with open(out_file, 'w') as outfile:
        outfile.write('location:' + target_file_and_hook + '\n')
        for i, line in enumerate(code):
            outfile.write('injection ' + str(i) + ':' + line + '\n')
    return code

# Generate rt_process.cpp faults
def generate_rt_process_faults():
    pre_trig = ''
    code = []
    trigger = 'packet_num'

    variable = [['device0.mech[i].joint[SHOULDER].current_cmd'],
            ['device0.mech[i].joint[ELBOW].current_cmd'],
            ['device0.mech[i].joint[Z_INS].current_cmd']
            ]

    for var in variable:
        for i in range(0, 10):
            t1 = randint(10, 15000)
            t2 = t1 + randint(1, 50)
            val = [randint(-15000, 15000)]
            code.append(_generate_ow_code(pre_trig, trigger, 
                    t1, t2, var, val))
    pprint(code)
    write_to_file(code, 'mfi2_rt_process_faults.txt', 'rt_process_preempt.cpp://HOOK')



#generate_network_layer_skip()
#generate_network_layer_delay()
#generate_u_delta_faults()
#generate_u_R_l_faults()
generate_rt_process_faults()
