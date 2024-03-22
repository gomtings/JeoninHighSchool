#include <ArduinoJson.h> //ArduinoJson 라이브러리
#include <TimerOne.h> // TimerOne 라이브러리
#include <SoftwareSerial.h>
SoftwareSerial serial2(11, 12);  // 5번을 RX, 6번을 TX 처럼 사용할 수 있게 핀지정
uint16_t space,strength;

#define SAND_TIME 100
int32_t sandTime = 0;
bool IssandeTime = false;

double distance1 = 0.00; // 2번 초음파 값
double distance2 = 0.00; // 2번 초음파 값
double Lidar = 0.00; // 라이다 값
int x,y,z; // 가속도 센서 XYZ축을 설정합니다.
void mainTimer(void);
void mainTimer(void){
  if(IssandeTime == false)
  {
    sandTime++;
    if(sandTime >= SAND_TIME) IssandeTime = true;
  }
}
void setup() {
  serial2.begin(9600);  //아두이노와 통신할 소프트웨어 시리얼 시작
  Serial.begin(9600);  //PC와 통신할 하드웨어 시리얼 시작
  Timer1.initialize(1000); // 1ms마다 인터럽트 발생
  Timer1.attachInterrupt(mainTimer); // 인터럽트 함수 지정
}
//write() 함수가 바이트 또는 바이트의 시퀀스를 그대로 보내는 반면, print() 함수는 데이터를 사람이 읽을 수 있는 ASCII 텍스트로 변환하여 보낸다
void loop() {
  if(IssandeTime == true){
    ReadData();
    sandTime = 0;
    IssandeTime = false;
    delay(1000);
  }
}
void ReadData(){
  serial2.listen(); //
  delay(1); // listen 함수 호출 후에 약간의 지연을 추가합니다.
  serial2.write('g'); // 'g' 라는 문자를 보내서 상대측에게 데이터 요청.

  unsigned long startTime = millis(); // 현재 시간을 저장합니다.
  while(!serial2.available()) {  // 소프트웨어 시리얼 포트에 데이터가 있는지 확인
    if (millis() - startTime > 3000) { // 1초 동안 데이터가 도착하지 않으면 루프를 종료 오류가 발생할 경우 시간을 늘려야 함. (아두이노간 통신 타이밍 문제 해결)
      Serial.println("Timeout waiting for data");
      return;
    }
  }

  StaticJsonDocument<256> doc;
  DeserializationError error = deserializeJson(doc, serial2);
  if (error) {
    Serial.println("Failed to read from serial port");
    IssandeTime = false;
    return;
  }
  distance1 = doc["distance1"];
  distance2 = doc["distance2"];
  Lidar = doc["Lidar"];
  x = doc["Accel_x"];
  y = doc["Accel_y"];
  z = doc["Accel_z"];
  Serial.println(distance1);
  Serial.println(distance2);
  Serial.println(Lidar);
  Serial.println(x);
  Serial.println(y);
  Serial.println(z);
}
/*
void ReadData(){
  serial2.listen(); //
  serial2.write('g'); // 'g' 라는 문자를 보내서 상대측에게 데이터 요청.
  if (serial2.available()) {  // 소프트웨어 시리얼 포트에 데이터가 있는지 확인
    StaticJsonDocument<256> doc;
    DeserializationError error = deserializeJson(doc, serial2);
    if (error) {
      Serial.println("Failed to read from serial port");
      IssandeTime = false;
      return;
    }
    distance = doc["distance"];
    Lidar = doc["Lidar"];
    x = doc["Accel_x"];
    y = doc["Accel_y"];
    z = doc["Accel_z"];
    Serial.println(distance);
    Serial.println(Lidar);
    Serial.println(x);
    Serial.println(y);
    Serial.println(z);
  }
}
*/