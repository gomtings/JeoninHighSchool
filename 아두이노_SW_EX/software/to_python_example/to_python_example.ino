#include <Wire.h>
#include "QGPMaker_MotorShield.h"

QGPMaker_MotorShield AFMS = QGPMaker_MotorShield();

QGPMaker_DCMotor *DCMotor_1 = AFMS.getMotor(1);
QGPMaker_DCMotor *DCMotor_2 = AFMS.getMotor(2);
QGPMaker_DCMotor *DCMotor_3 = AFMS.getMotor(3);
QGPMaker_DCMotor *DCMotor_4 = AFMS.getMotor(4);

// 초음파 센서 핀 설정
const int trigPin = 12;
const int echoPin = 13;

char cmd;

long duration;
int distance;

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


void setup() {
  Serial.begin(9600);

  AFMS.begin(50);

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
}

void loop() {
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  duration = pulseIn(echoPin, HIGH);

  // distance = duration * 0.0343 / 2;
  distance = duration * 17 / 1000; 

  Serial.println(distance);
  if (Serial.available()) { 
    cmd = Serial.read();

    if (cmd == '1') {
      forward(speed);
      // Serial.println("forward");
    }
    else if (cmd == '0') {
      stop(1000);
      // Serial.println("stop");
    }
  }
  delay(100);
}