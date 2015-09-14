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

/**\file r2_kinematics.cpp
 * \brief kinematic calculation of robot
 *
 * 	  Degenerate cases in inverse kinematics:
 *    1. All rotational joints have problems around +/-180.  (Unhandled exception)
 *    2. As tool tip approaches RCM, IK fails.  This case returns -2.
 *
 * \author Hawkeye King
 * \date Jun 18, 2012
 * \ingroup Kinematics
 */

#include <iostream>
#include <math.h>
#include <ros/ros.h>

#include "r2_kinematics.h"
#include "log.h"
#include "tool.h"
#include "local_io.h"
#include "defines.h"

extern int NUM_MECH;
extern struct DOF_type DOF_types[];

const static double d2r = M_PI/180;
const static double r2d = 180/M_PI;
const static double eps = 1.0e-5;

using namespace std;

extern unsigned long int gTime;

// Pointers are set to DH table for left or right arm
double const* dh_alpha;
double const* dh_a;
double *dh_theta;
double *dh_d;

// DH Parameters.
// Variable entries are marked "V" for clarity.
// Entered in table form, so alphas[0][0] is alpha_0 and thetas[0][0] is theta_1.
const double alphas[2][6] = {{0,    La12, M_PI- La23, 0,   M_PI/2, M_PI/2},
                             {M_PI, La12, La23,       0,   M_PI/2, M_PI/2}};  // Left / Right
const double aas[2][6]    = {{0,    0,    0,          La3, 0,      Lw},
                             {0,    0,    0,          La3, 0,      Lw}};
double ds[2][6]           = {{0,    0,    V,          d4,  0,      0},
                             {0,    0,    V,          d4,  0,      0}};
double robot_thetas[2][6] = {{V,    V,    M_PI/2,     V,   V,      V},
                             {V,    V,    -M_PI/2,    V,   V,      V}};

#ifdef simulator
int check_collision(ik_solution * iksols, double * gangels);
/// Parameters to check for fwd_kin
//int a_fwd = 0;
//int b_fwd = 6;
/// theta1, theta2, d3, theta4, theta5, theta6 (ignore theta4 for now)
///double thetas_fwd[6] = {35*d2r, 50*d2r, 323*0.001, 0*d2r,80*d2r, 20*d2r};
//double rthetas_fwd[6] = {30*d2r, 90*d2r, 435*0.001, 50*d2r,-80*d2r, 30*d2r};
//double lthetas_fwd[6] = {-150*d2r,-90*d2r, 430*0.001, 0*d2r,-90*d2r,-30*d2r};
# endif

int printIK = 0;
void print_btVector(tf::Vector3 vv);
int check_solutions(double *in_thetas, ik_solution * iksol, int &out_idx, double &out_err);
int apply_joint_limits(double *Js, double *Js_sat);

//--------------------------------------------------------------------------------
//  Calculate a transform between two links
//--------------------------------------------------------------------------------

/**\fn tf::Transform getFKTransform (int a, int b)
 * \brief Retrieve the forward kinematics transform from a to b, i.e., ^a_bT
 * \param a - an integer value, starting link frame id
 * \param b - an integer value, ending link frame id
 * \return a tf::Transform object transforms link a to link b
 *  \ingroup Kinematics
 */
tf::Transform getFKTransform(int a, int b)
{
	tf::Transform xf;
	if ( (b <= a) || b==0 )
	{
		ROS_ERROR("Invalid start/end indices.");
	}

	double xx = cos(dh_theta[a]),                  xy = -sin(dh_theta[a]),                   xz =  0;
	double yx = sin(dh_theta[a])*cos(dh_alpha[a]), yy =  cos(dh_theta[a])*cos(dh_alpha[a]),  yz = -sin(dh_alpha[a]);
	double zx = sin(dh_theta[a])*sin(dh_alpha[a]), zy =  cos(dh_theta[a])*sin(dh_alpha[a]),  zz =  cos(dh_alpha[a]);

	double px =  dh_a[a];
	double py = -sin(dh_alpha[a])*dh_d[a];
	double pz =  cos(dh_alpha[a])*dh_d[a];

        ///cout << "Step" << a << " : x, y, z:" << px << "," << py << "," << pz<<endl;
	
        xf.setBasis(tf::Matrix3x3(xx, xy, xz, yx, yy, yz, zx, zy, zz ));
	xf.setOrigin(tf::Vector3(px, py, pz));

	// recursively find transforms for following links
	if (b > a+1)
		xf *= getFKTransform(a+1, b);

	return xf;
}

int check_collision(ik_solution *iksols, double *gangels)
{
  
    //gangels[0] = 30*d2r;
    //gangels[1] = 30*d2r;
    //l_r arm;

    tf::Transform xf;
    tf::Matrix3x3 R_T0; 
    tf::Matrix3x3 L_T0; 
    tf::Matrix3x3 T6_b; 
    tf::Matrix3x3 T6;   
    tf::Matrix3x3 env_r; 

    // Constant Matrices for Transformation to Base Frame
    R_T0.setValue(0, 0, -1, 0, 1, 0, 1, 0, 0);
    L_T0.setValue(0, 0, 1, 0, -1, 0, 1, 0, 0);
    // Needs to be tuned to be more accurate
    tf::Vector3 R_disp(-250710,61000,-6000);
    tf::Vector3 L_disp(-379290,61000,-6000); 

    double R[3][3];
    double posx, posy, posz;
	double radius[2];
    double cen[2][3];

    for (int m = 0; m < NUM_MECH; m++)
	{    
		double iksol_thetas[6]= {iksols[m].th1, iksols[m].th2, iksols[m].d3, iksols[m].th4, iksols[m].th5, iksols[m].th6};

       /*if (m == 0) 
	   {
		   arm = dh_left;
	       iksol_thetas[0] = lthetas_fwd[0];
	       iksol_thetas[1] = lthetas_fwd[1];
	       iksol_thetas[2] = lthetas_fwd[2];
	       iksol_thetas[3] = lthetas_fwd[3];
	       iksol_thetas[4] = lthetas_fwd[4];
	       iksol_thetas[5] = lthetas_fwd[5];
       }
       else
	   {
           arm = dh_right;
     	   iksol_thetas[0] = rthetas_fwd[0];
	       iksol_thetas[1] = rthetas_fwd[1];
	       iksol_thetas[2] = rthetas_fwd[2];
	       iksol_thetas[3] = rthetas_fwd[3];
	       iksol_thetas[4] = rthetas_fwd[4];
	       iksol_thetas[5] = rthetas_fwd[5];
		}  
        iksols[m].arm = arm;*/

		fwd_kin(iksol_thetas, iksols[m].arm, xf); 
		posx = xf.getOrigin()[0] * (1000.0*1000.0);
		posy = xf.getOrigin()[1] * (1000.0*1000.0);
		posz = xf.getOrigin()[2] * (1000.0*1000.0);
                //cout << "Arm " << m << ":\n";
		//cout << "Position = ("<< posx << "," << posy << ","<< posz << ")\n";
		
        for (int i=0;i<3;i++)
		{
			for (int j=0; j<3; j++)
			{		
				R[i][j] = (xf.getBasis())[i][j];  
                //cout << R[i][j] << ",";
			}
			//cout << "\n";
		}
		T6_b.setValue(R[0][0], R[0][1], R[0][2], R[1][0], R[1][1], R[1][2], R[2][0], R[2][1], R[2][2]);

		radius[m] = 10.5/cos(gangels[m])*1000; 
	    //cout << "Radius = " << radius[m] << "\n";

		tf::Vector3 tmp;		
		if (iksols[m].arm == dh_left)
		{
			T6 = L_T0 * T6_b;
            tmp = L_T0*tf::Vector3(posx,posy,posz)+L_disp;  
		}		
		else
		{		
			T6 = R_T0 * T6_b;	
            tmp = R_T0*tf::Vector3(posx,posy,posz)+R_disp;  
		}
		posx = tmp[0];
		posy = tmp[1];
		posz = tmp[2]; 	

		//cout << "TPosition = ("<< posx << "," << posy << ","<< posz << ")\n";
		for (int i=0;i<3;i++)
		{
			for (int j=0; j<3; j++)
			{		
                //cout << T6[i][j] << ",";
			}
			//cout << "\n";
		}


	    tf::Vector3 env = T6.getColumn(0) * radius[m];
		cen[m][0] = posx+env[0];
        cen[m][1] = posy+env[1];
        cen[m][2] = posz+env[2];
        //cout << "env: "<< env[0] << "," << env[1] << "," << env[2]<<"\n";
        //cout << "center: "<< cen[m][0] << "," << cen[m][1] << "," <<cen[m][2]<<"\n";
	}
   
	double dis1 = radius[0]+radius[1];
    double sum_dev = pow((cen[0][0]-cen[1][0]),2)+pow((cen[0][1]-cen[1][1]),2)+pow((cen[0][2]-cen[1][2]),2);
    double dis2 = sqrt(sum_dev);

    //cout << dis2 << "---" << dis1 << "\n";
    if (dis2 < dis1)
		return -1;
	else 
		return 0;
}

//--------------------------------------------------------------------------------
//  Forward kinematics
//--------------------------------------------------------------------------------

/**\fn int r2_fwd_kin(struct device *d0, int runlevel)
 * \brief ravenII forward kinematics
 * \param d0 - a pointer points to the device struct, equivalent as robot_device struct, see define.h
 * \param runlevel - an integer value of the current runlevel
 * \return 0 on success -1 on failure
 *  \ingroup Kinematics
 */
int r2_fwd_kin(struct device *d0, int runlevel)
{
	l_r arm;
	tf::Transform xf;

	/// Do FK for each mechanism
	for (int m=0; m<NUM_MECH; m++)
	{
		/// get arm type and wrist actuation angle
		if (d0->mech[m].type == GOLD_ARM_SERIAL)
			arm = dh_left;
		else
			arm = dh_right;

		double wrist2          = (d0->mech[m].joint[GRASP2].jpos - d0->mech[m].joint[GRASP1].jpos) / 2.0;
		d0->mech[m].ori.grasp  = (d0->mech[m].joint[GRASP2].jpos + d0->mech[m].joint[GRASP1].jpos) * 1000;

		double joints[6] = {
				d0->mech[m].joint[SHOULDER].jpos,
				d0->mech[m].joint[ELBOW].jpos,
				d0->mech[m].joint[Z_INS].jpos,
				d0->mech[m].joint[TOOL_ROT].jpos,
				d0->mech[m].joint[WRIST].jpos,
				wrist2
		};

		// convert from joint angle representation to DH theta convention
		double lo_thetas[6];
//cout<<joints[0]*r2d<<endl;
		joint2theta(lo_thetas, joints, arm);

#ifdef simulator 
// These values should match what is sent by the packet generator
//log_file("Arm %d - Current JPos = %f, %f, %f, %f, %f, %f, %f\n", m, d0->mech[m].joint[SHOULDER].jpos*r2d, d0->mech[m].joint[ELBOW].jpos*r2d, d0->mech[m].joint[Z_INS].jpos*r2d, d0->mech[m].joint[TOOL_ROT].jpos*r2d, d0->mech[m].joint[WRIST].jpos*r2d, d0->mech[m].joint[GRASP1].jpos*r2d, d0->mech[m].joint[GRASP2].jpos*r2d); 	

//log_file("Arm %d - Current Thetas = %f, %f, %f, %f, %f, %f\n", m, lo_thetas[0] * r2d, lo_thetas[1] * r2d, lo_thetas[2], lo_thetas[3] * r2d, lo_thetas[4] * r2d,lo_thetas[5] * r2d);
#endif
		/// execute FK
//cout<<lo_thetas[0]*r2d<<endl;
		fwd_kin(lo_thetas, arm, xf);

		d0->mech[m].pos.x = xf.getOrigin()[0] * (1000.0*1000.0);
		d0->mech[m].pos.y = xf.getOrigin()[1] * (1000.0*1000.0);
		d0->mech[m].pos.z = xf.getOrigin()[2] * (1000.0*1000.0);
		
		for (int i=0;i<3;i++)
			for (int j=0; j<3; j++)
				d0->mech[m].ori.R[i][j] = (xf.getBasis())[i][j];  

#ifdef save_logs
        log_file("FK_Pos_Arm%d: %d, %d, %d", m, d0->mech[m].pos.x, d0->mech[m].pos.y, d0->mech[m].pos.z); 
        log_file("FK_Ori_Arm%d: %f, %f, %f, %f, %f, %f, %f, %f, %f\n", m, d0->mech[m].ori.R[0][0], d0->mech[m].ori.R[0][1], d0->mech[m].ori.R[0][2], d0->mech[m].ori.R[1][0], d0->mech[m].ori.R[1][1], d0->mech[m].ori.R[1][2], d0->mech[m].ori.R[2][0], d0->mech[m].ori.R[2][1], d0->mech[m].ori.R[2][2]);  

#endif            
                
 
	}

#ifdef simulator
        //log_file("RT_PROCESS) FWD Kinematics Done.\n");      
#endif
    if ((runlevel != RL_PEDAL_DN) && (runlevel != RL_INIT)) {
        // set cartesian pos_d = pos.
        // That way, if anything wonky happens during state transitions
        // there won't be any discontinuities.
        // Note: in init, this is done in setStartXYZ
        for (int m = 0; m < NUM_MECH; m++) {
          d0->mech[m].pos_d.x     = d0->mech[m].pos.x;
          d0->mech[m].pos_d.y     = d0->mech[m].pos.y;
          d0->mech[m].pos_d.z     = d0->mech[m].pos.z;
          d0->mech[m].ori_d.yaw   = d0->mech[m].ori.yaw;
          d0->mech[m].ori_d.pitch = d0->mech[m].ori.pitch;
          d0->mech[m].ori_d.roll  = d0->mech[m].ori.roll;
          d0->mech[m].ori_d.grasp = d0->mech[m].ori.grasp;

          for (int k = 0; k < 3; k++)
              for (int j = 0; j < 3; j++)
            	  d0->mech[m].ori_d.R[k][j] = d0->mech[m].ori.R[k][j];
        }
        updateMasterRelativeOrigin( d0 );   // Update the origin, to which master-side deltas are added.
    }
	return 0;
}

/**\fn int fwd_kin (double in_j[6], l_r in_arm, tf::Transform &out_xform )
 * \brief Runs the Raven II forward kinematics to determine end effector position of one arm
 * \param in_j[6] - 6 element array of joint angles ( float j[] = {shoulder, elbow, ins, roll, wrist, grasp} )
 * \param in_arm - Arm type, left / right ( kin.armtype arm = left/right)
 * \param out_xform - a reference of tf::Transform object represents the forward kinematic transfrom from zero frame to endeffector frame of one arm
 * \return: 0 on success, -1 on failure
 *  \ingroup Kinematics
 */
int fwd_kin (double in_j[6], l_r in_arm, tf::Transform &out_xform)
{
	dh_alpha = alphas[in_arm];
	dh_theta = robot_thetas[in_arm];
	dh_a     = aas[in_arm];
	dh_d     = ds[in_arm];

	for (int i=0;i<6;i++)
	{
		if (i==2)
			dh_d[i] = in_j[i];
		else
			dh_theta[i] = in_j[i];// *M_PI/180;
	}

	out_xform = getFKTransform(0,6);



	// rotate to match "tilted" base
/*
	const static tf::Transform zrot_l( tf::Matrix3x3 (cos(25*d2r),-sin(25*d2r),0,  sin(25*d2r),cos(25*d2r),0,  0,0,1), tf::Vector3 (0,0,0) );
	const static tf::Transform zrot_r( tf::Matrix3x3 (cos(-25*d2r),-sin(-25*d2r),0,  sin(-25*d2r),cos(-25*d2r),0,  0,0,1), tf::Vector3 (0,0,0) );


	if (in_arm == dh_left)
	{
		out_xform = zrot_l * out_xform;
	}
	else
	{
		out_xform = zrot_r * out_xform;
	}
*/
	return 0;
}



/**\fn int getATransform (struct mechanism &in_mch, tf::Transform &out_xform, int frameA, int frameB)
 * \brief Runs the Raven II forward kinematics to determine the desired transform from frame A to frame B
 * \param in_mch - a reference of one arm
 * \param out_xform - a reference of a tf::Transform obejct represents the output transfrom
 * \param frameA - an integer value, starting frame id
 * \param frameB - an integer value, ending frame id
 * \return 0 on success, -1 on failure
 *  \ingroup Kinematics
 */
int getATransform (struct mechanism &in_mch, tf::Transform &out_xform, int frameA, int frameB)
{
	l_r arm;

	/// get arm type and wrist actuation angle
	if (in_mch.type == GOLD_ARM_SERIAL)
			arm = dh_left;
		else
			arm = dh_right;

	double wrist2 = (in_mch.joint[GRASP2].jpos - in_mch.joint[GRASP1].jpos) / 2.0;

	double joints[6] = {
		in_mch.joint[SHOULDER].jpos,
		in_mch.joint[ELBOW].jpos,
		in_mch.joint[Z_INS].jpos,
		in_mch.joint[TOOL_ROT].jpos,
		in_mch.joint[WRIST].jpos,
		wrist2
	};

	// convert from joint angle representation to DH theta convention
	double lo_thetas[6];
	joint2theta(lo_thetas, joints, arm);

	dh_alpha = alphas[arm];
	dh_theta = robot_thetas[arm];
	dh_a     = aas[arm];
	dh_d     = ds[arm];

	for (int i=0;i<6;i++)
	{
		if (i==2)
			dh_d[i] = lo_thetas[i];
		else
			dh_theta[i] = lo_thetas[i];// *M_PI/180;
	}

	out_xform = getFKTransform(frameA, frameB);

	// rotate to match "tilted" base
	// Needed?  Yes, for transform ^0_xT to get a frame aligned with base (instead of rotated 25 degrees to zero angle of shoulder joint)
/*
	if (frameA == 0)
	{
		const static tf::Transform zrot_l( tf::Matrix3x3 (cos(25*d2r), -sin(25*d2r), 0,  sin(25*d2r), cos(25*d2r), 0,  0,0,1), tf::Vector3 (0,0,0) );
		const static tf::Transform zrot_r( tf::Matrix3x3 (cos(-25*d2r),-sin(-25*d2r),0,  sin(-25*d2r),cos(-25*d2r),0,  0,0,1), tf::Vector3 (0,0,0) );

		if (arm == dh_left)
		{
			out_xform = zrot_l * out_xform;
		}
		else
		{
			out_xform = zrot_r * out_xform;
		}
	}
*/
	return 0;

}



//-------------------------------------------------------------------------------
//  Inverse kinematics
//-------------------------------------------------------------------------------

/**\fn int r2_inv_kin(struct device *d0, int runlevel)
 * \brief run the ravenII inverse kinematics from device struct
 * \param d0  - a pointer points to robot_device struct
 * \param runlevel - an integer value represents the runlevel
 * \return 0 on success -1 on failure
 *  \ingroup Kinematics
 */
int r2_inv_kin(struct device *d0, int runlevel)
{
	l_r arm;
	tf::Transform xf;
	struct orientation * ori_d;
	struct position    * pos_d;
    ik_solution iksols[2] = {{},{}}; 
	double gangles[2]={0,0};
#ifdef save_logs
	for (int m=0; m<NUM_MECH; m++)
	{
     	//log_msg("Arm %d - Current Thetas = %f, %f, %f, %f, %f, %f\n", m, lo_thetas[0]*r2d, lo_thetas[1]*r2d, lo_thetas[2], lo_thetas[3]*r2d, lo_thetas[4]*r2d,lo_thetas[5]*r2d);
	log_file("Input to IK: JPos - Arm %d = %f, %f, %f, %f, %f, %f, %f, %f\n", m, 
               d0->mech[m].joint[0].jpos*r2d, 
               d0->mech[m].joint[1].jpos*r2d,
               d0->mech[m].joint[2].jpos, 
               d0->mech[m].joint[3].jpos*r2d, 
               d0->mech[m].joint[4].jpos*r2d,
               d0->mech[m].joint[5].jpos*r2d,
               d0->mech[m].joint[6].jpos*r2d,
               d0->mech[m].joint[7].jpos*r2d);
 	}
#endif
	//  Do FK for each mechanism
	for (int m=0; m<NUM_MECH; m++)
	{
		///log_msg("1.5. Was here  !!!!!!");
		// get arm type and wrist actuation angle
		if (d0->mech[m].type == GOLD_ARM)
	        {
			arm = dh_left;
		}
		else{

			arm = dh_right;
		}

		ori_d = &(d0->mech[m].ori_d);
		pos_d = &(d0->mech[m].pos_d);       	

#ifdef save_logs
	log_file("IK) Desired Pos - Arm %d = (%d, %d, %d)\n", m, pos_d->x, pos_d->y, pos_d->z);
                  
        log_file("IK) Desired Ori + Grasp = \n %f, %f, %f \n %f, %f, %f \n %f, %f, %f \n %d\n", ori_d->R[0][0], ori_d->R[0][1], ori_d->R[0][2], ori_d->R[1][0], ori_d->R[1][1], ori_d->R[1][2], ori_d->R[2][0], ori_d->R[2][1], ori_d->R[2][2], d0->mech[m].ori_d.grasp);
 
#endif

		// copy R matrix
		for (int i = 0; i < 3; i++)
			for (int j = 0; j < 3; j++)
				(xf.getBasis())[i][j] = ori_d->R[i][j];

//for (int i = 0; i < 3; i++)
		//	for (int j = 0; j < 3; j++)
//cout<<pos_d->x<<" "<<pos_d->y<<" "<<pos_d->z<< endl;


		xf.setBasis( tf::Matrix3x3(ori_d->R[0][0], ori_d->R[0][1], ori_d->R[0][2],
			     ori_d->R[1][0], ori_d->R[1][1], ori_d->R[1][2],
			     ori_d->R[2][0], ori_d->R[2][1], ori_d->R[2][2]  ) );
		xf.setOrigin( tf::Vector3(pos_d->x/(1000.0*1000.0),pos_d->y/(1000.0*1000.0), pos_d->z/(1000.0*1000.0)));



/*
		const static tf::Transform zrot_l( tf::Matrix3x3 (cos(25*d2r),-sin(25*d2r),0,  sin(25*d2r),cos(25*d2r),0,  0,0,1), tf::Vector3 (0,0,0) );
		const static tf::Transform zrot_r( tf::Matrix3x3 (cos(-25*d2r),-sin(-25*d2r),0,  sin(-25*d2r),cos(-25*d2r),0,  0,0,1), tf::Vector3 (0,0,0) );


		if (arm == dh_left)
		{
			xf = zrot_l.inverse() * xf;
		}
		else
		{
			xf = zrot_r.inverse() * xf;
		}
*/
		// DO IK
		ik_solution iksol[8] = {{},{},{},{},{},{},{},{}};

		int ret = inv_kin(xf, arm, iksol);
		if (ret < 0)
		{
			log_msg("ik failed gracefully (arm%d ret:%d)", arm, ret);
#ifdef save_logs
			log_file("Error: ik failed gracefully (arm%d ret:%d)", arm, ret);                 	
#endif		
		}
#ifdef save_logs	     		
		for (int i =0; i < 8;i++)
	        log_file("====== Arm %d - IK Solution %d = %f, %f, %f, %f, %f, %f\n", m, i+1 ,iksol[i].th1 * r2d, iksol[i].th2 * r2d, iksol[i].d3, iksol[i].th4 * r2d, iksol[i].th5 * r2d, iksol[i].th6 * r2d);

#endif
		// Check solutions - compare IK solutions to current joint angles...
		double wrist2 = (d0->mech[m].joint[GRASP2].jpos - d0->mech[m].joint[GRASP1].jpos) / 2.0; // grep "
		double joints[6] = {
				d0->mech[m].joint[SHOULDER].jpos,
				d0->mech[m].joint[ELBOW   ].jpos,
				d0->mech[m].joint[Z_INS   ].jpos,
				d0->mech[m].joint[TOOL_ROT].jpos,
				d0->mech[m].joint[WRIST   ].jpos,
				wrist2
		};

		// convert from joint angle representation to DH theta convention
		double lo_thetas[6];

		static int arm_check = 0;
                
		joint2theta(lo_thetas, joints, arm);  //this is the one that's wrong
     	
		int sol_idx=0;
		double sol_err;
		int check_result = 0;

		if ( (check_result = check_solutions(lo_thetas, iksol, sol_idx, sol_err)) < 0)
		{
			if(gTime%100 == 0)			
				cout << "IK failed\n";	
#ifdef save_logs
			log_file("Error: IK failed (arm %d)\n",arm);                	
#endif
			return -1;
		}

                
		double Js[6];
		double Js_sat[6];
		double thetas_sat[6];
		tf::Transform xf_sat;
		double gangle = double(d0->mech[m].ori_d.grasp) / 1000.0;
		theta2joint(iksol[sol_idx], Js);
/*		if(gTime%10 == 0)
		{
			cout<<" i am here============================================="<<endl;
			cout<<Js[0]*r2d<<" "<<Js[1]*r2d<<" "<<Js[2]<<" "<<Js[3]*r2d<<" "<<Js[4]*r2d
        	            << Js[5]*r2d<<" "<<Js[6]*r2d<<" "<<Js[7]<<endl;
		}*/
#ifdef simulator    
		if (m == 0)
		{
	            gangles[0] = gangle;
                    iksols[0] = iksol[sol_idx]; 
		}
		else
		{
		    gangles[1] = gangle;
                    iksols[1] = iksol[sol_idx]; 
	 	}	
		/*if(gTime%1000 == 0)	 
		   	log_msg("IK_Thetas_Arm%d: %f, %f, %f, %f, %f, %f, %f\n", 
                        m,iksol[sol_idx].th1*r2d,iksol[sol_idx].th2*r2d,
                        iksol[sol_idx].d3,
                        iksol[sol_idx].th4*r2d, iksol[sol_idx].th5*r2d,
                        iksol[sol_idx].th6*r2d, 
                        double(d0->mech[m].ori_d.grasp));*/
#ifdef save_logs
			log_file("IK Solution Js - Arm%d: %f, %f, %f, %f, %f, %f\n", 
                        m,
                        Js[0]*r2d,
                        Js[1]*r2d,
                        Js[2]*r2d,
                        Js[3]*r2d, 
                        Js[4]*r2d,
                        Js[5]*r2d);             	
#endif

#endif
		int limited = apply_joint_limits(Js,Js_sat);
		if (limited)
		{
			joint2theta(thetas_sat, Js_sat, arm);
			fwd_kin(thetas_sat, arm, xf_sat);
			d0->mech[m].pos_d.x = xf_sat.getOrigin()[0] * (1000.0*1000.0);
			d0->mech[m].pos_d.y = xf_sat.getOrigin()[1] * (1000.0*1000.0);
			d0->mech[m].pos_d.z = xf_sat.getOrigin()[2] * (1000.0*1000.0);
			for (int i=0;i<3;i++)
				for (int j=0; j<3; j++)
					d0->mech[m].ori_d.R[i][j] = (xf_sat.getBasis())[i][j];

			updateMasterRelativeOrigin(d0);
#ifdef save_logs
			log_file("Error: Saturated to Joint Limits (arm %d)\n", arm);                  	
#endif
		}
		else
		{
			for (int satloop=0; satloop<6; satloop++)
				Js_sat[satloop] = Js[satloop];
		}

		d0->mech[m].joint[SHOULDER].jpos_d = Js_sat[0];
		d0->mech[m].joint[ELBOW   ].jpos_d = Js_sat[1];
		d0->mech[m].joint[Z_INS   ].jpos_d = Js_sat[2];
		d0->mech[m].joint[TOOL_ROT].jpos_d = Js_sat[3];
		d0->mech[m].joint[WRIST   ].jpos_d = Js_sat[4];
		d0->mech[m].joint[GRASP1  ].jpos_d = -Js[5] +  gangle / 2;
		d0->mech[m].joint[GRASP2  ].jpos_d =  Js[5] +  gangle / 2;
#ifdef save_logs
			log_file("IK Solution Changed: Jpos - Arm%d: %f, %f, %f, %f, %f, %f, %f\n", 
                        m,
                        d0->mech[m].joint[SHOULDER].jpos_d*r2d,
                        d0->mech[m].joint[ELBOW   ].jpos_d*r2d,
                        d0->mech[m].joint[Z_INS   ].jpos_d*r2d,
                        d0->mech[m].joint[TOOL_ROT].jpos_d*r2d, 
                        d0->mech[m].joint[WRIST   ].jpos_d*r2d,
                        d0->mech[m].joint[GRASP1  ].jpos_d*r2d, 
                        d0->mech[m].joint[GRASP2  ].jpos_d*r2d);             	
#endif
		
         	if (printIK !=0 )// && d0->mech[m].type == GREEN_ARM_SERIAL )
		{
			log_msg("All IK solutions for mechanism %d.  Chosen solution:%d:",m, sol_idx);
			log_msg("Current     :\t( %3f,\t %3f,\t %3f,\t %3f,\t %3f,\t %3f (\t %3f/\t %3f))",
					joints[0] * r2d,
					joints[1] * r2d,
					joints[2],
					joints[3] * r2d,
					joints[4] * r2d,
					joints[5] * r2d,
					d0->mech[m].joint[GRASP2].jpos  * r2d,
					d0->mech[m].joint[GRASP2].jpos * r2d
			);
			for (int i=0; i<8; i++)
			{
				theta2joint(iksol[i], Js);
				/*log_msg("ik_joints[%d]:\t( %3f,\t %3f,\t %3f,\t %3f,\t %3f,\t %3f)",i,
						Js[0] * r2d,
						Js[1] * r2d,
						Js[2],
						Js[3] * r2d,
						Js[4] * r2d,
						Js[5] * r2d
						);*/
			}
		}
	}

	printIK=0;
#ifdef simulator
    int check_result = 0;
    static int counter = 0;
    counter++; 
    if (counter % 100 == 0)
    {

	if ((check_result = check_collision(iksols,gangles)) < 0 )
	{
		log_msg("Collision Detected\n");	
		log_file("Error: Collision Detected\n");
	}  
    }
        //log_file("RT_PROCESS) INV Kinematics Done.\n");            
#endif	
	return 0;
}




/**\fn  inv_kin(tf::Transform in_T06, l_r in_arm, ik_solution iksol[8])
 * \brief Runs the Raven II INVERSE kinematics to determine end effector position.
 *
 * See Hawkeye King, Sina Nia Kosari, Blake Hannaford, Ji Ma, 'Kinematic Analysis of the Raven-II(tm) Research Surgical Robot Platform,' University of Washington Electrical Engineering Department Technical Report ,Number 2012-0006, June 29, 2012. (Revised March 2014)
 *
 * \param in_T06 - a btTransfrom obejct, transforms the end effector frame to zero frame
 * \param in_arm - Arm type, left / right ( kin.armtype arm = left/right)
 * \param ik_solution iksol[8] - The 8 solutions:  8 element array of joint angles ( float j[] = {shoulder, elbow, vacant joint, ins,roll, wrist, grasp1, grasp2} )
 * \return 0 - success, -1 - bad arm, -2 - too close to RCM.
 * \question  why __attribute__ optimize?
 * \ingroup Kinematics
 */

int  __attribute__ ((optimize("0"))) inv_kin(tf::Transform in_T06, l_r in_arm, ik_solution iksol[8])
{
	dh_theta = robot_thetas[in_arm];
	dh_d     = ds[in_arm];
	dh_alpha = alphas[in_arm];
	dh_a     = aas[in_arm];
	for (int i=0;i<8;i++)
		iksol[i] = ik_zerosol;

	if  ( in_arm  >= dh_l_r_last)
	{
		ROS_ERROR("BAD ARM IN IK!!!");
		return -1;
	}

	for (int i=0;i<8;i++)    iksol[i].arm = in_arm;

	//  Step 1, Compute P5
	tf::Transform  T60 = in_T06.inverse();
	tf::Vector3    p6rcm = T60.getOrigin();
	tf::Vector3    p05[8];

	p6rcm[2]=0;    // take projection onto x-y plane
	for (int i= 0; i<2; i++)
	{
		tf::Vector3 p65 = (-1+2*i) * Lw * p6rcm.normalize();
		p05[4*i] = p05[4*i+1] = p05[4*i+2] = p05[4*i+3] = in_T06 * p65;
	}


	//  Step 2, compute displacement of prismatic joint d3
	for (int i=0;i<2;i++)
	{
		double insertion = 0;
		insertion += p05[4*i].length();  // Two step process avoids compiler optimization problem. (Yeah, right. It was the compiler's problem...)

		if (insertion <= Lw)
		{
			cerr << "WARNING: mechanism at RCM singularity(Lw:"<< Lw <<"ins:" << insertion << ").  IK failing.\n";
			iksol[4*i + 0].invalid = iksol[4*i + 1].invalid = ik_invalid;
			iksol[4*i + 2].invalid = iksol[4*i + 3].invalid = ik_invalid;
			return -2;
		}
		iksol[4*i + 0].d3 = iksol[4*i + 1].d3 = -d4 - insertion;
		iksol[4*i + 2].d3 = iksol[4*i + 3].d3 = -d4 + insertion;
	}




	//  Step 3, calculate theta 2
	for (int i=0; i<8; i+=2) // p05 solutions
	{
		double z0p5 = p05[i][2];

		double d = iksol[i].d3 + d4;
		double cth2=0;

		if (in_arm  == dh_left)
			cth2 = 1 / (GM1*GM3) * ((-z0p5 / d) - GM2*GM4);
		else
			cth2 = 1 / (GM1*GM3) * ((z0p5 / d) + GM2*GM4);

		// Smooth roundoff errors at +/- 1.
		if      (cth2 > 1  && cth2 <  1+eps) cth2 =  1;
		else if (cth2 < -1 && cth2 > -1-eps) cth2 = -1;

		if (cth2>1 || cth2 < -1) {
			iksol[i].invalid = iksol[i+1].invalid = ik_invalid;
		}
		else
		{
			iksol[ i ].th2 =  acos( cth2 );
			iksol[i+1].th2 = -acos( cth2 );
		}
	}


	//  Step 4: Compute theta 1
	for (int i=0;i<8;i++)
	{
		if (iksol[i].invalid == ik_invalid)
			continue;

		double cth2 = cos(iksol[i].th2);
		double sth2 = sin(iksol[i].th2);
		double d    = iksol[i].d3 + d4;
		double BB1 = sth2*GM3;
		double BB2=0;
		tf::Matrix3x3 Bmx;     // using 3 vector and matrix bullet types for convenience.
		tf::Vector3   xyp05(p05[i]);
		xyp05[2]=0;

		if (in_arm == dh_left)
		{
			BB2 = cth2*GM2*GM3 - GM1*GM4;
			Bmx.setValue(BB1,  BB2,0,   -BB2, BB1,0,   0,    0,  1 );
		}
		else
		{
			BB2 = cth2*GM2*GM3 + GM1*GM4;
			Bmx.setValue( BB1, BB2,0,   BB2,-BB1,0,    0,   0,  1 );
		}

		tf::Vector3 scth1 = Bmx.inverse() * xyp05 * (1/d);
		iksol[i].th1 = atan2(scth1[1],scth1[0]);
	}


	//  Step 5: get theta 4, 5, 6
	for (int i=0; i<8;i++)
	{
		if (iksol[i].invalid == ik_invalid)
			continue;

		// compute T03:
		dh_theta[0] = iksol[i].th1;
		dh_theta[1] = iksol[i].th2;
		dh_d[2]     = iksol[i].d3;
		tf::Transform T03 = getFKTransform(0, 3);
		tf::Transform T36 = T03.inverse() * in_T06;

		double c5 = -T36.getBasis()[2][2];
		double s5 = (T36.getOrigin()[2]-d4)/Lw;

		// Compute theta 4:
		double c4, s4;
		if (fabs(c5) > eps)
		{
			c4 =T36.getOrigin()[0] / (Lw * c5);
			s4 =T36.getOrigin()[1] / (Lw * c5);
		}
		else
		{
			c4 = T36.getBasis()[0][2] / s5;
			s4 = T36.getBasis()[1][2] / s5;
		}
		iksol[i].th4 = atan2(s4,c4);

		// Compute theta 5:
		iksol[i].th5 = atan2(s5, c5);


		// Compute theta 6:
		double s6, c6;
		if (fabs(s5) > eps)
		{
			c6 =  T36.getBasis()[2][0] / s5;
			s6 = -T36.getBasis()[2][1] / s5;
		}
		else
		{
			dh_theta[3] = iksol[i].th4;
			dh_theta[4] = iksol[i].th5;
			tf::Transform T05 = T03 * getFKTransform(3, 5);
			tf::Transform T56 = T05.inverse() * in_T06;
			c6 =T56.getBasis()[0][0];
			s6 =T56.getBasis()[2][0];
		}
		iksol[i].th6 = atan2(s6, c6);

//		if (gTime%1000 == 0 && in_arm == dh_left )
//		{
//			log_msg("dh_iksols: [%d]\t( %3f,\t %3f,\t %3f,\t %3f,\t %3f,\t %3f)",0,
//					iksol[i].th1 * r2d,
//					iksol[i].th2 * r2d,
//					iksol[i].d3,
//					iksol[i].th4 * r2d,
//					iksol[i].th5 * r2d,
//					iksol[i].th6 * r2d
//					);
//		}


	}
	return 0;
}

/**\fn int apply_joint_limits(double *Js, double *Js_sat)
 * \brief Apply joint limit on the selected inverse kinematics solution
 * \param Js - a double type pointer, Inverse Kinematics Solution Js
 * \param Js_sat - a double type pointer, Saturated Inverse Kinematics Solution Js_sat
 * \return 1 limit value of joint angle is appied, 0 inverse solution has not reached joint limit
 *  \ingroup Kinematics
 */
int apply_joint_limits(double *Js, double *Js_sat){
	int limited = 0;

	for (int i =0 ; i<6 ; i++)
		Js_sat[i] = Js[i];

	if (Js[0] <= DOF_types[SHOULDER].min_limit)
	{
		Js_sat[0] = DOF_types[SHOULDER].min_limit;
		limited = 1;
		std::cout<<"eblow min limit reached  = "<<Js_sat[0]<<std::endl;
	}
	else if(Js[0] >= DOF_types[SHOULDER].max_limit)
	{
		Js_sat[0] = DOF_types[SHOULDER].max_limit;
		limited = 1;
		std::cout<<"eblow max limit reached  = "<<Js_sat[0]<<std::endl;
	}

	if (Js[1] <= ELBOW_MIN_LIMIT)
	{
		Js_sat[1] = ELBOW_MIN_LIMIT;
		limited = 1;
		std::cout<<"eblow min limit reached  = "<<Js_sat[1]<<std::endl;
	}

	else if(Js[1] >= ELBOW_MAX_LIMIT)
	{
		Js_sat[1] = ELBOW_MAX_LIMIT;
		limited = 1;
		std::cout<<"eblow max limit reached  = "<<Js_sat[1]<<std::endl;
	}

	if (Js[2] <= DOF_types[Z_INS].min_limit)
	{
		Js_sat[2] = DOF_types[Z_INS].min_limit;
		limited = 1;
		std::cout<<"z min limit reached  = "<<Js_sat[2]<<std::endl;
	}
	else if(Js[2] >= DOF_types[Z_INS].max_limit)
	{
		Js_sat[2] = DOF_types[Z_INS].max_limit;
		limited = 1;
		std::cout<<"z max limit reached  = "<<Js_sat[2]<<std::endl;
	}

	if (Js[3] <= -150.0 DEG2RAD)
	{
		Js_sat[3] = -150.0 DEG2RAD;
		limited = 1;
		std::cout<<"rot min limit reached  = "<<Js_sat[3]<<std::endl;
	}

	else if(Js[3] >= 150.0 DEG2RAD)
	{
		Js_sat[3] = 150.0 DEG2RAD;
		limited = 1;
		std::cout<<"rot max limit reached  = "<<Js_sat[3]<<std::endl;
	}


	if (Js[4] <= DOF_types[WRIST].min_limit)
	{
		Js_sat[4] = DOF_types[WRIST].min_limit;
		limited = 1;
		std::cout<<"wrist min limit reached  = "<<Js_sat[4]<<std::endl;
	}
	else if(Js[4] >= DOF_types[WRIST].max_limit)
	{
		Js_sat[4] = DOF_types[WRIST].max_limit;
		limited = 1;
		std::cout<<"wrist max limit reached  = "<<Js_sat[4]<<std::endl;
	}

	//Js_sat[5] = Js[5];
	/*
	Js_sat[0] = Js[0];
	Js_sat[1] = Js[1];
	Js_sat[2] = Js[2];
	Js_sat[3] = Js[3];
	Js_sat[4] = Js[4];
	Js_sat[5] = Js[5];*/

	//if (limited) std::cout<<"A joint has been saturated"<<std::endl;

	return limited;
}

/**\fn int check_solutions(double *in_thetas, ik_solution * iksol, int &out_idx, double &out_err)
 * \brief check the inverse kinematic solutions
 * \param in_thetas a double type pointer points to the joint angle array
 * \param ik_sol
 * \param out_idx
 * \param out_error
 * \return 0 on success -1 on failure
 *  \ingroup Kinematics
 */
int check_solutions(double *in_thetas, ik_solution * iksol, int &out_idx, double &out_err)
{
	double minerr = 32765;
	int minidx=-1;
	double invalids = 0;
	double eps = M_PI;
	int rollover = 0;

	for (int i=0; i<8;i++)
	{
		if (iksol[i].invalid == ik_invalid)
		{
			invalids++;
			continue;
		}

		// check for rollover on tool roll
		if ( fabs(in_thetas[3] - iksol[i].th4) > 300 * d2r )
		{
			rollover=1;
			if (in_thetas[3] > iksol[i].th4)
				iksol[i].th4 += 2 * M_PI;
			else
				iksol[i].th4 -= 2 * M_PI;
		}

		double s2err = 0;
		s2err += pow(in_thetas[0] - iksol[i].th1, 2);
		s2err += pow(in_thetas[1] - iksol[i].th2, 2);
		s2err += pow( 100*(in_thetas[2] - iksol[i].d3) , 2);
		s2err += pow(in_thetas[3] - iksol[i].th4, 2);
		s2err += pow(in_thetas[4] - iksol[i].th5, 2);
		s2err += pow(in_thetas[5] - iksol[i].th6, 2);
		if (s2err < minerr)
		{
			minerr=s2err;
			minidx=i;
		}
        //cout << "==== Min Error"<< minerr << endl;
	}
	
        for (int i = 0; i<10000000; i++);
	if (minerr>eps)
	{
		minidx=9;
		minerr = 0;
		if (gTime %100 == 0 && iksol[minidx].arm == dh_left)
		{
				cout << "failed (err>eps) on j=\t\t(" << in_thetas[0] * r2d << ",\t" << in_thetas[1] *r2d << ",\t" << in_thetas[2] << ",\t" << in_thetas[3] * r2d << ",\t" << in_thetas[4] * r2d << ",\t" << in_thetas[5] * r2d << ")"<<endl;

			for (int idx=0;idx<8;idx++)
			{
				double s2err = 0;
				s2err += pow(in_thetas[0] - iksol[idx].th1*r2d, 2);
				s2err += pow(in_thetas[1] - iksol[idx].th2*r2d, 2);
				s2err += pow(in_thetas[2] - iksol[idx].d3, 2);
				s2err += pow(in_thetas[3] - iksol[idx].th4*r2d, 2);
				s2err += pow(in_thetas[4] - iksol[idx].th5*r2d, 2);
				s2err += pow(in_thetas[5] - iksol[idx].th6*r2d, 2);
//				cout << "sol[" << idx<<"]: err:"<<   s2err << "\t\t" << iksol[idx].th1*r2d << ",\t" << iksol[idx].th2*r2d << ",\t" <<iksol[idx].d3 << ",\t" <<iksol[idx].th4*r2d << ",\t" <<iksol[idx].th5*r2d << ",\t" <<iksol[idx].th6*r2d << ",\n";
			}
		}
		return -1;
	}
	//cout << "thetas" << in_thetas[4]*r2d << "-" << iksol[minidx].th5*r2d << endl;
	out_idx=minidx;
	out_err=minerr;
	return rollover;
}



//-------------------------------------------------------------------------------
// Utility functions to print out transforms
//-------------------------------------------------------------------------------

/**\fn void print_tf(tf::Transform xf)
 * \brief print a tf::Transform object
 * \param xf - a tf::Transform object to print
 * \return void
 *  \ingroup Kinematics
 */
void print_tf(tf::Transform xf)
{
	tf::Matrix3x3 rr = xf.getBasis();
	tf::Vector3 vv = xf.getOrigin();
	std::stringstream ss;

	cout << fixed;
	for (int i=0; i<3; i++)
	{
		for (int j=0; j<3; j++)
			ss << rr[i][j] << "\t ";
		ss << vv[i] << endl;
	}
	ss << "0\t 0\t 0\t 1\n";
	log_msg("\n%s", ss.str().c_str());
}


/**\fn void print_btVector(tf::Vector3 vv)
 * \brief print a tf::Vector3 object
 * \param vv - a tf::Vector3 obejct to print
 * \return void
 *  \ingroup Kinematics
 */
void print_btVector(tf::Vector3 vv)
{
	std::stringstream ss;

	for (int j=0; j<3; j++)
		ss << vv[j] << ",\t ";
	log_msg("(%s)", ss.str().c_str());
}




//------------------------------------------------------------------------------------------
// Conversion of J to Theta /// Theta 2 J
// J represents the physical robot joint angles.
// Theta is used by the kinematics.
// Theta convention was easier to solve the equations, while J was already coded in software.
//-----------------------------------------------------------------------------------------
const static double TH1_J0_L  = 205;//-180;//-205;   //add this to J0 to get \theta1 (in deg)
const static double TH2_J1_L  = 180;//-180;   //add this to J1 to get \theta2 (in deg)
const static double D3_J2_L   = 0.0;    //add this to J2 to get d3 (in meters????)
const static double TH4_J3_L  = 0;      //add this to J3 to get \theta4 (in deg)
const static double TH5_J4_L  = -90; //90;     //add this to J4 to get \theta5 (in deg)
const static double TH6A_J5_L = 0;     //add this to J5 to get \theta6a (in deg)
const static double TH6B_J6_L = 0;     //add this to J6 to get \theta6b (in deg)

const static double TH1_J0_R  = 25;//0;//-25;    //add this to J0 to get \theta1 (in deg)
const static double TH2_J1_R  = 0;      //add this to J1 to get \theta2 (in deg)
const static double D3_J2_R   = 0.0;    //add this to J2 to get d3 (in meters???)
const static double TH4_J3_R  = 0;     //add this to J3 to get \theta4 (in deg)
const static double TH5_J4_R  = -90; //90;     //add this to J4 to get \theta5 (in deg)
const static double TH6A_J5_R = 0;     //add this to J5 to get \theta6a (in deg)
const static double TH6B_J6_R = 0;     //add this to J6 to get \theta6b (in deg)

//void joint2thetaCallback(const sensor_msgs::JointStateConstPtr joint_state)

/**\fn void joint2theta(double *out_iktheta, double *in_J, l_r in_arm)
 * \brief converts the inverse kinematic solution to the thethas (detailes refer to the kinematic report)
 * \param out_iktheta - a double type pointer of the converted output
 * \param in_J - a double type pointer of the inverse kinetmatic solution
 * \param in_arm - Arm type gold/green
 * \return void
 * \question why just remove this conversion, set theta the same as joint angle????
 *  \ingroup Kinematics
 */

void joint2theta(double *out_iktheta, double *in_J, l_r in_arm)
{
	//convert J to theta
	if (in_arm == dh_left)
	{
	//======================LEFT ARM===========================
		out_iktheta[0] = in_J[0] + TH1_J0_L * d2r;
		out_iktheta[1] = in_J[1] + TH2_J1_L * d2r;
		out_iktheta[2] = in_J[2] + D3_J2_L;
		out_iktheta[3] = in_J[3] + TH4_J3_L * d2r;
		out_iktheta[4] = in_J[4] + TH5_J4_L * d2r;
		out_iktheta[5] = in_J[5] + TH6A_J5_L * d2r;

		static int larm_check = 0;
		if (larm_check < 2) {
			log_msg("why left arm? -- j2t");
			larm_check++;
		}

	}

	else
	{
	//======================RIGHT ARM===========================
		out_iktheta[0] = in_J[0] + TH1_J0_R * d2r;
		out_iktheta[1] = in_J[1] + TH2_J1_R * d2r;
		out_iktheta[2] = in_J[2] + D3_J2_R;
		out_iktheta[3] = in_J[3] + TH4_J3_R * d2r;
		out_iktheta[4] = in_J[4] + TH5_J4_R * d2r;
		out_iktheta[5] = in_J[5] + TH6A_J5_R * d2r;
		static int arm_check = 0;
		if (arm_check < 2) {
			log_msg("definitely still the right arm j2t");
			arm_check++;                        
		}
	}

	// bring to range {-pi , pi}
	for (int i=0;i<6;i++)
	{
		while(out_iktheta[i] > M_PI)
			out_iktheta[i] -= 2*M_PI;

		while(out_iktheta[i] < -M_PI)
			out_iktheta[i] += 2*M_PI;
	}
}


//void joint2thetaCallback(const sensor_msgs::JointStateConstPtr joint_state)

/**\fn void theta2joint(ik_solution in_iktheta, double *out_J)
 * \brief converts theta values to the joint angles (detailes refer to the kinematic report)
 * \param out_iktheta - a double type pointer of the theta values
 * \param in_J - a double type pointer of joint angles
 * \return void
 * \question why just remove this conversion, set theta the same as joint angle????
 */
void theta2joint(ik_solution in_iktheta, double *out_J)
{
	//convert J to theta
	if (in_iktheta.arm == dh_left)
	{
	//======================LEFT ARM===========================
		out_J[0] = in_iktheta.th1 - TH1_J0_L * d2r;
		out_J[1] = in_iktheta.th2 - TH2_J1_L * d2r;
		out_J[2] = in_iktheta.d3  - D3_J2_L;
		out_J[3] = in_iktheta.th4 - TH4_J3_L * d2r;
		out_J[4] = in_iktheta.th5 - TH5_J4_L * d2r;
		out_J[5] = in_iktheta.th6 - TH6A_J5_L * d2r;



	}

	else
	{
	//======================RIGHT ARM===========================
		out_J[0] = in_iktheta.th1 - TH1_J0_R * d2r;
		out_J[1] = in_iktheta.th2 - TH2_J1_R * d2r;
		out_J[2] = in_iktheta.d3  - D3_J2_R;
		out_J[3] = in_iktheta.th4 - TH4_J3_R * d2r;
		out_J[4] = in_iktheta.th5 - TH5_J4_R * d2r;
		out_J[5] = in_iktheta.th6 - TH6A_J5_R * d2r;

		static int arm_check = 0;
		if (arm_check < 2) {
			log_msg("definitely the right arm -- t2j");
			arm_check++;
		}
	}

	// bring to range {-pi , pi}
	for (int i=0;i<6;i++)
	{
		if (i==3) i++;
		while(out_J[i] > M_PI)
			out_J[i] -= 2*M_PI;

		while(out_J[i] < -M_PI)
			out_J[i] += 2*M_PI;
	}

}

/**\fn void showInverseKinematicsSolutions(struct device *d0, int runlevel)
 * \brief
 * \param d0
 * \param runlevel
 * \return void
 *  \ingroup Kinematics
 */
void showInverseKinematicsSolutions(struct device *d0, int runlevel)
{
	log_msg("print_ik_plz");
	printIK = 1;
	r2_inv_kin(d0, runlevel);
	log_msg("kthxbai");
}
