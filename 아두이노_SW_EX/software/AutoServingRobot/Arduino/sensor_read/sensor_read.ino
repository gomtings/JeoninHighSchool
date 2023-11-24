#include <Servo.h>

const int trigPin = 9;  // 초음파 센서의 Trig 핀
const int echoPin = 8;  // 초음파 센서의 Echo 핀
Servo myservo;          // 서보모터 객체

void setup() {
  Serial.begin(9600);
  myservo.attach(10);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
}

void loop() {
  long duration, distance;
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  duration = pulseIn(echoPin, HIGH);
  distance = duration * 0.034 / 2;
  
  Serial.println(distance);

  if (distance < 50) {
    myservo.write(90);
    } else {
    myservo.write(0);
  }

  delay(100); 
}
