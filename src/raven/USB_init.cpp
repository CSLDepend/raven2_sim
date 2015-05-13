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


/**\file USB_init.cpp
 * \brief USB initialization module
 * \author Ken Fodero
 * \author Hawkeye King
 * \ingroup IO
 */

#include <string.h>
#include <vector>
#include <map>
#include <dirent.h>
#include <iostream>
#include <stdio.h>
#include <ros/console.h>

#include "USB_init.h"
#include "parallel.h"

//Four device files for connection to four boards
#define BRL_USB_DEV_DIR     "/dev/"
#define BOARD_FILE_STR      "brl_usb"   /// Device file. xx is the place holder of the serial number. restricted to 2 digits for now
#define NUM_BOARDS 99
#define BOARD_FILE_STR_LEN sizeof(BOARD_FILE_STR)
#define BRL_RESET_BOARD     10
#define BRL_START_READ      4

// Keep board information
std::vector<int> boardFile;
std::map<int,int> boardFPs;

extern USBStruct USBBoards;
extern int NUM_MECH;

using namespace std;

#ifdef skip_init_button
int openSerialPort(void)
{
    int serialFileDescriptor = -1;
    struct termios options;
    // open the serial like POSIX C
    serialFileDescriptor = open("/dev/ttyACM0", O_RDWR | O_NOCTTY | O_NONBLOCK );

    if (serialFileDescriptor == -1)
    {
        cout << "Error opening serial port" << endl;
    	return -1;
    }

    // block non-root users from using this port
    if (ioctl(serialFileDescriptor, TIOCEXCL) == -1)
    {    
	cout << "Error setting TIOCEXCL" << endl;
    	return -1;
    }
    
    // clear the O_NONBLOCK flag, so that read() will
    //   block and wait for data.
    if (fcntl(serialFileDescriptor, F_SETFL, 0) == -1)
    {
        cout << "Error Clearing O_NONBLOCK" << endl;
    	return -1;
    }

    //int iFlags = TIOCM_DTR;
    //ioctl(serialFileDescriptor, TIOCMBIC, &iFlags);

    // grab the options for the serial port
    if (tcgetattr(serialFileDescriptor, &gOriginalTTYAttrs) == -1)
    {
        cout << "Error getting tty attributes" << endl;
    	return -1;
    }

    // setting raw-mode allows the use of tcsetattr() and ioctl()
    options = gOriginalTTYAttrs;
    cfmakeraw(&options);
    options.c_cc[VMIN] = 0;
    options.c_cc[VTIME] = 10;

    // specify any arbitrary baud rate
    speed_t baudRate = 9600;
    cfsetospeed(&options, B9600);
    /*if (ioctl(serialFileDescriptor, IOSSIOSPEED, &baudRate) ==1)
    {
        cout << "Error calling ioctl" << endl;
    	return -1;
    }*/

    //cout << "Opened connection to Arduino" << endl;
    return serialFileDescriptor;
}

int writeSerialPort(int serialFileDescriptor, void *buffer)
{
    ssize_t numBytes;
    numBytes = write(serialFileDescriptor, buffer, sizeof(buffer));
    //cout << "Wrote " << numBytes << " bytes to Arduino" << endl;
    cout << "Sent the start signal through Arduino.."<< endl;
    return numBytes;
}

void closeSerialPort(int serialFileDescriptor)
{
    if (tcdrain(serialFileDescriptor) == -1) {
       cout<< "Error waiting for drain" << endl;
    }
  
    // Traditionally it is good practice to reset a serial port back to
    // the state in which you found it. This is why the original termios struct
    // was saved.
    gOriginalTTYAttrs.c_cflag &= ~HUPCL; // disable hang-up-on-close to avoid reset
    if (tcsetattr(serialFileDescriptor, TCSANOW, &gOriginalTTYAttrs) == -1) {
        cout << "Error resetting tty attributes"<< endl;
    }

    close(serialFileDescriptor);
    //cout << "Closed connection to Arduino" << endl;
}
#endif
/**\fn int getdir(string dir, vector<string> &files)
 * \brief List directory contents matching BOARD_FILE_STR
 * \param dir - directory name of interest
 * \param &files - adress to write list of files in dir
 * \return 0 on success, error otherwise
 *  \ingroup IO
 */
int getdir(string dir, vector<string> &files)
{
    DIR *dp;
    struct dirent *dirp;

    if((dp  = opendir(dir.c_str())) == NULL) {
        cout << "Error(" << errno << ") opening " << dir << endl;
        return errno;
    }

    while ((dirp = readdir(dp)) != NULL) {
        if ( strstr(dirp->d_name, BOARD_FILE_STR) ){
            files.push_back(string(dirp->d_name));
        }
    }
    closedir(dp);
    return 0;
}


/**\fn int get_board_id_from_filename(string s)
 * \brief Gets the board ID number related to the file of interest
 * \param s - filename
 * \return board ID number
 * \ingroup IO
 */
int get_board_id_from_filename(string s)
{
    string tmp = s.substr(7,s.length()-7);
    return atoi(tmp.c_str());
}


/**\fn int write_zeros_to_board(int boardid)
 * \brief
 * \param boardid -
 * \return 0 on success,
 */
int write_zeros_to_board(int boardid)
{
    short int tmp = DAC_OFFSET;
    unsigned char buffer_out[MAX_OUT_LENGTH];

    buffer_out[0]= DAC;        //Type of USB packet
    buffer_out[1]= MAX_DOF_PER_MECH; //Number of DAC channels
    for(int i = 0; i < MAX_DOF_PER_MECH; i++) {
        buffer_out[2*i+2] = (char)tmp;
        buffer_out[2*i+3] = (char)tmp>>8;
    }
    buffer_out[OUT_LENGTH-1] = 0x00;

    //Write the packet to the USB Driver
    if(usb_write(boardid, &buffer_out, OUT_LENGTH )!= OUT_LENGTH){
        return -USB_WRITE_ERROR;
    }

    return 0;

}


 /**\fn int USBInit(struct device *device0)
 * \brief initialize the USB modules
 * \struct device
 * \param device0 - pointer to device struct
 * \return 0 if no USB board found, USB_INIT_ERROR if error was encountered, or # of boards if initialized successfully
 * \ingroup IO
 */
int USBInit(struct device *device0)
{
  //DELETEME    char buf[10]; //buffer to be used for clearing usb read buffers
    string boardStr;
    int boardid = 0;
    int okboards = 0;

    // Get list of files in dev dir
    vector<string> files = vector<string>();
    getdir(BRL_USB_DEV_DIR, files);
	sort(files.begin(), files.end());
reverse(files.begin(),files.end());

    log_msg("  Found board files::");
    for (unsigned int i = 0;i < files.size();i++) {
        log_msg("    %s", files[i].c_str());
    }

    //Initialize all active USB Boards
    //Open and reset available boards
    USBBoards.activeAtStart=0;
	int mechcounter = 0; // HACKHACKHACK
    for (uint i=0;i<files.size();i++)
    {
        boardStr = BRL_USB_DEV_DIR;
        boardStr += files[i];
        boardid = get_board_id_from_filename(files[i]);
		if((boardid == GREEN_ARM_SERIAL) || (boardid == GOLD_ARM_SERIAL ))
		{
	
	        // Open usb dev
	        int tmp_fileHandle = open(boardStr.c_str(), O_RDWR|O_NONBLOCK);    //Is NONBLOCK mode required??// open board chardev
	
	
	        if (tmp_fileHandle <=0 )
	        {
	            perror("ERROR: couldn't open board");
	            errno=0;
	            continue; //Failed to open board, move to next one
	        }
	
	        // Setup usb dev.  ioctl() performs an initialization in driver.
	        if ( ioctl(tmp_fileHandle, BRL_RESET_BOARD) != 0)
	        {
	            ROS_ERROR("ERROR: ioctl error opening board %s", boardStr.c_str());
	            errno = 0;
	        }
	
	        device0->mech[i].type = 0;
	        // Set mechanism type Green or Gold surgical robot
	        if (boardid == GREEN_ARM_SERIAL)
	        {
	            okboards++;
	            log_msg("  Green Arm on board #%d.",boardid);
	            device0->mech[mechcounter].type = GREEN_ARM;
				mechcounter++;
	        }
	        else if (boardid == GOLD_ARM_SERIAL)
	        {
	            okboards++;
	            log_msg("  Gold Arm on board #%d.",boardid);
	            device0->mech[mechcounter].type = GOLD_ARM;
				mechcounter++;
	        }
	        else
	        {
	            log_msg("*** WARNING: USB BOARD #%d NOT CONNECTED TO MECH (update defines?).",boardid);
	        }
	
	        // Store usb dev parameters
	        boardFile.push_back(tmp_fileHandle);  // Store file handle
	        USBBoards.boards.push_back(boardid);  // Store board array index
	        boardFPs[boardid] = tmp_fileHandle;   // Map serial (i) to fileHandle (tmp_fileHandle)
	        USBBoards.activeAtStart++;            // Increment board count
	
	        log_msg("board FPs ---> %i", boardFPs[boardid]);
	
	
	        if ( write_zeros_to_board(boardid) != 0){
	            ROS_ERROR("Warning: failed initial board reset (set-to-zero)");
       		 }
		}
    }

    if (okboards < 2){
        ROS_ERROR("Error: failed to init two boards!  Behavior is henceforce undetermined...");
//        return 0;
    }
    //Only now we have info about number of boards and set it to number of mechanisms
    NUM_MECH = USBBoards.activeAtStart;

    return USBBoards.activeAtStart;
}


 /**\fn void USBShutdown(void)
 * \brief shutsdown the USB modules, setting DAC outputs to zero before shutting down
 * \return void
 * \ingroup IO
 */
void USBShutdown(void)
{
    uint i;

    //Reset USB driver
    for (i=0;i<boardFile.size();i++)
    {
        if (boardFile[i]) //Shutdown configured boards
        {
            if ( ioctl(boardFile[i], BRL_RESET_BOARD) != 0)
            {
                perror("ioctl error in shutdown.");
                errno = 0;
                continue; //Failed to reset board. Move to next one
            }
        }
        close(boardFile[i]);                    // Close device
        boardFile[i]=0;
    }
}


 /**\fn int startUSBRead(int id)
 * \brief initialize data retrieval from a USB board. Must be run before usb_read
 * \param id - serial number of board of interest
 * \return
 * \ingroup IO
 */
int startUSBRead(int id)
{
	// Initiate read
  int ret = ioctl(boardFPs[id], BRL_START_READ, MAX_IN_LENGTH);

  if (ret < 0 )
    {
      ret = -errno;
    }
  return ret;
}


/**\fn int usb_read(int id, void *buffer, size_t len)
 * \brief read from usb board with serial number id
 * \param id - serial number of board to read
 * \param buffer - pointer to buffer to read into
 * \param len - length to read
 * \return
 * \ingroup IO
 */
int usb_read(int id, void *buffer, size_t len)
{
  int fp = boardFPs[id]; // file pointer
  int ret = read(fp, buffer, len);
  if (ret<0)
    {
      ret = -errno;
    }
  return ret;
}


/**\fn int usb_write(int id, void *buffer, size_t len)
 * \brief write to usb board with serial number id
 * \param id - serial number of board to write
 * \param buffer - pointer to buffer to write into
 * \param len - length to write
 * \return
 * \ingroup IO
 */
int usb_write(int id, void *buffer, size_t len)
{
    // write to board
    int ret = write(boardFPs[id], buffer, len);

    if (ret < 0)
      ret = -errno;
    return ret;
}


 /**\fn int usb_reset_encoders(int boardid)
 * \brief reset the encoder chips on the board
 * \param boardid - serial number of board to reset
 * \return 0
 * \ingroup IO
 */
int usb_reset_encoders(int boardid)
{
    log_msg("Resetting encoders on board %d", boardid);

    int fp = boardFPs[boardid]; // get file pointer from serial number
    //const size_t USB_MAX_OUT_LEN = 512;
    const size_t bufsize = OUT_LENGTH;
    const char reset_byte = 0x07;
    char buf[bufsize];

    memset(buf, reset_byte, bufsize);

    write(fp,buf,bufsize); //Clear buffers
    ioctl(fp, BRL_START_READ, MAX_IN_LENGTH);
    read(fp,buf,bufsize); //Clear buffers
    return 0;
}
