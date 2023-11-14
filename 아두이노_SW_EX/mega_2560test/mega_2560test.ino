#include <SoftwareSerial.h>
SoftwareSerial serial2(11,12); //15번을 RX, 14번을 TX, 처럼 사용할 수 있게 핀지정
int echo =9;
int trig = 10;
bool flag = false; 
int count = 0;
String str = "";
void setup() {
  Serial.begin(9600);    //PC와 통신할 하드웨어 시리얼 시작
  serial2.begin(9600);  //아두이노와 통신할 소프트웨어 시리얼 시작
  pinMode(trig,OUTPUT);
  pinMode(echo,INPUT);
}

void loop() {
  digitalWrite(trig,LOW);
  digitalWrite(echo,LOW);
  delay(1);
  digitalWrite(trig,HIGH);
  delay(1);
  digitalWrite(trig,LOW);
  unsigned long duration = pulseIn(echo,HIGH);
  float distance =  duration / 29.0/2.0;
  str = String(distance);
  if (serial2.available()||Serial.available()) {//시리얼 모니터에서 들어온 데이터가 있다면
    flag = true;
  }
  if(flag){
        serial2.println(str);//시리얼 모니터에 표기
        Serial.println(str);
   }
  delay(10);
}
//[출처] 아두이노 시리얼 통신(UART) 무작정해보기|작성자 GONGZIPSA
