/* Raven 2 Control - Control software for the Raven II robot
 * Copyright (C) 2005-2012  H. Hawkeye King, Blake Hannaford, and the University of Washington BioRobotics Laboratory
 *
 * This file is part of Raven 2 Control.
 *
 * Raven 2 Control is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * Raven 2 Control is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with Raven 2 Control.  If not, see <http://www.gnu.org/licenses/>.
 */

#include "update_device_state.h"
#include "log.h"

#ifdef save_logs
extern int logging;
int curr_pack_no = 0;
#endif
#ifdef packetgen
extern int program_state;
#endif

extern struct DOF_type DOF_types[];
extern struct traj trajectory[];
extern int NUM_MECH;
extern volatile int isUpdated;
extern unsigned long gTime;

unsigned int newDofTorqueSetting = 0;   // for setting torque from console
unsigned int newDofTorqueMech = 0;      // for setting torque from console
unsigned int newDofTorqueDof = 0;       //
int newDofTorqueTorque = 0;             // float for torque value in mNm
t_controlmode newRobotControlMode = homing_mode;

/**
 * updateDeviceState - Function that update the device state based on parameters passed from
 *       the user interface
 *
 * \param params_current    the current set of parameters
 * \param arams_update      the new set of parameters
 * \param device0           pointer to device informaiton
 *
 */
int updateDeviceState(struct param_pass *currParams, struct param_pass *rcvdParams, struct device *device0)
{
    //log_file("updateDeviceState %d", currParams->runlevel);///Added
    currParams->last_sequence = rcvdParams->last_sequence;
#ifdef packetgen
    program_state = 5;
#endif 
#ifdef save_logs
    if ((currParams->last_sequence == 111) && (curr_pack_no == 0))
    {
        logging = 0;
    }
    else
    {
	if (currParams->last_sequence != curr_pack_no)
	{
		if (curr_pack_no !=0)		 	
		{
			log_file("______________________________________________\n");
		}
		// Dropped
		if (currParams->last_sequence > (curr_pack_no+1))
		{
  		    for (int i=curr_pack_no+1;i<currParams->last_sequence;i++)   
                    {
			log_file("Packet: %d\n", i);
			log_file("Error: Packet Dropped.\n");  
			log_file ("______________________________________________\n");	  
	            }			
		}
		curr_pack_no = currParams->last_sequence;   
		log_file("Packet: %d\n", curr_pack_no);  
	}
    }
#endif
 
    for (int i = 0; i < NUM_MECH; i++)
    {
        currParams->xd[i].x = rcvdParams->xd[i].x;
        currParams->xd[i].y = rcvdParams->xd[i].y;
        currParams->xd[i].z = rcvdParams->xd[i].z;
        currParams->rd[i].yaw   = rcvdParams->rd[i].yaw;
        currParams->rd[i].pitch = rcvdParams->rd[i].pitch * WRIST_SCALE_FACTOR;
        currParams->rd[i].roll  = rcvdParams->rd[i].roll;
        currParams->rd[i].grasp = rcvdParams->rd[i].grasp;
    }

    // set desired mech position in pedal_down runlevel
    if (currParams->runlevel == RL_PEDAL_DN)
    {

#ifdef simulator 
	if (currParams->last_sequence == 1)
	{
	    log_msg("I am updating jpos_d\n");
 	    device0->mech[0].joint[SHOULDER].jpos_d = rcvdParams->jpos_d[0];
     	    device0->mech[0].joint[ELBOW].jpos_d = rcvdParams->jpos_d[1];
	    device0->mech[0].joint[Z_INS].jpos_d = rcvdParams->jpos_d[2];
	    device0->mech[0].joint[TOOL_ROT].jpos_d = rcvdParams->jpos_d[4];
	    device0->mech[0].joint[WRIST].jpos_d = rcvdParams->jpos_d[5];
	    device0->mech[0].joint[GRASP1].jpos_d = rcvdParams->jpos_d[6];
	    device0->mech[0].joint[GRASP2].jpos_d = rcvdParams->jpos_d[7];
	    device0->mech[1].joint[SHOULDER].jpos_d = rcvdParams->jpos_d[8];
     	    device0->mech[1].joint[ELBOW].jpos_d = rcvdParams->jpos_d[9];
	    device0->mech[1].joint[Z_INS].jpos_d = rcvdParams->jpos_d[10];
	    device0->mech[1].joint[TOOL_ROT].jpos_d = rcvdParams->jpos_d[12];
	    device0->mech[1].joint[WRIST].jpos_d = rcvdParams->jpos_d[13];
	    device0->mech[1].joint[GRASP1].jpos_d = rcvdParams->jpos_d[14];
	    device0->mech[1].joint[GRASP2].jpos_d = rcvdParams->jpos_d[15];
	}
	/*if (currParams->last_sequence == 1)	
 	{
	    log_msg("I am using some default jpos_d\n");
 	    device0->mech[0].joint[SHOULDER].jpos_d = 0.521722;
     	    device0->mech[0].joint[ELBOW].jpos_d = 1.585218;
	    device0->mech[0].joint[Z_INS].jpos_d = 0.400515;
	    device0->mech[0].joint[TOOL_ROT].jpos_d = -0.010442;
	    device0->mech[0].joint[WRIST].jpos_d = -0.001124;
	    device0->mech[0].joint[GRASP1].jpos_d = 0.774309;
	    device0->mech[0].joint[GRASP2].jpos_d = 0.841388;
	    device0->mech[1].joint[SHOULDER].jpos_d = 0.521301;
     	    device0->mech[1].joint[ELBOW].jpos_d = 1.584427;
	    device0->mech[1].joint[Z_INS].jpos_d = 0.400447;
	    device0->mech[1].joint[TOOL_ROT].jpos_d = 0.013722;
	    device0->mech[1].joint[WRIST].jpos_d = -0.070899;
	    device0->mech[1].joint[GRASP1].jpos_d = 0.702793;
	    device0->mech[1].joint[GRASP2].jpos_d = 0.729010;
	}*/
           /*for (int j=0;j<8;j++)    
                log_msg("jpos %d = %f\n", j,device0->mech[0].joint[j].jpos_d*180/M_PI);*/
#endif
        for (int i = 0; i < NUM_MECH; i++)
        {
            device0->mech[i].pos_d.x = rcvdParams->xd[i].x;
            device0->mech[i].pos_d.y = rcvdParams->xd[i].y;
            device0->mech[i].pos_d.z = rcvdParams->xd[i].z;
            device0->mech[i].ori_d.grasp  = rcvdParams->rd[i].grasp;

            for (int j=0;j<3;j++)
                for (int k=0;k<3;k++)
	           device0->mech[i].ori_d.R[j][k]  = rcvdParams->rd[i].R[j][k];
        }
    }

    // Switch control modes only in pedal up or init.
    if ( (currParams->runlevel == RL_E_STOP)   &&
         (currParams->robotControlMode != (int)newRobotControlMode) )
    {
        currParams->robotControlMode = (int)newRobotControlMode;
        log_msg("Control mode updated: %d",currParams->robotControlMode);
    }

    // Set new torque command from console user input
    if ( newDofTorqueSetting )
    {
        // reset all other joints to zero
        for (unsigned int idx=0; idx<MAX_MECH_PER_DEV*MAX_DOF_PER_MECH; idx++)
        {
            if ( idx == MAX_DOF_PER_MECH*newDofTorqueMech + newDofTorqueDof )
                currParams->torque_vals[idx] = newDofTorqueTorque;
            else
                currParams->torque_vals[idx] = 0;
        }
        newDofTorqueSetting = 0;
        log_msg("DOF Torque updated\n");
    }

    // Set new surgeon mode
    if ( device0->surgeon_mode != rcvdParams->surgeon_mode)
    {
        device0->surgeon_mode=rcvdParams->surgeon_mode; //store the surgeon_mode to DS0
    }
#ifdef save_logs
    //log_file("Surgoen mode = %d\n",device0->surgeon_mode);
    //log_msg("-----> Runlevel = %d\n",currParams->runlevel);
    //log_file("Current Control Mode: %d\n",currParams->robotControlMode);         
#endif
 
    return 0;
}

/**
*  setRobotControlMode()
*       Change controller mode, i.e. position control, velocity control, visual servoing, etc
*   \param t_controlmode    current control mode.
*/
void setRobotControlMode(t_controlmode in_controlMode){   
    newRobotControlMode = in_controlMode;
    log_msg("New control mode: %d",newRobotControlMode);
    isUpdated = TRUE;
}

/**
*  setDofTorque()
*    Set a torque to output on a joint.
*     Torque input is mNm
*   \param in_mech      Mechinism number of the joint
*   \param in_dof       DOF number
*   \param in_torque    Torque to set the DOF to (in mNm)
*/
void setDofTorque(unsigned int in_mech, unsigned int in_dof, int in_torque){
    if (    ((int)in_mech < NUM_MECH)        &&
            ((int)in_dof  < MAX_DOF_PER_MECH) )
    {
        newDofTorqueMech    = in_mech;
        newDofTorqueDof     = in_dof;
        newDofTorqueTorque  = in_torque;
        newDofTorqueSetting = 1;
    }
    isUpdated = TRUE;
}
