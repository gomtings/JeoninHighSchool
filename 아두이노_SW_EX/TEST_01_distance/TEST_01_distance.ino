#include <Servo.h>
int led = 13;
int echo =12;
int trig = 11;

int servo = 9;
Servo motor;
void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(led,OUTPUT);
  pinMode(trig,OUTPUT);
  pinMode(echo,INPUT);

  motor.attach(servo);
}

void loop() {
  // put your main code here, to run repeatedly:
  digitalWrite(trig,LOW);
  digitalWrite(echo,LOW);
  delay(1);
  digitalWrite(trig,HIGH);
  delay(1);
  digitalWrite(trig,LOW);
  unsigned long duration = pulseIn(echo,HIGH);
  float distance =  duration / 29.0/2.0;

  Serial.print(distance);Serial.println("cm");
  if(distance <= 20){
      digitalWrite(led,HIGH);
  }else{
   digitalWrite(led,LOW);
   motor.write(0);
   delay(100);
   motor.write(180);
   delay(100);
   motor.write(0);
   delay(100);
   motor.write(180);
   delay(100);
   }
}
