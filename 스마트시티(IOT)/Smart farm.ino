#include "DHT.h"
#include <DigitShield.h>

#define DHTPIN 12
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

int motor = 10;
int water_01 = 0 ;
int water_02 = 0 ;

unsigned long lastUpdate = 0;   // 마지막으로 표시한 시간
int displayState = 0;           // 현재 표시 상태 (0=습도, 1=온도, 2=수분1, 3=수분2)
const unsigned long interval = 2000; // 2초마다 값 변경


void setup() {
  Serial.begin(9600);
  DigitShield.begin();
  dht.begin();

  pinMode(motor, OUTPUT);
}
void loop() {  
  // 일정 주기로 표시 값 변경
  unsigned long now = millis();
  if (now - lastUpdate >= interval) {
    lastUpdate = now;
    displayState = (displayState + 1) % 4; // 0~3 반복
  }

  float h = dht.readHumidity();
  float t = dht.readTemperature();
  float f = dht.readTemperature(true);
  float hif = dht.computeHeatIndex(f, h);
  float hic = dht.computeHeatIndex(t, h, false);

  water_01 = analogRead(A3);
  water_02 = analogRead(A4);

  if (water_01 > 800) {
    digitalWrite(motor, HIGH);
    Serial.println("motor on");
  }
  else {
    digitalWrite(motor, LOW);
    Serial.println("motor off");
  }

  // 현재 상태에 따라 DigitShield에 표시
  switch (displayState) {
    case 0:
      DigitShield.setValue(h);      // 습도
      Serial.print("Humidity: ");
      Serial.print(h);
      Serial.print("% ");
      break;
    case 1:
      DigitShield.setValue(hic);      // 온도
        Serial.print("Temperature: ");
        Serial.print(hic);
        Serial.println("C");
      break;
    case 2:
      DigitShield.setValue(water_01); // 토양 수분 1
      Serial.print("Soil humidity 01: ");
      Serial.println(water_01);
      break;
    case 3:
      DigitShield.setValue(water_02); // 토양 수분 2
      Serial.print("Soil humidity 02: ");
      Serial.println(water_02);
      break;
  }
}