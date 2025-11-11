#include <Arduino.h>
#include <Wire.h>
#include "PS2X_lib.h"
#include "PID_v1.h"
#include "MotorController4WD.h"
#include "EasyBuzzer.h"
#include "KiKuPILineFollow.h"

#define DEBUG 0

#define TRIGGER_PIN A0

#define SPEED 180
#define MIN_ABS_SPEED 0

PS2X ps2x;
MotorController4WD motorController(1, 1);

//PID
double originalSetpoint = 0;
double setpoint = originalSetpoint;
double movingAngleOffset = 0.1;
double input, output;
int moveState = 0;                                       //0 = balance; 1 = back; 2 = forth
double Kp = 30;                                          // First adjustment  [20,100]  60
double Kd = 0.3;                                         // Second adjustment [0.0-1.0]  0.8
double Ki = 0.2;                                         // Third adjustment  [0.0-1.0]  0.5
PID pid(&input, &output, &setpoint, Kp, Ki, Kd, DIRECT) ; // kp = 55,kd=0.9

long ARM_MIN[] = {10, 10, 40, 10};
long ARM_MAX[] = {170, 140, 170, 102};

int mode = 0;

int pos;
int outlineCnt = 0;
int initial_motor_speed = 60; //90
bool tracing = true;
int adval[5];

KKPLINEFOLLOW sensorbar1;

//Grab something
void openGripper()
{
  motorController.writeServo(3, ARM_MIN[3]);
  // delay(300);
}

void closeGripper()
{
  motorController.writeServo(3, ARM_MAX[3]);
  //delay(300);
}


int echoTrace()
{
  int ret = 0;
  for (int i = 0; i < 5; i++)
  {
    adval[i] = sensorbar1.readSensor(i);
    // Serial.print(adval[i]);
    // Serial.print(",");
    if (adval[i] <= 0)
      ret += (0x1 << i);
  }
  // Serial.println(ret, BIN);
  return ret;
}

void pidWork()
{
  pos = echoTrace();
  if (pos == B00000 || pos == B11111)
  {
    outlineCnt++;
  }
  else if ((pos & 1) == 1)
  {
    outlineCnt = 0;
    input = 4;
  }
  else if ((pos & B10000) == B10000)
  {
    outlineCnt = 0;
    input = -4;
  }
  else if ((pos & B01000) == B01000)
  {
    outlineCnt = 0;
    input = -2;
  }
  else if ((pos & B00010) == B00010)
  {
    outlineCnt = 0;
    input = 2;
  }
  else
  {
    outlineCnt = 0;
    input = 0;
  }
  if (outlineCnt > 30)
  {
    //   motorController.stopMoving();
    mode = 0;
    EasyBuzzer.beep(1000, 3);
  }
  else
  {
//    readCOM();
    pid.Compute();
    int left_motor_speed = initial_motor_speed - output;
    int right_motor_speed = initial_motor_speed + output;
    //#if defined(DEBUG)
    //        Serial.print("IN:");
    //        Serial.print(input);
    //        Serial.print(",OUT:");
    //        Serial.print(output);
//    Serial.print(",L:");
//    Serial.print(left_motor_speed);
//    Serial.print(",R:");
//    Serial.println(right_motor_speed);
    //
    //        Serial.println("===========================================");
    //#endif
//    if (distance > 10 || distance == 0)
//    {

      motorController.move(left_motor_speed, right_motor_speed, MIN_ABS_SPEED);
//    }
//    else
//    {
//      motorController.stopMoving();
//      EasyBuzzer.beep(1000, 2);
//    }
  }
}


void setup()
{
  Serial.begin(9600);
  int error = 0;
  do
  {
    error = ps2x.config_gamepad(13, 11, 10, 12, true, true);
    if (error == 0)
    {
      break;
    }
    else
    {
      delay(100);
    }
  } while (1);

  // initialize device
  // Serial.println(F("Initializing ..."));
  motorController.begin();

  //setup PID
  pid.SetMode(AUTOMATIC);
  pid.SetSampleTime(10);
  pid.SetOutputLimits(-255, 255);

  motorController.writeServo(0, 90);
  motorController.writeServo(1, 90);
  motorController.writeServo(2, 90);
  motorController.writeServo(3, 90);
  for (size_t i = 0; i < 50; i++)
  {
    ps2x.read_gamepad(false, 0);
    delay(10);
  }

  if(sensorbar1.begin(0x20) == false){
    Serial.println("IIC sensorbar1 init failed");
    while(1);
  } 
  sensorbar1.enableSensor();
  //TODO buzzer
  EasyBuzzer.beep(
    1000, // Frequency in hertz(HZ).
    50,   // On Duration in milliseconds(ms).
    100,  // Off Duration in milliseconds(ms).
    2,    // The number of beeps per cycle.
    500,  // Pause duration.
    1);
}

void loop()
{
  EasyBuzzer.update();
  ps2x.read_gamepad(false, 0);
  if (ps2x.Button(PSB_PAD_UP))
  {

    if (ps2x.Button(PSB_L2))
    {
      motorController.moveLF4Mecanum(SPEED);
    }
    else if (ps2x.Button(PSB_R2))
    {
      motorController.moveRF4Mecanum(SPEED);
    }
    else
    {
      // Serial.println("*******************************");
      //距离小于5cm，停止
//      if (distance > 10 || distance == 0)
//      {
        motorController.moveForward(SPEED);
//      }
//      else
//      {
//        motorController.stopMoving();
//        EasyBuzzer.beep(1000, 2);
//      }
    }
  }
  else if (ps2x.Button(PSB_PAD_DOWN))
  {
    if (ps2x.Button(PSB_L2))
    {
      motorController.moveRB4Mecanum(SPEED);
    }
    else if (ps2x.Button(PSB_R2))
    {
      motorController.moveLB4Mecanum(SPEED);
    }
    else
    {
      motorController.moveBackward(SPEED);
    }
  }
  else if (ps2x.Button(PSB_PAD_LEFT))
  {
    motorController.turnLeft(SPEED);
  }
  else if (ps2x.Button(PSB_PAD_RIGHT))
  {
    motorController.turnRight(SPEED);
  }
  else if (ps2x.Button(PSB_L1))
  {
    motorController.moveLeft4Mecanum(SPEED);
  }
  else if (ps2x.Button(PSB_R1))
  {
    motorController.moveRight4Mecanum(SPEED);
  }
  else
  {
    if (mode == 0)
      motorController.stopMoving();
  }

  if (ps2x.Button(PSB_CIRCLE))
  {
    //TODO buzzer
    mode = 1;
    outlineCnt = 0;
    EasyBuzzer.beep(1000, 1);
    Serial.println("开始巡线");
  }
  // 按下手柄X按钮，手柄震动一下
  if (ps2x.Button(PSB_CROSS))
  {
    mode = 0;
    EasyBuzzer.beep(1000, 2);
    ps2x.read_gamepad(true, 200);
    delay(300);
    ps2x.read_gamepad(false, 0);
    Serial.println("结束巡线");
  }

  if (ps2x.Analog(PSS_LX) > 240)
  {
    if (motorController.readServo(0) > ARM_MIN[(int)(0)])
    {
      motorController.writeServo(0, (motorController.readServo(0) - 1));
    }
  }
  else if (ps2x.Analog(PSS_LX) < 10)
  {
    if (motorController.readServo(0) < ARM_MAX[(int)(0)])
    {
      motorController.writeServo(0, (motorController.readServo(0) + 1));
    }
  }

  if (ps2x.Analog(PSS_LY) > 240)
  {
    if (motorController.readServo(1) > ARM_MIN[(int)(1)])
    {
      motorController.writeServo(1, (motorController.readServo(1) - 1));
    }
  }
  else if (ps2x.Analog(PSS_LY) < 10)
  {
    if (motorController.readServo(1) < ARM_MAX[(int)(1)])
    {
      motorController.writeServo(1, (motorController.readServo(1) + 1));
    }
  }

  if (ps2x.Analog(PSS_RY) > 240)
  {
    if (motorController.readServo(2) > ARM_MIN[(int)(2)])
    {
      motorController.writeServo(2, (motorController.readServo(2) - 1));
    }
  }
  else if (ps2x.Analog(PSS_RY) < 10)
  {
    if (motorController.readServo(2) < ARM_MAX[(int)(2)])
    {
      motorController.writeServo(2, (motorController.readServo(2) + 1));
    }
  }

  if (ps2x.Analog(PSS_RX) > 240)
  {
    if (motorController.readServo(3) > ARM_MIN[(int)(3)])
    {
      motorController.writeServo(3, (motorController.readServo(3) - 1));
    }
  }
  else if (ps2x.Analog(PSS_RX) < 10)
  {
    if (motorController.readServo(3) < ARM_MAX[(int)(3)])
    {
      motorController.writeServo(3, (motorController.readServo(3) + 1));
    }
  }

  if (mode == 1)
  {
    pidWork();
    delay(10);
  }

  delay(5);
}
