#include <ArduinoJson.h> //ArduinoJson 라이브러리
#include <TimerOne.h> // TimerOne 라이브러리
#include <SoftwareSerial.h>
#include <DFRobot_TFmini.h>
#include <SparkFun_ADXL345.h>  // https://github.com/sparkfun/SparkFun_ADXL345_Arduino_Library
#include "Wire.h"
#include "I2Cdev.h"
#include "MPU9250.h"
#define slave_addr 0x01

const char *p = "Data Transfer to Slave\n";

SoftwareSerial mySerial(10,11); // RX, TX
DFRobot_TFmini  TFmini;

#define SANSING_TIME 20 // 초음파
int32_t sansingTime = 0;
bool IssansingTime = false;
#define READ_TIME 100 // 데이터 읽기
int32_t readTime = 0;
bool IsreadTime = false;
#define RADARING_TIME 10 // 라이다
int32_t radaringTime = 0;
bool IsradaringTime = false;

#define nine_axis_TIME 30// 9축 지자기 센서
int32_t nine_axisTime = 0;
bool Isnine_axisTime = false; 
// 초음파 센서
int echoPin1 = 2;
int trigPin1 = 3;
int echoPin2 = 4;
int trigPin2 = 5;
unsigned long duration1 = 0;
unsigned long duration2 = 0;
double distance1= 0;
double distance2= 0;
// 라이다 센서
double space,strength;

// 9축 지자기 센서
MPU9250 accelgyro;
I2Cdev   I2C_M;

uint8_t buffer_m[6];

int16_t ax, ay, az;
int16_t gx, gy, gz;
int16_t   mx, my, mz;

float heading;
float tiltheading;
float Axyz[3];
float Gxyz[3];
float Mxyz[3];
#define sample_num_mdate  5000
volatile float mx_sample[3];
volatile float my_sample[3];
volatile float mz_sample[3];

static float mx_centre = 0;
static float my_centre = 0;
static float mz_centre = 0;

volatile int mx_max = 0;
volatile int my_max = 0;
volatile int mz_max = 0;

volatile int mx_min = 0;
volatile int my_min = 0;
volatile int mz_min = 0;

float temperature;
float pressure;
float atm;
float altitude;



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
  if(Isnine_axisTime == false) // 9축 지자기 센서 읽기
  {
    nine_axisTime++;
    if(nine_axisTime >= nine_axis_TIME) Isnine_axisTime = true;
  }
}
void setup() {
  // 통신 초기화...
  Serial.begin(9600);  //PC와 통신할 하드웨어 시리얼 시작
  Wire.begin();
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
  // 라이다 초기화....
  TFmini.begin(mySerial); // 라이다 센서와 통신할 하드웨어 시리얼 시작 이걸 주석처리 하면.. 동작..???

//여기부터 9축 지자기
  Serial.println("Initializing I2C devices...");
  accelgyro.initialize();
  Serial.println("Testing device connections..."); 
  Serial.println(accelgyro.testConnection() ? "MPU9250 connection successful" : "MPU9250 connection failed");
  delay(100);
  Serial.println("     ");
  // 타이머 인터럽트 선언...
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
    mySerial.listen(); // 라이다 센서로 전환
    GetRader();
    radaringTime = 0;
    IsradaringTime = false;
  }else if(IsreadTime == true){ // 들어온 데이터를 확인하고 전송함.
    ReadData();
    readTime = 0;
    IsreadTime = false;
  }else if(Isnine_axisTime == true){
    geomagnetism(); 
    nine_axisTime = 0;
    Isnine_axisTime = false;
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
void GetRader(){
  if(TFmini.measure()){ // 거리와 신호의 강도를 측정합니다. 성공하면 을 반환하여 if문이 작동합니다.
    space = TFmini.getDistance(); // 거리값을 cm단위로 불러옵니다.
    strength = TFmini.getStrength();// 신호의 강도를 불러옵니다. 측정 대상이 넓으면 강도가 커집니다.
  }
}
void geomagnetism(){
  getAccel_Data();
  getGyro_Data();
  getCompassDate_calibrated(); 
  heading = getHeading();               
  tiltheading = getTiltHeading();
}

float getHeading(void)
{
    heading = 180 * atan2(Mxyz[1], Mxyz[0]) / PI;
    if (heading < 0) heading += 360;
    return heading;
}

float getTiltHeading(void)
{
    float pitch = asin(-Axyz[0]);
    float roll = asin(Axyz[1] / cos(pitch));

    float xh = Mxyz[0] * cos(pitch) + Mxyz[2] * sin(pitch);
    float yh = Mxyz[0] * sin(roll) * sin(pitch) + Mxyz[1] * cos(roll) - Mxyz[2] * sin(roll) * cos(pitch);
    float zh = -Mxyz[0] * cos(roll) * sin(pitch) + Mxyz[1] * sin(roll) + Mxyz[2] * cos(roll) * cos(pitch);
    tiltheading = 180 * atan2(yh, xh) / PI;
    if (yh < 0)    tiltheading += 360;
    return tiltheading;
}

void Mxyz_init_calibrated ()
{

    Serial.println(F("Before using 9DOF,we need to calibrate the compass frist,It will takes about 2 minutes."));
    Serial.print("  ");
    Serial.println(F("During  calibratting ,you should rotate and turn the 9DOF all the time within 2 minutes."));
    Serial.print("  ");
    Serial.println(F("If you are ready ,please sent a command data 'ready' to start sample and calibrate."));
    while (!Serial.find("ready"));
    Serial.println("  ");
    Serial.println("ready");
    Serial.println("Sample starting......");
    Serial.println("waiting ......");

    get_calibration_Data ();

    Serial.println("     ");
    Serial.println("compass calibration parameter ");
    Serial.print(mx_centre);
    Serial.print("     ");
    Serial.print(my_centre);
    Serial.print("     ");
    Serial.println(mz_centre);
    Serial.println("    ");
}


void get_calibration_Data ()
{
    for (int i = 0; i < sample_num_mdate; i++)
    {
        get_one_sample_date_mxyz();

        if (mx_sample[2] >= mx_sample[1])mx_sample[1] = mx_sample[2];
        if (my_sample[2] >= my_sample[1])my_sample[1] = my_sample[2]; //find max value
        if (mz_sample[2] >= mz_sample[1])mz_sample[1] = mz_sample[2];

        if (mx_sample[2] <= mx_sample[0])mx_sample[0] = mx_sample[2];
        if (my_sample[2] <= my_sample[0])my_sample[0] = my_sample[2]; //find min value
        if (mz_sample[2] <= mz_sample[0])mz_sample[0] = mz_sample[2];

    }

    mx_max = mx_sample[1];
    my_max = my_sample[1];
    mz_max = mz_sample[1];

    mx_min = mx_sample[0];
    my_min = my_sample[0];
    mz_min = mz_sample[0];

    mx_centre = (mx_max + mx_min) / 2;
    my_centre = (my_max + my_min) / 2;
    mz_centre = (mz_max + mz_min) / 2;
}

void get_one_sample_date_mxyz()
{
    getCompass_Data();
    mx_sample[2] = Mxyz[0];
    my_sample[2] = Mxyz[1];
    mz_sample[2] = Mxyz[2];
}

void getAccel_Data(void)
{
    accelgyro.getMotion9(&ax, &ay, &az, &gx, &gy, &gz, &mx, &my, &mz);
    Axyz[0] = (double) ax / 16384;
    Axyz[1] = (double) ay / 16384;
    Axyz[2] = (double) az / 16384;
}

void getGyro_Data(void)
{
    accelgyro.getMotion9(&ax, &ay, &az, &gx, &gy, &gz, &mx, &my, &mz);

    Gxyz[0] = (double) gx * 250 / 32768;
    Gxyz[1] = (double) gy * 250 / 32768;
    Gxyz[2] = (double) gz * 250 / 32768;
}

void getCompass_Data(void)
{
    I2C_M.writeByte(MPU9150_RA_MAG_ADDRESS, 0x0A, 0x01); //enable the magnetometer
    delay(10);
    I2C_M.readBytes(MPU9150_RA_MAG_ADDRESS, MPU9150_RA_MAG_XOUT_L, 6, buffer_m);

    mx = ((int16_t)(buffer_m[1]) << 8) | buffer_m[0] ;
    my = ((int16_t)(buffer_m[3]) << 8) | buffer_m[2] ;
    mz = ((int16_t)(buffer_m[5]) << 8) | buffer_m[4] ;

    Mxyz[0] = (double) mx * 1200 / 4096;
    Mxyz[1] = (double) my * 1200 / 4096;
    Mxyz[2] = (double) mz * 1200 / 4096;
}

void getCompassDate_calibrated ()
{
    getCompass_Data();
    Mxyz[0] = Mxyz[0] - mx_centre;
    Mxyz[1] = Mxyz[1] - my_centre;
    Mxyz[2] = Mxyz[2] - mz_centre;
}



void ReadData(){
  StaticJsonDocument<256> doc;
  doc["distance1"] = distance1; // 1번 초음파 센서 
  doc["distance2"] = distance2; //2번 초음파 센서
  doc["Lidar"] = space; // 라이다 센서 
  doc["tiltheading"] = tiltheading; // 여기서 부터 가속도 센서.
  doc["heading"] = heading;

  Wire.beginTransmission(slave_addr); // 인자로 전달한 주소의 Slave로 데이터 전송을 시작합니다.
  String output;
  serializeJson(doc, output);
  Wire.write(output.c_str(), output.length());
  Wire.endTransmission(); //write함수에 의해 버퍼에 기록된 데이터를 전송하고 통신을 마칩니다.
  delay(1000);
}

