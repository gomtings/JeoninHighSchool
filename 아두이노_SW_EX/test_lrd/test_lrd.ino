#include <SoftwareSerial.h>
SoftwareSerial serial2(5, 6);  // 5번을 RX, 6번을 TX 처럼 사용할 수 있게 핀지정
void setup() {
  serial2.begin(9600);  //아두이노와 통신할 소프트웨어 시리얼 시작
  Serial.begin(9600);  //PC와 통신할 하드웨어 시리얼 시작
}
void loop() {
    serial2.write(57);
    int ch = serial2.read();
    Serial.print(ch);
   delay(10);
}
