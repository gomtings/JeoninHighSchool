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
int targetRPM = 100;

// PID 계수
float Kp = 1.0; // 반응 속도 조절 (크면 빠르게 보정하지만 진동 가능)
float Ki = 0.1; // 오차 누적 보정 (느리지만 장기 오차 제거)
float Kd = 0.5; // 급격한 변화 억제 (진동 방지, 부드러운 제어)

// PID 변수
float error1, error2, error3, error4;
float prevError1 = 0, prevError2 = 0, prevError3 = 0, prevError4 = 0;
float integral1 = 0, integral2 = 0, integral3 = 0, integral4 = 0;

// 초기 속도
int baseSpeed = 150;

void setup() {
  Serial.begin(9600);
  AFMS.begin(50); // PWM 주파수 50Hz

  // 초기 속도 설정
  DCMotor_1->setSpeed(baseSpeed);
  DCMotor_2->setSpeed(baseSpeed);
  DCMotor_3->setSpeed(baseSpeed);
  DCMotor_4->setSpeed(baseSpeed);

  // 전진 방향 설정
  DCMotor_1->run(FORWARD);
  DCMotor_2->run(FORWARD);
  DCMotor_3->run(FORWARD);
  DCMotor_4->run(FORWARD);
}

void loop() {
  // 각 모터의 RPM 측정
  int rpm1 = Encoder1.getRPM();
  int rpm2 = Encoder2.getRPM();
  int rpm3 = Encoder3.getRPM();
  int rpm4 = Encoder4.getRPM();

  // 오차 계산
  error1 = targetRPM - rpm1;
  error2 = targetRPM - rpm2;
  error3 = targetRPM - rpm3;
  error4 = targetRPM - rpm4;

  // 적분값 누적
  integral1 += error1;
  integral2 += error2;
  integral3 += error3;
  integral4 += error4;

  // 미분값 계산
  float derivative1 = error1 - prevError1;
  float derivative2 = error2 - prevError2;
  float derivative3 = error3 - prevError3;
  float derivative4 = error4 - prevError4;

  // PID 제어 계산
  int speed1 = constrain(baseSpeed + Kp * error1 + Ki * integral1 + Kd * derivative1, 0, 255);
  int speed2 = constrain(baseSpeed + Kp * error2 + Ki * integral2 + Kd * derivative2, 0, 255);
  int speed3 = constrain(baseSpeed + Kp * error3 + Ki * integral3 + Kd * derivative3, 0, 255);
  int speed4 = constrain(baseSpeed + Kp * error4 + Ki * integral4 + Kd * derivative4, 0, 255);

  // 보정된 속도 적용
  DCMotor_1->setSpeed(speed1);
  DCMotor_2->setSpeed(speed2);
  DCMotor_3->setSpeed(speed3);
  DCMotor_4->setSpeed(speed4);

  // 이전 오차 저장
  prevError1 = error1;
  prevError2 = error2;
  prevError3 = error3;
  prevError4 = error4;

  // 디버깅 출력
  Serial.print("RPMs: ");
  Serial.print(rpm1); Serial.print(" ");
  Serial.print(rpm2); Serial.print(" ");
  Serial.print(rpm3); Serial.print(" ");
  Serial.print(rpm4); Serial.print(" | Speeds: ");
  Serial.print(speed1); Serial.print(" ");
  Serial.print(speed2); Serial.print(" ");
  Serial.print(speed3); Serial.print(" ");
  Serial.println(speed4);

  delay(100); // 제어 주기
}
