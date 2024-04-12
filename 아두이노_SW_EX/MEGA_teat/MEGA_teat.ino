//메가
#include <Wire.h>
#define slave_addr 0x01
#include <ArduinoJson.h> //ArduinoJson 라이브러리
#include <TimerOne.h> // TimerOne 라이브러리
#include <SoftwareSerial.h>
#include <DFRobot_TFmini.h>
#include <SparkFun_ADXL345.h>  // https://github.com/sparkfun/SparkFun_ADXL345_Arduino_Library
#include "Wire.h"
#include "I2Cdev.h"
#include "MPU9250.h"

const char *p = "Data Transfer to Slave\n";


SoftwareSerial mySerial(10,11); // RX, TX
DFRobot_TFmini  TFmini;

#define SANSING_TIME 20 // 초음파
int32_t sansingTime = 0;
bool IssansingTime = false;
#define READ_TIME 100 // 데이터 읽기
int32_t readTime = 0;
bool IsreadTime = false;

// 초음파 센서
int echoPin1 = 2;
int trigPin1 = 3;
int echoPin2 = 4;
int trigPin2 = 5;
unsigned long duration1 = 0;
unsigned long duration2 = 0;
double distance1= 0;
double distance2= 0;

void mainTimer(void){
  if(IssansingTime == false) // 초음파
  {
    sansingTime++;
    if(sansingTime >= SANSING_TIME) IssansingTime = true;
  }
}
void setup() {
  Wire.begin(); // I2C통신을 위한 초기화함수, 인자로 아무것도 넣지 않으면 Master로 동작, 주소값을 넣어주면 해당 주소의 Slave로 동작합니다.
  Serial.begin(9600);  //PC와 통신할 하드웨어 시리얼 시작
  delay(1);
  //각종 핀 설정...
  pinMode(trigPin1,OUTPUT);
  pinMode(echoPin1,INPUT);
  pinMode(trigPin2,OUTPUT);
  pinMode(echoPin2,INPUT);
  digitalWrite(trigPin1,LOW);
  digitalWrite(echoPin1,LOW);
  digitalWrite(trigPin2,LOW);
  digitalWrite(echoPin2,LOW);
}

void loop() {
  StaticJsonDocument<256> doc;
  doc["distance1"] = distance1; // 1번 초음파 센서 
  doc["distance2"] = distance2; //2번 초음파 센서
  Wire.beginTransmission(slave_addr); // 인자로 전달한 주소의 Slave로 데이터 전송을 시작합니다.
  for (int i = 0 ; i < strlen(p); i++) {
    Wire.write(p[i]); //"Data Trnasfer to Slave"문자열을 버퍼에 기록합니다.
  }
  Wire.endTransmission(); //write함수에 의해 버퍼에 기록된 데이터를 전송하고 통신을 마칩니다.
  delay(1000);
  if(IssansingTime == true){
    ultrasonic();
    sansingTime = 0;
    IssansingTime = false;
  }
}

void ultrasonic(){
  //1번 초음파
  delay(1);
  digitalWrite(trigPin1,HIGH);
  delay(1);
  digitalWrite(trigPin1,LOW);
  duration1 = pulseIn(echoPin1,HIGH);
  distance1 =  (duration1/29.0)/2.0;
  //2번 초음파
  delay(1);
  digitalWrite(trigPin2,HIGH);
  delay(1);
  digitalWrite(trigPin2,LOW);
  duration2 = pulseIn(echoPin2,HIGH);
  distance2 =  (duration2/29.0)/2.0;
  //Serial.println(distance1);
  //Serial.println(distance2);
}

