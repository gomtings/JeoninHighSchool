#include <SoftwareSerial.h>

SoftwareSerial esp8266(2, 3); // RX, TX
bool success = false;

String ssids[] = {"Solimatics", "Solimatics", "Solimatics", "Solimatics"}; // 검색하려는 AP의 SSID들

double calculateDistance(int rssi);

void setup(){
  Serial.begin(9600);
  esp8266.begin(9600);
  
  esp8266.write("AT\r\n"); // 통신 테스트...
  delay(1000); // ESP8266 모듈이 응답하는 데 필요한 시간을 기다립니다.
  while (esp8266.available()) { // 응답이 도착하면 읽습니다.
    String response = esp8266.readString();
    if (response.indexOf("OK") >= 0) { // 응답이 "OK"를 포함하면 다음 명령을 실행합니다.
      esp8266.write("AT+CWMODE?\r\n"); // 현재 모드 확인.
      delay(1000);
      while (esp8266.available()) { // Station 모드 여부 확인...
        response = esp8266.readString();
        if (response.indexOf("+CWMODE:1") >= 0) { // 이미 Station 모드인 경우
          Serial.print("이미 스테이션 모드 입니다. \n");
          success = true;
          esp8266.write("AT+CWLAP\r\n"); // 주변 AP 검색..
          delay(1000);
        } else { // Station 모드가 아닌 경우
          esp8266.write("AT+CWMODE=1\r\n"); // Station 모드 전환.
          delay(1000);
          while (esp8266.available()) { // Station 모드 전환 OK?
            response = esp8266.readString();
            if (response.indexOf("OK") >= 0) {
                Serial.print("스테이션 모드 전환 완료.\n");
                success = true;
                esp8266.write("AT+CWLAP\r\n"); // 주변 AP 검색..
                delay(1000);
            }
          }
        }
        // 이후에는 필요에 따라 추가적인 처리를 수행합니다.
      }
    }else{
        Serial.print("응답이 없습니다..\n");
        success = false;
    }
  }
}
void loop(){
    if(success){
        while (esp8266.available()) { // AP 검색 결과 읽기...
          String response = esp8266.readString();
          for (int i = 0; i < sizeof(ssids)/sizeof(ssids[0]); i++) {
            int ssidIndex = response.indexOf(ssids[i]);
            if (ssidIndex >= 0) { // 원하는 AP를 찾았다면...
              int rssiStartIndex = response.indexOf(",", ssidIndex) + 1;
              int rssiEndIndex = response.indexOf(",", rssiStartIndex);
              String rssi = response.substring(rssiStartIndex, rssiEndIndex);
              double dist = calculateDistance(rssi.toInt());
              Serial.print("Distance to ");
              Serial.print(rssi);
              Serial.print(": ");
              Serial.println(dist);
              esp8266.write("AT+CWLAP\r\n"); // 주변 AP 검색..
            }
          }
        }
    }
}

double calculateDistance(int rssi) {
  int txPower = -30; //1미터 거리에서 RSSI 값
  double n = 2.0; // 이것은 경로 손실 지수이며, 일반적으로 2.7에서 4.3 사이의 범위
  return pow(10, ((double)txPower - rssi) / (10 * n));
}