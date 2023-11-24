#include <Stepper.h>

const int STEPS = 2048;
Stepper stepper(STEPS, 8,9,10,11);

void setup() {
  // put your setup code here, to run once:
  stepper.setSpeed(14);
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
   if(Serial.available()) {
    int val=Serial.parseInt(); //회전각 int형으로 읽기
     
    val=map(val,0,360,0,2048); //회전각 스템 수
    stepper.step(val);
    Serial.println(val);
    delay(10);
  }
}
