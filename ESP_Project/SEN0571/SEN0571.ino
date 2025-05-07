const int sensorPin = 34; // ESP32의 아날로그 입력 핀
int sensorValue = 0;
void setup() {
    Serial.begin(115200);
}
void loop() {
    sensorValue = analogRead(sensorPin);
    Serial.print("SEN0571 : ");
    Serial.println(sensorValue);
    delay(1000);
}