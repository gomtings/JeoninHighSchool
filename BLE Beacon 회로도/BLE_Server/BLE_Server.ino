#include <SoftwareSerial.h>

SoftwareSerial mySerial(A4, A5); // RX, TX

void setup() {
  Serial.begin(9600);
  mySerial.begin(9600);
  Serial.println("BLE 장치 이름 설정 ");
  mySerial.print("AT+NAMEMASTER_BLE"); // JEONIN_BLE 로 설정함;.
  delay(500);
  while (mySerial.available()) {
    char c = mySerial.read();
    Serial.write(c);
  }
  Serial.println("BLE 장치 초기화 완료..");
  mySerial.print("AT+ROLE1"); // Set the HM-10 as Master
  delay(500);
}

void loop() {
  mySerial.print("AT+DISC?"); // Discover nearby devices
  delay(100);
  while (mySerial.available()) {
    char c = mySerial.read();
    Serial.write(c);
  }
}