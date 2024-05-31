#include <SoftwareSerial.h>
const int nPin_BTTx = 2; //전송
const int nPin_BTRx = 3; //수신
SoftwareSerial BTSerial(nPin_BTTx, nPin_BTRx); // RX, TX
void setup() {
  Serial.begin(9600);
  BTSerial.begin(9600);
  Serial.println("START"); 
}
void loop() {
  if (BTSerial.available())
        Serial.write(BTSerial.read());
  if (Serial.available())
        BTSerial.write(Serial.read());
}