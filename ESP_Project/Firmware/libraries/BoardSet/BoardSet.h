#ifndef BoardSet_h
#define BoardSet_h

#include <Arduino.h>
#include <WiFi.h>
#include <Wire.h>
#include <Typedef_Ari.h>

////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Define Paramerter Version
////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#define PARAMETER_VERSION "V2.2.5"

////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Define Board Type
////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#define DONGLE_FR  1
#define DONGLE_WP  2
#define DONGLE_EXT 3
#define DAQ_1ST    4
#define DAQ_FRNET  5 
#define DAQ_WPNET  6
#define DAQ_YOUNGJIN 7
#define DONGLE_YUPOONG 8
#define DAQ_EXCAVATOR 9
#define DAQ_BASIC 10
#define DAQ_DEMO 11
#define DAQ_SOOSAN 12
#define DAQ_MGTSHIP 13
#define WDCAS_FRIGER_QA 14
#define WDCAS_FRIGER_TSI 15
#define WDCAS_ADDON_WPT 16
#define WDCAS_ADDON_DAF 17

////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Define Setup
////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#define WIFI_SEL 1
#define ETHERNET_SEL 2

#define RED_LED 1
#define BLUE_LED 2
#define GREEN_LED 3

#define COMMON_ANODE_LED 1
#define COMMON_CATHODE_LED 2
#define WDCAS_MAIN_LED 3

////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Define Module Info
////////////////////////////////////////////////////////////////////////////////////////////////////////////////
const char ModuleName_01[] = "DONGLE_FR";
const char ModuleName_02[] = "DONGLE_WP";
const char ModuleName_03[] = "DONGLE_EXT";
const char ModuleName_04[] = "DAQ_1ST";
const char ModuleName_05[] = "DAQ_FRNET";
const char ModuleName_06[] = "DAQ_WPNET";
const char ModuleName_07[] = "DAQ_YOUNGJIN";
const char ModuleName_08[] = "DONGLE_YUPOONG";
const char ModuleName_09[] = "DAQ_EXCAVATORS";
const char ModuleName_10[] = "DAQ_BASIC";
const char ModuleName_11[] = "DAQ_DEMO";
const char ModuleName_12[] = "DAQ_SOOSAN";
const char ModuleName_13[] = "DAQ_MGTSHIP";
const char ModuleName_14[] = "WDCAS_FRIGER_QA";
const char ModuleName_15[] = "WDCAS_FRIGER_TSI";
const char ModuleName_16[] = "WDCAS_ADDON_WPT";
const char ModuleName_17[] = "WDCAS_ADDON_DAF";

const char ModuleType[] = "Ari_IoT";
const char ModuleVersion[] = "1901910001";
const char HardSoftVersion[] = "A000-0000";
const char SupplierName[] = "Ari-InfoTech";

const char WiFiSSID_01[] = "MD1W_AP1";
const char WiFiSSID_02[] = "WDCAS_WP";
const char WiFiSSID_03[] = "LTE_10521C894314";
const char WiFiSSID_04[] = "ARIIT_NET";
const char WiFiSSID_05[] = "MD1W_AP2";
const char WiFiSSID_06[] = "ARI_WDCAS_QA";
const char WiFiSSID_07[] = "ARI_WDCAS_TSI";

const char WiFiKey_01[] = "md1w13579";
const char WiFiKey_02[] = "pass_wdcas_wp";
const char WiFiKey_03[] = "ik09Pw72!!m";
const char WiFiKey_04[] = "987654321";

const char ServerIP_01[] = "192.168.10.138";
const char ServerIP_02[] = "139.150.80.81";
const char ServerIP_03[] = "211.169.215.170";
const char ServerIP_04[] = "211.169.215.170";
const char ServerIP_05[] = "112.221.85.116";
const char ServerIP_06[] = "192.168.15.30";

const char OTAServerIP_01[] = "192.168.10.138";
const char OTAServerIP_02[] = "139.150.80.81";
const char OTAServerIP_03[] = "211.169.215.170";
const char OTAServerIP_04[] = "211.169.215.170";
const char OTAServerIP_05[] = "112.221.85.116";

#define SERVERCHECK_PORT 9080
#define DATASEND_PORT 8190
#define MQTT_PORT 53200
#define UPDATE_PORT 8091
#define FILELOAD_PORT 9001
// 영진 장비 모델 코드
#define YJ5600HB 5600
#define YJ7000HB 7000

////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Define MQTT Topic name
////////////////////////////////////////////////////////////////////////////////////////////////////////////////
const char topic_fridge_forcedwrite[] = "/AABBCCDDEEFF/FridgeWrite";
const char topic_fridge_forcedwritereceived[] = "/FridgeWriteReceived";
const char topic_fridge_forcedwritefinished[] = "/FridgeWriteFinished";
const char topic_fridge_hassread[] = "/Event/FridgeRead";
const char topic_fridge_powerread[] = "/Event/PowerRead";
const char topic_fridge_tcread[] = "/Event/TCRead";

const char topic_purifier_forcedwrite[] = "/AABBCCDDEEFF/PurifierWrite";
const char topic_purifier_forcedwritereceived[] = "/PurifierWriteReceived";
const char topic_purifier_forcedwritefinished[] = "/PurifierWriteFinished";
const char topic_purifier_hassread[] = "/Event/ReadData";
const char topic_purifier_powerread[] = "/Event/PowerRead/WaterPurifier";
const char topic_purifier_tcread[] = "/Event/TCRead/WaterPurifier";

const char topic_demo_powerread[] = "Event/PowerRead/Demo/";
const char topic_demo_tcread[] = "Event/TCRead/Demo/";

const char topic_init_01[] = "/SysCtrl";
const char topic_timems_01[] = "/Brodcast/TimeMS";
const char topic_timems_02[] = "/Broadcast/TimeMS";
const char topic_version_01[] = "/Info/Version";
const char topic_test_01[] = "/Event/Test";
const char topic_hasserror[] = "/Event/HassError";
const char topic_hasschkdata[] = "/Event/HassChkData";

////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// New defined MQTT topic name
////////////////////////////////////////////////////////////////////////////////////////////////////////////////
const char topic_fridge_request_daqcode[] = "Request/DAQ/AABBCCDDEEFF/";
const char topic_response_daqcode[] = "Response/DAQ/";
const char topic_fridge_request_aridata[] = "Request/AriData/AABBCCDDEEFF/";
const char topic_response_aridata[] = "Response/AriData/";
const char topic_request_inform[] = "Request/Inform/";
const char topic_response_inform_def[] = "Response/Inform/AABBCCDDEEFF/";
const char topic_request_firmwareupdate[] = "Request/FirmwareUpdate/";
const char topic_response_firmwareupdate[] = "Response/FirmwareUpdate/";

const char topic_fridge_request_samplingtimeread[] = "Request/Refrigerator/SamplingTimeRead/AABBCCDDEEFF/";
const char topic_fridge_response_samplingtimeread[] = "Response/Refrigerator/SamplingTimeRead/Finished/";
const char topic_fridge_request_samplingtimewrite[] = "Request/Refrigerator/SamplingTimeWrite/AABBCCDDEEFF/";
const char topic_fridge_response_samplingtimewrite[] = "Response/Refrigerator/SamplingTimeWrite/Finished/";
const char topic_purifier_request_samplingtimeread[] = "Request/WaterPurifier/SamplingTimeRead/AABBCCDDEEFF/";
const char topic_purifier_response_samplingtimeread[] = "Response/WaterPurifier/SamplingTimeRead/Finished/";
const char topic_purifier_request_samplingtimewrite[] = "Request/WaterPurifier/SamplingTimeWrite/AABBCCDDEEFF/";
const char topic_purifier_response_samplingtimewrite[] = "Response/WaterPurifier/SamplingTimeWrite/Finished/";

const char topic_gen_init[] = "SysCtrl/";
const char topic_gen_timems[] = "Broadcast/TimeMS/";
const char topic_gen_version[] = "Info/Version/";
const char topic_gen_test[] = "Event/Test/";

const char topic_request_tmds_login[] = "Request/T-MDS/Login/AABBCCDDEEFF/";
const char topic_response_tmds_login[] = "Response/T-MDS/Login/AABBCCDDEEFF/";
const char topic_request_tmds_start[] = "Request/T-MDS/Start/AABBCCDDEEFF/";
const char topic_response_tmds_start[] = "Response/T-MDS/Start/AABBCCDDEEFF/";
const char topic_request_tmds_stop[] = "Request/T-MDS/Stop/AABBCCDDEEFF/";
const char topic_response_tmds_stop[] = "Response/T-MDS/Stop/AABBCCDDEEFF/";
const char topic_tmds_yjsensing[] = "Event/T-MDS/YJSensing/AABBCCDDEEFF/"; // 13 호기..를 위해서... 추가...
const char topic_analysis_data[] = "Event/T-MDS/Analysis/AABBCCDDEEFF/"; // 장비데이터 분석을 서버에서 진행 하기 위한 추가..
const char topic_yjsensing[] = "Event/T-MDS/YJSensing/";
const char topic_gnssdata[] = "Event/T-MDS/GNSSData/";
const char topic_sssensing[] = "Event/T-MDS/SSSensing/";
const char topic_crane[] = "Event/T-MDS/CraneSensing/";
const char topic_encsensing[] = "Event/T-MDS/Encoder/";
const char topic_beaconscandata[] = "Event/BeaconScanData/";
const char topic_shocksensing[] = "Event/T-MDS/ShockSensing/";
const char topic_addonwpt[] = "Event/Refrigerator/WaterPipeTest/";

////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Define Update URL
////////////////////////////////////////////////////////////////////////////////////////////////////////////////
const char update_fridge_dongle_path[] = "/Update/Fridge_Update.php";
const char update_purifier_dongle_path[] = "/Update/Purifier_Update.php";
const char update_dongle_ext_path[] = "/Update/DongleExt_Update.php";
const char update_daq_1st_path[] = "/Update/DAQ1st_Update.php";
const char update_fridge_daq_path[] = "/Update/DAQFRNet_Update.php";
const char update_purifier_daq_path[] = "/Update/DAQWPNet_Update.php";
const char update_daq_youngjin_path[] = "/Update/DAQYoungJin_Update.php";
const char update_daq_excavator_path[] = "/Update/DAQExcavator_Update.php";
const char update_daq_basic_path[] = "/Update/DAQBasic_Update.php";
const char update_daq_demo_path[] = "/Update/DAQDemo_Update.php";
const char update_daq_soosan_path[] = "/Update/DAQSooSan_Update.php";
const char update_daq_mgtship_path[] = "/Update/DAQMGTShip_Update.php";
const char update_wdcas_friger_qa_path[] = "/Update/WDCASFrigerQA_Update.php";
const char update_wdcas_friger_tsi_path[] = "/Update/WDCASFrigerTSI_Update.php";
const char update_wdcas_addon_wpt_path[] = "/Update/WDCASAddonWPT_Update.php";
const char update_wdcas_addon_daf_path[] = "/Update/WDCASAddonDAF_Update.php";

////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Define Modbus Command
////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#define MODBUSCMD_NUM 8
#define TCDATA_OFFSET 1

const uint8_t ModbusCmdData[MODBUSCMD_NUM][8] = {
  {0x01, 0x04, 0x00, 0x00, 0x00, 0x0A, 0x00, 0x00},  // Read PZEM-016
  {0x02, 0x03, 0x00, 0x00, 0x00, 0x08, 0x00, 0x00},  // Read TC data 01-08 ch
  {0x03, 0x03, 0x00, 0x00, 0x00, 0x08, 0x00, 0x00},  // Read TC data 09-16 ch
  {0x04, 0x03, 0x00, 0x00, 0x00, 0x08, 0x00, 0x00},  // Read TC data 17-24 ch
  {0x05, 0x03, 0x00, 0x00, 0x00, 0x08, 0x00, 0x00},  // Read TC data 25-32 ch
  {0x06, 0x04, 0x11, 0x00, 0x00, 0x4C, 0x00, 0x00},  // Read PM-3112-100
  {0x07, 0x04, 0x00, 0x00, 0x00, 0x16, 0x00, 0x00},  
  {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00},  // No device
};

const int16_t Fridge_ModbusDataPackets[MODBUSCMD_NUM] = {1,     1,     1,     1,     1,     1,    0,    0};
const int32_t Fridge_ModbusCmdSendTime[MODBUSCMD_NUM] = {30000, 30000, 30000, 30000, 30000, 30000, 1000, 0};
const int32_t Fridge_ModbusCmdTimeInit[MODBUSCMD_NUM] = {28000, 18000, 17000, 16000, 15000, 29000, 700, 0};
const bool Fridge_ModbusCmdSendSeq[MODBUSCMD_NUM] =    {true, false, false, false, true,  true, false, false};

const int16_t Purifier_ModbusDataPackets[MODBUSCMD_NUM] = {1,     15,    0,     0,     0,     1,    0,    0};
const int32_t Purifier_ModbusCmdSendTime[MODBUSCMD_NUM] = {30000, 1000, 1000, 1000, 1000, 30000, 1000, 0};
const int32_t Purifier_ModbusCmdTimeInit[MODBUSCMD_NUM] = {28000, 200, 400, 600, 800, 29000, 700, 0};
const uint8_t Purifier_ModbusCmdSendSeq[MODBUSCMD_NUM] =    {true, true, false, false, false, true, false, false};

const int16_t Demo_ModbusDataPackets[MODBUSCMD_NUM] = {0,     6,    0,     0,     0,     0,    0,    0};
const int32_t Demo_ModbusCmdSendTime[MODBUSCMD_NUM] = {30000, 5000, 30000, 30000, 30000, 30000, 1000, 0};
const int32_t Demo_ModbusCmdTimeInit[MODBUSCMD_NUM] = {30000, 4000, 17000, 16000, 15000, 19000, 700, 0};
const uint8_t Demo_ModbusCmdSendSeq[MODBUSCMD_NUM] =    {false, true, false, false, false, false, false, false};

////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Define Hass Command
////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#define HASSCMD_NUM 20

const uint8_t Fridge_HassStartCode[HASSCMD_NUM] =      {  0xA5,  0xA5,  0xA5, 0xA5,  0xA5,   0xA5,     0xA5,   0xA5,   0xA6,  0xA6,  0xA6,  0xA6, 0xA6, 0, 0, 0, 0, 0, 0, 0};
const uint8_t Fridge_HassCmdCode[HASSCMD_NUM] =      {  0x05,   0x11,  0x12,  0x14,  0x30,   0x44,     0x52,    0x61,   0x02,   0x03,  0x10,  0x11, 0x12,  0, 0, 0, 0, 0, 0, 0};
const int16_t Fridge_HassDataLength[HASSCMD_NUM] =     {  15,      24,     4,      7,        5,      13,        10,      13,      11,     15,     23,    19,    12,        0, 0, 0, 0, 0, 0, 0};
const int16_t Fridge_HassDataPackets[HASSCMD_NUM] =    {   1,        3,     3,      30,       1,       1,         1,        3,      30,      1,      3,      3,     3,          0, 0, 0, 0, 0, 0, 0};
const int32_t Fridge_HassCmdSendTime[HASSCMD_NUM] = {60000,30000,30000, 1000, 600000,600000, 3600000, 30000, 2000, 600000,30000,30000,30000, 0, 0, 0, 0, 0, 0, 0};
const int32_t Fridge_HassCmdTimeInit[HASSCMD_NUM] =   {50000,10000,13000,  500,  450000,400000, 3000000, 16000, 1500, 350000,21000,24000,19000, 0, 0, 0, 0, 0, 0, 0};

const uint8_t Purifier_HassStartCode[HASSCMD_NUM] =      { 0xA5, 0xA5, 0xA5,  0xA5, 0xA5,  0xA5,  0xA5,  0xA5,     0xA5, 0xA6,  0xA6,  0xA6,  0xA6, 0xA6,  0, 0, 0, 0, 0, 0};
const uint8_t Purifier_HassCmdCode[HASSCMD_NUM] =      { 0x05, 0x09,  0x11,  0x12,  0x14,  0x30,  0x44,   0x52,     0x61,  0x02,  0x03,  0x12,  0x21,  0x23,  0, 0, 0, 0, 0, 0};
const int16_t Purifier_HassDataLength[HASSCMD_NUM] =    {  15,    15,      3,      1,      1,       5,      6,      10,         2,      3,     15,      4,      5,    21,    0, 0, 0, 0, 0, 0};
const int16_t Purifier_HassDataPackets[HASSCMD_NUM] =   {   2,     2,      10,     30,    30,       2,      2,       1,        10,     60,    10,     10,     30,    10,    0, 0, 0, 0, 0, 0};
const int32_t Purifier_HassCmdSendTime[HASSCMD_NUM] ={60000,60000,12000,2000, 2000, 60000,  60000, 3600000, 12000, 500,  12000,12000, 2000, 12000, 0, 0, 0, 0, 0, 0};
const int32_t Purifier_HassCmdTimeInit[HASSCMD_NUM] =  {20000,35000,  2000,    0,   500, 25000,  30000, 3550000,  3000,  200,  5000,  7000, 1000,  9000,  0, 0, 0, 0, 0, 0};
////////////////////////////////////////////////////////////////////////////////////////////////////////////////

class BoardSet
{
  public:
    BoardSet();
    void BoardInit(int id);
    void BoardInit_DONGLE_FR(void);
    void BoardInit_DONGLE_WP(void);
    void BoardInit_DONGLE_EXT(void);
    void BoardInit_DAQ_1ST(void);
    void BoardInit_DAQ_FRNET(void);
    void BoardInit_DAQ_WPNET(void);
    void BoardInit_DAQ_YOUNGJIN(void);
    void BoardInit_DAQ_EXCAVATOR(void);
    void BoardInit_DONGLE_YUPOONG(void);
    void BoardInit_DAQ_BASIC(void);
    void BoardInit_DAQ_DEMO(void);
    void BoardInit_DAQ_SOOSAN(void);
    void BoardInit_DAQ_MGTSHIP(void);
    void BoardInit_WDCAS_FRIGER_QA(void);
    void BoardInit_WDCAS_FRIGER_TSI(void);
    void BoardInit_WDCAS_ADDON_WPT(void);
    void BoardInit_WDCAS_ADDON_DAF(void);
    void BoardLedOn(int led);
    void BoardLedOff(int led);

    int LedType;
    int PortRedLed;
    int PortBlueLed;
    int PortGreenLed;
    int PortSelUart0;
    int PortNetSel;
    int Port485ReN;
    int Port485DeP;

    int PortRxdEn0;
    int PortTxdEn0;
    int PortRxdEn2;
    int PortTxdEn2; 
    int Port485ReN0;
    int Port485DeP0;
    int Port485ReN2;
    int Port485DeP2;

    char* ptrModuleName;
    char* ptrModuleType;
    char* ptrSupplierName;
    char* ptrModuleVersion;
    char* ptrHardSoftVersion;
    char* ptrWiFiSSID;
    char WiFiSSID[30];
    char* ptrWiFiKey;
    char* ptrServerIP;
    char* ptrOTAServerIP;

    int16_t ServerCheckPort;
    int16_t DataSendPort;
    int16_t MQTTPort;
    int16_t UpdatePort;
    int16_t FileLoadPort;

    // 모델별 데이터.
    int16_t MODEL_Code;
    int32_t Encoder;

    char topic_init[50];
    char topic_timems[50];
    char topic_version[50];
    char topic_test[50];
    char topic_forcedwrite[50];
    char topic_forcedwritereceived[50];
    char topic_forcedwritefinished[50];
    char topic_hassread[50];
    char topic_powerread[50];
    char topic_tcread[50];
    char topic_request_daqcode[50];
    char topic_request_aridata[50];
    char topic_request_samplingtimeread[70];
    char topic_response_samplingtimeread[70];
    char topic_request_samplingtimewrite[70];
    char topic_response_samplingtimewrite[70];
    char topic_response_inform[50];

    char topic_request_login[50];
    char topic_response_login[50];
    char topic_request_start[50];
    char topic_response_start[50];
    char topic_request_stop[50];
    char topic_response_stop[50];
    char topic_analysisdata[50]; // 작업데이터 분석결과 수신
    char topic_yjsensing_new[50]; // 신규버전 을 위한 수정..  라즈베리파이 제거.
    char topic_info[50]; // 신규버전 을 위한 수정..  라즈베리파이 제거.
    char update_path[50];

    int HassCmdNum;
    int ModbusCmdNum;

    uint8_t* ptrHassStartCode;
    uint8_t* ptrHassCmdCode;
    int16_t* ptrHassDataLength;
    int16_t* ptrHassDataPackets;
    int32_t* ptrHassCmdSendTime;
    int32_t* ptrHassCmdTimeInit;

    int16_t* ptrModbusDataPackets;
    int32_t* ptrModbusCmdSendTime;
    int32_t* ptrModbusCmdTimeInit;
    bool* ptrModbusCmdSendSeq;

    int NetSel = WIFI_SEL;

  private:

};

#endif
