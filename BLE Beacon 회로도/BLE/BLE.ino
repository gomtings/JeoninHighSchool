#include <SoftwareSerial.h>

SoftwareSerial mySerial(8, 9); // RX, TX

void setup() {
  Serial.begin(9600);
  mySerial.begin(9600);
  Serial.println("BLE 장치 이름 설정 ");
  mySerial.print("AT+NAMEJEONIN_BLE"); // JEONIN_BLE 로 설정함;.
  delay(500);
  while (mySerial.available()) {
    char c = mySerial.read();
    Serial.write(c);
  }
  Serial.println("BLE 장치 초기화 완료..");
}

void loop() {
  // Read RSSI value from HM-10 module
  mySerial.println("AT+RSSI?");
  //delay(500);
  if (mySerial.available()) {
    String rssi = mySerial.readString();
    Serial.print("RSSI: ");
    Serial.println(rssi);

    // Calculate distance from RSSI value
    int rssiVal = rssi.toInt();
    double distance = pow(10, ((-69 - (rssiVal))/(10 * 2)));
    Serial.print("Distance: ");
    Serial.println(distance);

    // Advertise RSSI value and distance
    mySerial.print("AT+ADVDATA=");
    mySerial.print("RSSI: ");
    mySerial.print(rssi);
    mySerial.print(", Distance: ");
    mySerial.println(distance);
  }
}