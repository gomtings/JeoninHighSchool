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

#define PROGRAM_VER "2505138003"
#define HARDSOFT_VER "A005-0004"
////////////////////////////////////////////////////////////////////////////////////


////////////////////////////////////////////////////////////////////////////////////
// Parameter Data
////////////////////////////////////////////////////////////////////////////////////

bool DoUseMainParameter = false; //PROGRAM_VER이 바뀌고 DoUseMainParameter가 true인 경우 위의 파라메터가 eeprom에 저장됨

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
char macaddr[20] = "";
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
bool IsTopicAnalysisDataReceived = false;
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

#define YJSENDING_TIME 300 // 센서데이터 MQTT 업데이트 타임
int32_t YJSendingTime = 0;
bool IsYJSendingTime = false;

#define SENEOR_1_TIME 50
int32_t Sensor1Time = 0;
bool IsSensor1Time = false;

#define SENEOR_2_TIME 50
int32_t Sensor2Time = 0;
bool IsSensor2Time = false;

#define SENEOR_3_TIME 50
int32_t Sensor3Time = 0;
bool IsSensor3Time = false;

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
////////////////////////////////////////////////////////////////////////////////////
// BLE Data
////////////////////////////////////////////////////////////////////////////////////
bool IsBLEConnected = false;

BLEAdvertising *pAdvertising = nullptr;
BLEServer* pServer = nullptr;
BLEServer* oldServer = nullptr;
BLEService *pService = nullptr;
BLECharacteristic *pTransmitCharacteristic = nullptr;
BLECharacteristic *pReceiveCharacteristic = nullptr;
BLE2902 *pTransmitDescriptor = nullptr;

#define NUS_SERVICE_UUID "6E400001-B5A3-F393-E0A9-E50E24DCCA9E" // 서비스 
#define NUS_RX_CHAR_UUID "6E400002-B5A3-F393-E0A9-E50E24DCCA9E" // 수신
#define NUS_TX_CHAR_UUID "6E400003-B5A3-F393-E0A9-E50E24DCCA9E" // 데이터 송신
////////////////////////////////////////////////////////////////////////////////////


////////////////////////////////////////////////////////////////////////////////////
// Function define
////////////////////////////////////////////////////////////////////////////////////
void Sensor_1(void);
void Sensor_2(void);
void Sensor_3(void);
void InitHardwares(void);
void InitParameters(void);
void InitTimer(void);
void mainTimer(void);
void InitNetwork(void);
void InitMqtt(void);
bool ConnectMqtt(void);
bool NetworkChk(void);
void NetworkRestore(void);
bool ConnectServer(void);
bool ConnectWiFi(void);
void ScanAP(void);
void SaveAPInfo(int num, int ap_no);
void SortAPSequence(void);
void MQTT_callback(char* topic, byte* payload, unsigned int length);
void SetWillMessage(void);
void SetSubscribeTopic(void);
void PublishTopicVersion(void);
void PublishTopicResponseLogin(void);
void PublishTopicResponseStart(void);
void PublishTopicResponseStop(void);
void PublishTopicYJSensing(void);
void PublishNetworkStatus(void);
void TopicTimeMSChk(byte* payload, unsigned int length);
void TopicRequestLoginChk(byte* payload, unsigned int length);
void TopicRequestStartChk(byte* payload, unsigned int length);
void TopicRequestStopChk(byte* payload, unsigned int length);
void TopicAnalysisData(byte* payload, unsigned int length); // 장비의 작업데이터 분석 결과를 받음.
void BaseTime64Chk(void);
void InitBLE(void);
void Write_BLE(const char* topic,const char* data);
void RedLedOn(int msec);
void GreenLedOn(int msec);
void BlueLedOn(int msec);
void LedOn(int led, int msec);
void LedAllOff(void);
//void mcp_wrapper(void) { ADC.IRQ_handler(); }
////////////////////////////////////////////////////////////////////////////////////


////////////////////////////////////////////////////////////////////////////////////
// Module Function
////////////////////////////////////////////////////////////////////////////////////

void Sensor_1(void)
{
  //  센서 1
}
void Sensor_2(void)
{
  //  센서 2
}
void Sensor_3(void)
{
  //센서 3
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
  if(IsSensor1Time == false)
  {
    Sensor1Time++;
    if(Sensor1Time >= SENEOR_1_TIME) IsSensor1Time = true; // 50ms
  } 
  if(IsSensor2Time == false)
  {
    Sensor2Time++;
    if(Sensor2Time >= SENEOR_2_TIME) IsSensor2Time = true;
  }
  if(IsSensor3Time == false)
  {
    Sensor3Time++;
    if(Sensor3Time >= SENEOR_3_TIME) IsSensor3Time = true;
  }
  
  if(IsYJSendingTime == false)
  {
    YJSendingTime++;
    if(YJSendingTime >= YJSENDING_TIME) IsYJSendingTime = true; // 300ms
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
  InitNetwork();
  InitTimer();
}

void loop()
{
  if(IsSensor1Time == true) // 50ms
  {
    Sensor_1();
    Sensor1Time = 0;
    IsSensor1Time = false;
  }
  else if(IsSensor2Time == true) // 270ms
  {
      Sensor_2();
      Sensor2Time = 0;
      IsSensor2Time = false;
  }
  else if(IsSensor3Time == true)
  {
    Sensor_3();
    Sensor3Time = 0;
    IsSensor3Time = false;
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
      if(IsYJSendingTime == true) // 센서 데이터 업데이트. 
      {
        PublishTopicYJSensing();
        BlueLedOn(100);
        YJSendingTime = 0;
        IsYJSendingTime = false;
      }
    }
  }
  if(payload_status == true)
  {
    //Serial.printf("\r\nSub %s : ", payload_topic, payload_length);
    if(payload_length > 200) payload_buf[200] = 0x00;
    else payload_buf[payload_length] = 0x00;
    //Serial.print((char*)payload_buf);
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

void InitTimer(void)
{
  mainTicker.attach_ms(1, mainTimer);

  esp_task_wdt_init(WDT_TIMEOUT, true);
  esp_task_wdt_add(NULL);
}
////////////////////////////////////////////////////////////////////////////////////
// Network Function
////////////////////////////////////////////////////////////////////////////////////
void InitNetwork(void)
{
  uint8_t macnum[6];
  strcpy(WiFiSSID, Par.ptrWiFiSSID);
  strcpy(WiFiKey, Par.ptrWiFiKey);
  WiFi.mode(WIFI_STA);
  WiFi.macAddress(macnum);
  strcpy(ServerIP, Par.ptrServerIP);
  strcpy(OTAServerIP, Par.ptrOTAServerIP);
  PortMqtt = Par.ptrConnectionPort[2];
  PortUpdate = Par.ptrConnectionPort[3];
  sprintf(macaddr, "%02X%02X%02X%02X%02X%02X", macnum[0], macnum[1], macnum[2], macnum[3], macnum[4], macnum[5]);
  sprintf(clientname,"ARIIoT%s%d",Par.ptrMacAddressHex,PowerOnTime);
  sprintf(UpdateURL, "http://%s:%d%s?x-ESP32-version=%s", OTAServerIP, Par.ptrConnectionPort[3], BSet.update_path, Par.ptrModuleVersion);

  Serial.printf("\r\nOTACheckTime = %d", OTACheckTime);
  Serial.printf("\r\nUpdateURL = %s", UpdateURL);
  espClient.setTimeout(2);

  InitMqtt();
  ConnectServer();
}

void InitMqtt(void)
{
  mqttClient.setClient(espClient);
  mqttClient.setServer(ServerIP, PortMqtt);
  mqttClient.setCallback(MQTT_callback);
  SetWillMessage();
}

bool ConnectServer(void)
{
  BlueLedOn(LEDONTIME_MAX);  //Connection is started

  WiFiFailCnt++;
  if((WiFi.status() == WL_CONNECTED)&&(WiFiFailCnt < WIFI_FAILCNT_MAX))
  {
    IsNetworkConnected = true;
    mqttClient.setClient(espClient);
    IsServerConnected = ConnectMqtt();
    if(IsServerConnected == true) WiFiFailCnt = 0;
  }
  else
  {
    if(WiFi.status() == WL_CONNECTED)
    {
      WiFi.disconnect();
      delay(2000);
    }
    
    if(ConnectWiFi() == true)
    {
      WiFiFailCnt = 0;
      IsNetworkConnected = true;
      mqttClient.setClient(espClient);
      IsServerConnected = ConnectMqtt();
    }
    else
    {
      IsNetworkConnected = false;
      IsServerConnected = false;
    }    
  }
  return IsServerConnected;
}

bool ConnectWiFi(void)
{
  Serial.print("\r\nTrying to connect WiFi");

  ScanAP();
  if(AP_NUM <= 0)
  {
    Serial.printf("\r\n%s WiFi is not found", WiFiSSID);
    return false;
  }
  Serial.printf("\r\nWIFI Connection to %s : %s : %d", AP_SSID[0], AP_KEY[0], AP_RSSI[0]);

  //WiFi.disconnect();
  WiFi.begin(AP_SSID[0], AP_KEY[0], AP_CHANNEL[0], AP_MAC[0], true);
  for(int i=0; i<20; i++)
  {
    delay(500);
    Serial.print(".");
    if(WiFi.status() == WL_CONNECTED)
    {
      AriMT.qnetstatus.IsWiFiConnected = true;
      Serial.print("Connected!");
      return true;
    }
  }
  AriMT.qnetstatus.IsWiFiConnected = false;
  Serial.print("Failed!");
  return false;
}

bool ConnectMqtt(void)
{
  sprintf(clientname,"ARIIoT%s%d",Par.ptrMacAddressHex,PowerOnTime);
  Serial.printf("\r\nAttempting MQTT connection...(%s)",clientname);

  //mqttClient.disconnect();
  if(mqttClient.connect(clientname,MQTT_ID,MQTT_PWD) == true)
  {
    mqttClient.loop();
    SetSubscribeTopic();
    Serial.print(" connected!");
    AriMT.qnetstatus.IsServerConnected = true;
    return true;
  }
  Serial.print(" connection failed!");
  AriMT.qnetstatus.IsServerConnected = false;
  return false;
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
  }
  return IsServerConnected;
}

void NetworkRestore(void)
{
  if(WiFi.status() == WL_CONNECTED) ConnectMqtt();
  else ConnectServer();
}
////////////////////////////////////////////////////////////////////////////////////


////////////////////////////////////////////////////////////////////////////////////
// 1. AP를 SCAN한다.
// 2. 관심있는 AP를 선별한다.
// 3. 선별된 AP중 가장 신호세기가 큰 AP 순서로 정렬한다.
////////////////////////////////////////////////////////////////////////////////////
void ScanAP(void)
{
  int n = WiFi.scanNetworks();
  Serial.printf("\r\nScan is done : %d networks are founded", n);

  AP_NUM = 0;
  for(int i=0; i<n; i++)
  {
    String Scan_SSID = WiFi.SSID(i);
    if(Scan_SSID.equals(WiFiSSID))
    {
      SaveAPInfo(AP_NUM, i);
      if(AP_NUM < AP_SCAN_MAX) AP_NUM++;
      Serial.println();
      Serial.print(Scan_SSID);
      Serial.printf(" Channel(%d)  RSSI(%d)  MAC:", WiFi.channel(i), WiFi.RSSI(i));
      uint8_t *pBSSID = WiFi.BSSID(i);
      for(int j=0; j<6; j++) Serial.printf("%02X", pBSSID[j]);
    }
  }
  SortAPSequence();
}

void SaveAPInfo(int num, int ap_no)
{
  if(num >= AP_SCAN_MAX) return;

  AP_CHANNEL[num] = WiFi.channel(ap_no);
  AP_RSSI[num] = WiFi.RSSI(ap_no);
  uint8_t *pBSSID = WiFi.BSSID(ap_no);
  for(int i=0; i<6; i++)  AP_MAC[num][i] = pBSSID[i];
  strcpy(AP_SSID[num], WiFiSSID);
  strcpy(AP_KEY[num], WiFiKey);
}

void SortAPSequence(void)
{
  uint8_t chbak;
  char chtemp[30];
  int intbak;

  for(int i=0; i<AP_NUM - 1; i++)
  {
    int tmp = i;
    for(int j = i + 1; j < AP_NUM; j++)
    {
      if(AP_RSSI[j] > AP_RSSI[tmp]) tmp = j;
    }

    for(int j=0; j<6; j++) {
      chbak = AP_MAC[i][j];
      AP_MAC[i][j] = AP_MAC[tmp][j];
      AP_MAC[tmp][j] = chbak;
    }

    strcpy(chtemp, AP_SSID[i]);
    strcpy(AP_SSID[i], AP_SSID[tmp]);
    strcpy(AP_SSID[tmp], chtemp);

    strcpy(chtemp, AP_KEY[i]);
    strcpy(AP_KEY[i], AP_KEY[tmp]);
    strcpy(AP_KEY[tmp], chtemp);

    intbak = AP_CHANNEL[i];
    AP_CHANNEL[i] = AP_CHANNEL[tmp];
    AP_CHANNEL[tmp] = intbak;

    intbak = AP_RSSI[i];
    AP_RSSI[i] = AP_RSSI[tmp];
    AP_RSSI[tmp] = intbak;
  }

  for(int i=0; i<AP_NUM; i++)
  {
    Serial.printf("\r\nSSID(%s) KEY(%s) RSSI(%d)", AP_SSID[i], AP_KEY[i], AP_RSSI[i]);
    Serial.printf(" MAC(%02x:%02x:%02x:%02x:%02x:%02x)", AP_MAC[i][0], AP_MAC[i][1], AP_MAC[i][2], AP_MAC[i][3], AP_MAC[i][4], AP_MAC[i][5]);
    Serial.printf(" CH(%d)", AP_CHANNEL[i]);
  }
}
////////////////////////////////////////////////////////////////////////////////////


////////////////////////////////////////////////////////////////////////////////////
// MQTT Function
////////////////////////////////////////////////////////////////////////////////////
void MQTT_callback(char* topic, byte* payload, unsigned int length)
{
  IsMqttRecvStatus = true;
  Serial.print("\r\nMQTTCallback Start");
  if(strcmp(topic, topic_gen_timems) == 0) TopicTimeMSChk(payload, length);
  else if(strcmp(topic, BSet.topic_request_login) == 0) TopicRequestLoginChk(payload, length);
  else if(strcmp(topic, BSet.topic_request_start) == 0) TopicRequestStartChk(payload, length);
  else if(strcmp(topic, BSet.topic_request_stop) == 0) TopicRequestStopChk(payload, length);
  else if(strcmp(topic, BSet.topic_analysisdata) == 0) TopicAnalysisData(payload, length); // 분석 결과 수신

  if(payload_status == false)
  {
    strcpy(payload_topic, topic);
    for(int i=0; i<length; i++) payload_buf[i] = payload[i];
    payload_length = length;
    payload_status = true;
  }
  Serial.print("  MQTTCallback Stop");
  IsMqttRecvStatus = false;
}

void SetSubscribeTopic(void)
{
  mqttClient.subscribe(topic_gen_timems,MQTTQOS0); mqttClient.loop();
  mqttClient.subscribe(BSet.topic_request_login,MQTTQOS0); mqttClient.loop();
  mqttClient.subscribe(BSet.topic_request_start,MQTTQOS0); mqttClient.loop();
  mqttClient.subscribe(BSet.topic_request_stop,MQTTQOS0); mqttClient.loop();
  mqttClient.subscribe(BSet.topic_analysisdata,MQTTQOS0); mqttClient.loop(); // 작업 데이터 분석 결과 수신 을 위한 mqtt 구독
  
#ifdef MQTT_DISPLAY_EN
  mqttClient.subscribe(topic_gen_version,MQTTQOS0); mqttClient.loop();
#endif
}

void SetWillMessage(void)
{
  strcpy(AriMT.qinfo.MAC, Par.ptrMacAddressHex);
  strcpy(AriMT.qinfo.AP_MAC, "");
  strcpy(AriMT.qinfo.IOT_SPPL_CD, Par.ptrSupplierName);
  strcpy(AriMT.qinfo.IOT_MODEL, Par.ptrModuleName);
  strcpy(AriMT.qinfo.MCIP, "");
  strcpy(AriMT.qinfo.MCID, "");
  strcpy(AriMT.qinfo.STS, "OFF");
  strcpy(AriMT.qinfo.VER, Par.ptrHardSoftVersion);
  AriMT.PublishTopicInit();
  strcpy(WillMsg, AriMT.qbuf);
}

void PublishTopicVersion(void)
{
  //Serial.print("\r\nPublishTopicVersion Start");  
  strcpy(AriMT.qversion.MAC, Par.ptrMacAddressHex);
  strcpy(AriMT.qversion.ProgramVer, Par.ptrModuleVersion);
  strcpy(AriMT.qversion.HardSoftVer, Par.ptrHardSoftVersion);
  strcpy(AriMT.qversion.Type,"T-MDS");
  AriMT.qversion.BootCount = Par.UPData.data.BootCount;
  AriMT.qversion.PowerOnTime = PowerOnTime;
  strcpy(AriMT.qversion.Message, Message);
  Message[0] = 0x00;
  AriMT.PublishTopicVersion();

  while(IsMqttRecvStatus==true)delay(1);
  int length = AriMT.CheckQbufLength();
  uint8_t* pubmsg = (uint8_t *)malloc(length+1);
  for(int i=0;i<length;i++) pubmsg[i] = AriMT.qbuf[i];
  pubmsg[length] = 0;
  Write_BLE("info",(const char*)pubmsg);
  mqttClient.publish(topic_gen_version, (const uint8_t*)pubmsg, length, false);
  mqttClient.loop();
  //Serial.printf("\r\nPublished Version(%s) : %s",topic_gen_version,pubmsg);
  free(pubmsg);
  
  //mqttClient.publish(topic_gen_version, (const uint8_t*)AriMT.qbuf, length, false);
  //mqttClient.loop();
  //Serial.printf("  PublishTopicVersion Stop(%d)",length);
}

void PublishTopicResponseLogin(void)
{
  //Serial.print("\r\nPublishTopicResponseLogin Start");  
  AriMT.qresponselogin.WorkerIdx = AriMT.qrequestlogin.WorkerIdx;
  AriMT.PublishTopicResponseLogin();
  
  while(IsMqttRecvStatus==true)delay(1);
  int length = AriMT.CheckQbufLength();
  uint8_t* pubmsg = (uint8_t *)malloc(length+1);
  for(int i=0;i<length;i++) pubmsg[i] = AriMT.qbuf[i];
  pubmsg[length] = 0;
  Write_BLE("Login",(const char*)pubmsg);
  mqttClient.publish(BSet.topic_response_login, (const uint8_t*)pubmsg, length, false);
  mqttClient.loop();
  //Serial.printf("\r\nPublished LOGIN(%s) : %s",BSet.topic_response_login,pubmsg);  
  free(pubmsg);
  
  //mqttClient.publish(BSet.topic_response_login, (const uint8_t*)AriMT.qbuf, length, false);
  //mqttClient.loop();
  //Serial.printf("  PublishTopicResponseLogin Stop(%d)",length);  
}

void PublishTopicResponseStart(void)
{
  //Serial.print("\r\nPublishTopicResponseStart Start");  
  AriMT.qresponsestart.WorkerIdx = AriMT.qrequeststart.WorkerIdx;
  AriMT.qresponsestart.WorkUnitIdx = AriMT.qrequeststart.WorkUnitIdx;
  AriMT.qresponsestart.TargetDepth = AriMT.qrequeststart.TargetDepth;
  AriMT.PublishTopicResponseStart();
  
  while(IsMqttRecvStatus==true)delay(1);
  int length = AriMT.CheckQbufLength();
  uint8_t* pubmsg = (uint8_t *)malloc(length+1);
  for(int i=0;i<length;i++) pubmsg[i] = AriMT.qbuf[i];
  pubmsg[length] = 0;
  Write_BLE("Start",(const char*)pubmsg);
  mqttClient.publish(BSet.topic_response_start, (const uint8_t*)pubmsg, length, false);
  mqttClient.loop();
  //Serial.printf("\r\nPublished START(%s) : %s",BSet.topic_response_start,pubmsg);  
  free(pubmsg);
  
  //mqttClient.publish(BSet.topic_response_start, (const uint8_t*)AriMT.qbuf, length, false);
  //mqttClient.loop();
  //Serial.printf("  PublishTopicResponseStart Stop",length);
}

void PublishTopicResponseStop(void)
{
  //Serial.print("\r\nPublishTopicResponseStop Start");
  AriMT.qresponsestop.WorkerIdx = AriMT.qrequeststop.WorkerIdx;
  AriMT.qresponsestop.WorkUnitIdx = AriMT.qrequeststop.WorkUnitIdx;
  AriMT.PublishTopicResponseStop();
  
  while(IsMqttRecvStatus==true)delay(1);
  int length = AriMT.CheckQbufLength();
  uint8_t* pubmsg = (uint8_t *)malloc(length+1);
  for(int i=0;i<length;i++) pubmsg[i] = AriMT.qbuf[i];
  pubmsg[length] = 0;
  Write_BLE("Stop",(const char*)pubmsg);  
  mqttClient.publish(BSet.topic_response_stop, (const uint8_t*)pubmsg, length, false);
  mqttClient.loop();
  //Serial.printf("\r\nPublished STOP(%s) : %s",BSet.topic_response_stop,pubmsg);
  free(pubmsg);
  //mqttClient.publish(BSet.topic_response_stop, (const uint8_t*)AriMT.qbuf, length, false);
  //mqttClient.loop();
  //Serial.printf("  PublishTopicResponseStop Stop(%d)",length);
}

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
  AriMT.qyjsensing.Holl[0] = Holl;
  
  AriMT.PublishTopicYJSensing();

  while(IsMqttRecvStatus==true)delay(1);  
  int length = AriMT.CheckQbufLength();
  uint8_t* pubmsg = (uint8_t *)malloc(length+1);
  for(int i=0;i<length;i++) pubmsg[i] = AriMT.qbuf[i];
  pubmsg[length] = 0;
  Write_BLE("Sensing",(const char*)pubmsg);
  mqttClient.publish(BSet.topic_yjsensing_new, (const uint8_t*)pubmsg, length, false);
  mqttClient.loop();
  //Serial.printf("\r\nPublished YJSensing(%s) : %s",BSet.topic_yjsensing_new,pubmsg);
  free(pubmsg);
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
void TopicAnalysisData(byte* payload, unsigned int length) // 분석 결과 데이터 파싱
{
  AriMT.ParsingTopicAnalysisData(payload, length);
  IsTopicAnalysisDataReceived = true;
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
    BLEDevice::init("DSOL-2000");// 초기화
    delay(100);

    pServer = BLEDevice::createServer();
    pService = pServer->createService(NUS_SERVICE_UUID);
    
    BLE_Callbacks* BLE_Callback = new BLE_Callbacks();
    
    // TX (송신) 특성 설정
    pTransmitCharacteristic = pService->createCharacteristic(
        NUS_TX_CHAR_UUID,
        BLECharacteristic::PROPERTY_READ |
        BLECharacteristic::PROPERTY_WRITE |
        BLECharacteristic::PROPERTY_NOTIFY |
        BLECharacteristic::PROPERTY_INDICATE
    );
    pTransmitCharacteristic->setCallbacks(BLE_Callback);

    // RX (수신) 특성 설정
    pReceiveCharacteristic = pService->createCharacteristic(
        NUS_RX_CHAR_UUID,
        BLECharacteristic::PROPERTY_WRITE | 
        BLECharacteristic::PROPERTY_WRITE_NR
    );
    pReceiveCharacteristic->setCallbacks(BLE_Callback);
    
    // Descriptor 및 서비스 시작
    pTransmitDescriptor = new BLE2902();
    pTransmitDescriptor->setNotifications(true);
    pTransmitCharacteristic->addDescriptor(pTransmitDescriptor);

    pService->start();
    pServer->setCallbacks(BLE_Callback); // 서버에 콜백 설정
    pAdvertising = pServer->getAdvertising();
    pAdvertising->start();
}

void Write_BLE(const char* topic,const char* data)
{
  std::string combined = std::string(topic) + "_" + std::string(data);
  pTransmitCharacteristic->setValue(combined.c_str());
  pTransmitCharacteristic->notify();
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
