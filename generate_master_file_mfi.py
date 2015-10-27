# Generates bkpt_inject_by_file.txt
# Authors: Homa Alemzadeh and Daniel Chen
# Created: 11/10/2014

master_file = './selected_injection.txt'
pos_range = ['-200','200']
Ri_range = ['0','6.28'] # Yaw Pitch Roll Range
jpos_range = ['-2','2'] # To be used later, now absolute values based on trajectories

# The variable name, the type (i, f, r) and the range of possible values
# i = integer, f = float, r = rotation
# User Input Injections - about 154 injections
input_locations = ['network_layer.cpp://MFI_HOOK']
input_triggers = ['u.sequence > 1000, u.sequence < 1010', 
                  'u.sequence > 1000, u.sequence < 1100',
                  'u.sequence > 1000, u.sequence < 1500']                  
#                  'program_state == 3', 'program_state == 4','program_state == 5',
#                  'program_state == 6', 'program_state == 7','program_state == 8',
#                  'program_state == 9', 'program_state == 10','program_state == 11',
#                  'program_state == 12', 'program_state == 13','program_state == 14',
#                  'program_state == 15']
input_targets= [#('u.sequence','i','-10','1000'),
                ('u.delx[0]','i',pos_range[0],pos_range[1]),
                ('u.dely[0]','i',pos_range[0],pos_range[1]),
                ('u.delz[0]','i',pos_range[0],pos_range[1]),
                ('u.delx[1]','i',pos_range[0],pos_range[1]),
                ('u.dely[1]','i',pos_range[0],pos_range[1]),
                ('u.delz[1]','i',pos_range[0],pos_range[1]),
                ('u.R_l','r',Ri_range[0],Ri_range[1]),
                ('u.R_r','r',Ri_range[0],Ri_range[1]),
                ('u.grasp[0]','i','0','45'),
                ('u.grasp[1]','i','0','45'),
                ('u.surgeon_mode','i','0','1')]

# Control Software Injections - about 456 injections
control_locations = ['update_device_state.cpp:57', 'update_device_state.cpp:134',
                     'update_device_state.cpp:163',
                     'rt_raven.cpp:96', 'rt_raven.cpp:111','rt_raven.cpp:117',
                     'rt_raven.cpp:128','rt_raven.cpp:151','rt_raven.cpp:169',
                     'rt_raven.cpp:253', 'rt_raven.cpp:259','rt_raven.cpp:265']
control_triggers = ['currParams->last_sequence > 1000 , currParams->last_sequence < 1500']
control_targets=[('device0->mech[0].pos.x', 'i',pos_range[0],pos_range[1]),
                ('device0->mech[0].pos.y', 'i',pos_range[0],pos_range[1]),
                ('device0->mech[0].pos.z', 'i',pos_range[0],pos_range[1]),
                ('device0->mech[1].pos.x', 'i',pos_range[0],pos_range[1]),
                ('device0->mech[1].pos.y', 'i',pos_range[0],pos_range[1]),
                ('device0->mech[1].pos.z', 'i',pos_range[0],pos_range[1]),
                ('device0->mech[0].ori.R','f',Ri_range[0],Ri_range[1]),
                ('device0->mech[1].ori.R','f',Ri_range[0],Ri_range[1]),
                ('device0->mech[0].ori.grasp','i','0','45'),
                ('device0->mech[1].ori.grasp','i','0','45'),
                ('device0->surgeon_mode','i','0','1'),
                ('currParams->robotControlMode','i','0','7'),
                ('currParams->runlevel','i','0','3'),
                ('newRobotControlMode','i','0','7'),
                ('device0->mech[0].pos_d.x', 'i',pos_range[0],pos_range[1]),
                ('device0->mech[0].pos_d.y', 'i',pos_range[0],pos_range[1]),
                ('device0->mech[0].pos_d.z', 'i',pos_range[0],pos_range[1]),
                ('device0->mech[1].pos_d.x', 'i',pos_range[0],pos_range[1]),
                ('device0->mech[1].pos_d.y', 'i',pos_range[0],pos_range[1]),
                ('device0->mech[1].pos_d.z', 'i',pos_range[0],pos_range[1]),
                ('device0->mech[0].ori_d.R','f',Ri_range[0],Ri_range[1]),
                ('device0->mech[1].ori_d.R','f',Ri_range[0],Ri_range[1]),
                ('device0->mech[0].ori_d.grasp','i','0','45'),
                ('device0->mech[1].ori_d.grasp','i','0','45'),
                ('device0->mech[0].joint[0].jpos_d','f','0','90'),
                ('device0->mech[0].joint[1].jpos_d','f','25','127'),
                ('device0->mech[0].joint[2].jpos_d','f','15','32'),
                ('device0->mech[0].joint[3].jpos_d','f','-325','260'),
                ('device0->mech[0].joint[4].jpos_d','f','-40','78'),         
                ('device0->mech[0].joint[5].jpos_d','f','-73','125'),
                ('device0->mech[0].joint[6].jpos_d','f','-105','105'),    
                ('device0->mech[1].joint[0].jpos_d','f','0','86'), 
                ('device0->mech[1].joint[1].jpos_d','f','37','126'), 
                ('device0->mech[1].joint[2].jpos_d','f','18','31'),
                ('device0->mech[1].joint[3].jpos_d','f','-300','268'),
                ('device0->mech[1].joint[4].jpos_d','f','-68','123'),
                ('device0->mech[1].joint[5].jpos_d','f','-37','127'),        
                ('device0->mech[1].joint[6].jpos_d','f','-55','160')]

# Feedback Injections - about 126 injections
feedback_locations = ['rt_raven.cpp:96','rt_raven.cpp:111','rt_raven.cpp:117',
                      'rt_raven.cpp:128','rt_raven.cpp:151','rt_raven.cpp:169',
                      'rt_raven.cpp:253', 'rt_raven.cpp:259','rt_raven.cpp:265']
feedback_triggers = ['currParams->last_sequence > 1000 , currParams->last_sequence < 1500']
feedback_targets = [('device0->mech[0].joint[0].jpos_d','f','0','90'),
                ('device0->mech[0].joint[1].jpos','f','25','127'),
                ('device0->mech[0].joint[2].jpos','f','15','32'),
                ('device0->mech[0].joint[3].jpos','f','-325','260'),
                ('device0->mech[0].joint[4].jpos','f','-40','78'),         
                ('device0->mech[0].joint[5].jpos','f','-73','125'),
                ('device0->mech[0].joint[6].jpos','f','-105','105'),    
                ('device0->mech[1].joint[0].jpos','f','0','86'), 
                ('device0->mech[1].joint[1].jpos','f','37','126'), 
                ('device0->mech[1].joint[2].jpos','f','18','31'),
                ('device0->mech[1].joint[3].jpos','f','-300','268'),
                ('device0->mech[1].joint[4].jpos','f','-68','123'),
                ('device0->mech[1].joint[5].jpos','f','-37','127'),        
                ('device0->mech[1].joint[6].jpos','f','-55','160')]

state_locations = ['t_to_DAC_val.cpp:77']
state_triggers = ['device0->runlevel == 1', 'gTime > 2000, gTime < 3000', 
                   'gTime > 20000, gTime < 30000']
state_targets = [('device0->mech[i].joint[j].current_cmd','f','-1','1'),
                  ('device0->mech[i].joint[j].current_cmd','f','2','100')]

USB_locations = [# get
                 ['get_USB_packet.cpp:75'],
                 ['get_USB_packet.cpp:80'],
                 ['get_USB_packet.cpp:92'],
                 ['get_USB_packet.cpp:124'],
                 # put
                 ['put_USB_packet.cpp:43'],
                 ['put_USB_packet.cpp:46'],
                 ['put_USB_packet.cpp:81']]
USB_triggers = ['gTime > 10, gTime < 100', 'gTime > 2000, gTime < 3000', 
                'gTime > 20000, gTime < 30000']
USB_targets = [[('USBBoards.activeAtStart','i','3','100'),
                ('USBBoards.activeAtStart','i','0','0'),
                ('USBBoards.activeAtStart','i','1','1'),
                ('USBBoards.activeAtStart','i','2','2'),
                ('USBBoards.activeAtStart','i','-10','0')],
               [('i','i','2','2')],
               [('ret','i','-19','-19')],
               [('buffer[4]','i','-100','100')],
               [('mech->joint[i].current_cmd', 'i','-20000','20000'), 
                ('mech->outputs', 'i','-20000','20000') ]]


def get_type(key):
    if key == 'i':
        return 'rand_int'
    elif key == 'f':
        return 'rand_float'
    elif key == 'r':
        return 'rand_rotation'
    else:
        print 'Error: undefined type - %s' % key
        return 'Error: undefined type - %s' % key

def generate_master_file_r(in_range, locations, triggers, targets, r_count):
    """ r_count: is the number of random injection to perform for
        each variable.
    """
    global index 
    for location in locations:
        fd.writelines('location, %s\n\n' % location)
        for trigger in triggers:
            fd.writelines('trigger, %s\n\n' % trigger)
            for target in targets:
                # if injection of random number inside the range 
                if (in_range == 1):             
                    target_line = 'target_r, %s %s %s %s' %  \
                                  (target[0], get_type(target[1]), target[2], target[3])
                    fd.writelines('injection, %d\n' % index)
                    fd.writelines('%s\n' % target_line)
                    fd.writelines('injection, %d, %d\n\n' % (index, r_count))
                    index = index + 1
                # if injection of random number outside the range  
                else:
                    target_line = 'target_r, %s %s %s %s' %  \
                                  (target[0], get_type(target[1]), '-200000', target[2])
                    fd.writelines('injection, %d\n' % index)
                    fd.writelines('%s\n' % target_line) 
                    fd.writelines('injection, %d, %d\n\n' % (index, r_count))
                    index = index + 1

                    target_line = 'target_r, %s %s %s %s' %  \
                                  (target[0], get_type(target[1]), target[3], '200000')
                    fd.writelines('injection, %d\n' % index)
                    fd.writelines('%s\n' % target_line)
                    fd.writelines('injection, %d, %d\n\n' % (index, r_count))
                    index = index + 1
                                
# Main code starts
index = 1
fd = open(master_file,'w')

# Random Injections to input within range
generate_master_file_r(1, input_locations, input_triggers,input_targets, 10)
# Outside range
generate_master_file_r(0, input_locations, input_triggers, 
        input_targets, 10)

# Random Injections to device feedback within range
#generate_master_file_r(1, feedback_locations, feedback_triggers, feedback_targets, 1)
# Outside range
generate_master_file_r(0, feedback_locations, feedback_triggers,feedback_targets, 1)
for i in range(0,4):
    generate_master_file_r(1, USB_locations[i], USB_triggers, USB_targets[i], 1)

# Random Injections to device commands 
generate_master_file_r(1, USB_locations[4], USB_triggers, USB_targets[0], 1)
generate_master_file_r(1, USB_locations[5], USB_triggers, USB_targets[1], 1)
generate_master_file_r(1, USB_locations[6], USB_triggers, USB_targets[4], 1)

# Random Injections to control within range
#generate_master_file_r(1, control_locations, control_triggers, control_targets, 1)
# Outside range
#generate_master_file_r(0, control_locations, control_triggers, control_targets, 1)
generate_master_file_r(1, state_locations, state_triggers, state_targets, 1)

fd.close()

