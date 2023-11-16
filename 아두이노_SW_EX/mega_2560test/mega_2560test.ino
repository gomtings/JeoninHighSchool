#include <SoftwareSerial.h>
SoftwareSerial serial2(11,12); //15번을 RX, 14번을 TX, 처럼 사용할 수 있게 핀지정
int echo =9;
int trig = 10;
unsigned long duration = 0;
double distance= 0;
void setup() {
  serial2.begin(9600);  //아두이노와 통신할 소프트웨어 시리얼 시작
  Serial.begin(9600);  //PC와 통신할 하드웨어 시리얼 시작
  pinMode(trig,OUTPUT);
  pinMode(echo,INPUT);
  digitalWrite(trig,LOW);
  digitalWrite(echo,LOW);
}
//write() 함수가 바이트 또는 바이트의 시퀀스를 그대로 보내는 반면, print() 함수는 데이터를 사람이 읽을 수 있는 ASCII 텍스트로 변환하여 보낸다
void loop() {
  delay(1);
  digitalWrite(trig,HIGH);
  delay(1);
  digitalWrite(trig,LOW);
  duration = pulseIn(echo,HIGH);
  distance =  (duration/29.0)/2.0;
  if (serial2.available()) {  // 소프트웨어 시리얼 포트에 데이터가 있는지 확인
    char ch = serial2.read();  // 데이터를 읽음
    if (ch == 'g') {  // 읽은 데이터가 'g'인지 확인 맞다면 센서 데이터를 전송한다.
      serial2.println(distance);
      Serial.println(distance);
    }
  }
  delay(10);
}
