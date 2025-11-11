#include <Wire.h>
#include "QGPMaker_MotorShield.h"
#include "QGPMaker_Encoder.h"

QGPMaker_MotorShield AFMS = QGPMaker_MotorShield();
QGPMaker_DCMotor *DCMotor_1 = AFMS.getMotor(1); // Front Left
QGPMaker_DCMotor *DCMotor_2 = AFMS.getMotor(2); // Front Right
QGPMaker_DCMotor *DCMotor_3 = AFMS.getMotor(3); // Rear Left
QGPMaker_DCMotor *DCMotor_4 = AFMS.getMotor(4); // Rear Right

QGPMaker_Encoder Encoder1(1); // Front Left Encoder
QGPMaker_Encoder Encoder2(2); // Front Right Encoder
QGPMaker_Encoder Encoder3(3); // Rear Left Encoder
QGPMaker_Encoder Encoder4(4); // Rear Right Encoder

// 메카넘 휠 각 모터별 목표 RPM (FL, FR, RL, RR)
int targetRPM_FL = 0;
int targetRPM_FR = 0;
int targetRPM_RL = 0;
int targetRPM_RR = 0;

// PID 계수 (조정 필요)
// 메카넘 휠은 정교한 제어가 필요하므로, 이 값들을 신중하게 튜닝해야 합니다.
float Kp = 0.8;   // 이전보다 조금 더 높게 설정 (초기 반응성)
float Ki = 0.05;  // 잔류 오차 제거
float Kd = 0.2;   // 오버슈트 방지 및 안정화

// PID 변수 (각 모터별로 유지)
float error_FL, error_FR, error_RL, error_RR;
float prevError_FL = 0, prevError_FR = 0, prevError_RL = 0, prevError_RR = 0;
float integral_FL = 0, integral_FR = 0, integral_RL = 0, integral_RR = 0;

// PID 주기 (더 짧게 가져가는 것이 메카넘 제어에 유리)
unsigned long lastPIDTime = 0;
const int PID_INTERVAL = 50; // 50ms (20Hz)

// PID 변수를 일괄 초기화하는 함수 (움직임 전환 시 필요)
void resetPID() {
  integral_FL = 0; integral_FR = 0; integral_RL = 0; integral_RR = 0;
  prevError_FL = 0; prevError_FR = 0; prevError_RL = 0; prevError_RR = 0;
}

// 새로운 함수: 4개 모터의 목표 RPM과 방향을 설정
void setMecanumMotors(int fl_rpm, int fr_rpm, int rl_rpm, int rr_rpm) {
  // PID 변수 초기화 (움직임 패턴이 바뀔 때 오차 누적 방지)
  resetPID();

  // 각 모터의 목표 RPM 설정
  // abs()를 사용하여 목표 RPM은 항상 양수 값으로 저장
  targetRPM_FL = abs(fl_rpm);
  targetRPM_FR = abs(fr_rpm);
  targetRPM_RL = abs(rl_rpm);
  targetRPM_RR = abs(rr_rpm);

  // 각 모터의 방향 설정
  // rpm 값이 0이면 RELEASE (정지)
  DCMotor_1->run(fl_rpm > 0 ? FORWARD : (fl_rpm < 0 ? BACKWARD : RELEASE)); // Front Left
  DCMotor_2->run(fr_rpm > 0 ? FORWARD : (fr_rpm < 0 ? BACKWARD : RELEASE)); // Front Right
  DCMotor_3->run(rl_rpm > 0 ? FORWARD : (rl_rpm < 0 ? BACKWARD : RELEASE)); // Rear Left
  DCMotor_4->run(rr_rpm > 0 ? FORWARD : (rr_rpm < 0 ? BACKWARD : RELEASE)); // Rear Right
}

void setup() {
  Serial.begin(9600);
  AFMS.begin(50); // PWM 주파수 설정 (기본값 50Hz)

  // 초기에는 모든 모터를 정지 상태로 설정
  setMecanumMotors(0, 0, 0, 0);

  // setup()에서 DCMotor_x->run()과 setSpeed()를 개별적으로 호출하는 대신
  // setMecanumMotors(0,0,0,0)을 호출하여 모든 모터를 RELEASE 상태로 설정하는 것이 좋습니다.
  // DCMotor_1->run(FORWARD);
  // DCMotor_2->run(FORWARD);
  // DCMotor_3->run(FORWARD);
  // DCMotor_4->run(FORWARD);

  // DCMotor_1->setSpeed(baseSpeed);
  // DCMotor_2->setSpeed(baseSpeed);
  // DCMotor_3->setSpeed(baseSpeed);
  // DCMotor_4->setSpeed(baseSpeed);
}

void loop() {
  // Serial 입력으로 메카넘 움직임을 제어하는 예시
  if (Serial.available()) {
    char command = Serial.read();
    int speedVal = 80; // 예시 RPM (목표 RPM은 보통 0~100 사이, 모터에 따라 다름)

    switch (command) {
      case 'W': // 전진 (Forward)
        setMecanumMotors(speedVal, speedVal, speedVal, speedVal);
        Serial.println("Forward");
        break;
      case 'S': // 후진 (Backward)
        setMecanumMotors(-speedVal, -speedVal, -speedVal, -speedVal);
        Serial.println("Backward");
        break;
      case 'A': // 좌측 이동 (Strafe Left)
        setMecanumMotors(-speedVal, speedVal, speedVal, -speedVal);
        Serial.println("Strafe Left");
        break;
      case 'D': // 우측 이동 (Strafe Right)
        setMecanumMotors(speedVal, -speedVal, -speedVal, speedVal);
        Serial.println("Strafe Right");
        break;
      case 'Q': // 제자리 좌회전 (Rotate Left - Counter-clockwise)
        setMecanumMotors(-speedVal, speedVal, -speedVal, speedVal);
        Serial.println("Rotate Left");
        break;
      case 'E': // 제자리 우회전 (Rotate Right - Clockwise)
        setMecanumMotors(speedVal, -speedVal, speedVal, -speedVal);
        Serial.println("Rotate Right");
        break;
      case 'X': // 정지 (Stop)
        setMecanumMotors(0, 0, 0, 0); // 모든 모터의 목표 RPM을 0으로 설정하고 RELEASE
        Serial.println("Stop");
        break;
      // 대각선 이동 등 다른 조합도 추가 가능 (W, A, S, D, Q, E, X가 아닌 다른 키를 할당)
      // 예: 대각선 전방 좌측 이동 (Front Left Diagonal)
      case 'Z': // W + A
        setMecanumMotors(0, speedVal, speedVal, 0); // FL:0, FR:속도, RL:속도, RR:0
        Serial.println("Front Left Diagonal");
        break;
      // 예: 대각선 전방 우측 이동 (Front Right Diagonal)
      case 'C': // W + D
        setMecanumMotors(speedVal, 0, 0, speedVal); // FL:속도, FR:0, RL:0, RR:속도
        Serial.println("Front Right Diagonal");
        break;
    }
  }

  // PID 루프
  if (millis() - lastPIDTime >= PID_INTERVAL) {
    lastPIDTime = millis();

    int rpm_FL = Encoder1.getRPM(); // DCMotor_1에 해당
    int rpm_FR = Encoder2.getRPM(); // DCMotor_2에 해당
    int rpm_RL = Encoder3.getRPM(); // DCMotor_3에 해당
    int rpm_RR = Encoder4.getRPM(); // DCMotor_4에 해당

    // 오차 계산
    error_FL = targetRPM_FL - rpm_FL;
    error_FR = targetRPM_FR - rpm_FR;
    error_RL = targetRPM_RL - rpm_RL;
    error_RR = targetRPM_RR - rpm_RR;

    // 적분 항 계산 및 제한
    integral_FL = constrain(integral_FL + error_FL, -100, 100);
    integral_FR = constrain(integral_FR + error_FR, -100, 100);
    integral_RL = constrain(integral_RL + error_RL, -100, 100);
    integral_RR = constrain(integral_RR + error_RR, -100, 100);

    // 미분 항 계산
    float derivative_FL = error_FL - prevError_FL;
    float derivative_FR = error_FR - prevError_FR;
    float derivative_RL = error_RL - prevError_RL;
    float derivative_RR = error_RR - prevError_RR;

    // PID 보정 계산
    // baseSpeed 개념 없이, PID 출력이 바로 모터 속도가 됩니다.
    // constrain 범위는 0~255 (모터 속도 최대/최소)
    int speed_FL = constrain(Kp * error_FL + Ki * integral_FL + Kd * derivative_FL, 0, 255);
    int speed_FR = constrain(Kp * error_FR + Ki * integral_FR + Kd * derivative_FR, 0, 255);
    int speed_RL = constrain(Kp * error_RL + Ki * integral_RL + Kd * derivative_RL, 0, 255);
    int speed_RR = constrain(Kp * error_RR + Ki * integral_RR + Kd * derivative_RR, 0, 255);

    // 계산된 속도를 모터에 적용
    DCMotor_1->setSpeed(speed_FL);
    DCMotor_2->setSpeed(speed_FR);
    DCMotor_3->setSpeed(speed_RL);
    DCMotor_4->setSpeed(speed_RR);

    // 이전 오차 업데이트
    prevError_FL = error_FL;
    prevError_FR = error_FR;
    prevError_RL = error_RL;
    prevError_RR = error_RR;

    // 시리얼 모니터로 RPM과 적용된 속도 출력
    Serial.print("RPM: ");
    Serial.print(rpm_FL); Serial.print(" ");
    Serial.print(rpm_FR); Serial.print(" ");
    Serial.print(rpm_RL); Serial.print(" ");
    Serial.print(rpm_RR); Serial.print(" | S: ");
    Serial.print(speed_FL); Serial.print(" ");
    Serial.print(speed_FR); Serial.print(" ");
    Serial.print(speed_RL); Serial.print(" ");
    Serial.println(speed_RR);
  }
}