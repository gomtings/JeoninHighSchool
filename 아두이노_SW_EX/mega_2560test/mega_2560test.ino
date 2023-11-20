#include <ArduinoJson.h> //ArduinoJson 라이브러리
#include <TimerOne.h> // TimerOne 라이브러리
#include <SoftwareSerial.h>
SoftwareSerial serial2(11,12); //15번을 RX, 14번을 TX, 처럼 사용할 수 있게 핀지정

#define SANSING_TIME 100
int32_t sansingTime = 0;
bool IssansingTime = false;
#define SAND_TIME 100
int32_t sandTime = 0;
bool IssandeTime = false;

int echo =9;
int trig = 10;
unsigned long duration = 0;
double distance= 0;
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
  pinMode(trig,OUTPUT);
  pinMode(echo,INPUT);
  digitalWrite(trig,LOW);
  digitalWrite(echo,LOW);
  Timer1.initialize(1000); // 1ms마다 인터럽트 발생
  Timer1.attachInterrupt(mainTimer); // 인터럽트 함수 지정
}
//write() 함수가 바이트 또는 바이트의 시퀀스를 그대로 보내는 반면, print() 함수는 데이터를 사람이 읽을 수 있는 ASCII 텍스트로 변환하여 보낸다
void loop() {
 if(IssansingTime == true){
    ultrasonic();
    sansingTime = 0;
    IssansingTimeTime = false;
 }else if(IssandeTime == true){
    sandjson();
    sandTime = 0;
    IssandeTime = false;
 }
  ReadData();
}

void ultrasonic(){
  delay(1);
  digitalWrite(trig,HIGH);
  delay(1);
  digitalWrite(trig,LOW);
  duration = pulseIn(echo,HIGH);
  distance =  (duration/29.0)/2.0;
}
void sandjson(){
      StaticJsonDocument<200> doc;
      doc["distance"] = distance;
      doc["Lidar"] = 0;
      serializeJson(doc, serial2);
      serial2.println();
}
void ReadData(){
  if (serial2.available()) {  // 소프트웨어 시리얼 포트에 데이터가 있는지 확인
    char ch = serial2.read();  // 데이터를 읽음
    if (ch == 'g') {  // 읽은 데이터가 'g'인지 확인 맞다면 센서 데이터를 전송한다.
      sandjson()
    }
  }
  delay(10);
}
