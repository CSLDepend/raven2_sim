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
 * You should have received a copy of the GNU  General Public License
 * along with Raven 2 Control.  If not, see <http://www.gnu.org/licenses/>.
 */

/**
 * defines.h
 *
 * Global defines
 *
 */

#ifndef __DEFINE_H__
#define __DEFINE_H__

#include <math.h>

//#define simulator
#define simulator_packet
#define skip_init_button
#define skip_restart_button
#define surgeon_packet_gen
//#define test_gdb
//#define no_logging

#define RAVEN_MODULE_VERSION RAVEN_II_RELEASE_02
#define device robot_device

#define SURGICAL_ROBOT     	1
#define RAVEN_II        	1
//#define KIST

//#define RAVEN_TOOLS
#define DV_ADAPTER			1
//#define RAVEN_II_SQUARE    1 //for Santa Cruz style tool carriage
//#define RICKS_TOOLS

#undef RAVEN_TOOLS
//#undef DV_ADAPTER
#undef RAVEN_II_SQUARE
#undef RICKS_TOOLS


// Two arm identification
// Change this to match device ID in /dev/brl_usbXX
#define GREEN_ARM_SERIAL 29
#define GOLD_ARM_SERIAL  37

#define GREEN_ARM        GREEN_ARM_SERIAL
#define GOLD_ARM         GOLD_ARM_SERIAL



//KIST configuration is GREEN ONLY and no tools(ricks tools)
#ifdef KIST

#ifndef GREEN_ONLY
#define GREEN_ONLY //if only using the green arm and one USB board
#endif

#undef RAVEN_TOOLS
#undef DV_ADAPTER
#undef RAVEN_II_SQUARE


#define RICKS_TOOLS

#endif

// Event logging function
//  Log levels:
//     0: Trivial   1: Normal/informational    2: Critical/Important
//  Log Codes:
//     0-3: Entered runlevel 0-3   4: RT_Process started  5: RT_Process ended
// \todo Redefine rt_printk to suitable debugging function
#define ROBOT_LOG(logLevel, logCode, fmt, args...) //rt_printk("ROBOT LOG[%d/%d]: " fmt, logLevel, logCode, ##args)

//Include current clipping
#define CURRENT_CLIPPING

// Degree - radian converion
#define DEG2RAD *(M_PI/180.0)
#define RAD2DEG *(180.0/M_PI)

#define ENC_CNT_PER_DEG (float)(ENC_CNTS_PER_REV / 360)
#define ENC_CNT_PER_RAD (float)(ENC_CNTS_PER_REV / (2*M_PI))

//Verbose mode
//#define MORE_MESSAGES 1

// Software can set runlevels
//#define SOFTWARE_RUNLEVELS 1

// PLC can set runlevels (PLC takes priority if SOFTWARE_RUNLEVELS is also defined.)
#define PLC_RUNLEVELS 1

//RUN LEVELS
#define RL_E_STOP    0
#define RL_INIT      1
#define RL_PEDAL_UP  2
#define RL_PEDAL_DN  3

#define SL_PD_CTRL   0
#define SL_DAC_CTRL  1
#define SL_AUTO_INIT 3

//Joint Defines
#define SHOULDER   0
#define ELBOW      1
#define Z_INS      2
//<not connected>    3
#define TOOL_ROT   4
#define WRIST      5
#define GRASP1     6
#define GRASP2     7
#define NO_CONNECTION 3

//GOLD Arm Defines
#define SHOULDER_GOLD   0
#define ELBOW_GOLD      1
#define Z_INS_GOLD      2
//<not connected>    3
#define TOOL_ROT_GOLD   4
#define WRIST_GOLD      5
#define GRASP1_GOLD     6
#define GRASP2_GOLD     7
#define NO_CONNECTION_GOLD 3

//GREEN Arm Defines
#define SHOULDER_GREEN   8
#define ELBOW_GREEN      9
#define Z_INS_GREEN      10
//<not connected>    11
#define TOOL_ROT_GREEN   12
#define WRIST_GREEN      13
#define GRASP1_GREEN     14
#define GRASP2_GREEN     15
#define NO_CONNECTION_GREEN 11

//Joint Scale Factors
#define WRIST_SCALE_FACTOR (float)(1.5) /*used in update_device_state.c on incoming param*/

//Amplifier constants.
#define K_DAC_PER_AMP_LOW_CURRENT   5461   // Empirically validated as the same as MFHD constant
#define K_DAC_PER_AMP_HIGH_CURRENT  2730   // High current amplifiers output double the low.

// Gear box ratios
#define GEAR_BOX_GP42_TR (49.0/4.0)  // 12.25
#define GEAR_BOX_GP32_TR (26.0/7.0)	// 3.7

#define GEAR_BOX_TR_BIG_MOTOR     GEAR_BOX_GP42_TR
#define GEAR_BOX_TR_SMALL_MOTOR   GEAR_BOX_GP32_TR

//Transmission Ratios
// See also, motor.h
#define CABLE_RADIUS_1050 (1.19/2.0)
#define CABLE_RADIUS_1024 (0.61/2.0)

#define PARTIAL_PULLEY_LINK1_RADIUS (62.5  + CABLE_RADIUS_1050)
#define PARTIAL_PULLEY_LINK2_RADIUS (40.85 + CABLE_RADIUS_1050)
#define CAPSTAN_LINK2_LARGE_RADIUS (7.82  + CABLE_RADIUS_1050)
#define CAPSTAN_LINK2_SMALL_RADIUS (5.60  + CABLE_RADIUS_1050)

//#define CAPSTAN_RADIUS_GP42 6.0 // (5.4 + CABLE_RADIUS_1050) // 5.4+0.595 = 5.995 ->6mm
#define CAPSTAN_RADIUS_GP42 (11.35/2)  // measured using caliper, plus validated empirically
#define CAPSTAN_RADIUS_GP32 (4.7  + CABLE_RADIUS_1024)
#define CAPSTAN_TOOL_RADIUS (10.6 + CABLE_RADIUS_1024)

// Cable coupling constants
//  Note: The numbering is wierd b/c the UCSC software puts Z-axis after tool rotation.
//        Take care to use the #defined name (e.g. Z_INS / TOOL_ROT) when possible.
//        If not, then may god have mercy on your soul.  sSee fwd_cable_coupling.cpp for example
//
//   Note: By observation Hawkeye determined the following:
// TR1 : First joint, Shoulder
// TR2 : Second joint, Elbow
// TR3 : Fourth joint, Tool rotation
// TR4 : Third joint, Z-Insertion, prismatic
// TR5 : Fifth Joint, Wrist
// TR6 : Sixth joint, Grasper jaw 1
// TR7 : Seventh joint, Grasper jaw 2
//    This is most critical in init.cpp - initDOFparams() and
#define SHOULDER_TR_GREEN_ARM (float)( (PARTIAL_PULLEY_LINK1_RADIUS/CAPSTAN_RADIUS_GP42) * GEAR_BOX_GP42_TR) // RE-40, GP-42 // UNITLESS
#define ELBOW_TR_GREEN_ARM    (float)( (PARTIAL_PULLEY_LINK2_RADIUS/CAPSTAN_LINK2_SMALL_RADIUS)  *  (CAPSTAN_LINK2_LARGE_RADIUS/CAPSTAN_RADIUS_GP42) * GEAR_BOX_GP42_TR) // RE-40, GP-42 // UNITLESS
#define Z_INS_TR_GREEN_ARM    (float)( (1.0/((2*M_PI*CAPSTAN_RADIUS_GP42)/1000.0)) * GEAR_BOX_GP42_TR *2*M_PI) // UNITS: rad/meter  Note: 2pi cancels
#define TOOL_ROT_TR_GREEN_ARM (float)( CAPSTAN_TOOL_RADIUS/CAPSTAN_RADIUS_GP32 * GEAR_BOX_GP32_TR * 120.0/180.0) // (asked 180, received 120)
#define WRIST_TR_GREEN_ARM    (float)( CAPSTAN_TOOL_RADIUS/CAPSTAN_RADIUS_GP32 * GEAR_BOX_GP32_TR * 200.0/180.0) //  RE-30, GP-32  ( /180 is a fudge factor put in by HK through observation. Was 140/180
#define GRASP1_TR_GREEN_ARM   (float)( CAPSTAN_TOOL_RADIUS/CAPSTAN_RADIUS_GP32 * GEAR_BOX_GP32_TR * 100.0/90.0) //  RE-30, GP-32 (100/90 is a fudge factor put in by HK through observation. Was 75/90
#define GRASP2_TR_GREEN_ARM   (float)( CAPSTAN_TOOL_RADIUS/CAPSTAN_RADIUS_GP32 * GEAR_BOX_GP32_TR * 100.0/90.0) //  RE-30, GP-32

#define SHOULDER_TR_GOLD_ARM   (SHOULDER_TR_GREEN_ARM)
#define ELBOW_TR_GOLD_ARM      (ELBOW_TR_GREEN_ARM)
#define Z_INS_TR_GOLD_ARM      (Z_INS_TR_GREEN_ARM)
#define TOOL_ROT_TR_GOLD_ARM   (TOOL_ROT_TR_GREEN_ARM)
#define WRIST_TR_GOLD_ARM      (WRIST_TR_GREEN_ARM)
#define GRASP1_TR_GOLD_ARM     (GRASP1_TR_GREEN_ARM)
#define GRASP2_TR_GOLD_ARM     (GRASP2_TR_GREEN_ARM)

//Link Angles/Lengths
#define A12 (float)(1.30899694)    /*Link1 - 75deg in RAD*/
#define A23 (float)(0.907571211)    /*Link2 - 52deg in RAD - was set to 60*/

//Kinematic Zero Offset (encoder space)
#define SHOULDER_GOLD_KIN_OFFSET (float)(0.0) //(62.0)
#define ELBOW_GOLD_KIN_OFFSET    (float)(0.0) //(-328.0)//d enc -offset
#define Z_INS_GOLD_KIN_OFFSET    (float)(0.0)

#define SHOULDER_GREEN_KIN_OFFSET SHOULDER_GOLD_KIN_OFFSET
#define ELBOW_GREEN_KIN_OFFSET    ELBOW_GOLD_KIN_OFFSET
#define Z_INS_GREEN_KIN_OFFSET    Z_INS_GOLD_KIN_OFFSET

//Kinematic Zero Offset (encoder space) RAVEN_I used differnet kin. eq's
//#define SHOULDER_A_KIN_OFFSET (float)(-62.0)
//#define ELBOW_A_KIN_OFFSET    (float)(-32.0)
//#define Z_INS_A_KIN_OFFSET    (float)(0.0)
//
//#define SHOULDER_B_KIN_OFFSET (float)(62.0)
//#define ELBOW_B_KIN_OFFSET    (float)(-328.0)
//#define Z_INS_B_KIN_OFFSET    (float)(0.0)


//InvKinematic Software Stops
//   Kinematics equations for R+II are formulated so that joint ranges are identical on each arm.
#define SHOULDER_MIN_LIMIT (float)(   0.0 DEG2RAD)
#define SHOULDER_MAX_LIMIT (float)(  90.0 DEG2RAD)
#define ELBOW_MIN_LIMIT (float)(  45.0 DEG2RAD)
#define ELBOW_MAX_LIMIT (float)( 135.0 DEG2RAD)

/*#define TOOL_GRASP1_MIN_LIMIT (float)(-45.0 DEG2RAD)
#define TOOL_GRASP1_MAX_LIMIT (float)( 45.0 DEG2RAD)
#define TOOL_GRASP2_MIN_LIMIT (float)(-45.0 DEG2RAD)
#define TOOL_GRASP2_MAX_LIMIT (float)( 45.0 DEG2RAD)
*/

//DAC
#define DAC_OFFSET        0x8000  /* Used to convert DAC vals to midrange */

// Current limits
#ifdef RAVEN_II_SQUARE
#define MAX_INST_DAC 12000 //20000 //32000

// Doubled position joints 4-Apr-2013 by HK
#define SHOULDER_MAX_DAC   5000   // 2000 usually moves 1000 doesn't
#define ELBOW_MAX_DAC      5000   //  ""
#define Z_INS_MAX_DAC      4000   //  1000 moves but doesn't overcome friction in tool joints
#define TOOL_ROT_MAX_DAC   4500  // 10000   These are set really low for safety sake //up from 3500 on 2/28/14
#define WRIST_MAX_DAC      4500  // up from 1900 on 10/10/2013 //up from 2500 on 2/28/14
#define GRASP1_MAX_DAC     4500  // up from 2000 on 10/10/2013 //up from 2500 on 2/28/14
#define GRASP2_MAX_DAC     4500  // up from 2000 on 10/10/2013 //up from 2500 on 2/28/14

#else
#define MAX_INST_DAC 12000 //20000 //32000

// Doubled position joints 4-Apr-2013 by HK
#define SHOULDER_MAX_DAC   10000//5000   // 2000 usually moves 1000 doesn't
#define ELBOW_MAX_DAC      10000//5000   //  ""
#define Z_INS_MAX_DAC      8000//4000   //  1000 moves but doesn't overcome friction in tool joints
#define TOOL_ROT_MAX_DAC   6000//3000  // 10000   These are set really low for safety sake
#define WRIST_MAX_DAC      2700//1900  // 20000
#define GRASP1_MAX_DAC     4800//2400  // 15000
#define GRASP2_MAX_DAC     4800//2400


#endif


#define SHOULDER_MAX_ANGLE   0.0
#define ELBOW_MAX_ANGLE      3*M_PI/4 + (2.5*M_PI/180)



#define SHOULDER_HOME_ANGLE   M_PI/6
#define ELBOW_HOME_ANGLE      M_PI/2
#define Z_INS_HOME_ANGLE      0.4
#define TOOL_ROT_HOME_ANGLE   0
#define WRIST_HOME_ANGLE      0
#define GRASP1_HOME_ANGLE     M_PI/4
#define GRASP2_HOME_ANGLE     M_PI/4


#define MICRON_PER_M      1000000.0
#define MICRORADS_PER_RAD 1000000.0

#define PI           ((float)3.1415926535)
#define ZERO_THRESHOLD ((float)0.000001)

//Time Defines
#define ONE_MS       ((float)0.001)
#define STEP_PERIOD  ONE_MS
#define SECOND       1000

//Speed Limits
#define V_MAX        ((float)3.0) /* rad/s   */
#define A_MAX        ((float)1.0) /* rad/s^2 */

//Grasping Defines
#define GRASP_OPEN   1
#define GRASP_CLOSE  0

//Footpedal states
#define PEDAL_UP 0
#define PEDAL_DN 1

//Watchdog timer Period
#define WD_PERIOD      50

//Master connection timeout (time to trigger pedal up)
#define MASTER_CONN_TIMEOUT 5000


#endif
