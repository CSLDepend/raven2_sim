//  RelayShieldDemoCode.pde  to control seeed relay shield by arduino.
//  Copyright (c) 2010 seeed technology inc.
//  Author: Steve Chang
//  Version: september 2, 2010
//
//  This library is free software; you can redistribute it and/or
//  modify it under the terms of the GNU Lesser General Public
//  License as published by the Free Software Foundation; either
//  version 2.1 of the License, or (at your option) any later version.
//
//  This library is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
//  Lesser General Public License for more details.
//
//  You should have received a copy of the GNU Lesser General Public
//  License along with this library; if not, write to the Free Software
//  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

unsigned char relayPin[4] = {4,5,6,7};
int relayNum = 3;
String inputString = "";         // a string to hold incoming data
boolean stringComplete = false;  // whether the string is complete

void(*resetFunc)(void)=0;

void setup()
{
  // initialize serial communication at 9600 bits per second:
  Serial.begin(9600);
  // Relay Pin for resetting PLC
  pinMode(relayPin[relayNum],OUTPUT);  
}

void loop() {
  // print the string when a newline arrives:
  if (inputString == "1")
  {    
    //Serial.println("Send Start Signal..");
    digitalWrite(relayPin[relayNum],HIGH);
    delay(1000);
    digitalWrite(relayPin[relayNum],LOW);
    delay(1000);     
  }  
  // clear the string:
  inputString = "";
}

// Wait for the start signal sent by the code, then send it
void serialEvent() {
  while (Serial.available()) {
    // get the new byte:
    inputString += (char)Serial.read();
    //Serial.println(inputString);   
  }
}

