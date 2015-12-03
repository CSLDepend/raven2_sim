from pprint import pprint
import sys
import os
from math import pi, sqrt
from rotation_math import tsp_to_r, r_to_tsp
from franges import frange
from random import randint
import csv

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

def _generate_add_code(pre_trig, trigger, t1, t2, variable, stuck_value):
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
    code = 'if(%s %s>=%s && %s<%s) {' % \
            (pre_trig, trigger, t1, trigger, t2)
    for v, s in zip(variable, stuck_value):
        l = '%s+=%s;' % (v,s)
        code = code + l
    code = code + '}'
    return code

def _generate_add_once_code(pre_trig, trigger, t1, t2, vtype, variable, stuck_value):
    """ Example 
        trigger = 'u.sequence'
        t1 = '1000'
        t2 = '1100'
        type = ['int', 'int']
        variable = ['u.delay[0]', 'u.delay[1]']
        stuck_value = ['100','110']

        if(device0.runlevel == 3 && u.sequence >= 1000 && u.sequqnce < 1100) {
            int my_int1;
            int my_int2;
            if (trigger == t1) { 
                my_int1 = variable[1] + stuck_value[1]}
                my_int2 = variable[2] + stuck_value[2]}
            }
            variable[1] = my_int1;
            variable[2] = my_int2;
        }
    """
    assert(len(vtype) == len(variable) == len(stuck_value))
    code = 'if(%s %s>=%s && %s<%s) {' % \
            (pre_trig, trigger, t1, trigger, t2)
    for i, t in enumerate(vtype):
        # e.g.: int _v0;float _v1;
        l = '%s _v%d;' % (t, i)
        code = code + l

    l = 'if(%s==%s) {' % (trigger, t1)
    code = code + l

    for i, (v, s) in enumerate(zip(variable, stuck_value)):
        # e.g.: _v0 = v0 + s0
        l = '_v%i=%s+(%s);' % (i, v,s)
        code = code + l
    code = code + '}'

    for i, v in enumerate(variable):
        l = '%s=_v%d;' % (v, i)
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

def _write_to_file(code, param, exp_name, target_file_and_hook):
    out_file = 'mfi2.txt'
    param_file = 'mfi2_params.csv'

    with open(out_file, 'w') as outfile:
        outfile.write('title:' + exp_name + '\n')
        outfile.write('location:' + target_file_and_hook + '\n')
        for i, line in enumerate(code):
            outfile.write('injection ' + str(i) + ':' + line + '\n')

    with open(param_file, 'w') as outfile:
        for i, line in enumerate(param):
            outfile.write(str(i) + ',' + line + '\n')

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


# network_layer.cpp faults
def generate_xyz_dist_faults():
    pre_trig = ''
    trigger = 'u.sequence'
    dist = ('250', '500', '1000', '2000', '4000','8000')
    code = []
    param = []
    variable = ['u.delx[0]', 'u.dely[0]','u.delz[0]']
    for d in dist:
        for t1 in range(1000,3000,1000):#(10,3000,1000):
            for dt in range(1,50,1):#(1,15):
                t2 = t1 + dt
                delta = str(float(d)/sqrt(3))
                code.append(_generate_add_code(pre_trig, trigger,
                        t1, t2, variable, [delta, delta, delta]))
                param.append(','.join(['distance',str(t1),str(dt),str(delta)]))
    pprint(code)
    print(len(code))
    _write_to_file(code, param, 'mfi2_xyz_dist_faults', 
            'network_layer.cpp://MFI_HOOK')

def generate_toggle_surgeon_mode():
    code = []
    param = []
    pre_trig = ''
    trigger = 'u.sequence'
    t1 = '10'
    t2 = '110'
    variable = ['u.surgeon_mode']
    value = ['u.sequence % 2 ? 0:1']
    code.append(_generate_ow_code(pre_trig, trigger,
                t1, t2, variable, value))
    param.append(','.join([variable,t1,t2,value]))
    pprint(code)
    _write_to_file(code, 'mfi2_toggle_surgeon_mode.txt', 
            'network_layer.cpp://MFI_HOOK')

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
                t_range[0], t_range[1], variable, str(v)))
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

# Generate rt_process.cpp faults
def generate_rt_process_faults():
    pre_trig = ''
    code = []
    param = []
    trigger = 'packet_num'

    variable = [['device0.mech[i].joint[SHOULDER].current_cmd'],
            ['device0.mech[i].joint[ELBOW].current_cmd'],
            ['device0.mech[i].joint[Z_INS].current_cmd']
            ]

    '''for var in variable:
        for i in range(0, 500):
            t1 = randint(10, 14000)
            t2 = t1 + randint(1, 50)
            val = [randint(-15000, 15000)]
            code.append(_generate_ow_code(pre_trig, trigger, 
                    t1, t2, var, val))'''
    # Injection parameters
    for var in [['device0.mech[i].joint[SHOULDER].current_cmd']]:
        for t1 in range(10,5000,500):
            for dt in range(1,20):
                for val in range(-15000, 15000, 500):
                    t2 = t1 + dt
                    code.append(_generate_ow_code(pre_trig, trigger,t1, t2, var, [val]))
                    param.append(','.join([str(var),str(t1),str(dt),str(val)]))
                            
                     
    pprint(code)
    _write_to_file(code, param, 'mfi2_rt_process_faults', 
            'rt_process_preempt.cpp://HOOK')

def generate_rt_process_once_faults():
    pre_trig = ''
    code = []
    param = []
    trigger = 'packet_num'
    vtype = ['int']
    variable = [['device0.mech[i].joint[SHOULDER].current_cmd']]
            #,['device0.mech[i].joint[ELBOW].current_cmd'],
            #['device0.mech[i].joint[Z_INS].current_cmd']
            #]

    '''for var in variable:
        for i in range(0, 500):
            t1 = randint(10, 14000)
            t2 = t1 + randint(1, 50)
            val = [randint(-15000, 15000)]
            code.append(_generate_ow_code(pre_trig, trigger, 
                    t1, t2, var, val))'''
    # Injection parameters
    for var in variable:
        for t1 in range(1000,3000,1000):
            for dt in range(1,20):
                for val in [100, 1000, 2000, 3000, 5000, 10000, 100000, 200000, 400000,800000]:#range(-12000, 15000, 1000):
                    t2 = t1 + dt
                    code.append(_generate_add_once_code(pre_trig, trigger,t1, t2, vtype, var, [val]))
                    param.append(','.join([str(var),str(t1),str(dt),str(val)]))
                            
    pprint(code)
    _write_to_file(code, param, 'mfi2_rt_process_once_faults', 
            'rt_process_preempt.cpp://HOOK')
def generate_empty_test():
    code = [';']*20
    param = [','.join(['none','0','0','0'])]*20
    _write_to_file(code, param, 'mfi2_empty_test', 
            'rt_process_preempt.cpp://HOOK')

def _compute_euclidean_distance(tsp):
    x = map(lambda t:t[0], tsp)
    y = map(lambda t:t[1], tsp)
    z = map(lambda t:t[2], tsp)
    
    d = []
    for x1, x2, y1, y2, z1, z2 in zip(x[:-1], x[1:], y[:-1], y[1:], z[:-1], z[1:]):
        d.append(sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2))
    return d

def _generate_tsp_delta(distance):
    """ Return the tsp delta to be added to the original tsp.

    t range [-pi/2, pi/2]
    s range [-2pi, 2pi]
    p range [-2pi, 2pi]
    So we divide the distance to 9 parts
    """
    unit = distance/sqrt(3)/9
    return (unit, unit*4, unit*4)

def generate_r_faults():
    r = []
    tsp = []
    new_tsp = []
    new_r = []
    sender = 'teleop_data/new_test_3.csv'
    with open(sender, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for i, line in enumerate(reader):
            if i == 0:
                if line[15] != 'field.ori0':
                    print("Error: Incorrect CSV format")
                    break
            else:
                r.append(tuple(map(lambda t:float(t), line[15:24])))
                tsp.append(r_to_tsp(','.join(line[15:24])))

    #for distance = range(0, 14):
    tsp_delta = _generate_tsp_delta(6.25)
    for item in tsp:
        new_tsp.append((item[0]+tsp_delta[0],
            item[1]+tsp_delta[1],
            item[2]+tsp_delta[2]))
    new_r = map(tsp_to_r, new_tsp)
    print tsp[0]
    print tsp_delta
    print new_tsp[0]
    print r[0]
    print new_r[0]

def generate_test():
    # Generate code
    pre_trig = ''
    trigger = 'u.sequence'
    t1 = 100
    t2 = 200
    vtype = ['int', 'float']
    variable = ['u.delx', 'u.dely']
    value = ['100', '200']
    code = _generate_add_once_code(pre_trig, trigger, t1, t2, vtype, variable, value)
    print code

#generate_network_layer_skip()
#generate_network_layer_delay()
#generate_xyz_dist_faults()
#generate_u_R_l_faults()
#generate_rt_process_faults()
generate_rt_process_once_faults()
#generate_toggle_surgeon_mode()
#generate_empty_test()
#generate_r_faults()
#generate_test()
