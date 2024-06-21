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
QGPMaker_DCMotor *DCMotor_1 = AFMS.getMotor(1);
QGPMaker_DCMotor *DCMotor_2 = AFMS.getMotor(2);
QGPMaker_DCMotor *DCMotor_3 = AFMS.getMotor(3);
QGPMaker_DCMotor *DCMotor_4 = AFMS.getMotor(4);

// speed : 0 ~ 255
int speed = 30;

char cmd;
char cmd_arr[16];
int inx = 0;
bool success = false;

uint16_t space,strength;

#define LED 13
#define SAND_TIME 200
int32_t sandTime = 0;
bool IssandeTime = false;

double distance1 = 0.00; // 1번 초음파 값
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
  Serial.begin(9600);  //아두이노와 통신할 소프트웨어 시리얼 시작
  Wire.begin(slave_addr); //slave_addr의 주소값을 갖는 slave로 동작
  Wire.onReceive(Receive_Int); //Master에서 보낸 데이터를 수신했을때 호출할 함수를 등록
  Timer1.initialize(1000); // 1ms마다 인터럽트 발생
  Timer1.attachInterrupt(mainTimer); // 인터럽트 함수 지정
  // Serial.println("test1");
  AFMS.begin(50); // create with the default frequency 50Hz

  // Serial.println("test");
  // forward(speed);
  // delay(500);
  // stop(0);
}
//write() 함수가 바이트 또는 바이트의 시퀀스를 그대로 보내는 반면, print() 함수는 데이터를 사람이 읽을 수 있는 ASCII 텍스트로 변환하여 보낸다
void loop() {
  if(IssandeTime == true){
    ReadData();
    sandTime = 0;
    IssandeTime = false;
    // delay(1000);
  
  // 실제로 while문을 사용할 때는 무한 루프에 유의해야 하며, 그렇기에 while문 사용은 별로 추천되지 않는다.
  // 당장은 프로그램 구조가 간단하므로 별 문제없이 사용했다.
  while (Serial.available()) {
    cmd = Serial.read();
    if (cmd == '\n') {
      success = true;
      break;
    }
    cmd_arr[inx++] = cmd;
  }
  cmd_arr[inx] = '\0'; // 문자열의 끝을 표시

  if (success) {
    // Serial.println(cmd_arr);
    if (strcmp(cmd_arr, "forward") == 0) {
      forward(speed);
    }
    else if (strcmp(cmd_arr, "turn_left") == 0) {
      turn_left(speed);
      // delay(2300);
      // forward(speed);
    }
    else if (strcmp(cmd_arr, "turn_right") == 0) {
      turn_right(speed);
      // delay(2300);
      // forward(speed);
    }
    else if (strcmp(cmd_arr, "go_left") == 0) {
      move_left(speed);
    }
    else if (strcmp(cmd_arr, "go_right") == 0) {
      move_right(speed);
    }
    else if (strcmp(cmd_arr, "stop") == 0) {
      stop(0);
    }
    else {
      stop(0);
    }
    success = false;
    inx = 0;
    memset(cmd_arr,NULL, sizeof(cmd_arr));
  }
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
  // delay(1); // listen 함수 호출 후에 약간의 지연을 추가합니다.

  if(Check_Data == true){
    StaticJsonDocument<256> doc;
    DeserializationError error = deserializeJson(doc, MsgBuf);
    if (!error) {
      String jsonString;
      serializeJson(doc, jsonString);
      Serial.println(jsonString);
    } else {
      // test
    }

    MsgBuf[pos] = 0;
    pos =0 ;
    Check_Data = false;
  }
}

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