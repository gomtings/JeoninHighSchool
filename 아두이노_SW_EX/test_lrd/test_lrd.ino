#include <SoftwareSerial.h>
SoftwareSerial serial2(5, 6);  // 5번을 RX, 6번을 TX 처럼 사용할 수 있게 핀지정
bool start = true; 
void setup() {
  serial2.begin(9600);  //아두이노와 통신할 소프트웨어 시리얼 시작
  Serial.begin(9600);    //PC와 통신할 하드웨어 시리얼 시작
}

void loop() {
  //delay(1000);
  if(start){
    serial2.write(100);//다른 아두이노로 전송
    start = false;
  }
  if (serial2.available()) { //다른 아두이노에서 온 데이터가 있다면
    String a = serial2.readString();
    Serial.println(a);//시리얼 모니터에 표기
  }
  delay(10);
}
//[출처] 아두이노 시리얼 통신(UART) 무작정해보기|작성자 GONGZIPSA
