/******************************************************************************
  KiKuPILineFollow.h
  KiKuPI Line Follow Sensor Library Source File
  Creation Date: 2024-07-12
  @ 7gp.cn
******************************************************************************/

#include "Arduino.h"
#include <Wire.h>
#include "sx1508.h"

#ifndef KIKUPILINEFOLLOW_H
#define KIKUPILINEFOLLOW_H

#define SX1508_ADDRESS 0x20  // I2C address

#define LINESENSOR1 0  // line follow sensor 1
#define LINESENSOR2 1  // line follow sensor 2
#define LINESENSOR3 2  // line follow sensor 3
#define LINESENSOR4 3  // line follow sensor 4
#define LINESENSOR5 4  // line follow sensor 5
#define LINESENSOR6 5  // line follow sensor 6
#define LINESENSOR7 6  // line follow sensor 7
#define LINESENSOREN 7  // line follow sensor enable pin

class KKPLINEFOLLOW
{
  public:
    KKPLINEFOLLOW(uint8_t address = SX1508_ADDRESS);
    uint8_t begin(uint8_t address = SX1508_ADDRESS);
    uint8_t readSensor(uint8_t numSensor);       //读取传感器值
    void disableSensor();      //禁用传感器
    void enableSensor();       //使能传感器
    void analogWrite(uint8_t numSensor, uint8_t value);    //扩展端口模拟输出
  private:
    SX1508 _sx1508;
};


KKPLINEFOLLOW::KKPLINEFOLLOW(uint8_t address) {}

//初始化传感器
uint8_t KKPLINEFOLLOW::begin(uint8_t address) {
  // Wire.begin(18,19); //esp32
  Wire.begin();
  return  _sx1508.begin(address);
}

//读取传感器值
// numSensor : 0 1 2 3 4  ; 5路巡线传感器
uint8_t KKPLINEFOLLOW::readSensor(uint8_t numSensor) {
  return _sx1508.digitalRead(numSensor);
}

//禁用传感器
void KKPLINEFOLLOW::disableSensor() {
  _sx1508.pinMode(LINESENSOREN, OUTPUT);
  _sx1508.digitalWrite(LINESENSOREN, HIGH);
}

//使能传感器
void KKPLINEFOLLOW::enableSensor() {
  _sx1508.pinMode(LINESENSOREN, OUTPUT);
  _sx1508.digitalWrite(LINESENSOREN, LOW);
  
}

void KKPLINEFOLLOW::analogWrite(uint8_t numSensor, uint8_t value){
  _sx1508.pinMode(numSensor, ANALOG_OUTPUT);
  _sx1508.analogWrite(numSensor, value);
}

#endif
