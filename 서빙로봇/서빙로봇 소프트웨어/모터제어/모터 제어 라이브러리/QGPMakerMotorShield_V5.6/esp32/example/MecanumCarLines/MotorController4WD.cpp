#include "MotorController4WD.h"
#include "Arduino.h"
#include "QGPMaker_MotorShield.h"
#include "Adafruit_MS_PWMServoDriver.h"

QGPMaker_MotorShield JFMS = QGPMaker_MotorShield();
QGPMaker_DCMotor *DCMotor_L1 = JFMS.getMotor(1);
QGPMaker_DCMotor *DCMotor_L2 = JFMS.getMotor(2);

QGPMaker_DCMotor *DCMotor_R3 = JFMS.getMotor(3);
QGPMaker_DCMotor *DCMotor_R4 = JFMS.getMotor(4);
// Adafruit_Servo servos[4] = Adafruit_Servo[4];
// Adafruit_Servo *Servo = AFMS.getServo(1);
// Adafruit_Servo *Servo2 = AFMS.getServo(2);
// Adafruit_Servo *Servo3 = AFMS.getServo(3);
// Adafruit_Servo *Servo4 = AFMS.getServo(4);

MotorController4WD::MotorController4WD(double motorAConst, double motorBConst)
{
  _motorAConst = motorAConst;
  _motorBConst = motorBConst;
}

void MotorController4WD::begin()
{
  JFMS.begin(50);
}

void MotorController4WD::move(int leftSpeed, int rightSpeed, int minAbsSpeed)
{
  if (rightSpeed < 0)
  {
    rightSpeed = min(rightSpeed, -1 * minAbsSpeed);
    rightSpeed = max(rightSpeed, -255);
  }
  else if (rightSpeed > 0)
  {
    rightSpeed = max(rightSpeed, minAbsSpeed);
    rightSpeed = min(rightSpeed, 255);
  }

  int realRightSpeed = map(abs(rightSpeed), 0, 255, minAbsSpeed, 255);

  if (leftSpeed < 0)
  {
    leftSpeed = min(leftSpeed, -1 * minAbsSpeed);
    leftSpeed = max(leftSpeed, -255);
  }
  else if (leftSpeed > 0)
  {
    leftSpeed = max(leftSpeed, minAbsSpeed);
    leftSpeed = min(leftSpeed, 255);
  }

  int realLeftSpeed = map(abs(leftSpeed), 0, 255, minAbsSpeed, 255);

  DCMotor_L1->setSpeed(realLeftSpeed * _motorBConst);
  DCMotor_L1->run(leftSpeed > 0 ?  BACKWARD :FORWARD);
  DCMotor_L2->setSpeed(realLeftSpeed * _motorBConst);
  DCMotor_L2->run(leftSpeed > 0 ? BACKWARD : FORWARD);

  DCMotor_R3->setSpeed(realRightSpeed * _motorAConst);
  DCMotor_R3->run(rightSpeed > 0 ? FORWARD : BACKWARD);
  DCMotor_R4->setSpeed(realRightSpeed * _motorAConst);
  DCMotor_R4->run(rightSpeed > 0 ? FORWARD : BACKWARD);
}

void MotorController4WD::move(int speed, int minAbsSpeed)
{
  //      DCMotor_L3->setSpeed( 150);
  //  DCMotor_L3->run(  FORWARD );

  int direction = 1;

  if (speed < 0)
  {
    direction = -1;

    speed = min(speed, -1 * minAbsSpeed);
    speed = max(speed, -255);
  }
  else
  {
    speed = max(speed, minAbsSpeed);
    speed = min(speed, 255);
  }

  if (speed == _currentSpeed)
    return;

  int realSpeed = max(minAbsSpeed, abs(speed));
  Serial.println(realSpeed);
  //  DCMotor_L3->setSpeed(realSpeed * _motorBConst);
  //  DCMotor_L3->run( speed > 0 ? BACKWARD : FORWARD);
  //  DCMotor_R2->setSpeed(realSpeed * _motorAConst);
  //  DCMotor_R2->run( speed > 0 ? BACKWARD : FORWARD);

  //  digitalWrite(_in1, speed > 0 ? HIGH : LOW);
  //  digitalWrite(_in2, speed > 0 ? LOW : HIGH);
  //  digitalWrite(_in3, speed > 0 ? HIGH : LOW);
  //  digitalWrite(_in4, speed > 0 ? LOW : HIGH);
  //  analogWrite(_ena, realSpeed * _motorAConst);
  //  analogWrite(_enb, realSpeed * _motorBConst);

  _currentSpeed = direction * realSpeed;
}

void MotorController4WD::move(int speed)
{
  if (speed == _currentSpeed)
    return;

  if (speed > 255)
    speed = 255;
  else if (speed < -255)
    speed = -255;

  //  DCMotor_L3->setSpeed( abs(speed) * _motorBConst);
  //  DCMotor_L3->run( speed > 0 ? FORWARD : BACKWARD);
  //  DCMotor_R2->setSpeed( abs(speed) * _motorAConst);
  //  DCMotor_R2->run( speed > 0 ? FORWARD : BACKWARD);

  //  digitalWrite(_in1, speed > 0 ? HIGH : LOW);
  //  digitalWrite(_in2, speed > 0 ? LOW : HIGH);
  //  digitalWrite(_in3, speed > 0 ? HIGH : LOW);
  //  digitalWrite(_in4, speed > 0 ? LOW : HIGH);
  //  analogWrite(_ena, abs(speed) * _motorAConst);
  //  analogWrite(_enb, abs(speed) * _motorBConst);

  _currentSpeed = speed;
}

void MotorController4WD::moveForward(int speed)
{
  DCMotor_L1->setSpeed(speed * _motorBConst);
  DCMotor_L1->run(BACKWARD);
  DCMotor_L2->setSpeed(speed * _motorBConst);
  DCMotor_L2->run(BACKWARD);

  DCMotor_R3->setSpeed(speed * _motorAConst);
  DCMotor_R3->run(FORWARD);
  DCMotor_R4->setSpeed(speed * _motorAConst);
  DCMotor_R4->run(FORWARD);
}

void MotorController4WD::moveBackward(int speed)
{
  DCMotor_L1->setSpeed(speed * _motorBConst);
  DCMotor_L1->run(FORWARD);
  DCMotor_L2->setSpeed(speed * _motorBConst);
  DCMotor_L2->run(FORWARD);

  DCMotor_R3->setSpeed(speed * _motorAConst);
  DCMotor_R3->run(BACKWARD);
  DCMotor_R4->setSpeed(speed * _motorAConst);
  DCMotor_R4->run(BACKWARD);
}

void MotorController4WD::turnLeft(int speed, bool kick)
{
  DCMotor_L1->setSpeed(speed * _motorBConst);
  DCMotor_L1->run(FORWARD);
  DCMotor_L2->setSpeed(speed * _motorBConst);
  DCMotor_L2->run(FORWARD);

  DCMotor_R3->setSpeed(speed * _motorAConst);
  DCMotor_R3->run(FORWARD);
  DCMotor_R4->setSpeed(speed * _motorAConst);
  DCMotor_R4->run(FORWARD);
}

void MotorController4WD::turnRight(int speed, bool kick)
{
  DCMotor_L1->setSpeed(speed * _motorBConst);
  DCMotor_L1->run(BACKWARD);
  DCMotor_L2->setSpeed(speed * _motorBConst);
  DCMotor_L2->run(BACKWARD);

  DCMotor_R3->setSpeed(speed * _motorAConst);
  DCMotor_R3->run(BACKWARD);
  DCMotor_R4->setSpeed(speed * _motorAConst);
  DCMotor_R4->run(BACKWARD);
}

void MotorController4WD::brakeAll()
{
  DCMotor_L1->setSpeed(0);
  DCMotor_L1->run(BRAKE);
  DCMotor_L2->setSpeed(0);
  DCMotor_L2->run(BRAKE);
  DCMotor_R3->setSpeed(0);
  DCMotor_R3->run(BRAKE);
  DCMotor_R4->setSpeed(0);
  DCMotor_R4->run(BRAKE);
  _currentSpeed = 0;
}

void MotorController4WD::stopMoving()
{
  DCMotor_L1->setSpeed(0);
  DCMotor_L1->run(RELEASE);
  DCMotor_L2->setSpeed(0);
  DCMotor_L2->run(RELEASE);
  DCMotor_R3->setSpeed(0);
  DCMotor_R3->run(RELEASE);
  DCMotor_R4->setSpeed(0);
  DCMotor_R4->run(RELEASE);
  _currentSpeed = 0;
}

void MotorController4WD::writeServo(int num, int angle)
{
  QGPMaker_Servo *Servo = JFMS.getServo(num);
  Servo->writeServo(angle);
}

int MotorController4WD::readServo(int num)
{
  QGPMaker_Servo *Servo = JFMS.getServo(num);
  return Servo->readDegrees();
}

void MotorController4WD::moveLeft4Mecanum(int speed)
{
  DCMotor_L1->setSpeed(speed * _motorBConst);
  DCMotor_L1->run(FORWARD);
  DCMotor_L2->setSpeed(speed * _motorBConst);
  DCMotor_L2->run(BACKWARD);

  DCMotor_R3->setSpeed(speed * _motorAConst);
  DCMotor_R3->run(BACKWARD);
  DCMotor_R4->setSpeed(speed * _motorAConst);
  DCMotor_R4->run(FORWARD);
}
void MotorController4WD::moveRight4Mecanum(int speed)
{
  DCMotor_L1->setSpeed(speed * _motorBConst);
  DCMotor_L1->run(BACKWARD);
  DCMotor_L2->setSpeed(speed * _motorBConst);
  DCMotor_L2->run(FORWARD);

  DCMotor_R3->setSpeed(speed * _motorAConst);
  DCMotor_R3->run(FORWARD);
  DCMotor_R4->setSpeed(speed * _motorAConst);
  DCMotor_R4->run(BACKWARD);
}

void MotorController4WD::moveLF4Mecanum(int speed)
{
  DCMotor_L2->setSpeed(speed * _motorBConst);
  DCMotor_L2->run(BACKWARD);
  DCMotor_R4->setSpeed(speed * _motorAConst);
  DCMotor_R4->run(FORWARD);

  DCMotor_L1->setSpeed(0);
  DCMotor_L1->run(RELEASE);
  DCMotor_R3->setSpeed(0);
  DCMotor_R3->run(RELEASE);
}

void MotorController4WD::moveLB4Mecanum(int speed)
{
  DCMotor_L1->setSpeed(speed * _motorBConst);
  DCMotor_L1->run(FORWARD);
  DCMotor_R3->setSpeed(speed * _motorAConst);
  DCMotor_R3->run(BACKWARD);

  DCMotor_L2->setSpeed(0);
  DCMotor_L2->run(RELEASE);
  DCMotor_R4->setSpeed(0);
  DCMotor_R4->run(RELEASE);
}

void MotorController4WD::moveRF4Mecanum(int speed)
{
  DCMotor_L1->setSpeed(speed * _motorBConst);
  DCMotor_L1->run(BACKWARD);
  DCMotor_R3->setSpeed(speed * _motorAConst);
  DCMotor_R3->run(FORWARD);

  DCMotor_L2->setSpeed(0);
  DCMotor_L2->run(RELEASE);
  DCMotor_R4->setSpeed(0);
  DCMotor_R4->run(RELEASE);
}

void MotorController4WD::moveRB4Mecanum(int speed)
{
  DCMotor_L2->setSpeed(speed * _motorBConst);
  DCMotor_L2->run(FORWARD);
  DCMotor_R4->setSpeed(speed * _motorAConst);
  DCMotor_R4->run(BACKWARD);

  DCMotor_L1->setSpeed(0);
  DCMotor_L1->run(RELEASE);
  DCMotor_R3->setSpeed(0);
  DCMotor_R3->run(RELEASE);
}

void MotorController4WD::runMotor(int motor, int speed) {

}
void MotorController4WD::stopMotor(int motor) {

}
