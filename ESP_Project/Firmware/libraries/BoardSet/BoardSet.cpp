#include "BoardSet.h"

BoardSet::BoardSet()
{
}

void BoardSet::BoardInit_DONGLE_FR(void)
{
  Serial.begin(115200);
  Serial2.begin(9600);

  LedType = COMMON_CATHODE_LED;
  PortRedLed = 22;
  PortBlueLed = 21;
  PortGreenLed = 14;  // Not used
  PortSelUart0 = 32;  // Not used
  PortNetSel = 35;  // Not used
  Port485ReN = 33;  // Not used
  Port485DeP = 25;  // Not used

  ptrModuleName = (char*)ModuleName_01;
  ptrWiFiSSID = (char*)WiFiSSID_01;
  ptrWiFiKey = (char*)WiFiKey_01;
  ptrServerIP = (char*)ServerIP_01;
  ptrOTAServerIP = (char*)OTAServerIP_01;

  strcpy(topic_init, topic_init_01);
  strcpy(topic_timems, topic_timems_01);
  strcpy(topic_version, topic_version_01);
  strcpy(topic_test, topic_test_01);
  strcpy(topic_forcedwrite, topic_fridge_forcedwrite);
  strcpy(topic_forcedwritereceived, topic_fridge_forcedwritereceived);
  strcpy(topic_forcedwritefinished, topic_fridge_forcedwritefinished);
  strcpy(topic_hassread, topic_fridge_hassread);
  strcpy(topic_powerread, topic_fridge_powerread);
  strcpy(topic_tcread, topic_fridge_tcread);
  strcpy(update_path, update_fridge_dongle_path);

  HassCmdNum = 13;
  ptrHassStartCode = (uint8_t*)Fridge_HassStartCode;
  ptrHassCmdCode = (uint8_t*)Fridge_HassCmdCode;
  ptrHassDataLength = (int16_t*)Fridge_HassDataLength;
  ptrHassDataPackets = (int16_t*)Fridge_HassDataPackets;
  ptrHassCmdSendTime = (int32_t*)Fridge_HassCmdSendTime;
  ptrHassCmdTimeInit = (int32_t*)Fridge_HassCmdTimeInit;

  uint8_t macnum[6];
  WiFi.macAddress(macnum);
  char mactext[20];
  sprintf(mactext,"%02X%02X%02X%02X%02X%02X",macnum[0],macnum[1],macnum[2],macnum[3],macnum[4],macnum[5]);
  for(int i=0;i<12;i++)
  {
    topic_forcedwrite[i+1] = mactext[i];
  }
}

void BoardSet::BoardInit_DONGLE_WP(void)
{
  Serial.begin(115200);
  Serial2.begin(9600);

  LedType = COMMON_CATHODE_LED;
  PortRedLed = 22;
  PortBlueLed = 21;
  PortGreenLed = 14;  // Not used
  PortSelUart0 = 32;  // Not used
  PortNetSel = 35;  // Not used
  Port485ReN = 33;  // Not used
  Port485DeP = 25;  // Not used

  ptrModuleName = (char*)ModuleName_02;
  ptrWiFiSSID = (char*)WiFiSSID_01;
  ptrWiFiKey = (char*)WiFiKey_01;
  ptrServerIP = (char*)ServerIP_01;
  ptrOTAServerIP = (char*)OTAServerIP_01;

  strcpy(topic_init, topic_init_01);
  strcpy(topic_timems, topic_timems_01);
  strcpy(topic_version, topic_version_01);
  strcpy(topic_test, topic_test_01);
  strcpy(topic_forcedwrite, topic_purifier_forcedwrite);
  strcpy(topic_forcedwritereceived, topic_purifier_forcedwritereceived);
  strcpy(topic_forcedwritefinished, topic_purifier_forcedwritefinished);
  strcpy(topic_hassread, topic_purifier_hassread);
  strcpy(topic_powerread, topic_purifier_powerread);
  strcpy(topic_tcread, topic_purifier_tcread);
  strcpy(topic_request_samplingtimeread, topic_purifier_request_samplingtimeread);
  strcpy(topic_response_samplingtimeread, topic_purifier_response_samplingtimeread);
  strcpy(topic_request_samplingtimewrite, topic_purifier_request_samplingtimewrite);
  strcpy(topic_response_samplingtimewrite, topic_purifier_response_samplingtimewrite);
  strcpy(update_path, update_purifier_dongle_path);

  HassCmdNum = 14;
  ModbusCmdNum = 0;
  ptrHassStartCode = (uint8_t*)Purifier_HassStartCode;
  ptrHassCmdCode = (uint8_t*)Purifier_HassCmdCode;
  ptrHassDataLength = (int16_t*)Purifier_HassDataLength;
  ptrHassDataPackets = (int16_t*)Purifier_HassDataPackets;
  ptrHassCmdSendTime = (int32_t*)Purifier_HassCmdSendTime;
  ptrHassCmdTimeInit = (int32_t*)Purifier_HassCmdTimeInit;
  ptrModbusDataPackets = (int16_t*)Purifier_ModbusDataPackets;
  ptrModbusCmdSendTime = (int32_t*)Purifier_ModbusCmdSendTime;
  ptrModbusCmdTimeInit = (int32_t*)Purifier_ModbusCmdTimeInit;
  ptrModbusCmdSendSeq = (bool*)Purifier_ModbusCmdSendSeq;

  uint8_t macnum[6];
  WiFi.macAddress(macnum);
  char mactext[20];
  sprintf(mactext,"%02X%02X%02X%02X%02X%02X",macnum[0],macnum[1],macnum[2],macnum[3],macnum[4],macnum[5]);
  for(int i=0;i<12;i++)
  {
    topic_request_samplingtimeread[i+39] = mactext[i];
    topic_request_samplingtimewrite[i+40] = mactext[i];
    topic_forcedwrite[i+1] = mactext[i];
  }
}

void BoardSet::BoardInit_DONGLE_EXT(void)
{
  Serial.begin(115200);
  Serial2.begin(9600);

  delay(100);
  Wire.begin(21,22);
  delay(100);

  LedType = COMMON_ANODE_LED;
  PortRedLed = 33;
  PortBlueLed = 23;
  PortGreenLed = 32;  // Not used
  PortSelUart0 = 32;  // Not used
  PortNetSel = 35;  // Not used

  PortRxdEn0 = 19;
  PortTxdEn0 = 18;
  PortRxdEn2 = 4;
  PortTxdEn2 = 6;
  Port485ReN0 = 25;
  Port485DeP0 = 26;
  Port485ReN2 = 27;
  Port485DeP2 = 14;
  Port485ReN = Port485ReN2;
  Port485DeP = Port485DeP2;

  ptrModuleName = (char*)ModuleName_03;
  ptrWiFiSSID = (char*)WiFiSSID_01;
  ptrWiFiKey = (char*)WiFiKey_01;
  ptrServerIP = (char*)ServerIP_01;
  ptrOTAServerIP = (char*)OTAServerIP_01;
/*
  pinMode(PortRxdEn2, OUTPUT);
  pinMode(PortTxdEn2, OUTPUT);
  digitalWrite(PortRxdEn2, HIGH);
  digitalWrite(PortTxdEn2, HIGH);
*/
/*
  pinMode(Port485ReN0, OUTPUT);
  pinMode(Port485DeP0, OUTPUT);
  digitalWrite(Port485ReN0, HIGH);
  digitalWrite(Port485DeP0, LOW);

  pinMode(PortRxdEn0, OUTPUT);
  pinMode(PortTxdEn0, OUTPUT);
  digitalWrite(PortRxdEn0, LOW);
  digitalWrite(PortTxdEn0, LOW);
*/
}

void BoardSet::BoardInit_DAQ_1ST(void)
{
  Serial.begin(9600);
  Serial2.begin(9600);

  LedType = COMMON_CATHODE_LED;
  PortRedLed = 25;
  PortBlueLed = 26;
  PortGreenLed = 27;
  PortSelUart0 = 14;  // Not used
  PortNetSel = 35;  // Not used
  Port485ReN = 32;
  Port485DeP = 33;

  ptrModuleName = (char*)ModuleName_04;
  ptrWiFiSSID = (char*)WiFiSSID_01;
  ptrWiFiKey = (char*)WiFiKey_01;
  ptrServerIP = (char*)ServerIP_01;
  ptrOTAServerIP = (char*)OTAServerIP_01;

  strcpy(topic_init, topic_init_01);
  strcpy(topic_timems, topic_timems_01);
  strcpy(topic_version, topic_version_01);
  strcpy(topic_test, topic_test_01);
  strcpy(topic_forcedwrite, topic_fridge_forcedwrite);
  strcpy(topic_forcedwritereceived, topic_fridge_forcedwritereceived);
  strcpy(topic_forcedwritefinished, topic_fridge_forcedwritefinished);
  strcpy(topic_hassread, topic_fridge_hassread);
  strcpy(topic_powerread, topic_fridge_powerread);
  strcpy(topic_tcread, topic_fridge_tcread);
  strcpy(update_path, update_daq_1st_path);

  HassCmdNum = 13;
  ModbusCmdNum = 6;
  ptrHassStartCode = (uint8_t*)Fridge_HassStartCode;
  ptrHassCmdCode = (uint8_t*)Fridge_HassCmdCode;
  ptrHassDataLength = (int16_t*)Fridge_HassDataLength;
  ptrHassDataPackets = (int16_t*)Fridge_HassDataPackets;
  ptrHassCmdSendTime = (int32_t*)Fridge_HassCmdSendTime;
  ptrHassCmdTimeInit = (int32_t*)Fridge_HassCmdTimeInit;
  ptrModbusDataPackets = (int16_t*)Fridge_ModbusDataPackets;
  ptrModbusCmdSendTime = (int32_t*)Fridge_ModbusCmdSendTime;
  ptrModbusCmdTimeInit = (int32_t*)Fridge_ModbusCmdTimeInit;
  ptrModbusCmdSendSeq = (bool*)Fridge_ModbusCmdSendSeq;

  uint8_t macnum[6];
  WiFi.macAddress(macnum);
  char mactext[20];
  sprintf(mactext,"%02X%02X%02X%02X%02X%02X",macnum[0],macnum[1],macnum[2],macnum[3],macnum[4],macnum[5]);
  for(int i=0;i<12;i++)
  {
    topic_forcedwrite[i+1] = mactext[i];
  }
}

void BoardSet::BoardInit_DAQ_FRNET(void)
{
  Serial.begin(9600);
  Serial2.begin(9600);

  LedType = COMMON_ANODE_LED;
  PortRedLed = 26;
  PortBlueLed = 27;
  PortGreenLed = 14;
  PortSelUart0 = 32;
  PortNetSel = 35;
  Port485ReN = 33;
  Port485DeP = 25;

  ptrModuleName = (char*)ModuleName_05;
  ptrWiFiSSID = (char*)WiFiSSID_01;
  ptrWiFiKey = (char*)WiFiKey_01;
  ptrServerIP = (char*)ServerIP_01;
  ptrOTAServerIP = (char*)OTAServerIP_01;

  strcpy(topic_init, topic_init_01);
  strcpy(topic_timems, topic_timems_01);
  strcpy(topic_version, topic_version_01);
  strcpy(topic_test, topic_test_01);
  strcpy(topic_forcedwrite, topic_fridge_forcedwrite);
  strcpy(topic_forcedwritereceived, topic_fridge_forcedwritereceived);
  strcpy(topic_forcedwritefinished, topic_fridge_forcedwritefinished);
  strcpy(topic_hassread, topic_fridge_hassread);
  strcpy(topic_powerread, topic_fridge_powerread);
  strcpy(topic_tcread, topic_fridge_tcread);
  strcpy(topic_request_samplingtimeread, topic_fridge_request_samplingtimeread);
  strcpy(topic_response_samplingtimeread, topic_fridge_response_samplingtimeread);
  strcpy(topic_request_samplingtimewrite, topic_fridge_request_samplingtimewrite);
  strcpy(topic_response_samplingtimewrite, topic_fridge_response_samplingtimewrite);
  strcpy(update_path, update_fridge_daq_path);

  HassCmdNum = 13;
  ModbusCmdNum = 7;
  ptrHassStartCode = (uint8_t*)Fridge_HassStartCode;
  ptrHassCmdCode = (uint8_t*)Fridge_HassCmdCode;
  ptrHassDataLength = (int16_t*)Fridge_HassDataLength;
  ptrHassDataPackets = (int16_t*)Fridge_HassDataPackets;
  ptrHassCmdSendTime = (int32_t*)Fridge_HassCmdSendTime;
  ptrHassCmdTimeInit = (int32_t*)Fridge_HassCmdTimeInit;
  ptrModbusDataPackets = (int16_t*)Fridge_ModbusDataPackets;
  ptrModbusCmdSendTime = (int32_t*)Fridge_ModbusCmdSendTime;
  ptrModbusCmdTimeInit = (int32_t*)Fridge_ModbusCmdTimeInit;
  ptrModbusCmdSendSeq = (bool*)Fridge_ModbusCmdSendSeq;

  uint8_t macnum[6];
  WiFi.macAddress(macnum);
  char mactext[20];
  sprintf(mactext,"%02X%02X%02X%02X%02X%02X",macnum[0],macnum[1],macnum[2],macnum[3],macnum[4],macnum[5]);
  for(int i=0;i<12;i++)
  {
    topic_request_samplingtimeread[i+38] = mactext[i];
    topic_request_samplingtimewrite[i+39] = mactext[i];
    topic_forcedwrite[i+1] = mactext[i];
  }
}

void BoardSet::BoardInit_DAQ_WPNET(void)
{
  Serial.begin(9600);
  Serial2.begin(9600);

  LedType = COMMON_ANODE_LED;
  PortRedLed = 26;
  PortBlueLed = 27;
  PortGreenLed = 14;
  PortSelUart0 = 32;
  PortNetSel = 35;
  Port485ReN = 33;
  Port485DeP = 25;

  ptrModuleName = (char*)ModuleName_06;
  ptrWiFiSSID = (char*)WiFiSSID_02;
  ptrWiFiKey = (char*)WiFiKey_02;
  ptrServerIP = (char*)ServerIP_01;
  ptrOTAServerIP = (char*)OTAServerIP_01;

  strcpy(topic_init, topic_init_01);
  strcpy(topic_timems, topic_timems_01);
  strcpy(topic_version, topic_version_01);
  strcpy(topic_test, topic_test_01);
  strcpy(topic_forcedwrite, topic_purifier_forcedwrite);
  strcpy(topic_forcedwritereceived, topic_purifier_forcedwritereceived);
  strcpy(topic_forcedwritefinished, topic_purifier_forcedwritefinished);
  strcpy(topic_hassread, topic_purifier_hassread);
  strcpy(topic_powerread, topic_purifier_powerread);
  strcpy(topic_tcread, topic_purifier_tcread);
  strcpy(topic_request_samplingtimeread, topic_purifier_request_samplingtimeread);
  strcpy(topic_response_samplingtimeread, topic_purifier_response_samplingtimeread);
  strcpy(topic_request_samplingtimewrite, topic_purifier_request_samplingtimewrite);
  strcpy(topic_response_samplingtimewrite, topic_purifier_response_samplingtimewrite);
  strcpy(update_path, update_purifier_daq_path);

  HassCmdNum = 14;
  ModbusCmdNum = 6;
  ptrHassStartCode = (uint8_t*)Purifier_HassStartCode;
  ptrHassCmdCode = (uint8_t*)Purifier_HassCmdCode;
  ptrHassDataLength = (int16_t*)Purifier_HassDataLength;
  ptrHassDataPackets = (int16_t*)Purifier_HassDataPackets;
  ptrHassCmdSendTime = (int32_t*)Purifier_HassCmdSendTime;
  ptrHassCmdTimeInit = (int32_t*)Purifier_HassCmdTimeInit;
  ptrModbusDataPackets = (int16_t*)Purifier_ModbusDataPackets;
  ptrModbusCmdSendTime = (int32_t*)Purifier_ModbusCmdSendTime;
  ptrModbusCmdTimeInit = (int32_t*)Purifier_ModbusCmdTimeInit;
  ptrModbusCmdSendSeq = (bool*)Purifier_ModbusCmdSendSeq;

  uint8_t macnum[6];
  WiFi.macAddress(macnum);
  char mactext[20];
  sprintf(mactext,"%02X%02X%02X%02X%02X%02X",macnum[0],macnum[1],macnum[2],macnum[3],macnum[4],macnum[5]);
  for(int i=0;i<12;i++)
  {
    topic_request_samplingtimeread[i+39] = mactext[i];
    topic_request_samplingtimewrite[i+40] = mactext[i];
    topic_forcedwrite[i+1] = mactext[i];
  }
}

void BoardSet::BoardInit_DAQ_YOUNGJIN(void)
{
  Serial.begin(115200);
  Serial2.begin(9600);

  LedType = COMMON_ANODE_LED;
  PortRedLed = 26;
  PortBlueLed = 27;
  PortGreenLed = 14;
  PortSelUart0 = 32;
  PortNetSel = 35;
  Port485ReN = 33;
  Port485DeP = 25;

  ptrModuleName = (char*)ModuleName_07;
  //ptrWiFiSSID = (char*)WiFiSSID_03;
  ptrWiFiKey = (char*)WiFiKey_03;
  ptrServerIP = (char*)ServerIP_03;
  ptrOTAServerIP = (char*)OTAServerIP_03;
  
  // 영진 모텔 초기화.
  MODEL_Code = YJ5600HB;
  Encoder = 0;

  strcpy(topic_init, topic_gen_init);
  strcpy(topic_timems, topic_gen_timems);
  strcpy(topic_version, topic_gen_version);
  strcpy(topic_test, topic_gen_test);
  strcpy(topic_request_login, topic_request_tmds_login);
  strcpy(topic_response_login, topic_response_tmds_login);
  strcpy(topic_request_start, topic_request_tmds_start);
  strcpy(topic_response_start, topic_response_tmds_start);
  strcpy(topic_request_stop, topic_request_tmds_stop);
  strcpy(topic_response_stop, topic_response_tmds_stop);
  strcpy(topic_yjsensing_new, topic_tmds_yjsensing); // 13 호기를 위한 추가...
  strcpy(update_path, update_daq_youngjin_path);
  strcpy(topic_analysisdata, topic_analysis_data); // 장비데이터 분석을 서버에서 진행 하기 위한 추가.. 분석결과를 받음.
  uint8_t macnum[6];
  WiFi.macAddress(macnum);
  char mactext[20];
  sprintf(mactext,"%02X%02X%02X%02X%02X%02X",macnum[0],macnum[1],macnum[2],macnum[3],macnum[4],macnum[5]);
  for(int i=0;i<12;i++)
  {
    topic_request_login[i+20] = mactext[i];
    topic_response_login[i+21] = mactext[i];
    topic_request_start[i+20] = mactext[i];
    topic_response_start[i+21] = mactext[i];
    topic_request_stop[i+19] = mactext[i];
    topic_response_stop[i+20] = mactext[i]; //"Response/T-MDS/Stop/AABBCCDDEEFF/";
    topic_yjsensing_new[i+22] = mactext[i]; //"Event/T-MDS/YJSensing/AABBCCDDEEFF/"
    topic_analysisdata[i+21] = mactext[i];  //"Event/T-MDS/Analysis/AABBCCDDEEFF/"
  }
  sprintf(WiFiSSID,"LTE_%s",mactext);
  ptrWiFiSSID = (char*)WiFiSSID;
}

void BoardSet::BoardInit_DONGLE_YUPOONG(void)
{
  LedType = COMMON_CATHODE_LED;
  PortRedLed = 22;
  PortBlueLed = 21;
  PortGreenLed = 14;  // Not used
  PortSelUart0 = 32;  // Not used
  PortNetSel = 35;  // Not used
  Port485ReN = 33;  // Not used
  Port485DeP = 25;  // Not used

  ptrModuleName = (char*)ModuleName_08;
  ptrWiFiSSID = (char*)WiFiSSID_04;
  ptrWiFiKey = (char*)WiFiKey_04;
  ptrServerIP = (char*)ServerIP_04;
  ptrOTAServerIP = (char*)OTAServerIP_04;

  strcpy(topic_init, topic_gen_init);
  strcpy(topic_timems, topic_gen_timems);
  strcpy(topic_version, topic_gen_version);
  strcpy(topic_test, topic_gen_test);
}

void BoardSet::BoardInit_DAQ_BASIC(void)
{
  Serial.begin(115200);
  Serial2.begin(9600);

  LedType = COMMON_ANODE_LED;
  PortRedLed = 26;
  PortBlueLed = 27;
  PortGreenLed = 14;
  PortSelUart0 = 32;
  PortNetSel = 35;
  Port485ReN = 33;
  Port485DeP = 25;

  ptrModuleName = (char*)ModuleName_10;
  //ptrWiFiSSID = (char*)WiFiSSID_04;
  ptrWiFiKey = (char*)WiFiKey_04;
  ptrServerIP = (char*)ServerIP_05;
  ptrOTAServerIP = (char*)OTAServerIP_05;

  strcpy(topic_init, topic_gen_init);
  strcpy(topic_timems, topic_gen_timems);
  strcpy(topic_version, topic_gen_version);
  strcpy(topic_test, topic_gen_test);
  strcpy(topic_powerread, topic_demo_powerread);
  strcpy(topic_tcread, topic_demo_tcread);
  strcpy(update_path, update_daq_basic_path);

  uint8_t macnum[6];
  WiFi.macAddress(macnum);
  char mactext[20];
  sprintf(mactext,"%02X%02X%02X%02X%02X%02X",macnum[0],macnum[1],macnum[2],macnum[3],macnum[4],macnum[5]);
  sprintf(WiFiSSID,"LTE_%s",mactext);
  ptrWiFiSSID = (char*)WiFiSSID;
}

void BoardSet::BoardInit_DAQ_DEMO(void)
{
  Serial.begin(9600);
  Serial2.begin(115200);

  LedType = COMMON_ANODE_LED;
  PortRedLed = 26;
  PortBlueLed = 27;
  PortGreenLed = 14;
  PortSelUart0 = 32;
  PortNetSel = 35;
  Port485ReN = 33;
  Port485DeP = 25;

  ptrModuleName = (char*)ModuleName_11;
  ptrWiFiSSID = (char*)WiFiSSID_03;
  ptrWiFiKey = (char*)WiFiKey_03;
  ptrServerIP = (char*)ServerIP_03;
  ptrOTAServerIP = (char*)OTAServerIP_04;

  strcpy(topic_init, topic_gen_init);
  strcpy(topic_timems, topic_gen_timems);
  strcpy(topic_version, topic_gen_version);
  strcpy(topic_test, topic_gen_test);
  strcpy(topic_powerread, topic_demo_powerread);
  strcpy(topic_tcread, topic_demo_tcread);
  strcpy(update_path, update_daq_demo_path);

  ModbusCmdNum = 6;
  ptrModbusDataPackets = (int16_t*)Demo_ModbusDataPackets;
  ptrModbusCmdSendTime = (int32_t*)Demo_ModbusCmdSendTime;
  ptrModbusCmdTimeInit = (int32_t*)Demo_ModbusCmdTimeInit;
  ptrModbusCmdSendSeq = (bool*)Demo_ModbusCmdSendSeq;

  uint8_t macnum[6];
  WiFi.macAddress(macnum);
  char mactext[20];
  sprintf(mactext,"%02X%02X%02X%02X%02X%02X",macnum[0],macnum[1],macnum[2],macnum[3],macnum[4],macnum[5]);
  sprintf(WiFiSSID,"LTE_%s",mactext);
  //ptrWiFiSSID = (char*)WiFiSSID;
}


void BoardSet::BoardInit_DAQ_SOOSAN(void)
{
  Serial.begin(115200);
  Serial2.begin(115200);

  LedType = WDCAS_MAIN_LED;
  PortRedLed = 2;
  PortBlueLed = 12;
  PortGreenLed = 15;
  PortSelUart0 = 33;
  Port485ReN = 27;
  Port485DeP = 14;
  PortNetSel = 35;

  ptrModuleName = (char*)ModuleName_12;
  //ptrWiFiSSID = (char*)WiFiSSID_03;
  ptrWiFiKey = (char*)WiFiKey_03;
  ptrServerIP = (char*)ServerIP_03;
  ptrOTAServerIP = (char*)OTAServerIP_03;

  strcpy(topic_init, topic_gen_init);
  strcpy(topic_timems, topic_gen_timems);
  strcpy(topic_version, topic_gen_version);
  strcpy(topic_test, topic_gen_test);
  strcpy(topic_request_start, topic_request_tmds_start);
  strcpy(topic_response_start, topic_response_tmds_start);
  strcpy(update_path, update_daq_soosan_path);

  uint8_t macnum[6];
  WiFi.macAddress(macnum);
  char mactext[20];
  sprintf(mactext,"%02X%02X%02X%02X%02X%02X",macnum[0],macnum[1],macnum[2],macnum[3],macnum[4],macnum[5]);
  for(int i=0;i<12;i++)
  {
    topic_request_start[i+20] = mactext[i];
    topic_response_start[i+21] = mactext[i];
  }
  sprintf(WiFiSSID,"LTE_%s",mactext);
  ptrWiFiSSID = (char*)WiFiSSID;
}


void BoardSet::BoardInit_DAQ_MGTSHIP(void)
{
  Serial.begin(9600);
  Serial2.begin(115200);

  LedType = COMMON_ANODE_LED;
  PortRedLed = 26;
  PortBlueLed = 27;
  PortGreenLed = 14;
  PortSelUart0 = 32;
  PortNetSel = 35;
  Port485ReN = 33;
  Port485DeP = 25;

  ptrModuleName = (char*)ModuleName_13;
  ptrWiFiSSID = (char*)WiFiSSID_03;
  ptrWiFiKey = (char*)WiFiKey_03;
  ptrServerIP = (char*)ServerIP_06;
  ptrOTAServerIP = (char*)OTAServerIP_04;

  strcpy(topic_init, topic_gen_init);
  strcpy(topic_timems, topic_gen_timems);
  strcpy(topic_version, topic_gen_version);
  strcpy(topic_test, topic_gen_test);
  strcpy(update_path, update_daq_mgtship_path);
}

void BoardSet::BoardInit_WDCAS_FRIGER_QA(void)
{
  Serial.begin(9600);
  Serial2.begin(9600);

  LedType = WDCAS_MAIN_LED;
  PortRedLed = 2;
  PortBlueLed = 12;
  PortGreenLed = 15;
  PortSelUart0 = 33;
  Port485ReN = 27;
  Port485DeP = 14;
  PortNetSel = 35;

  ptrModuleName = (char*)ModuleName_14;
  ptrWiFiSSID = (char*)WiFiSSID_06;
  ptrWiFiKey = (char*)WiFiKey_01;
  ptrServerIP = (char*)ServerIP_01;
  ptrOTAServerIP = (char*)OTAServerIP_01;

  strcpy(topic_init, topic_init_01);
  strcpy(topic_timems, topic_timems_01);
  strcpy(topic_version, topic_version_01);
  strcpy(topic_test, topic_test_01);
  strcpy(topic_forcedwrite, topic_fridge_forcedwrite);
  strcpy(topic_forcedwritereceived, topic_fridge_forcedwritereceived);
  strcpy(topic_forcedwritefinished, topic_fridge_forcedwritefinished);
  strcpy(topic_hassread, topic_fridge_hassread);
  strcpy(topic_powerread, topic_fridge_powerread);
  strcpy(topic_tcread, topic_fridge_tcread);
  strcpy(topic_request_daqcode, topic_fridge_request_daqcode);
  strcpy(topic_request_aridata, topic_fridge_request_aridata);
  strcpy(topic_request_samplingtimeread, topic_fridge_request_samplingtimeread);
  strcpy(topic_response_samplingtimeread, topic_fridge_response_samplingtimeread);
  strcpy(topic_request_samplingtimewrite, topic_fridge_request_samplingtimewrite);
  strcpy(topic_response_samplingtimewrite, topic_fridge_response_samplingtimewrite);
  strcpy(topic_response_inform, topic_response_inform_def);
  strcpy(update_path, update_wdcas_friger_qa_path);

  HassCmdNum = 13;
  ModbusCmdNum = 6;
  ptrHassStartCode = (uint8_t*)Fridge_HassStartCode;
  ptrHassCmdCode = (uint8_t*)Fridge_HassCmdCode;
  ptrHassDataLength = (int16_t*)Fridge_HassDataLength;
  ptrHassDataPackets = (int16_t*)Fridge_HassDataPackets;
  ptrHassCmdSendTime = (int32_t*)Fridge_HassCmdSendTime;
  ptrHassCmdTimeInit = (int32_t*)Fridge_HassCmdTimeInit;
  ptrModbusDataPackets = (int16_t*)Fridge_ModbusDataPackets;
  ptrModbusCmdSendTime = (int32_t*)Fridge_ModbusCmdSendTime;
  ptrModbusCmdTimeInit = (int32_t*)Fridge_ModbusCmdTimeInit;
  ptrModbusCmdSendSeq = (bool*)Fridge_ModbusCmdSendSeq;

  uint8_t macnum[6];
  WiFi.macAddress(macnum);
  char mactext[20];
  sprintf(mactext,"%02X%02X%02X%02X%02X%02X",macnum[0],macnum[1],macnum[2],macnum[3],macnum[4],macnum[5]);
  for(int i=0;i<12;i++)
  {
    topic_request_samplingtimeread[i+38] = mactext[i];
    topic_request_samplingtimewrite[i+39] = mactext[i];
    topic_forcedwrite[i+1] = mactext[i];
    topic_request_daqcode[i+12] = mactext[i];
    topic_request_aridata[i+16] = mactext[i];
    topic_response_inform[i+16] = mactext[i];
  }
}

void BoardSet::BoardInit_WDCAS_FRIGER_TSI(void)
{
  Serial.begin(9600);
  Serial2.begin(9600);

  LedType = WDCAS_MAIN_LED;
  PortRedLed = 2;
  PortBlueLed = 12;
  PortGreenLed = 15;
  PortSelUart0 = 33;
  Port485ReN = 27;
  Port485DeP = 14;
  PortNetSel = 35;

  ptrModuleName = (char*)ModuleName_15;
  ptrWiFiSSID = (char*)WiFiSSID_07;
  ptrWiFiKey = (char*)WiFiKey_01;
  ptrServerIP = (char*)ServerIP_01;
  ptrOTAServerIP = (char*)OTAServerIP_01;

  strcpy(topic_init, topic_init_01);
  strcpy(topic_timems, topic_timems_01);
  strcpy(topic_version, topic_version_01);
  strcpy(topic_test, topic_test_01);
  strcpy(topic_forcedwrite, topic_fridge_forcedwrite);
  strcpy(topic_forcedwritereceived, topic_fridge_forcedwritereceived);
  strcpy(topic_forcedwritefinished, topic_fridge_forcedwritefinished);
  strcpy(topic_hassread, topic_fridge_hassread);
  strcpy(topic_powerread, topic_fridge_powerread);
  strcpy(topic_tcread, topic_fridge_tcread);
  strcpy(topic_request_daqcode, topic_fridge_request_daqcode);
  strcpy(topic_request_aridata, topic_fridge_request_aridata);
  strcpy(topic_response_inform, topic_response_inform_def);
  strcpy(topic_request_samplingtimeread, topic_fridge_request_samplingtimeread);
  strcpy(topic_response_samplingtimeread, topic_fridge_response_samplingtimeread);
  strcpy(topic_request_samplingtimewrite, topic_fridge_request_samplingtimewrite);
  strcpy(topic_response_samplingtimewrite, topic_fridge_response_samplingtimewrite);
  strcpy(update_path, update_wdcas_friger_tsi_path);

  HassCmdNum = 13;
  ModbusCmdNum = 6;
  ptrHassStartCode = (uint8_t*)Fridge_HassStartCode;
  ptrHassCmdCode = (uint8_t*)Fridge_HassCmdCode;
  ptrHassDataLength = (int16_t*)Fridge_HassDataLength;
  ptrHassDataPackets = (int16_t*)Fridge_HassDataPackets;
  ptrHassCmdSendTime = (int32_t*)Fridge_HassCmdSendTime;
  ptrHassCmdTimeInit = (int32_t*)Fridge_HassCmdTimeInit;
  ptrModbusDataPackets = (int16_t*)Fridge_ModbusDataPackets;
  ptrModbusCmdSendTime = (int32_t*)Fridge_ModbusCmdSendTime;
  ptrModbusCmdTimeInit = (int32_t*)Fridge_ModbusCmdTimeInit;
  ptrModbusCmdSendSeq = (bool*)Fridge_ModbusCmdSendSeq;

  uint8_t macnum[6];
  WiFi.macAddress(macnum);
  char mactext[20];
  sprintf(mactext,"%02X%02X%02X%02X%02X%02X",macnum[0],macnum[1],macnum[2],macnum[3],macnum[4],macnum[5]);
  for(int i=0;i<12;i++)
  {
    topic_request_samplingtimeread[i+38] = mactext[i];
    topic_request_samplingtimewrite[i+39] = mactext[i];
    topic_forcedwrite[i+1] = mactext[i];
    topic_request_daqcode[i+12] = mactext[i];
    topic_request_aridata[i+16] = mactext[i];
    topic_response_inform[i+16] = mactext[i];
  }
}

void BoardSet::BoardInit_WDCAS_ADDON_WPT(void)
{
  Serial.begin(9600);
  Serial2.begin(9600);

  LedType = WDCAS_MAIN_LED;
  PortRedLed = 2;
  PortBlueLed = 12;
  PortGreenLed = 15;
  PortSelUart0 = 33;
  Port485ReN = 27;
  Port485DeP = 14;
  PortNetSel = 35;

  ptrModuleName = (char*)ModuleName_15;
  ptrWiFiSSID = (char*)WiFiSSID_07;
  ptrWiFiKey = (char*)WiFiKey_01;
  ptrServerIP = (char*)ServerIP_01;
  ptrOTAServerIP = (char*)OTAServerIP_01;

  strcpy(topic_init, topic_init_01);
  strcpy(topic_version, topic_version_01);
  strcpy(topic_response_inform, topic_response_inform_def);
  strcpy(update_path, update_wdcas_addon_wpt_path);

  uint8_t macnum[6];
  WiFi.macAddress(macnum);
  char mactext[20];
  sprintf(mactext,"%02X%02X%02X%02X%02X%02X",macnum[0],macnum[1],macnum[2],macnum[3],macnum[4],macnum[5]);
  for(int i=0;i<12;i++)
  {
    topic_response_inform[i+16] = mactext[i];
  }
}

void BoardSet::BoardInit_WDCAS_ADDON_DAF(void)
{
  Serial.begin(9600);
  Serial2.begin(9600);

  LedType = WDCAS_MAIN_LED;
  PortRedLed = 2;
  PortBlueLed = 12;
  PortGreenLed = 15;
  PortSelUart0 = 33;
  Port485ReN = 27;
  Port485DeP = 14;
  PortNetSel = 35;

  ptrModuleName = (char*)ModuleName_15;
  ptrWiFiSSID = (char*)WiFiSSID_07;
  ptrWiFiKey = (char*)WiFiKey_01;
  ptrServerIP = (char*)ServerIP_01;
  ptrOTAServerIP = (char*)OTAServerIP_01;

  strcpy(topic_init, topic_init_01);
  strcpy(topic_version, topic_version_01);
  strcpy(topic_response_inform, topic_response_inform_def);
  strcpy(update_path, update_wdcas_addon_daf_path);

  uint8_t macnum[6];
  WiFi.macAddress(macnum);
  char mactext[20];
  sprintf(mactext,"%02X%02X%02X%02X%02X%02X",macnum[0],macnum[1],macnum[2],macnum[3],macnum[4],macnum[5]);
  for(int i=0;i<12;i++)
  {
    topic_response_inform[i+16] = mactext[i];
  }
}

void BoardSet::BoardInit(int id)
{
  delay(300);

  ptrModuleType = (char*)ModuleType;
  ptrModuleVersion = (char*)ModuleVersion;
  ptrHardSoftVersion = (char*)HardSoftVersion;
  ptrSupplierName = (char*)SupplierName;

  ServerCheckPort = SERVERCHECK_PORT;
  DataSendPort = DATASEND_PORT;
  MQTTPort = MQTT_PORT;
  UpdatePort = UPDATE_PORT;
  FileLoadPort = FILELOAD_PORT;

  HassCmdNum = 0;
  ModbusCmdNum = 0;

  switch(id)
  {
    case DONGLE_FR  : BoardInit_DONGLE_FR(); break;
    case DONGLE_WP  : BoardInit_DONGLE_WP(); break;
    case DONGLE_EXT : BoardInit_DONGLE_EXT(); break;
    case DAQ_1ST    : BoardInit_DAQ_1ST(); break;
    case DAQ_FRNET  : BoardInit_DAQ_FRNET(); break;
    case DAQ_WPNET  : BoardInit_DAQ_WPNET(); break;
    case DAQ_YOUNGJIN : BoardInit_DAQ_YOUNGJIN(); break;
    case DONGLE_YUPOONG : BoardInit_DONGLE_YUPOONG(); break;
    case DAQ_BASIC : BoardInit_DAQ_BASIC(); break;
    case DAQ_DEMO : BoardInit_DAQ_DEMO(); break;
    case DAQ_SOOSAN : BoardInit_DAQ_SOOSAN(); break;
    case DAQ_MGTSHIP : BoardInit_DAQ_MGTSHIP(); break;
    case WDCAS_FRIGER_QA : BoardInit_WDCAS_FRIGER_QA(); break;
    case WDCAS_FRIGER_TSI : BoardInit_WDCAS_FRIGER_TSI(); break;
    case WDCAS_ADDON_WPT : BoardInit_WDCAS_ADDON_WPT(); break;
    case WDCAS_ADDON_DAF : BoardInit_WDCAS_ADDON_DAF(); break;
    default : BoardInit_DAQ_FRNET(); break;
  }

  uint8_t macnum[6];
  WiFi.macAddress(macnum);
  char mactext[20];
  sprintf(mactext,"%02X%02X%02X%02X%02X%02X",macnum[0],macnum[1],macnum[2],macnum[3],macnum[4],macnum[5]);
  Serial.printf("\r\n%s\r\n",mactext);
  Serial.flush();

  pinMode(PortSelUart0,OUTPUT);
  digitalWrite(PortSelUart0,HIGH);

  if(LedType == COMMON_CATHODE_LED)
  {
    pinMode(PortRedLed,OUTPUT);
    pinMode(PortBlueLed,OUTPUT);
    pinMode(PortGreenLed,OUTPUT);
  }
  else if(LedType == WDCAS_MAIN_LED)
  {
    pinMode(PortRedLed,OUTPUT);
    pinMode(PortBlueLed,OUTPUT);
    pinMode(PortGreenLed,OUTPUT);
  }
  else
  {
    pinMode(PortRedLed,OUTPUT_OPEN_DRAIN);
    pinMode(PortBlueLed,OUTPUT_OPEN_DRAIN);
    pinMode(PortGreenLed,OUTPUT_OPEN_DRAIN);
  }

  for(int i=0;i<3;i++)
  {
    BoardLedOn(RED_LED);
    BoardLedOff(BLUE_LED);
    BoardLedOff(GREEN_LED);
    delay(200);
    BoardLedOff(RED_LED);
    BoardLedOn(BLUE_LED);
    BoardLedOff(GREEN_LED);
    delay(200);
    BoardLedOff(RED_LED);
    BoardLedOff(BLUE_LED);
    BoardLedOn(GREEN_LED);
    delay(200);
  }
  BoardLedOff(RED_LED);
  BoardLedOff(BLUE_LED);
  BoardLedOff(GREEN_LED);

  pinMode(PortNetSel,INPUT_PULLUP);
  delay(10);
  int cnt = 0;
  int val = digitalRead(PortNetSel);
  int bval = val;
  while(cnt <5)
  {
    delay(10);
    val = digitalRead(PortNetSel);
    if(bval != val) cnt = 0;
    else cnt++;
    bval = val;
  }
  if(val == HIGH) NetSel = WIFI_SEL;
  else NetSel = ETHERNET_SEL;

  switch(id)
  {
    case DONGLE_FR  : NetSel = WIFI_SEL; break;
    case DONGLE_WP  : NetSel = WIFI_SEL; break;
    case DONGLE_EXT : NetSel = WIFI_SEL; break;
    case DAQ_1ST    : NetSel = WIFI_SEL; break;
    case DAQ_FRNET  : break;
    case DAQ_WPNET  : NetSel = WIFI_SEL; break;
    case DAQ_YOUNGJIN : NetSel = WIFI_SEL; break;
    case DONGLE_YUPOONG : break;
    case DAQ_BASIC: NetSel = WIFI_SEL; break;
    case DAQ_DEMO: NetSel = WIFI_SEL; break;
    case DAQ_SOOSAN : NetSel = WIFI_SEL; break;
    case DAQ_MGTSHIP : NetSel = WIFI_SEL; break;
    case WDCAS_FRIGER_QA : NetSel = ETHERNET_SEL; break;
    case WDCAS_FRIGER_TSI : NetSel = ETHERNET_SEL; break;
    case WDCAS_ADDON_WPT : NetSel = ETHERNET_SEL; break;
    case WDCAS_ADDON_DAF : NetSel = ETHERNET_SEL; break;
    default : break;
  }
}

void BoardSet::BoardLedOn(int led)
{
  if(LedType == COMMON_CATHODE_LED)
  {
    switch(led)
    {
      case RED_LED : digitalWrite(PortRedLed,HIGH); break;
      case BLUE_LED : digitalWrite(PortBlueLed,HIGH); break;
      case GREEN_LED : digitalWrite(PortGreenLed,HIGH); break;
      default : break;
    }
  }
  else if(LedType == WDCAS_MAIN_LED)
  {
    switch(led)
    {
      case RED_LED : digitalWrite(PortRedLed,HIGH); break;
      case BLUE_LED : digitalWrite(PortBlueLed,HIGH); break;
      case GREEN_LED : digitalWrite(PortGreenLed,LOW); break;
      default : break;
    }
  }
  else
  {
    switch(led)
    {
      case RED_LED : digitalWrite(PortRedLed,LOW); break;
      case BLUE_LED : digitalWrite(PortBlueLed,LOW); break;
      case GREEN_LED : digitalWrite(PortGreenLed,LOW); break;
      default : break;
    }
  }
}

void BoardSet::BoardLedOff(int led)
{
  if(LedType == COMMON_CATHODE_LED)
  {
    switch(led)
    {
      case RED_LED : digitalWrite(PortRedLed,LOW); break;
      case BLUE_LED : digitalWrite(PortBlueLed,LOW); break;
      case GREEN_LED : digitalWrite(PortGreenLed,LOW); break;
      default : break;
    }
  }
  else if(LedType == WDCAS_MAIN_LED)
  {
    switch(led)
    {
      case RED_LED : digitalWrite(PortRedLed,LOW); break;
      case BLUE_LED : digitalWrite(PortBlueLed,LOW); break;
      case GREEN_LED : digitalWrite(PortGreenLed,HIGH); break;
      default : break;
    }
  }
  else
  {
    switch(led)
    {
      case RED_LED : digitalWrite(PortRedLed,HIGH); break;
      case BLUE_LED : digitalWrite(PortBlueLed,HIGH); break;
      case GREEN_LED : digitalWrite(PortGreenLed,HIGH); break;
      default : break;
    }
  }
}

void BoardSet::BoardInit_DAQ_EXCAVATOR(void)
{
  delay(300);

  Serial.begin(115200);
  Serial2.begin(115200);

  LedType = COMMON_ANODE_LED;
  PortRedLed = 26;
  PortBlueLed = 27;
  PortSelUart0 = 32;
  Port485ReN = 33;
  Port485DeP = 25;

  ptrModuleType = (char*)ModuleType;
  ptrModuleVersion = (char*)ModuleVersion;
  ptrHardSoftVersion = (char*)HardSoftVersion;
  ptrSupplierName = (char*)SupplierName;

  ptrModuleName = (char*)ModuleName_09;
  ptrWiFiSSID = (char*)WiFiSSID_03;
  ptrWiFiKey = (char*)WiFiKey_03;
  ptrServerIP = (char*)ServerIP_03;
  ptrOTAServerIP = (char*)OTAServerIP_03;

  pinMode(PortSelUart0,OUTPUT);
  digitalWrite(PortSelUart0,HIGH);

  if(LedType == COMMON_CATHODE_LED)
  {
    pinMode(PortRedLed,OUTPUT);
    pinMode(PortBlueLed,OUTPUT);
  }
  else
  {
    pinMode(PortRedLed,OUTPUT_OPEN_DRAIN);
    pinMode(PortBlueLed,OUTPUT_OPEN_DRAIN);
  }

  for(int i=0;i<3;i++)
  {
    BoardLedOn(RED_LED);
    BoardLedOff(BLUE_LED);
    delay(200);
    BoardLedOff(RED_LED);
    BoardLedOn(BLUE_LED);
    delay(200);
    BoardLedOff(RED_LED);
    BoardLedOff(BLUE_LED);
    delay(200);
  }
  BoardLedOff(RED_LED);
  BoardLedOff(BLUE_LED);
}
