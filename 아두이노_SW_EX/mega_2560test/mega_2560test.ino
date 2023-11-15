#include <SoftwareSerial.h>
SoftwareSerial serial2(12,11); //15번을 RX, 14번을 TX, 처럼 사용할 수 있게 핀지정
int echo =9;
int trig = 10;
bool start = false;
void setup() {
  serial2.begin(9600);  //아두이노와 통신할 소프트웨어 시리얼 시작
  Serial.begin(9600);  //PC와 통신할 하드웨어 시리얼 시작
  pinMode(trig,OUTPUT);
  pinMode(echo,INPUT);
  digitalWrite(trig,LOW);
  digitalWrite(echo,LOW);
}
void loop() {
  delay(1);
  digitalWrite(trig,HIGH);
  delay(1);
  digitalWrite(trig,LOW);
  unsigned long duration = pulseIn(echo,HIGH);
  double distance =  (duration/29.0)/2.0;
  int ch = serial2.read();
  if(ch >= -1){
    serial2.print(distance);
  }
  delay(10);
}
