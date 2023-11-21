#include <Wire.h>
#include "QGPMaker_MotorShield.h"
#include "QGPMaker_Encoder.h"

// Create the motor shield object with the default I2C address
QGPMaker_MotorShield AFMS = QGPMaker_MotorShield();

// Select which 'port' M1, M2, M3 or M4. In this case, M3
QGPMaker_DCMotor *DCMotor_1 = AFMS.getMotor(1);
QGPMaker_DCMotor *DCMotor_2 = AFMS.getMotor(2);
QGPMaker_DCMotor *DCMotor_3 = AFMS.getMotor(3);
QGPMaker_DCMotor *DCMotor_4 = AFMS.getMotor(4);

// encoder
QGPMaker_Encoder encoder1(1);
QGPMaker_Encoder encoder2(2);
QGPMaker_Encoder encoder3(3);
QGPMaker_Encoder encoder4(4);

// speed : 0 ~ 255
int speed = 100;

void forward(int speed) { 
  DCMotor_1->setSpeed(speed);
  DCMotor_1->run(FORWARD);
  DCMotor_2->setSpeed(speed);
  DCMotor_2->run(FORWARD);
  DCMotor_3->setSpeed(speed);
  DCMotor_3->run(FORWARD);
  DCMotor_4->setSpeed(speed);
  DCMotor_4->run(FORWARD);
}
void setup(){
  AFMS.begin(50); // create with the default frequency 50Hz
  forward(speed);
}

void loop(){
  int en1_rpm = Encoder1.getRPM();
  int en2_rpm = Encoder2.getRPM();
  int en3_rpm = Encoder3.getRPM();
  int en4_rpm = Encoder4.getRPM();
}