/******************************************************************
   Super amazing BT controller Arduino Library v1.8
      http://www.7gp.cn



  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or(at your option) any later version.
  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.
  <http://www.gnu.org/licenses/>

******************************************************************/

#ifndef WFJoystick_h
#define WFJoystick_h
#define LOG(...) printf(__VA_ARGS__)
#include "Arduino.h"
#include <WiFi.h>
#include "PubSubClient.h"
/*
9 	8	  7 6	5	4	3	2	1	0
SW2	SW1	R	L		D	C		B	A
*/

#define BTN_A _BV(WFJoystick::nBTN_A)
#define BTN_B _BV(WFJoystick::nBTN_B)
#define BTN_MENU _BV(WFJoystick::nBTN_MENU)
#define BTN_C _BV(WFJoystick::nBTN_X)
#define BTN_D _BV(WFJoystick::nBTN_Y)
#define BTN_X _BV(WFJoystick::nBTN_X)
#define BTN_Y _BV(WFJoystick::nBTN_Y)
#define BTN_RSV1 _BV(WFJoystick::nBTN_RSV1)
#define BTN_L1 _BV(WFJoystick::nBTN_L1)
#define BTN_R1 _BV(WFJoystick::nBTN_R1)

#define BTN_SW1 _BV(WFJoystick::nBTN_L2)
#define BTN_SW2 _BV(WFJoystick::nBTN_R2)
#define BTN_L2 _BV(WFJoystick::nBTN_L2)
#define BTN_R2 _BV(WFJoystick::nBTN_R2)
#define BTN_SEL _BV(WFJoystick::nBTN_SEL)
#define BTN_START _BV(WFJoystick::nBTN_START)
#define BTN_POWER _BV(WFJoystick::nBTN_POWER)
#define BTN_LTHUMB _BV(WFJoystick::nBTN_LTHUMB)
#define BTN_RTHUMB _BV(WFJoystick::nBTN_RTHUMB)
#define BTN_RSV3 _BV(WFJoystick::nBTN_RSV3)

#define BTN_DPAD_UP _BV(WFJoystick::nBTN_DPAD_UP)
#define BTN_DPAD_RIGHT _BV(WFJoystick::nBTN_DPAD_RIGHT)
#define BTN_DPAD_DOWN _BV(WFJoystick::nBTN_DPAD_DOWN)
#define BTN_DPAD_LEFT _BV(WFJoystick::nBTN_DPAD_LEFT)

#define BTN_SHIFT_L _BV(WFJoystick::nBTN_L2)
#define BTN_SHIFT_R _BV(WFJoystick::nBTN_R2)

#define VJ_LX 0
#define VJ_LY 1
#define VJ_RX 2
#define VJ_RY 3


// ======================================== 
// Must match the receiver structure
typedef struct
{
  unsigned char commandID;
  unsigned char lenth;
} struct_message_head;


typedef struct
{
  unsigned char commandID;
  unsigned char lenth;
  unsigned char lx;
  unsigned char ly;
  unsigned char rx;
  unsigned char ry;
  unsigned char buttons[4];
} struct_message_JOYData;

// ========================================

class WFJoystick
{
private:
  struct_message_head receive_Head;
  struct_message_JOYData receive_joyData;

  WiFiClient wifiClient;
  PubSubClient mqtt_client;

  unsigned char AXISData[4]={128,128,128,128};
  uint32_t last_buttons;
  uint32_t buttons;

  String mqtt_broker;
  String mqtt_username;
  String mqtt_password;
  uint16_t mqtt_port;

  String mqtt_topic;
  String mqtt_data;
  boolean mqtt_status;
  String project;

  String mqtt_topic_pub;

public:
  enum
  {
    nBTN_A = 0,
    nBTN_B,
    nBTN_MENU,
    nBTN_X,
    nBTN_Y,
    nBTN_RSV1,
    nBTN_L1,
    nBTN_R1,

    nBTN_L2 = 8,
    nBTN_R2,
    nBTN_SEL,
    nBTN_START,
    nBTN_POWER,
    nBTN_LTHUMB,
    nBTN_RTHUMB,
    nBTN_RSV3,

    nBTN_DPAD_UP = 16,
    nBTN_DPAD_RIGHT,
    nBTN_DPAD_DOWN,
    nBTN_DPAD_LEFT
  } BTN_T;

  WFJoystick(String mqtt_broker, int mqtt_port, String mqtt_username, String mqtt_password,String uid);

  void begin();
  // void loop();
  void readCommand();

  boolean isEnabled();

  /****************************************************************************************/
  boolean NewButtonState();

  /****************************************************************************************/
  boolean NewButtonState(uint32_t button);

  /****************************************************************************************/
  boolean ButtonPressed(uint32_t button);

  /****************************************************************************************/
  boolean ButtonReleased(uint32_t button);

  /****************************************************************************************/
  boolean Button(uint32_t button);

  /****************************************************************************************/
  uint32_t ButtonDataByte();

  /****************************************************************************************/
  byte Analog(byte button);

  void reConnect();

protected:
  void cbMQTT(char *topic, byte *payload, unsigned int length);
};

#endif
