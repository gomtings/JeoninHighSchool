#include <Wire.h>
#include "QGPMaker_MotorShield.h"
#include "QGPMaker_Encoder.h"

QGPMaker_MotorShield AFMS = QGPMaker_MotorShield();
QGPMaker_DCMotor *DCMotor_1 = AFMS.getMotor(1);
QGPMaker_DCMotor *DCMotor_2 = AFMS.getMotor(2);
QGPMaker_DCMotor *DCMotor_3 = AFMS.getMotor(3);
QGPMaker_DCMotor *DCMotor_4 = AFMS.getMotor(4);

QGPMaker_Encoder Encoder1(1);
QGPMaker_Encoder Encoder2(2);
QGPMaker_Encoder Encoder3(3);
QGPMaker_Encoder Encoder4(4);

// 목표 RPM
int targetRPM = 50;

// PID 계수 (매우 약하게 적용)
float Kp = 0.3;
float Ki = 0.02;
float Kd = 0.1;

// PID 변수
float error1, error2, error3, error4;
float prevError1 = 0, prevError2 = 0, prevError3 = 0, prevError4 = 0;
float integral1 = 0, integral2 = 0, integral3 = 0, integral4 = 0;

// 초기 속도 (확실히 움직일 정도)
int baseSpeed = 10;

// PID 주기 느리게 (PID보다 주행 안정성이 우선)
unsigned long lastPIDTime = 0;
const int PID_INTERVAL = 200; // 200ms 마다 조정

void setup() {
  Serial.begin(9600);
  AFMS.begin(50);

  DCMotor_1->run(FORWARD);
  DCMotor_2->run(FORWARD);
  DCMotor_3->run(FORWARD);
  DCMotor_4->run(FORWARD);

  DCMotor_1->setSpeed(baseSpeed);
  DCMotor_2->setSpeed(baseSpeed);
  DCMotor_3->setSpeed(baseSpeed);
  DCMotor_4->setSpeed(baseSpeed);
}

void loop() {

  if (millis() - lastPIDTime >= PID_INTERVAL) {
    lastPIDTime = millis();

    int rpm1 = Encoder1.getRPM();
    int rpm2 = Encoder2.getRPM();
    int rpm3 = Encoder3.getRPM();
    int rpm4 = Encoder4.getRPM();

    // 오차 계산
    error1 = targetRPM - rpm1;
    error2 = targetRPM - rpm2;
    error3 = targetRPM - rpm3;
    error4 = targetRPM - rpm4;

    // 적분 최소 적용 (너무 강하게 안 함)
    integral1 = constrain(integral1 + error1, -100, 100);
    integral2 = constrain(integral2 + error2, -100, 100);
    integral3 = constrain(integral3 + error3, -100, 100);
    integral4 = constrain(integral4 + error4, -100, 100);

    float derivative1 = error1 - prevError1;
    float derivative2 = error2 - prevError2;
    float derivative3 = error3 - prevError3;
    float derivative4 = error4 - prevError4;

    // PID 보정은 아주 약하게만 적용
    int speed1 = constrain(baseSpeed + Kp * error1 + Ki * integral1 + Kd * derivative1, 150, 255);
    int speed2 = constrain(baseSpeed + Kp * error2 + Ki * integral2 + Kd * derivative2, 150, 255);
    int speed3 = constrain(baseSpeed + Kp * error3 + Ki * integral3 + Kd * derivative3, 150, 255);
    int speed4 = constrain(baseSpeed + Kp * error4 + Ki * integral4 + Kd * derivative4, 150, 255);

    DCMotor_1->setSpeed(speed1);
    DCMotor_2->setSpeed(speed2);
    DCMotor_3->setSpeed(speed3);
    DCMotor_4->setSpeed(speed4);

    prevError1 = error1;
    prevError2 = error2;
    prevError3 = error3;
    prevError4 = error4;

    Serial.print("RPM: ");
    Serial.print(rpm1); Serial.print(" ");
    Serial.print(rpm2); Serial.print(" ");
    Serial.print(rpm3); Serial.print(" ");
    Serial.print(rpm4); Serial.print(" | S: ");
    Serial.print(speed1); Serial.print(" ");
    Serial.print(speed2); Serial.print(" ");
    Serial.print(speed3); Serial.print(" ");
    Serial.println(speed4);
  }
}