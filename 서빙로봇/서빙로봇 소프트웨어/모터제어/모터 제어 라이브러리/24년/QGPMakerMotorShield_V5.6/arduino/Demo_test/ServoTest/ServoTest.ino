
#include <Wire.h>
#include "QGPMaker_MotorShield.h"

QGPMaker_MotorShield AFMS = QGPMaker_MotorShield(); //创建驱动器对象
QGPMaker_Servo *Servo3 = AFMS.getServo(3); //获取3号舵机



void setup() {
  Serial.begin(9600);           // set up Serial library at 9600 bps
  Serial.println("DC Motor test!");

  AFMS.begin(50);
  
}

void loop() {
  Servo3->writeServo(10); //3#舵机转到10度位置
  delay(1000);
  Servo3->writeServo(120); //3#舵机转到120度位置
  delay(1000);

  int deg=Servo3->readDegrees();//读取3#舵机当前角度
  Serial.println(deg);

}
