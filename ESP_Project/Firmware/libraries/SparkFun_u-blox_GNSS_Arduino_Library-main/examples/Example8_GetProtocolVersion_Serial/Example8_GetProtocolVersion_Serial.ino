/*
  Reading the protocol version of a u-blox module
  By: Nathan Seidle
  SparkFun Electronics
  Date: January 3rd, 2019
  License: MIT. See license file for more information but you can
  basically do whatever you want with this code.

  This example shows how to query a u-blox module for its protocol version.

  Note: this may fail on boards like the UNO (ATmega328P) with modules like the ZED-F9P
        because getProtocolVersion returns a lot of data - more than the UNO's serial buffer can hold

  Various modules have various protocol version. We've seen v18 up to v27. Depending
  on the protocol version there are different commands available. This is a handy
  way to predict which commands will or won't work.

  Leave NMEA parsing behind. Now you can simply ask the module for the datums you want!

  Feel like supporting open source hardware?
  Buy a board from SparkFun!
  ZED-F9P RTK2: https://www.sparkfun.com/products/15136
  NEO-M8P RTK: https://www.sparkfun.com/products/15005
  SAM-M8Q: https://www.sparkfun.com/products/15106

  Hardware Connections:
  Plug a Qwiic cable into the GNSS and a BlackBoard
  If you don't have a platform with a Qwiic connection use the SparkFun Qwiic Breadboard Jumper (https://www.sparkfun.com/products/14425)
  Open the serial monitor at 115200 baud to see the output
*/

#include <SoftwareSerial.h>

//#define mySerial Serial1 // Uncomment this line to connect via Serial1
// - or -
//SoftwareSerial mySerial(10, 11); // Uncomment this line to connect via SoftwareSerial(RX, TX). Connect pin 10 to GNSS TX pin.
// - or -
#define mySerial Serial // Uncomment this line if you just want to keep using Serial

#include <SparkFun_u-blox_GNSS_Arduino_Library.h> //http://librarymanager/All#SparkFun_u-blox_GNSS
SFE_UBLOX_GNSS myGNSS;

long lastTime = 0; //Simple local timer. Limits amount if I2C traffic to u-blox module.

void setup()
{
  Serial.begin(115200);
  while (!Serial); //Wait for user to open terminal
  Serial.println("SparkFun u-blox Example");

  Serial.println("Trying 38400 baud");
  mySerial.begin(38400);
  if (myGNSS.begin(mySerial))
  {
    Serial.println("GNSS connected at 38400 baud");
  }
  else
  {
    Serial.println("Trying 9600 baud");
    mySerial.begin(9600);
    if (myGNSS.begin(mySerial))
    {
      Serial.println("GNSS connected at 9600 baud");
    }
    else
    {
      Serial.println("Could not connect to GNSS. Freezing...");
      while(1); // Do nothing more
    }
  }

  Serial.print(F("Version: "));
  byte versionHigh = myGNSS.getProtocolVersionHigh();
  Serial.print(versionHigh);
  Serial.print(".");
  byte versionLow = myGNSS.getProtocolVersionLow();
  Serial.print(versionLow);
}

void loop()
{
  //Do nothing
}
