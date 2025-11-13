#ifndef MotorController4WD_h
#define MotorController4WD_h

#include "Arduino.h"
#include "QGPMaker_MotorShield.h"
#include "Adafruit_MS_PWMServoDriver.h"

#define M1 1
#define M2 2
#define M3 4
#define M4 8
#define M_LEFT 3 //M1&M2
#define M_RIGHT 12 //M3&M4
#define M_ALL 15


class MotorController4WD
{
  protected:
    int _ena, _in1, _in2, _enb, _in3, _in4;
    int _currentSpeed;
    double _motorAConst, _motorBConst;

  public:
    MotorController4WD(double motorAConst = 1.0, double motorBConst = 1.0);
    void begin();
    void move(int leftSpeed, int rightSpeed, int minAbsSpeed);
    void move(int speed);
    void move(int speed, int minAbsSpeed);
    void moveForward(int speed);
    void moveBackward(int speed);

    void moveLeft4Mecanum(int speed);
    void moveRight4Mecanum(int speed);

    void moveLF4Mecanum(int speed);
    void moveLB4Mecanum(int speed);
    void moveRF4Mecanum(int speed);
    void moveRB4Mecanum(int speed);

    void turnLeft(int speed, bool kick = false);
    void turnRight(int speed, bool kick = false);
    void stopMoving();
    void brakeAll();
    
    void runMotor(int motor, int speed);
    void stopMotor(int motor);

    void writeServo(int num, int angle);
    int readServo(int num);
};

#endif
