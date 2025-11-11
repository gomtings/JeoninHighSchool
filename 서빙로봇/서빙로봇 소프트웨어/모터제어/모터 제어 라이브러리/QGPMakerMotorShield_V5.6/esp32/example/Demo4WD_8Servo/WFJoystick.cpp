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

#include "WFJoystick.h"
using namespace std::placeholders;
void WFJoystick::begin()
{
  IPAddress ip(121,89,198,103); 
  ip.fromString(mqtt_broker);
  mqtt_client.setServer(ip, mqtt_port);
  mqtt_client.setCallback(std::bind(&WFJoystick::cbMQTT, this, _1, _2, _3));
  
}

WFJoystick::WFJoystick(String mqtt_broker, int mqtt_port, String mqtt_username, String mqtt_password,String uid) : mqtt_client(wifiClient)
{
  this->mqtt_broker = mqtt_broker;
  this->mqtt_port = mqtt_port;
  this->mqtt_username = mqtt_username;
  this->mqtt_password = mqtt_password;
  this->mqtt_topic = String("evtopic/wfjy/"+uid); //evtopic/wfjy/MAC
  this->mqtt_topic_pub =String("evtopic/wfjy/"+uid+"/pub");
}

/****************************************************************************************/
boolean WFJoystick::NewButtonState()
{
    return ((last_buttons ^ buttons) > 0);
}

/****************************************************************************************/
boolean WFJoystick::NewButtonState(uint32_t button)
{
    return (((last_buttons ^ buttons) & button) > 0);
}

/****************************************************************************************/
boolean WFJoystick::ButtonPressed(uint32_t button)
{
    return (NewButtonState(button) & Button(button));
}

/****************************************************************************************/
boolean WFJoystick::ButtonReleased(uint32_t button)
{
    return ((NewButtonState(button)) & ((last_buttons & button) > 0));
}

/****************************************************************************************/
boolean WFJoystick::Button(uint32_t button)
{
    // LOG("BTN:%d %d \n", buttons, button);
    return ((buttons & button) > 0);
}

/****************************************************************************************/
uint32_t WFJoystick::ButtonDataByte()
{
    return (buttons);
}

/****************************************************************************************/
byte WFJoystick::Analog(byte button)
{
    return AXISData[button];
}

// void WFJoystick::loop()
// {
// }



void WFJoystick::reConnect()
{
  
  if (!mqtt_client.connected())
  {
    while (!mqtt_client.connected())
    {
      String client_id = "esp-client-";
      client_id += String(WiFi.macAddress());
      Serial.printf("The client %s connects to the public mqtt broker\n", client_id.c_str());

      if (mqtt_client.connect(client_id.c_str(), mqtt_username.c_str(), mqtt_password.c_str()))
      {
        Serial.println("connected");
        // subTopicCenterFlag = true;
        mqtt_client.subscribe(mqtt_topic.c_str());
        // mqtt_client.publish(mqtt_topic_pub.c_str(), "live");
      }
      else
      {
        Serial.print("failed, rc=");
        Serial.print(mqtt_client.state());
        Serial.println(" try again in 1 seconds");
        if (!WiFi.isConnected())
        {
          WiFi.begin();
        }
        delay(1000);
      }
    }
  }
}

void WFJoystick::readCommand()
{
  reConnect();
  mqtt_client.loop();
}

boolean WFJoystick::isEnabled()
{
  return true;
}


void WFJoystick::cbMQTT(char *topic, byte *payload, unsigned int length){
  memset(&receive_Head, 0, sizeof(receive_Head));
  memcpy(&receive_Head, payload, 2); //--> Copy the information in the "incomingData" variable into the "receive_Data" structure variable.
  // ----------------------------------------
  if (receive_Head.commandID == 0x01)
  {
    Serial.println("l:0x01");
    // prev_cmd_time = millis();
    uint32_t btn = 0;
    memset(&receive_joyData, 0, sizeof(receive_joyData));
    memcpy(&receive_joyData, payload, 10);
    btn = (uint32_t)(int(receive_joyData.buttons[2]) << 16 | int(receive_joyData.buttons[1] << 8) | receive_joyData.buttons[0]);
    AXISData[0]=receive_joyData.lx;
    AXISData[1]=receive_joyData.ly;
    AXISData[2]=receive_joyData.rx;
    AXISData[3]=receive_joyData.ry;
    last_buttons=buttons;
    buttons = btn;
    // _cmdHandler.onStickChanged(receive_joyData.lx, (int)receive_joyData.ly, (int)receive_joyData.rx, (int)receive_joyData.ry, 0, 0, btn);
  }else if (receive_Head.commandID == 0x02)
  {
    Serial.print("live-->");
    mqtt_client.publish(mqtt_topic_pub.c_str(),(const char*)payload);
    Serial.print("finish!");
  }
}