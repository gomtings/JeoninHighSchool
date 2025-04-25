const int sensorPin = 34; // ESP32의 아날로그 입력 핀
void setup() {
    Serial.begin(115200);
}
void loop() {
    int sensorValue = analogRead(sensorPin);
    Serial.print("value : ");
    Serial.println(sensorValue);
    delay(500);
}