#include <ArduinoJson.h> //ArduinoJson 라이브러리
#include <TimerOne.h> // TimerOne 라이브러리
#include "QGPMaker_MotorShield.h"
#include <Wire.h>
#define slave_addr 0x01

char MsgBuf[100]; //Master로 부터 전송받은 데이터를 저장할 버퍼
volatile byte pos;
volatile boolean Check_Data = false;

// Create the motor shield object with the default I2C address
QGPMaker_MotorShield AFMS = QGPMaker_MotorShield();

// Select which 'port' M1, M2, M3 or M4. In this case, M3
QGPMaker_DCMotor *DCMotor_1 = AFMS.getMotor(6);
QGPMaker_DCMotor *DCMotor_2 = AFMS.getMotor(7);
QGPMaker_DCMotor *DCMotor_3 = AFMS.getMotor(8);
QGPMaker_DCMotor *DCMotor_4 = AFMS.getMotor(9);

// speed : 0 ~ 255
int speed = 100;

uint16_t space,strength;

#define LED 13
#define SAND_TIME 100
int32_t sandTime = 0;
bool IssandeTime = false;

double distance1 = 0.00; // 2번 초음파 값
double distance2 = 0.00; // 2번 초음파 값
double Lidar = 0.00; // 라이다 값
float heading = 0.0f; //float 값에는 f가 붙음, 9축 지자기 센서 값
float tiltheading = 0.0f;
void mainTimer(void);

void mainTimer(void){
  if(IssandeTime == false)
  {
    sandTime++;
    if(sandTime >= SAND_TIME) IssandeTime = true;
  }
}
void setup() {
  Wire.begin(slave_addr); //slave_addr의 주소값을 갖는 slave로 동작
  Wire.onReceive(Receive_Int); //Master에서 보낸 데이터를 수신했을때 호출할 함수를 등록

  Serial.begin(9600);  //아두이노와 통신할 소프트웨어 시리얼 시작
  Timer1.initialize(1000); // 1ms마다 인터럽트 발생
  Timer1.attachInterrupt(mainTimer); // 인터럽트 함수 지정
  AFMS.begin(50); // create with the default frequency 50Hz
  
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
void Receive_Int() { //Master에서 보낸 데이터가 수신되면 호출되는 함수
  byte m;
  
  while(Wire.available()){ //읽어올 데이터가 있다면
    m = Wire.read(); 
    if(pos < sizeof(MsgBuf)){
      MsgBuf[pos++] = m; //데이터를 버퍼에 저장합니다.
    }
    if(m =='\n'){ // 개행 문자 인식 -> 데이터 정상 수신 확인.
      Check_Data = true; 
    }
  } 
}
void ReadData(){
  delay(1); // listen 함수 호출 후에 약간의 지연을 추가합니다.
  //Serial.write('g'); // 'g' 라는 문자를 보내서 상대측에게 데이터 요청.

  /*unsigned long startTime = millis(); // 현재 시간을 저장합니다.
  while(!Serial.available()) {  // 소프트웨어 시리얼 포트에 데이터가 있는지 확인
    if (millis() - startTime > 3000) { // 1초 동안 데이터가 도착하지 않으면 루프를 종료 오류가 발생할 경우 시간을 늘려야 함. (아두이노간 통신 타이밍 문제 해결)
      Serial.println("Timeout waiting for data");
      return;
    }
  }
  StaticJsonDocument<256> doc;
  DeserializationError error = deserializeJson(doc, Serial);
  if (error) {
    Serial.println("Failed to read from serial port");
    IssandeTime = false;
    return;
  }*/
  if(Check_Data == true){
    StaticJsonDocument<256> doc;
    DeserializationError error = deserializeJson(doc, MsgBuf);
    //Serial.print(MsgBuf);
    distance1 = doc["distance1"];
    distance2 = doc["distance2"];
    Lidar = doc["Lidar"];
    heading = doc["heading"];
    tiltheading = doc["tiltheading"];

    Serial.println("초음파1:");
    Serial.println(distance1);
    Serial.println("초음파2:");
    Serial.println(distance2);
    Serial.println("라이다:");
    Serial.println(Lidar);
    Serial.println("heading:");
    Serial.println(heading);
    Serial.println("tiltheading:");
    Serial.println(tiltheading);
    MsgBuf[pos] = 0;
    pos =0 ;
    Check_Data = false;
  }
}
/*
void ReadData(){
  Serial.listen(); //
  Serial.write('g'); // 'g' 라는 문자를 보내서 상대측에게 데이터 요청.
  if (Serial.available()) {  // 소프트웨어 시리얼 포트에 데이터가 있는지 확인
    StaticJsonDocument<256> doc;
    DeserializationError error = deserializeJson(doc, Serial);
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
//RC카 제어
void forward(int speed) { 
  DCMotor_1->setSpeed(speed);
  DCMotor_1->run(FORWARD);
  DCMotor_2->setSpeed(speed);
  DCMotor_2->run(FORWARD);
  DCMotor_3->setSpeed(speed);
  DCMotor_3->run(FORWARD);
  DCMotor_4->setSpeed(speed);
  DCMotor_4->run(FORWARD);
}
void backward(int speed) { 
  DCMotor_1->setSpeed(speed);
  DCMotor_1->run(BACKWARD);
  DCMotor_2->setSpeed(speed);
  DCMotor_2->run(BACKWARD);
  DCMotor_3->setSpeed(speed);
  DCMotor_3->run(BACKWARD);
  DCMotor_4->setSpeed(speed);
  DCMotor_4->run(BACKWARD);
}
void move_left(int speed) { 
  DCMotor_1->setSpeed(speed);
  DCMotor_1->run(BACKWARD);
  DCMotor_2->setSpeed(speed);
  DCMotor_2->run(FORWARD);
  DCMotor_3->setSpeed(speed);
  DCMotor_3->run(BACKWARD);
  DCMotor_4->setSpeed(speed);
  DCMotor_4->run(FORWARD);
}
void move_right(int speed) { 
  DCMotor_1->setSpeed(speed);
  DCMotor_1->run(FORWARD);
  DCMotor_2->setSpeed(speed);
  DCMotor_2->run(BACKWARD);
  DCMotor_3->setSpeed(speed);
  DCMotor_3->run(FORWARD);
  DCMotor_4->setSpeed(speed);
  DCMotor_4->run(BACKWARD);
}
void turn_left(int speed) { 
  DCMotor_1->setSpeed(speed);
  DCMotor_1->run(BACKWARD);
  DCMotor_2->setSpeed(speed);
  DCMotor_2->run(BACKWARD);
  DCMotor_3->setSpeed(speed);
  DCMotor_3->run(FORWARD);
  DCMotor_4->setSpeed(speed);
  DCMotor_4->run(FORWARD);
}
void turn_right(int speed) { 
  DCMotor_1->setSpeed(speed);
  DCMotor_1->run(FORWARD);
  DCMotor_2->setSpeed(speed);
  DCMotor_2->run(FORWARD);
  DCMotor_3->setSpeed(speed);
  DCMotor_3->run(BACKWARD);
  DCMotor_4->setSpeed(speed);
  DCMotor_4->run(BACKWARD);
}
void stop(int delay_time) {
  DCMotor_1->setSpeed(0);
  DCMotor_1->run(RELEASE);
  DCMotor_2->setSpeed(0);
  DCMotor_2->run(RELEASE);
  DCMotor_3->setSpeed(0);
  DCMotor_3->run(RELEASE);
  DCMotor_4->setSpeed(0);
  DCMotor_4->run(RELEASE);
  delay(delay_time);
}



