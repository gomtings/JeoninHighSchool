#include <Wire.h>
#include <ArduinoJson.h> //ArduinoJson 라이브러리
#define slave_addr 0x01

const char *p = "Data Transfer to Slave\n";

void setup() {
  Wire.begin(); // I2C통신을 위한 초기화함수, 인자로 아무것도 넣지 않으면 Master로 동작, 주소값을 넣어주면 해당 주소의 Slave로 동작합니다.
  Serial.begin(9600);
  Wire.setClock(400000); // 클럭 속도를 400kHz로 설정
}

void loop() {
    StaticJsonDocument<256> doc;
    doc["distance1"] = 0; // 1번 초음파 센서 
    doc["distance2"] = 0; //2번 초음파 센서
    doc["Lidar"] = 0; // 라이다 센서 
    doc["tiltheading"] = 0; // 여기서 부터 가속도 센서.
    doc["heading"] = 0;
    char output[256]; // 문자 배열 선언
    serializeJson(doc, output); // JSON 문자열을 문자 배열에 저장
    strcat(output, "\n"); // 문자열 끝에 개행 문자 추가

    const int maxChunkSize = 32; // 한 번에 전송할 수 있는 최대 바이트 수
    int outputLength = strlen(output); // 전체 문자열의 길이
    int sentBytes = 0; // 지금까지 전송한 바이트 수

    while (sentBytes < outputLength) {
        Wire.beginTransmission(slave_addr); // 인자로 전달한 주소의 Slave로 데이터 전송을 시작합니다.
        for (int i = 0; i < maxChunkSize && sentBytes < outputLength; i++) {
            Wire.write(output[sentBytes++]); // 문자열의 일부를 버퍼에 기록합니다.
        }
        Wire.endTransmission(); // write 함수에 의해 버퍼에 기록된 데이터를 전송하고 통신을 마칩니다.
    }
    delay(1000);
} 
