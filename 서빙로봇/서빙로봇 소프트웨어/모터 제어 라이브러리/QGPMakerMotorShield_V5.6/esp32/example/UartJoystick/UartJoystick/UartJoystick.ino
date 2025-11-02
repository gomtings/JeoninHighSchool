/**接收串口遥控数据
  格式：2个字节校验符
  4个2字节电机速度数据
  4个1字节舵机角度数据*/
#include <Wire.h>
#include "QGPMaker_MotorShield.h"

QGPMaker_MotorShield AFMS = QGPMaker_MotorShield();

QGPMaker_Servo *Servo1 = AFMS.getServo(0);
QGPMaker_Servo *Servo2 = AFMS.getServo(1);
QGPMaker_Servo *Servo3 = AFMS.getServo(2);
QGPMaker_Servo *Servo4 = AFMS.getServo(3);
QGPMaker_DCMotor *DCMotor_2 = AFMS.getMotor(2);
QGPMaker_DCMotor *DCMotor_4 = AFMS.getMotor(4);
QGPMaker_DCMotor *DCMotor_1 = AFMS.getMotor(1);
QGPMaker_DCMotor *DCMotor_3 = AFMS.getMotor(3);

void moveMotor(int motor1Spd, int motor2Spd, int motor3Spd, int motor4Spd)
{
  if(motor1Spd >= 0)
    DCMotor_1->run(FORWARD);
  else
    DCMotor_1->run(BACKWARD);
  DCMotor_1->setSpeed(motor1Spd);

  if(motor2Spd >= 0)
    DCMotor_2->run(FORWARD);
  else
    DCMotor_2->run(BACKWARD);
  DCMotor_2->setSpeed(motor2Spd);

  if(motor3Spd >= 0)
    DCMotor_3->run(FORWARD);
  else
    DCMotor_3->run(BACKWARD);
  DCMotor_3->setSpeed(motor3Spd);

  if(motor4Spd >= 0)
    DCMotor_4->run(FORWARD);
  else
    DCMotor_4->run(BACKWARD);
  DCMotor_4->setSpeed(motor4Spd);
}

void rotateServo(int sev1Angle, int sev2Angle, int sev3Angle, int sev4Angle)
{
  if(sev1Angle >=0 && sev1Angle <= 180){
    if (Servo1->readDegrees() > sev1Angle) {
      Servo1->writeServo((Servo1->readDegrees() - 1));
    }else if (Servo1->readDegrees() < sev1Angle) {
      Servo1->writeServo((Servo1->readDegrees() + 1));
    }
  }

  if(sev2Angle >=0 && sev2Angle <= 180){
    if (Servo2->readDegrees() > sev2Angle) {
      Servo2->writeServo((Servo2->readDegrees() - 1));
    }else if (Servo2->readDegrees() < sev2Angle) {
      Servo2->writeServo((Servo2->readDegrees() + 1));
    }
  }

   if(sev3Angle >=0 && sev3Angle <= 180){
    if (Servo3->readDegrees() > sev3Angle) {
      Servo3->writeServo((Servo3->readDegrees() - 1));
    }else if (Servo3->readDegrees() < sev3Angle) {
      Servo3->writeServo((Servo3->readDegrees() + 1));
    }
  }

   if(sev4Angle >=0 && sev4Angle <= 180){
    if (Servo4->readDegrees() > sev4Angle) {
      Servo4->writeServo((Servo4->readDegrees() - 1));
    }else if (Servo4->readDegrees() < sev4Angle) {
      Servo4->writeServo((Servo4->readDegrees() + 1));
    }
  }
  
}

void setup() 
{
  AFMS.begin(50);
  Serial.begin(115200);

  Servo1->writeServo(90);
  Servo2->writeServo(90);
  Servo3->writeServo(90);
  Servo4->writeServo(60);
}

void loop() 
{
  if (Serial.available() >= 14) 
  { 
    // 读取前两个字节作为校验符号  
    byte checksum1 = Serial.read();  
    byte checksum2 = Serial.read();  
  
    // 检查校验符号是否为1, 255  
    if (checksum1 == 1 && checksum2 == 255) 
    {  
      //读取4个电机的速度,占2个字节，取值范围-255至255
      byte intByte1 = Serial.read();  
      byte intByte2 = Serial.read();  
      int16_t motor1 = (intByte1 << 8) | intByte2;  
      intByte1 = Serial.read();  
      intByte2 = Serial.read();  
      int16_t motor2 = (intByte1 << 8) | intByte2;  
      intByte1 = Serial.read();  
      intByte2 = Serial.read();  
      int16_t motor3 = (intByte1 << 8) | intByte2;  
      intByte1 = Serial.read();  
      intByte2 = Serial.read();  
      int16_t motor4 = (intByte1 << 8) | intByte2;  
  
      // 读取4个舵机的角度，占1个字节，取值范围：0-180
      byte svo1 = Serial.read();  
      byte svo2 = Serial.read();  
      byte svo3 = Serial.read();  
      byte svo4 = Serial.read();  

      moveMotor(motor1, motor2, motor3, motor4);
      rotateServo(svo1, svo2, svo3, svo4);

      // 打印出来（串口输出） 
      Serial.print(motor1);  
      Serial.print(",");  Serial.print(motor2);  
      Serial.print(",");  Serial.print(motor3);  
      Serial.print(",");  Serial.print(motor4);  
      Serial.print(",");  Serial.print(svo1);  
      Serial.print(",");  Serial.print(svo2);  
      Serial.print(",");  Serial.print(svo3);  
      Serial.print(",");  Serial.println(svo4);  
    } else {  
      Serial.print("校验码错误:");  
      Serial.print(checksum1); Serial.print(","); Serial.println(checksum2);
    }  
  }  

}
