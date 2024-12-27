////////////////////////////////////////////////////////////////////////////////////
// Programmed by LDH 2022.06.01
// Edit by LSW 2023.06.13 ~ 
////////////////////////////////////////////////////////////////////////////////////
#include <Arduino.h>
#include <esp_task_wdt.h>
#include <WiFi.h>
#include <Ticker.h>
#include <HTTPClient.h>
#include <ESP32httpUpdate.h>
#include <PubSubClient.h>
#include <BluetoothSerial.h>
#include <MqttTopic_Solimatics.h>
#include <Parameter.h>
#include <BoardSet.h>
#include <CANModule.h>
#include <mcp_can.h>
#include <MCP3564.h>
#include <Wire.h>
#include <CarParameter.h>
#include <BLEDevice.h> //ble 관련 라이브러리들 헤더
#include <BLEUtils.h> //
#include <BLEServer.h> //
#include <BLE2902.h>  //

////////////////////////////////////////////////////////////////////////////////////
// Board ID, Program Version
////////////////////////////////////////////////////////////////////////////////////
int BoardID = DAQ_YOUNGJIN;

#define PROGRAM_VER "2410108001"
#define HARDSOFT_VER "A005-0004"
////////////////////////////////////////////////////////////////////////////////////


////////////////////////////////////////////////////////////////////////////////////
// Parameter Data
////////////////////////////////////////////////////////////////////////////////////

bool DoUseMainParameter = true; //PROGRAM_VER이 바뀌고 DoUseMainParameter가 true인 경우 위의 파라메터가 eeprom에 저장됨

const char MAIN_WIFI_SSID_PREFIX[] = "LTE_";
#define MAIN_WIFI_KEY "ik09Pw72!!m"
#define MAIN_SERVER_IP "211.169.215.170"
#define MAIN_OTASERVER_IP "211.169.215.170"

#define MQTT_ID "ari_mqtt"
#define MQTT_PWD "25846ec82"

HTTPClient http;
const char* headerNames[] = {"Content-Length", "Content-Type", "DoUpgrade", "RevVer"};

char* ptrURL;
char UpdateURL[200];
String OTA_FILENAME;

#define NEXT_OTACHECKTIME 3600000  // 다음 OTA 체크는 1시간 후에
int32_t OTACheckTime = NEXT_OTACHECKTIME;
int32_t OTATime = NEXT_OTACHECKTIME - 60000;
int IsOTATime = false;

Parameter Par;

bool IsParameterChanged = false;
bool IsNetworkChanged = false;
////////////////////////////////////////////////////////////////////////////////////


////////////////////////////////////////////////////////////////////////////////////
// Network Data
////////////////////////////////////////////////////////////////////////////////////
#define AP_SCAN_MAX 10

char AP_SSID[AP_SCAN_MAX][40];
char AP_KEY[AP_SCAN_MAX][40];
uint8_t AP_MAC[AP_SCAN_MAX][6];
int AP_CHANNEL[AP_SCAN_MAX];
int AP_RSSI[AP_SCAN_MAX];
int AP_NUM;

#define MQTT_FAILCNT_MAX 30
int MqttFailCnt = 0;

#define WIFI_FAILCNT_MAX 3
int WiFiFailCnt = 0;

bool IsNetworkConnected = false;
bool IsServerConnected = false;

WiFiClient espClient;
PubSubClient mqttClient;

char WiFiSSID[50] = "";
char WiFiKey[50] = "";
char ServerIP[50] = "";
char OTAServerIP[50] = "";
char clientname[50] = "";
int PortMqtt;
int PortUpdate;

#define NETWORK_CHKTIME 20   // MQTT 연결 체크 : 자주 해야 좋음
int32_t NetworkChkTime = 0;
int IsNetworkChkTime = false;

bool IsTopicRequestLoginReceived = false;
bool IsTopicRequestStartReceived = false;
bool IsTopicRequestStopReceived = false;
bool IsTopicRequestGnssReceived = false;
bool IsTopicRequestModelReceived = false;
////////////////////////////////////////////////////////////////////////////////////


////////////////////////////////////////////////////////////////////////////////////
// MQTT Data
////////////////////////////////////////////////////////////////////////////////////
#define MQTT_VERSIONTIME 120000   // MQTT IoT Infomation 전달
int32_t MqttVersionTime = 60000;
int IsMqttVersionTime = false;
char Message[100] = "";

MqttTopic AriMT;
bool IsMqttDataReady = false;

char WillMsg[300];

char payload_topic[100];
byte payload_buf[1024];
unsigned int payload_length = 0;
bool payload_status = false;

bool IsMqttRecvStatus = false;
////////////////////////////////////////////////////////////////////////////////////


////////////////////////////////////////////////////////////////////////////////////
// Module data
////////////////////////////////////////////////////////////////////////////////////
BoardSet BSet;
MCP3564 ADC;
MCP_CAN CAN0(CAN0_CS);
CANModule AriCAN;
bool IsCANActive = false;
bool CANPreStatus = false;
bool CANOpStatus = false;
bool DidEncoderBaseRead = false;
int32_t EncoderBase = 0; 
int32_t EncoderRead = 0; 
int32_t EncoderDist = 0; 
int32_t InclinationX = 0;
int32_t InclinationY = 0;
int32_t InclinationX_BufX[3] = {0,0,0};
int32_t InclinationX_BufY = 0;
bool first_InclinationX = false;
int32_t InclinationY_BufX[3] = {0,0,0};
int32_t InclinationY_BufY = 0;
bool first_InclinationY= false;

#define CANSYNC_COUNTMAX 50
int CANSyncCount = 0;

// Model 값...
int32_t Encoder_Bottom = 0;
int16_t model = 0;
int16_t D1_LOW = 0;
int16_t D1_MAX = 0;
int16_t D2_LOW = 0;
int16_t D2_MAX = 0;

// GNSS
#define GNSSSENDING_TIME 10000
int32_t GNSSSendingTime = 0;
bool IsGNSSSendingTime = false;

int32_t Latitude = 0;
int32_t Longitude = 0;
int32_t Altitude = 0;
float Azimuth = 0.0f;

#define SYNC_TIME 50
int32_t SyncTime = 0;
bool IsSyncTime = false;

#define YJSENDING_TIME 300 // 센서데이터 MQTT 업데이트 타임
int32_t YJSendingTime = 0;
bool IsYJSendingTime = false;

#define STATE_TIME 2000 // 컨트롤러 상태 업데이트
int32_t StateTime = 0;
bool IsStateTime = false;

#define Rod_Length 8000//8350
uint32_t JobTimer = 0;
bool IsJobTimerActive = false;
uint32_t WorkerIdx = 1;
uint32_t WorkUnitIdx = 1;
int32_t TargetDepth = 0; //뎁스알고리즘 실험 임시 적용... 20m
float Pressure = 0;
float Torque = 0;

#define Max_Rod 6 // 해머 포함 최대 로드 갯수
uint8_t RodCount = 0;
int32_t MaxDepth = 0; //최대 깊이
int32_t BitPosition = 0;// 현재 비트포지젼
int32_t PreBitPosition = 0; // 이전.. 비트포지션값
int32_t rawBitPosition = 0;// 이전 최대 깊이
int32_t Final_BitPosition = 0; // 이전..
int32_t OffsetBitPosition = 0; // 뎁스 보정..
int32_t hammer = 0;
#define ROD_SWITCH_TIME 50
int32_t RodSwitchTime = 0;
bool IsRodSwitchTime = false;

#define ADC_READ_TIME 270
int32_t ADCReadTime = 0;
bool IsADCReadTime = false;

int32_t ADCData[3];
bool ADCStatus[3];

#define ROD_SWITCH_IN 16
#define SWITCH_ON 1
#define SWITCH_OFF 0
uint8_t RodSwitch[2] = {SWITCH_OFF, SWITCH_OFF};
uint8_t RodSwitchPre = SWITCH_OFF;
uint8_t RodSwitchCur = SWITCH_OFF;
// 동작 상태 확인 및 천공 깊이 Idle
#define Sample_time 50
#define opangle 15.00

int32_t op_Incliy = 0;
float Resultangle = 0;
int avr_angle = 0;
bool verticality = false;

// Road Change 조건 인식을 위한 조건 변수들.
int D1_Chk_Count = 0;
int D2_Chk_Count = 0;
bool Is_D1 = false;
bool Is_D2 = false;
bool Pre_Change_Road = false;
bool Is_Change_Road = false;
bool Is_BitChanged_Rod = false;
bool Is_perforation_start = false; // 천공의 시작 플래그...
//SW 노이즈 에대한 판단.
int Switc_Noise_Cont = 0;
bool Is_Switc_Noise = 0;
////////////////////////////////////////////////////////////////////////////////////


////////////////////////////////////////////////////////////////////////////////////
// Timer Interrupt
////////////////////////////////////////////////////////////////////////////////////
Ticker mainTicker;

volatile uint32_t PowerOnTime = 0;
volatile int32_t Timer32 = 0;
int64_t BaseTime64 = 0;
bool IsTimeUse = false;

#define CURTIME32_MAX 864000000  // 10 days
#define DIFFBASETIME64_MAX 20000
int32_t CurTime32;
int64_t OldBaseTime64;
int64_t NewBaseTime64;
int64_t DiffBaseTime64;

#define LEDONTIME_MAX 60000
bool IsLedOn = false;
int LedTime = 0;

#define WDT_TIMEOUT 60
bool wdt_rst_flag = false;
////////////////////////////////////////////////////////////////////////////////////


////////////////////////////////////////////////////////////////////////////////////
// Bluetooth Data
////////////////////////////////////////////////////////////////////////////////////
BluetoothSerial BTSerial;
/*bool IsBTConnected = false;

#define BTCHK_TIME 50
uint32_t BTChkTime = 0;
bool IsBTChkTime = false;

#define BTON_TIME 600000  // Bluetooth On for 10 minutes after power on
uint32_t BTOnTime = 0;
bool IsBTOnTime = true;
bool DoBTDisable = false;

char BTRecvBuf[200];
int BTRecvLength = 0;
int BTRecvCnt = 0;
bool IsBTRecvDone = false;

char BTName[20];*/
////////////////////////////////////////////////////////////////////////////////////
// CAN RELAY 
////////////////////////////////////////////////////////////////////////////////////
#define RELAY_OUT 21
#define RELAY_ON 0
#define RELAY_OFF 1
////////////////////////////////////////////////////////////////////////////////////
// BLE Data
////////////////////////////////////////////////////////////////////////////////////
bool IsBLEConnected = false;

BLEAdvertising *pAdvertising = nullptr;
BLEServer* pServer = nullptr;
BLEServer* oldServer = nullptr;
BLEService *pService = nullptr;
BLECharacteristic *pSensingCharacteristic = nullptr;
BLE2902 *pSensingDescriptor = nullptr;
#define SERVICE_UUID  "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define Sensing_UUID  "beb5483e-36e1-4688-b7f5-ea07361b26a8" // 보낼 데이터에 대한 구분...
////////////////////////////////////////////////////////////////////////////////////


////////////////////////////////////////////////////////////////////////////////////
// Function define
////////////////////////////////////////////////////////////////////////////////////
void ReadRodSwitch(void);
bool ReadADC(void);
void InitHardwares(void);
void InitParameters(void);
void InitModuleData(void);
void InitTimer(void);
void mainTimer(void);
bool NetworkChk(void);
void NetworkRestore(void);
bool ConnectServer(void);
void PublishTopicResponseLogin(void);
void PublishTopicResponseStart(void);
void PublishTopicResponseStop(void);
void PublishTopicGNSSData(void);
void PublishTopicYJSensing(void);
void TopicTimeMSChk(byte* payload, unsigned int length);
void TopicRequestLoginChk(byte* payload, unsigned int length);
void TopicRequestStartChk(byte* payload, unsigned int length);
void TopicRequestStopChk(byte* payload, unsigned int length);
void BaseTime64Chk(void);
void OTA_Update_Check(void);
void OTA_Update(void);
void InitBLE(void);
void Write_BLE(const char* topic,const char* data);
void RedLedOn(int msec);
void GreenLedOn(int msec);
void BlueLedOn(int msec);
void LedOn(int led, int msec);
void LedAllOff(void);
//void mcp_wrapper(void) { ADC.IRQ_handler(); }
////////////////////////////////////////////////////////////////////////////////////

void ReadRodSwitch(void)
{
  if(digitalRead(ROD_SWITCH_IN) == HIGH)
  {
    for(int i=0;i<10;i++);
    if(digitalRead(ROD_SWITCH_IN) == HIGH)
    {
      for(int i=0;i<10;i++);
      if(digitalRead(ROD_SWITCH_IN) == HIGH)
      {
        RodSwitch[1] = RodSwitch[0];
        RodSwitch[0] = SWITCH_OFF;
      }
      else return;
    }
    else return;
  }
  else
  {
    for(int i=0;i<10;i++);
    if(digitalRead(ROD_SWITCH_IN) == LOW)
    {
      for(int i=0;i<10;i++);
      if(digitalRead(ROD_SWITCH_IN) == LOW)
      {
        RodSwitch[1] = RodSwitch[0];
        RodSwitch[0] = SWITCH_ON;
      }
      else return;
    }
    else return;
  }

  if(RodSwitch[1]==RodSwitch[0])
  { // 스위치.. 상시..
    RodSwitchPre = RodSwitchCur;
    RodSwitchCur = RodSwitch[0];
    if(RodSwitchPre != RodSwitchCur)
    { // 스위치 동작에 변화가 있을 경우. ON -> OFF or OFF -> ON
      if(RodSwitchCur == SWITCH_OFF){ // 스위치가 ON -> 0FF 가 될때.
        if(Switc_Noise_Cont <= 100){ // 50*100 = 약 5초 미만의 의 시간으로 들어온 SW 신호는 노이즈로 판단함.
          Is_Switc_Noise = true;
          Switc_Noise_Cont = 0;
        }
        if(!Is_Switc_Noise){ // false 일때 true 
          if(BitPosition > 1000){
            if(Is_D2 && Is_D1){
              Is_Change_Road = true;
              Is_perforation_start = false;
            }else{
              Is_Change_Road = false;
            }//Serial.printf("\r\n State %d , %d , %d",(!Is_Change_Road),(!Is_BitChanged_Rod),(!Is_Switc_Noise)); // 로드 스위치 동작.. 체크...
            if(!Is_Change_Road){
              if(!Is_BitChanged_Rod){
                if(Encoder_Bottom !=0){
                  OffsetBitPosition = (8000 + Final_BitPosition);
                }
                if(RodCount == 0){
                  MaxDepth -= 1480;
                }
                RodCount++; // RodCount 를 증가 시킨다.
                Is_BitChanged_Rod = true;
              }
            }else{
              RodCount = 0;
              MaxDepth = 0;
              OffsetBitPosition = 0;
              Is_BitChanged_Rod = false;
            }
            Is_D1 = false;
            Is_D2 = false;
            D1_Chk_Count = 0;
            D2_Chk_Count = 0;
            Final_BitPosition = BitPosition; // 최종 비트포지션과 현재 위치를 동기화 시킴.
            //Serial.printf("\r\n Is_Change_Road = %d",Is_Change_Road); // 로드 스위치 동작.. 체크...
          }
        }
        Is_Switc_Noise = false;
        Switc_Noise_Cont = 0;
        //Serial.printf("\r\nRodSwitchCur == SWITCH_OFF"); // 로드 스위치 동작.. 체크...
      }
      //Serial.printf("\r\nRodCount(%d), Rod Switch is changed! %d>>%d",RodCount,RodSwitchPre,RodSwitchCur); // 로드 스위치 상변화
    }
    if(RodSwitchCur == SWITCH_ON){ // 스위치 신호가 들어옴.
      if(Is_D2){ //탈거 인식 -2 D1 포인트 인식..
        if((BitPosition >= D1_LOW) && (BitPosition <= D1_MAX)){
          D1_Chk_Count++;
          if(D1_Chk_Count >= Chk_Point){
            Is_D1 = true;
          }
        }else{
          Is_Change_Road = false;
          D1_Chk_Count = 0;
          if(!Is_D1){
            Is_D1 = false;
          }
        }
      }else{
        Is_D2 = false;
        Is_Change_Road = false;
      }
      Switc_Noise_Cont++; // 동작시간 체크.
      //Serial.printf("\r\n Switc_Noise_Cont = %d",Switc_Noise_Cont); // 로드 스위치 동작.. 체크...
    }//Serial.printf("\r\n RodSwitchCur = %d",RodSwitchCur); // 로드 스위치 동작.. 체크...
  }
}
bool ReadADC(void)
{
  if(digitalRead(ADC_INT) == 0)
  {
    ADC.readADCData();
      
    if(ADC.adc_ch == 0)
    {
      ADCData[0] = ADC.adc_sample;
      ADCStatus[0] = true;
    }
    if(ADC.adc_ch == 2)
    {
      ADCData[2] = ADC.adc_sample;
      ADCStatus[2] = true;
    }
  }
  //Serial.printf("\r\n adc_ch(%d) adc_sample(%d)",ADC.adc_ch,ADC.adc_sample);
  if((ADCStatus[0]==true)&&(ADCStatus[2]==true))
  {
    // Pressure = (Vout-1)/4*500
    // Torque = Pressure*9520/628
    // at 1V : 0x0001B000
    // at 5V : 0x00095000
  
    int32_t adata, rdata;
    float fdata;
    if(ADCData[0] < 0x0001B000) adata = 0;
    else
    {
      if(ADCData[0] > 0x000F0000) adata = 0;
      else adata = ADCData[0]-0x0001B000;
    }
    rdata = (adata*500)/4997;
    if(rdata > 50000) fdata = 50000;
    else fdata = (float)rdata;
    Pressure = fdata * 0.01;
    
    if(ADCData[2] < 0x0001B000) adata = 0;
    else
    {
      if(ADCData[2] > 0x000F0000) adata = 0;
      else adata = ADCData[2]-0x0001B000;
    }
    rdata = (adata*500)/4997;
    if(rdata > 50000) fdata = 50000;
    else fdata = (float)rdata;
    Torque = fdata*0.15159236;

    ADCStatus[0] = false;
    ADCStatus[2] = false;
    //Serial.printf("\r\nADCData[0](%08X) ADCData[2](%08X)Pressure(%f) Torque(%f)",ADCData[0],ADCData[2],Pressure,Torque);
    return true;
  }
  return false;
}
////////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////////////////


////////////////////////////////////////////////////////////////////////////////////
// 1msec Timer, setup, loop
////////////////////////////////////////////////////////////////////////////////////
void mainTimer(void)
{
  PowerOnTime++;
  Timer32++;

  if(IsJobTimerActive == true) JobTimer++;
  
  if(IsNetworkChkTime == false)
  {
    NetworkChkTime++;
    if(NetworkChkTime >= NETWORK_CHKTIME) IsNetworkChkTime = true;
  }

  if(IsMqttVersionTime == false)
  {
    MqttVersionTime++;
    if(MqttVersionTime >= MQTT_VERSIONTIME) IsMqttVersionTime = true;
  }

  if(IsOTATime == false)
  {
    OTATime++;
    if(OTATime >= OTACheckTime) IsOTATime = true;
  }
  if(IsGNSSSendingTime == false)
  {
    GNSSSendingTime++;
    if(GNSSSendingTime >= GNSSSENDING_TIME) IsGNSSSendingTime = true;
  }
  if(IsSyncTime == false)
  {
    SyncTime++;
    if(SyncTime >= SYNC_TIME) IsSyncTime = true; // 50ms
  }  
  
  if(IsADCReadTime == false)
  {
    ADCReadTime++;
    if(ADCReadTime >= ADC_READ_TIME) IsADCReadTime = true;
  }

  if(IsYJSendingTime == false)
  {
    YJSendingTime++;
    if(YJSendingTime >= YJSENDING_TIME) IsYJSendingTime = true; // 200ms
  }

  if(IsRodSwitchTime == false)
  {
    RodSwitchTime++;
    if(RodSwitchTime >= ROD_SWITCH_TIME) IsRodSwitchTime = true; // 50ms
  } 
  if(IsStateTime == false)
  {
    StateTime++;
    if(StateTime >= STATE_TIME) IsStateTime = true; // 50ms
  } 
  if(IsLedOn == true)
  {
    LedTime--;
    if(LedTime <= 0)
    {
      IsLedOn = false;
      LedAllOff();
    }
  }

  wdt_rst_flag = true;
}

void setup()
{
  InitBLE();
  InitHardwares();
  InitParameters();
  InitModuleData();
  InitTimer();
}

void loop()
{
  else if(IsGNSSSendingTime == true)
  {
    PublishTopicGNSSData();
    BlueLedOn(100);
    GNSSSendingTime = 0;
    IsGNSSSendingTime = false;
  }
  else if(IsRodSwitchTime == true) // 50ms
  {
    ReadRodSwitch();
    RodSwitchTime = 0;
    IsRodSwitchTime = false;
  }
  else if(IsADCReadTime == true) // 270ms
  {
    if(ReadADC() == true)
    {
      ADCReadTime = 0;
      IsADCReadTime = false;
    }
  }
  // Upload Data Chk
  if(IsNetworkChkTime == true)
  {
    bool nstaus = NetworkChk(); 
    AriMT.qnetstatus.IsControllerConnected = nstaus;
    NetworkChkTime = 0;
    IsNetworkChkTime = false;
    if(nstaus == true)
    {
      if(IsOTATime == true && IsNetworkConnected ==true)
      {
        Serial.print("\r\nOTA Time");
        GreenLedOn(LEDONTIME_MAX);
        OTA_Update_Check();
        NetworkRestore();
        OTATime = 0;
        OTACheckTime = NEXT_OTACHECKTIME;
        IsOTATime = false;
        LedAllOff();
        Serial.printf("\r\n Next OTA Check Time : %d", PowerOnTime + OTACheckTime);
      }
      if(IsYJSendingTime == true) // 센서 데이터 업데이트. 
      {
        PublishTopicYJSensing();
        BlueLedOn(100);
        YJSendingTime = 0;
        IsYJSendingTime = false;
      }
      else if(IsStateTime == true)
      {
        PublishNetworkStatus();
        StateTime = 0;
        IsStateTime = false;
      }
    }
  }
  if(payload_status == true)
  {
    Serial.printf("\r\nSub %s : ", payload_topic, payload_length);
    if(payload_length > 200) payload_buf[200] = 0x00;
    else payload_buf[payload_length] = 0x00;
    Serial.print((char*)payload_buf);
    payload_status = false;
  }

  if(wdt_rst_flag == true)
  {
    esp_task_wdt_reset();
    wdt_rst_flag = false;
  }
}
////////////////////////////////////////////////////////////////////////////////////


////////////////////////////////////////////////////////////////////////////////////
// Initialize function
////////////////////////////////////////////////////////////////////////////////////
void InitHardwares(void)
{
  BSet.BoardInit(BoardID);
  delay(2000);
  pinMode(RELAY_OUT, OUTPUT);
  digitalWrite(RELAY_OUT,RELAY_ON);
  
  delay(5000);
  pinMode(ROD_SWITCH_IN, INPUT);   

  pinMode(ADC_CS, OUTPUT);
  pinMode(ADC_INT, INPUT);  
  SPI.begin();
  delay(500); // I think we need an initial delay.
  ADC.ResetYJ();
  //ADC.printRegisters();
}

void InitParameters(void)
{
  Par.ptrBTSerial = &BTSerial;
  Par.ptrBSet = &BSet;
  Par.InitParameter(HARDSOFT_VER);

  if(strcmp(Par.ptrModuleVersion, PROGRAM_VER) != 0)
  {Serial.printf("\r\n %s , %s",Par.ptrModuleVersion,PROGRAM_VER);
    if(DoUseMainParameter == true)
    {
      char ssidtext[30];
      uint8_t macnum[6];
      WiFi.macAddress(macnum);
      sprintf(ssidtext,"%s%02X%02X%02X%02X%02X%02X",MAIN_WIFI_SSID_PREFIX,macnum[0],macnum[1],macnum[2],macnum[3],macnum[4],macnum[5]);
      strcpy(Par.ptrWiFiSSID, ssidtext);
      //strcpy(Par.ptrWiFiSSID, MAIN_WIFI_SSID);
      strcpy(Par.ptrWiFiKey, MAIN_WIFI_KEY);
      strcpy(Par.ptrServerIP, MAIN_SERVER_IP);
      strcpy(Par.ptrOTAServerIP, MAIN_OTASERVER_IP);
      // 모델별 파라메터 
      Par.ptrModel = YJ5600HB;
      Par.ptrEncoder_Bottom = Encoder_Bottom;
    }
    strcpy(Par.ptrModuleVersion, PROGRAM_VER);
    Par.WriteParameter();
  }
  Par.SerialShowParameter();
}

void InitModuleData(void)
{
}

void InitTimer(void)
{
  mainTicker.attach_ms(1, mainTimer);

  esp_task_wdt_init(WDT_TIMEOUT, true);
  esp_task_wdt_add(NULL);
}

bool NetworkChk(void)
{
  if(IsNetworkConnected == true)
  {
    if(mqttClient.connected() == true)
    {
      mqttClient.loop();
      MqttFailCnt = 0;
      IsServerConnected = true;
    }else if(IsBLEConnected == true){ //IsBLEConnected
      MqttFailCnt++;
      IsServerConnected = true;
    }else
    {
      MqttFailCnt++;
      IsServerConnected = false;
    }
  }else if(IsBLEConnected ==true){
    MqttFailCnt++;
    IsServerConnected = true;
  }else{
    MqttFailCnt++;
    IsServerConnected = false;
  }
  //Serial.printf("\r\n IsNetworkConnected : %d", IsNetworkConnected);
  //Serial.printf("\nMqttFailCnt : %d",MqttFailCnt);
  if(MqttFailCnt >= MQTT_FAILCNT_MAX)
  {
    MqttFailCnt = 0;
    ConnectServer();
  }
  if(IsBLEConnected){
    GreenLedOn(10);
  }else{
    RedLedOn(10);
  }
  return IsServerConnected;
}

void NetworkRestore(void)
{
  //if(WiFi.status() == WL_CONNECTED)
}
////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////

void PublishTopicYJSensing(void)
{
  //Serial.print("\r\nPublishTopicYJSensing Start");
  strcpy(AriMT.qyjsensing.MAC, Par.ptrMacAddressHex);  
  AriMT.qyjsensing.WorkerIdx = WorkerIdx;
  AriMT.qyjsensing.WorkUnitIdx = WorkUnitIdx;
  AriMT.qyjsensing.TargetDepth = TargetDepth;
  
  AriMT.qyjsensing.Packets = 1;
  AriMT.qyjsensing.BaseTime.llbuf = BaseTime64;
  AriMT.qyjsensing.Time[0] = Timer32;
  AriMT.qyjsensing.JobTime[0] = JobTimer;
  AriMT.qyjsensing.Pressure[0] = Pressure;
  AriMT.qyjsensing.Torque[0] = Torque;
  AriMT.qyjsensing.InclinationX[0] = InclinationX;
  AriMT.qyjsensing.InclinationY[0] = InclinationY;
  AriMT.qyjsensing.RodCount[0] = RodCount;
  AriMT.qyjsensing.Encoder[0] = EncoderDist;
  AriMT.qyjsensing.MaxDepth[0] = MaxDepth;
  AriMT.qyjsensing.BitPosition[0] = BitPosition;
  AriMT.qyjsensing.Switch[0] = RodSwitchCur;
  AriMT.qyjsensing.Bottom[0] = Encoder_Bottom;
  AriMT.qyjsensing.offset[0] = OffsetBitPosition;
  
  AriMT.PublishTopicYJSensing();

  while(IsMqttRecvStatus==true)delay(1);  
  int length = AriMT.CheckQbufLength();
  uint8_t* pubmsg = (uint8_t *)malloc(length+1);
  for(int i=0;i<length;i++) pubmsg[i] = AriMT.qbuf[i];
  pubmsg[length] = 0;
  //mqttClient.publish(topic_yjsensing, (const uint8_t*)pubmsg, length, false);
  Write_BLE("Sensing",(const char*)pubmsg);
  mqttClient.publish(BSet.topic_yjsensing_new, (const uint8_t*)pubmsg, length, false);
  mqttClient.loop();  
  //Serial.printf("\r\nPublished YJSensing(%s) : %s",BSet.topic_yjsensing_new,pubmsg);
  free(pubmsg);
  //mqttClient.publish(topic_yjsensing, (const uint8_t*)AriMT.qbuf, length, false);
  //mqttClient.loop();
  //Serial.printf("  PublishTopicYJSensing Stop(%d)",length);
}
void PublishNetworkStatus(void)
{
  AriMT.PublishTopicNetworkStatus();

  while(IsMqttRecvStatus==true)delay(1);  
  int length = AriMT.CheckQbufLength();
  uint8_t* pubmsg = (uint8_t *)malloc(length+1);
  for(int i=0;i<length;i++) pubmsg[i] = AriMT.qbuf[i];
  pubmsg[length] = 0;
  Write_BLE("NetState",(const char*)pubmsg);
  //Serial.printf("\r\nPublished GNSS(%s) : %s",topic_gnssdata,pubmsg);
  free(pubmsg);
  
  //mqttClient.publish(topic_gnssdata, (const uint8_t*)AriMT.qbuf, length, false);
  //mqttClient.loop();
  //Serial.printf("PublishTopicGNSS Stop(%d)",length);  
}
void TopicRequestLoginChk(byte* payload, unsigned int length)
{
  AriMT.ParsingTopicRequestLogin(payload, length);
  IsTopicRequestLoginReceived = true;
}

void TopicRequestStartChk(byte* payload, unsigned int length)
{
  AriMT.ParsingTopicRequestStart(payload, length);
  IsTopicRequestStartReceived = true;
}

void TopicRequestStopChk(byte* payload, unsigned int length)
{
  AriMT.ParsingTopicRequestStop(payload, length);
  IsTopicRequestStopReceived = true;
}
void TopicRequestGnssChk(byte* payload, unsigned int length) // GNSS 데이터 파싱
{
  AriMT.ParsingTopicRequestGnss(payload, length);
  IsTopicRequestGnssReceived = true;
}
void TopicRequestModelChk(byte* payload, unsigned int length) // Model 데이터 파싱
{
  AriMT.ParsingModelData(payload, length);
  IsTopicRequestModelReceived = true;
}
void TopicTimeMSChk(byte* payload, unsigned int length)
{
  CurTime32 = Timer32;
  AriMT.ParsingTopicTimeMS(payload, length);
  NewBaseTime64 = AriMT.qtimems.T.llbuf;
  BaseTime64Chk();
  /*
    int64_t btime64bit = NewBaseTime64 >> 10;
    int32_t btime32bit = (int32_t)btime64bit;
    int32_t quotient = btime32bit / 0x00014997;
    Serial.printf("\r\n%d days passed from the baseday 2020.01.01",quotient);
  */
}

void BaseTime64Chk(void)
{
  if(IsTimeUse == true) return;

  if(BaseTime64 == 0)
  {
    Timer32 = Timer32 - CurTime32;
    BaseTime64 = NewBaseTime64;
    return;
  }

  OldBaseTime64 = BaseTime64 + (int64_t)CurTime32;
  if(CurTime32 < CURTIME32_MAX)
  {
    if(NewBaseTime64 > OldBaseTime64) DiffBaseTime64 = NewBaseTime64 - OldBaseTime64;
    else DiffBaseTime64 = OldBaseTime64 - NewBaseTime64;
    //Serial.printf("\r\nBaseTime Differences : %lld",DiffBaseTime64);
    if(DiffBaseTime64 < DIFFBASETIME64_MAX) return;
  }

  Timer32 = Timer32 - CurTime32;
  BaseTime64 = NewBaseTime64;
  Serial.printf("\r\nBaseTime is changed!");

  char cbuf[100];
  sprintf(cbuf,"BaseTime Diff(%lld)",DiffBaseTime64);
  strcpy(Message,cbuf);
}
////////////////////////////////////////////////////////////////////////////////////


////////////////////////////////////////////////////////////////////////////////////
// OTA(Over The Air) Update (WIFI Update Function)
////////////////////////////////////////////////////////////////////////////////////
void OTA_Update_Check(void)
{
  Serial.printf("\r\nOTA Checking");
  if(IsNetworkConnected == true)
  {
    http.collectHeaders(headerNames, sizeof(headerNames) / sizeof(headerNames[0]));
    ptrURL = UpdateURL;
    http.begin(UpdateURL);
    int code = http.GET();
    String res = http.getString();
    OTA_FILENAME = "/Update" + http.header("DoUpgrade");
    Serial.print("\r\nDoUpgrade:");
    Serial.print(OTA_FILENAME);
    Serial.print(res);
    http.end();

    int ssize = OTA_FILENAME.length();
    char file_ext[4];
    file_ext[0] = OTA_FILENAME[ssize - 3];
    file_ext[1] = OTA_FILENAME[ssize - 2];
    file_ext[2] = OTA_FILENAME[ssize - 1];
    file_ext[3] = 0;
    if(strcmp(file_ext, "bin") == 0) OTA_Update();
  }
}

void OTA_Update(void)
{
  //BTSerial.disconnect();
  //BTSerial.end();
  //delay(500);
  char fileURL[200];
  sprintf(fileURL, "http://%s:%d%s", OTAServerIP, PortUpdate, OTA_FILENAME.c_str());
  Serial.printf("\r\nProgressing OTA: %s", fileURL);

  t_httpUpdate_return ret = ESPhttpUpdate.update(fileURL);
  switch (ret)
  {
    case HTTP_UPDATE_FAILED:
      Serial.printf("HTTP_UPDATE_FAILD Error (%d): %s", ESPhttpUpdate.getLastError(), ESPhttpUpdate.getLastErrorString().c_str());
      break;
    case HTTP_UPDATE_NO_UPDATES:
      Serial.println("HTTP_UPDATE_NO_UPDATES");
      break;
    case HTTP_UPDATE_OK:
      Serial.println("HTTP_UPDATE_OK");
      break;
  }
  strcpy(Message,"UPDATE Fail");
}
////////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////////////////
// BLE Function
////////////////////////////////////////////////////////////////////////////////////
class BLE_Callbacks: public BLECharacteristicCallbacks ,public BLEServerCallbacks {
    void onWrite(BLECharacteristic *pCharacteristic){
      std::string value = pCharacteristic->getValue();
      size_t commaIndex = value.find('_');
      std::string topic = value.substr(0, commaIndex);
      std::string json = value.substr(commaIndex + 1);
      if (commaIndex != std::string::npos) {
          byte* payload = (byte*)json.data(); //byte 형태로 변환함.
          unsigned int length = json.length();
          // JSON 무결성 확인
          if (payload[0] != '{' || payload[length-1] != '}') {
              // JSON is not valid
              Serial.println("Invalid JSON received");
              return;
          }
          if(topic.compare("GNSS")==0){
              TopicRequestGnssChk(payload, length);
          }else if(topic.compare("Start")==0){
              TopicRequestStartChk(payload, length);
          } else if(topic.compare("Stop")==0){
              TopicRequestStopChk(payload, length);
          } else if(topic.compare("Login")==0){
              TopicRequestLoginChk(payload,length);
          } else if(topic.compare("InitModel")==0){ // 모델 선택
              TopicRequestModelChk(payload,length);
          }
      }
    }
    void onConnect(BLEServer* pServer) {
        IsBLEConnected = true;
        pAdvertising->stop();// 광고를 중지합니다.
        //Serial.println("BLE connected");
    }
    void onDisconnect(BLEServer* pServer) {
      // 클라이언트가 연결 해제되었을 때 실행되는 코드
      // 연결 정보를 리셋합니다.
      IsBLEConnected = false;
      //delay(10);
      pAdvertising->start();
      Serial.println("BLE disconnected");
    }
};
void handleData(std::string value) {
    if (value.length() > 0) {
        for (int i = 0; i < value.length(); i++){
            Serial.print(value[i]);
        }
        Serial.println();
    }
}
void InitBLE(void){
    BLEDevice::init("DSOL-2000");
    pServer = BLEDevice::createServer();

    pService = pServer->createService(SERVICE_UUID);
    pSensingCharacteristic = pService->createCharacteristic(
                                             Sensing_UUID,
                                             BLECharacteristic::PROPERTY_READ |
                                             BLECharacteristic::PROPERTY_WRITE |
                                             BLECharacteristic::PROPERTY_NOTIFY |
                                             BLECharacteristic::PROPERTY_INDICATE
                                           );
    // CCCD 추가
    // Client(Central, 모바일 기기등)에서 pTxCharacteristic 속성을 읽거나 설정할수 있게 UUID 2902를 등록
    // Client가 ESP32에서 보내는 데이터를 받기위해 해당 설정이 필요함.
    BLE_Callbacks* BLE_Callback = new BLE_Callbacks();
    pServer->setCallbacks(BLE_Callback);// 서버에 콜백 설정
    pSensingCharacteristic->setCallbacks(BLE_Callback); // topic 에대한 콜백 설정

    pSensingDescriptor = new BLE2902();
    pSensingDescriptor->setNotifications(true);
    pSensingCharacteristic->addDescriptor(pSensingDescriptor);
    delay(100);
    pService->start();
    pAdvertising = pServer->getAdvertising();
    pAdvertising->start();
}

void Write_BLE(const char* topic,const char* data)
{
  std::string combined = std::string(topic) + "_" + std::string(data);
  pSensingCharacteristic->setValue(combined.c_str());
  pSensingCharacteristic->notify();
}

void RedLedOn(int msec)
{
  if(IsLedOn == false)
    LedOn(RED_LED, msec);
}

void GreenLedOn(int msec)
{
  LedAllOff();
  LedOn(GREEN_LED, msec);
}

void BlueLedOn(int msec)
{
  LedAllOff();
  LedOn(BLUE_LED, msec);
}

void LedOn(int led, int msec)
{
  BSet.BoardLedOn(led);
  IsLedOn = true;
  LedTime = msec;
}

void LedAllOff(void)
{
  IsLedOn = false;
  BSet.BoardLedOff(RED_LED);
  BSet.BoardLedOff(BLUE_LED);
  BSet.BoardLedOff(GREEN_LED);
}
