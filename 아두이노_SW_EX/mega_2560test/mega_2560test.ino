#include <ArduinoJson.h> //ArduinoJson 라이브러리
#include <TimerOne.h> // TimerOne 라이브러리
#include <SoftwareSerial.h>
#include <DFRobot_TFmini.h>
#include <SparkFun_ADXL345.h>  // https://github.com/sparkfun/SparkFun_ADXL345_Arduino_Library

SoftwareSerial serial2(11,12); //15번을 RX, 14번을 TX, 처럼 사용할 수 있게 핀 지정
SoftwareSerial mySerial(50,51); // RX, TX
DFRobot_TFmini  TFmini;

#define SANSING_TIME 10 // 초음파
int32_t sansingTime = 0;
bool IssansingTime = false;
#define READ_TIME 100 // 데이터 읽기
int32_t readTime = 0;
bool IsreadTime = false;
#define RADARING_TIME 50 // 라이다
int32_t radaringTime = 0;
bool IsradaringTime = false;
#define ACCEL_TIME 30// 가속도 센서
int32_t AccelingTime = 0;
bool IsAccelingTime = false; 
// 초음파 센서
int echo =9;
int trig = 10;
unsigned long duration = 0;
double distance= 0;
// 라이다 센서
double space,strength;
// ADXL345 
//ADXL345 adxl = ADXL345();    // I2C통신이므로 이렇게 수정해야합니다.
int x,y,z;                     // XYZ축을 설정합니다.

void mainTimer(void);
void mainTimer(void){
  if(IsradaringTime == false) // 라이다 
  {
    radaringTime++;
    if(radaringTime >= RADARING_TIME) IsradaringTime = true;
  }
  if(IssansingTime == false) // 초음파
  {
    sansingTime++;
    if(sansingTime >= SANSING_TIME) IssansingTime = true;
  }
  if(IsreadTime == false) // 데이터읽기
  {
    readTime++;
    if(readTime >= READ_TIME) IsreadTime = true;
  }
  if(IsAccelingTime == false) // 가속도 센서 읽기
  {
    AccelingTime++;
    if(AccelingTime >= ACCEL_TIME) IsAccelingTime = true;
  }
}
void setup() {
  Serial.begin(9600);  //PC와 통신할 하드웨어 시리얼 시작
  serial2.begin(9600);  //아두이노와 통신할 소프트웨어 시리얼 시작
  TFmini.begin(mySerial); // 라이다 센서와 통신할 하드웨어 시리얼 시작 이걸 주석처리 하면.. 동작..???
  pinMode(trig,OUTPUT);
  pinMode(echo,INPUT);
  digitalWrite(trig,LOW);
  digitalWrite(echo,LOW);
  //adxl.powerOn();              // ADXL345을 켭니다.
  //adxl.setRangeSetting(4);     // 2g는 가장높은 감도이고, 4g, 8g,16g는 낮은 감도입니다. 감도를 자유롭게 설정하세요.


  Timer1.initialize(1000); // 1ms마다 인터럽트 발생
  Timer1.attachInterrupt(mainTimer); // 인터럽트 함수 지정
}
//write() 함수가 바이트 또는 바이트의 시퀀스를 그대로 보내는 반면, print() 함수는 데이터를 사람이 읽을 수 있는 ASCII 텍스트로 변환하여 보낸다
void loop() {
 if(IssansingTime == true){
    ultrasonic();
    sansingTime = 0;
    IssansingTime = false;
 }else if(IsradaringTime == true){
    GetRader();
    radaringTime = 0;
    IsradaringTime = false;
 }else if(IsreadTime == true){ // 들어온 데이터를 확인하고 전송함.
    ReadData();
    readTime = 0;
    IsreadTime = false;
 }else if(IsAccelingTime == true){
    //adxl.readAccel(&x, &y, &z);  //  x, y, z를 읽습니다.
    AccelingTime = 0;
    IsAccelingTime = false;
 }
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
      StaticJsonDocument<256> doc;
      doc["distance"] = distance; // 초음파 센서 
      doc["Lidar"] = space; // 라이다 센서 
      doc["Accel_x"] = x; // 여기서 부터 가속도 센서.
      doc["Accel_y"] = y;
      doc["Accel_z"] = z;
      serializeJson(doc, serial2);
      serial2.println();
}
void GetRader(){
  mySerial.listen(); // sw시리얼을 두개 이상 사용하려면 listen 를 호출 해야 한다. //https://blog.naver.com/roboholic84/220550737629
  if(TFmini.measure()){ // 거리와 신호의 강도를 측정합니다. 성공하면 을 반환하여 if문이 작동합니다.
    space = TFmini.getDistance(); // 거리값을 cm단위로 불러옵니다.
    strength = TFmini.getStrength();// 신호의 강도를 불러옵니다. 측정 대상이 넓으면 강도가 커집니다.
  }
}
void ReadData(){
  serial2.listen(); //
  if (serial2.available()) {  // 소프트웨어 시리얼 포트에 데이터가 있는지 확인 serial2.available()
    char ch = serial2.read();  // 데이터를 읽음
    if (ch == 'g') { // 읽은 데이터가 'g'인지 확인 맞다면 센서 데이터를 전송한다.
      sandjson();
    }Serial.println("doc");
  }
}
