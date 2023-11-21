// 이동 함수 제작, 30cm 앞의 장애물 발견 시 정

#include <Wire.h>
#include "QGPMaker_MotorShield.h"

// Create the motor shield object with the default I2C address
QGPMaker_MotorShield AFMS = QGPMaker_MotorShield();

// Select which 'port' M1, M2, M3 or M4. In this case, M3
QGPMaker_DCMotor *DCMotor_1 = AFMS.getMotor(1);
QGPMaker_DCMotor *DCMotor_2 = AFMS.getMotor(2);
QGPMaker_DCMotor *DCMotor_3 = AFMS.getMotor(3);
QGPMaker_DCMotor *DCMotor_4 = AFMS.getMotor(4);

const int trigPin = 12;
const int echoPin = 13;

long duration;
int distance;

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
void backward(int speed) { 
  DCMotor_1->setSpeed(speed);
  DCMotor_1->run(BACKWARD);
  DCMotor_2->setSpeed(speed);
  DCMotor_2->run(BACKWARD);
  DCMotor_3->setSpeed(speed);
  DCMotor_3->run(BACKWARD);
  DCMotor_4->setSpeed(speed);
  DCMotor_4->run(BACKWARD);
}
void move_left(int speed) { 
  DCMotor_1->setSpeed(speed);
  DCMotor_1->run(BACKWARD);
  DCMotor_2->setSpeed(speed);
  DCMotor_2->run(FORWARD);
  DCMotor_3->setSpeed(speed);
  DCMotor_3->run(BACKWARD);
  DCMotor_4->setSpeed(speed);
  DCMotor_4->run(FORWARD);
}
void move_right(int speed) { 
  DCMotor_1->setSpeed(speed);
  DCMotor_1->run(FORWARD);
  DCMotor_2->setSpeed(speed);
  DCMotor_2->run(BACKWARD);
  DCMotor_3->setSpeed(speed);
  DCMotor_3->run(FORWARD);
  DCMotor_4->setSpeed(speed);
  DCMotor_4->run(BACKWARD);
}
void turn_left(int speed) { 
  DCMotor_1->setSpeed(speed);
  DCMotor_1->run(BACKWARD);
  DCMotor_2->setSpeed(speed);
  DCMotor_2->run(BACKWARD);
  DCMotor_3->setSpeed(speed);
  DCMotor_3->run(FORWARD);
  DCMotor_4->setSpeed(speed);
  DCMotor_4->run(FORWARD);
}
void turn_right(int speed) { 
  DCMotor_1->setSpeed(speed);
  DCMotor_1->run(FORWARD);
  DCMotor_2->setSpeed(speed);
  DCMotor_2->run(FORWARD);
  DCMotor_3->setSpeed(speed);
  DCMotor_3->run(BACKWARD);
  DCMotor_4->setSpeed(speed);
  DCMotor_4->run(BACKWARD);
}
void stop(int delay_time) {
  DCMotor_1->setSpeed(0);
  DCMotor_1->run(RELEASE);
  DCMotor_2->setSpeed(0);
  DCMotor_2->run(RELEASE);
  DCMotor_3->setSpeed(0);
  DCMotor_3->run(RELEASE);
  DCMotor_4->setSpeed(0);
  DCMotor_4->run(RELEASE);
  delay(delay_time);
}
// int get_distance(int trigPin, int echoPin) {
//   digitalWrite(trigPin, HIGH);
//   delayMicroseconds(10);
//   digitalWrite(trigPin, LOW);

//   duration = pulseIn(echoPin, HIGH);

//   // distance = duration * 0.0343 / 2;
//   distance = duration * 17 / 1000; 

//   return distance;
// }

void setup(){
  Serial.begin(9600);
  AFMS.begin(50); // create with the default frequency 50Hz

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  
  forward(50);
}

void loop(){
  // distance = get_distance(trigPin, echoPin);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  duration = pulseIn(echoPin, HIGH);

  // distance = duration * 0.0343 / 2;
  distance = duration * 17 / 1000; 

  // Serial.println(distance);
  delay(100);
  if (distance <= 30) {
    stop(100);
  }
  else {
    forward(50);
  }
}
// 타이머 통해서 제어 추가