Link to Wiki of Raven:
http://brl.ee.washington.edu/ravenIIwiki/index.php/Raven_II_systems
Username: UIUC
Pass: RavenUIUC

Link to Doxgyn documentation:
http://brl.ee.washington.edu/raven2docs/

_________________________________________________
Command to run the code:
export ROS_PACKAGE_PATH=$ROS_PACKAGE_PATH:/home/homa/Documents/raven_2
cd raven_2
roslaunch raven_2 raven_2.launch


Prefix for GDB: should be added in ./launch/raven_2.launch
launch-prefix="xterm -e gdb --args"
___________________________________________________

- Pedal status variables:
This variable 
runlevel: Takes the following values:In rt_process_preempt.cpp it is currParams.runlevel = RL_PEDAL_DN;

This variable comes from user:
surgeon_mode: 0 = Pedal up, 1 = Pedal down
surgoen_mode is manually set to 1 in the "local_io.cpp"
It can be also changed from the network process inside the network_layer.cpp by changing the surgeon_mode in us_t data structure.. 

-data1 is the local data structure  between netwrok and control processes

-device is the data structure holding the current and desired positions, which
are either read by the encoders (pos) or are going to be written to motors (pos_d)
__________________________________________________________________________________
Code:

Main file that initiates the threads: 
\raven2-indigo\src\raven\rt_process_preempt.cpp

Three main processes:
1. Network process
\raven2-indigo\src\raven\network_layer.cpp

2. RT_Process calls ControlRaven (Controls and starts the actuall kinematics)
* Runs all raven control functions.
* This a thread run in parallel with rt_process_preempt in order to provide more flexibility.
\raven2-indigo\src\raven\rt_raven.cpp

3. Console Process:
* Lets the user to set different control modes and outputs data to the console periodically.
* User can toggle to either specify joint torque, set control mode, or toggle console messages.
\raven2-indigo\src\raven\console_process.cpp

