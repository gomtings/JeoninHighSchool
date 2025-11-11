#include <Wire.h>
#include "PS2X_lib.h"
#include "QGPMaker_MotorShield.h"

long ARM_MIN[]={10, 10, 40, 10, 0, 0, 0, 0};
long ARM_MAX[]={170, 140, 170, 102, 180, 180, 180, 180};

PS2X ps2x;
QGPMaker_MotorShield AFMS = QGPMaker_MotorShield();

QGPMaker_Servo *Servo0 = AFMS.getServo(0);
QGPMaker_Servo *Servo1 = AFMS.getServo(1);
QGPMaker_Servo *Servo2 = AFMS.getServo(2);
QGPMaker_Servo *Servo3 = AFMS.getServo(3);
QGPMaker_Servo *Servo4 = AFMS.getServo(4);
QGPMaker_Servo *Servo5 = AFMS.getServo(5);
QGPMaker_Servo *Servo6 = AFMS.getServo(6);
QGPMaker_Servo *Servo7 = AFMS.getServo(7);
QGPMaker_DCMotor *DCMotor_2 = AFMS.getMotor(2);
QGPMaker_DCMotor *DCMotor_4 = AFMS.getMotor(4);
QGPMaker_DCMotor *DCMotor_1 = AFMS.getMotor(1);
QGPMaker_DCMotor *DCMotor_3 = AFMS.getMotor(3);

void forward() {
  DCMotor_1->setSpeed(200);
  DCMotor_1->run(FORWARD);
  DCMotor_2->setSpeed(200);
  DCMotor_2->run(FORWARD);
  DCMotor_3->setSpeed(200);
  DCMotor_3->run(FORWARD);
  DCMotor_4->setSpeed(200);
  DCMotor_4->run(FORWARD);
}

void turnLeft() {
  DCMotor_1->setSpeed(200);
  DCMotor_1->run(BACKWARD);
  DCMotor_2->setSpeed(200);
  DCMotor_2->run(BACKWARD);
  DCMotor_3->setSpeed(200);
  DCMotor_3->run(FORWARD);
  DCMotor_4->setSpeed(200);
  DCMotor_4->run(FORWARD);
}

void turnRight() {
  DCMotor_1->setSpeed(200);
  DCMotor_1->run(FORWARD);
  DCMotor_2->setSpeed(200);
  DCMotor_2->run(FORWARD);
  DCMotor_3->setSpeed(200);
  DCMotor_3->run(BACKWARD);
  DCMotor_4->setSpeed(200);
  DCMotor_4->run(BACKWARD);
}

void moveLeft() {
  DCMotor_1->setSpeed(200);
  DCMotor_1->run(BACKWARD);
  DCMotor_2->setSpeed(200);
  DCMotor_2->run(FORWARD);
  DCMotor_3->setSpeed(200);
  DCMotor_3->run(BACKWARD);
  DCMotor_4->setSpeed(200);
  DCMotor_4->run(FORWARD);
}

void moveRight() {
  DCMotor_1->setSpeed(200);
  DCMotor_1->run(FORWARD);
  DCMotor_2->setSpeed(200);
  DCMotor_2->run(BACKWARD);
  DCMotor_3->setSpeed(200);
  DCMotor_3->run(FORWARD);
  DCMotor_4->setSpeed(200);
  DCMotor_4->run(BACKWARD);
}

void backward() {
  DCMotor_1->setSpeed(200);
  DCMotor_1->run(BACKWARD);
  DCMotor_2->setSpeed(200);
  DCMotor_2->run(BACKWARD);
  DCMotor_3->setSpeed(200);
  DCMotor_3->run(BACKWARD);
  DCMotor_4->setSpeed(200);
  DCMotor_4->run(BACKWARD);
}

void stopMoving() {
  DCMotor_1->setSpeed(0);
  DCMotor_1->run(RELEASE);
  DCMotor_2->setSpeed(0);
  DCMotor_2->run(RELEASE);
  DCMotor_3->setSpeed(0);
  DCMotor_3->run(RELEASE);
  DCMotor_4->setSpeed(0);
  DCMotor_4->run(RELEASE);
}

void setup(){
  AFMS.begin(50);
         
  int error = 0;
  do{
    error = ps2x.config_gamepad(18,23,5,19, true, true);
    if(error == 0){
      break;
    }else{
      delay(100);
    }
  }while(1); 
  for(size_t i = 0; i < 50; i++)
  {
        ps2x.read_gamepad(false, 0);
        delay(10);
  }

  Servo0->writeServo(90);
  Servo1->writeServo(90);
  Servo2->writeServo(90);
  Servo3->writeServo(90);
  Servo4->writeServo(90);
  Servo5->writeServo(90);
  Servo6->writeServo(90);
  Servo7->writeServo(90);
}

void loop(){
  ps2x.read_gamepad(false, 0);
  delay(3);
  if (ps2x.Button(PSB_PAD_UP)) {
    if (ps2x.Button(PSB_L2)) {
      DCMotor_2->setSpeed(200);
      DCMotor_2->run(FORWARD);
      DCMotor_4->setSpeed(200);
      DCMotor_4->run(FORWARD);

    } else if (ps2x.Button(PSB_R2)) {
      DCMotor_1->setSpeed(200);
      DCMotor_1->run(FORWARD);
      DCMotor_3->setSpeed(200);
      DCMotor_3->run(FORWARD);
    } else {
      forward();

    }

  } else if (ps2x.Button(PSB_PAD_DOWN)) {
    if (ps2x.Button(PSB_L2)) {
      DCMotor_2->setSpeed(200);
      DCMotor_2->run(BACKWARD);
      DCMotor_4->setSpeed(200);
      DCMotor_4->run(BACKWARD);

    } else if (ps2x.Button(PSB_R2)) {
      DCMotor_1->setSpeed(200);
      DCMotor_1->run(BACKWARD);
      DCMotor_3->setSpeed(200);
      DCMotor_3->run(BACKWARD);
    } else {
      backward();

    }
  } else if (ps2x.Button(PSB_PAD_LEFT)) {
    turnLeft();
  } else if (ps2x.Button(PSB_PAD_RIGHT)) {
    turnRight();
  } else if (ps2x.Button(PSB_L1)) {
    moveLeft();
  } else if (ps2x.Button(PSB_R1)) {
    moveRight();
  } else {
    stopMoving();

  }
  // ps2手柄按钮
  if (ps2x.Button(PSB_CROSS)) {
    ps2x.read_gamepad(true, 200);
    delay(300);
    ps2x.read_gamepad(false, 0);

  }
  if (ps2x.Button(PSB_R2)) {
    if (ps2x.Analog(PSS_LX) > 240) {
      if (Servo4->readDegrees() > ARM_MIN[4]) {
        Servo4->writeServo((Servo4->readDegrees() - 1));
      }

    } else if (ps2x.Analog(PSS_LX) < 10) {
      if (Servo4->readDegrees() < ARM_MIN[4]) {
        Servo4->writeServo((Servo4->readDegrees() + 1));
      }
    }
    if (ps2x.Analog(PSS_LY) > 240) {
      if (Servo5->readDegrees() > ARM_MIN[5]) {
        Servo5->writeServo((Servo5->readDegrees() - 1));
      }

    } else if (ps2x.Analog(PSS_LY) < 10) {
      if (Servo5->readDegrees() < ARM_MAX[5]) {
        Servo5->writeServo((Servo5->readDegrees() + 1));
      }
    }
    if (ps2x.Analog(PSS_RY) > 240) {
      if (Servo6->readDegrees() > ARM_MIN[6]) {
        Servo6->writeServo((Servo6->readDegrees() - 1));
      }

    } else if (ps2x.Analog(PSS_RY) < 10) {
      if (Servo6->readDegrees() < ARM_MAX[6]) {
        Servo6->writeServo((Servo6->readDegrees() + 1));
      }
    }
    if (ps2x.Analog(PSS_RX) > 240) {
      if (Servo7->readDegrees() > ARM_MIN[7]) {
        Servo7->writeServo((Servo7->readDegrees() - 1));
      }

    } else if (ps2x.Analog(PSS_RX) < 10) {
      if (Servo7->readDegrees() < ARM_MAX[7]) {
        Servo7->writeServo((Servo7->readDegrees() + 1));
      }
    }

  } else {
    if (ps2x.Analog(PSS_LX) > 240) {
      if (Servo0->readDegrees() > ARM_MIN[0]) {
        Servo0->writeServo((Servo0->readDegrees() - 1));
      }

    } else if (ps2x.Analog(PSS_LX) < 10) {
      if (Servo0->readDegrees() < ARM_MAX[0]) {
        Servo0->writeServo((Servo0->readDegrees() + 1));
      }
    }
    if (ps2x.Analog(PSS_LY) > 240) {
      if (Servo1->readDegrees() > ARM_MIN[1]) {
        Servo1->writeServo((Servo1->readDegrees() - 1));
      }

    } else if (ps2x.Analog(PSS_LY) < 10) {
      if (Servo1->readDegrees() < ARM_MAX[1]) {
        Servo1->writeServo((Servo1->readDegrees() + 1));
      }
    }
    if (ps2x.Analog(PSS_RY) > 240) {
      if (Servo2->readDegrees() > ARM_MIN[2]) {
        Servo2->writeServo((Servo2->readDegrees() - 1));
      }

    } else if (ps2x.Analog(PSS_RY) < 10) {
      if (Servo2->readDegrees() < ARM_MAX[2]) {
        Servo2->writeServo((Servo2->readDegrees() + 1));
      }
    }
    if (ps2x.Analog(PSS_RX) > 240) {
      if (Servo3->readDegrees() > ARM_MIN[3]) {
        Servo3->writeServo((Servo3->readDegrees() - 1));
      }

    } else if (ps2x.Analog(PSS_RX) < 10) {
      if (Servo3->readDegrees() < ARM_MAX[3]) {
        Servo3->writeServo((Servo3->readDegrees() + 1));
      }
    }
    delay(2);

  }

}