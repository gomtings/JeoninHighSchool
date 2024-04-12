//우노
#include <ArduinoJson.h> //ArduinoJson 라이브러리
#include <TimerOne.h> // TimerOne 라이브러리
#include "QGPMaker_MotorShield.h"
#include <Wire.h>
#define slave_addr 0x01
#define SAND_TIME 100
char MsgBuf[100]; //Master로 부터 전송받은 데이터를 저장할 버퍼
volatile byte pos;
volatile boolean Print_Int = false;
volatile boolean Check_Data = false;
// Create the motor shield object with the default I2C address
QGPMaker_MotorShield AFMS = QGPMaker_MotorShield();

// speed : 0 ~ 255
int speed = 100;

uint16_t space,strength;
double distance1 = 0.00; // 1번 초음파 값
double distance2 = 0.00; // 2번 초음파 값
int32_t sandTime = 0;
bool IssandeTime = false;

void mainTimer(void);

void mainTimer(void){
  if(IssandeTime == false)
  {
    sandTime++;
    if(sandTime >= SAND_TIME) IssandeTime = true;
  }
}

void setup() {
  Serial.begin(9600);
  Wire.begin(slave_addr); //slave_addr의 주소값을 갖는 slave로 동작
  Wire.onReceive(Receive_Int); //Master에서 보낸 데이터를 수신했을때 호출할 함수를 등록
  Timer1.initialize(1000); // 1ms마다 인터럽트 발생
  Timer1.attachInterrupt(mainTimer); // 인터럽트 함수 지정
  AFMS.begin(50); // create with the default frequency 50Hz
}

void loop() {
  if(Print_Int){
    MsgBuf[pos] = 0;
    Serial.print(MsgBuf);
    pos =0 ;
    Print_Int = false;
  }
  if(IssandeTime == true){
    ReadData();
    sandTime = 0;
    IssandeTime = false;
    delay(1000);
  }
}


void Receive_Int() { //Master에서 보낸 데이터가 수신되면 호출되는 함수
  byte m;
  
  while(Wire.available()){ //읽어올 데이터가 있다면
    m = Wire.read(); 
    if(pos < sizeof(MsgBuf)){
      MsgBuf[pos++] = m; //데이터를 버퍼에 저장합니다.
    }
    if(m =='\n'){ //'\n'문자를 만나면 
      Print_Int = true; //Print_Int를 true로 바꿔주고 loop()문에서 데이터를 출력합니다. 
    }
  } 
}

void ReadData() {
    if(Check_Data == true){
    StaticJsonDocument<256> doc;
    DeserializationError error = deserializeJson(doc, MsgBuf);
    //Serial.print(MsgBuf);
    distance1 = doc["distance1"];
    distance2 = doc["distance2"];
    Serial.println("초음파1:");
    Serial.println(distance1);
    Serial.println("초음파2:");
    Serial.println(distance2);
    MsgBuf[pos] = 0;
    pos =0 ;
    Check_Data = false;
  }
}



