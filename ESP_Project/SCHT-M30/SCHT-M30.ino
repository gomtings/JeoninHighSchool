#include <Wire.h>

#define SENSOR_ADDR 0x44 // SCHT-M30 기본 I2C 주소

void setup() {
    Serial.begin(115200);
    Wire.begin();
}

void loop() {
    Wire.beginTransmission(SENSOR_ADDR);
    Wire.write(0x2C); // 측정 명령
    Wire.write(0x06);
    Wire.endTransmission();
    delay(500);

    Wire.requestFrom(SENSOR_ADDR, 6);
    if (Wire.available() == 6) {
        uint16_t temp_raw = (Wire.read() << 8) | Wire.read();
        Wire.read(); // CRC 무시
        uint16_t hum_raw = (Wire.read() << 8) | Wire.read();
        Wire.read(); // CRC 무시

        float temperature = -45 + (175 * (temp_raw / 65535.0));
        float humidity = 100 * (hum_raw / 65535.0);

        Serial.print("Temperature: ");
        Serial.print(temperature);
        Serial.print(" °C, Humidity: ");
        Serial.print(humidity);
        Serial.println(" %");
    }
    delay(2000);
}