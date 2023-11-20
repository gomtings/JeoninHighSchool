#include <ArduinoJson.h> //ArduinoJson 라이브러리
#include <TimerOne.h> // TimerOne 라이브러리
#include <SoftwareSerial.h>
SoftwareSerial serial2(5, 6);  // 5번을 RX, 6번을 TX 처럼 사용할 수 있게 핀지정

#define SAND_TIME 100
int32_t sandTime = 0;
bool IssandeTime = false;

void mainTimer(void);
void mainTimer(void){
  if(IssansingTime == false)
  {
    sansingTime++;
    if(sansingTime >= SANSING_TIME) IssansingTime = true;
  }
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
    sandjson();
    sandTime = 0;
    IssandeTime = false;
  }
}
void ReadData(){
  serial2.write('g'); // 'g' 라는 문자를 보내서 상대측에게 데이터 요청.
  if (serial2.available()) {  // 소프트웨어 시리얼 포트에 데이터가 있는지 확인
    float distance = serial2.parseFloat();  // 부동 소수점 숫자를 읽음
    Serial.print("Received distance: ");
    Serial.println(distance);
  }
  delay(10);
}
void parseJson() {
  StaticJsonDocument<200> doc;
  DeserializationError error = deserializeJson(doc, Serial2);

  if (error) {
    Serial2.println("Failed to read from serial port");
    return;
  }

  if (doc.containsKey("distance")) {
    int distance = doc["distance"];
    Serial2.println(distance);
  }

  if (doc.containsKey("Lidar")) {
    int Lidar = doc["Lidar"];
    Serial2.println(Lidar);
  }
}
