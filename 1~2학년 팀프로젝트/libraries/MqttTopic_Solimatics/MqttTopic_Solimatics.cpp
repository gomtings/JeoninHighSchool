#include <MqttTopic_Solimatics.h>

MqttTopic::MqttTopic()
{
}

void MqttTopic::PublishTopicInit(void)
{
  const size_t capacity = JSON_OBJECT_SIZE(8);
  DynamicJsonDocument doc(capacity);
  doc["IOT_MAC"] = (const char*)qinfo.MAC;
  doc["AP_MAC"] = (const char*)qinfo.AP_MAC;
  doc["IOT_SPPL_CD"] = (const char*)qinfo.IOT_SPPL_CD;
  doc["IOT_MODEL"] = (const char*)qinfo.IOT_MODEL;
  doc["MCIP"] = (const char*)qinfo.MCIP;
  doc["MCID"] = (const char*)qinfo.MCID;
  doc["STS"] = (const char*)qinfo.STS;
  doc["VER"] = (const char*)qinfo.VER;
  serializeJson(doc, qbuf);
}

void MqttTopic::PublishTopicVersion(void)
{
  DynamicJsonDocument doc(1024);

  doc["MAC"] = (const char*)qversion.MAC;
  doc["ProgramVer"] = (const char*)qversion.ProgramVer;
  doc["HardSoftVer"] = (const char*)qversion.HardSoftVer;
  doc["Type"] = (const char*)qversion.Type;
  doc["BootCount"] = qversion.BootCount;
  doc["PowerOnTime"] = qversion.PowerOnTime;
  doc["Message"] = (const char*)qversion.Message;
  serializeJson(doc, qbuf);
}

void MqttTopic::PublishTopicResponseLogin(void)
{
  StaticJsonDocument<256> doc;
  doc["WORKER_IDX"] = qresponselogin.WorkerIdx;
  serializeJson(doc, qbuf);
}

void MqttTopic::PublishTopicResponseStart(void)
{
  StaticJsonDocument<256> doc;
  doc["WORKER_IDX"] = qresponsestart.WorkerIdx;
  doc["WORKUNIT_IDX"] = qresponsestart.WorkUnitIdx;
  doc["TARGET_DEPTH"] = qresponsestart.TargetDepth;
  serializeJson(doc, qbuf);
}

void MqttTopic::PublishTopicResponseStop(void)
{
  StaticJsonDocument<256> doc;
  doc["WORKER_IDX"] = qresponsestop.WorkerIdx;
  doc["WORKUNIT_IDX"] = qresponsestop.WorkUnitIdx;
  serializeJson(doc, qbuf);
}

void MqttTopic::PublishTopicResponseModel(void)
{
  StaticJsonDocument<256> doc;
  doc["Model"] = modeldata.model;
  doc["Encoder"] = modeldata.Encod_low;
  doc["D1_LOW"] = modeldata.D1_LOW;
  doc["D1_MAX"] = modeldata.D1_MAX;
  doc["D2_LOW"] = modeldata.D2_LOW;
  doc["D2_MAX"] = modeldata.D2_MAX;
  serializeJson(doc, qbuf);
}

void MqttTopic::PublishTopicYJSensing(void)
{
  StaticJsonDocument<4096> doc;
  doc["MAC"] = (const char*)qyjsensing.MAC;
  doc["WORKER_IDX"] = qyjsensing.WorkerIdx;
  doc["WORKUNIT_IDX"] = qyjsensing.WorkUnitIdx;
  doc["TARGET_DEPTH"] = qyjsensing.TargetDepth;
  doc["PACKETS"] = qyjsensing.Packets;
  JsonArray BASETIME = doc.createNestedArray("BASETIME");
  for(int i=0;i<8;i++)
  {
    BASETIME.add(qyjsensing.BaseTime.sbuf[i]);
  }
  int arraynum = qyjsensing.Packets;
  JsonArray TIME = doc.createNestedArray("TIME");
  for(int i=0;i<arraynum;i++)
  {
    TIME.add(qyjsensing.Time[i]);
  }
  JsonArray JOB_TIME = doc.createNestedArray("JOB_TIME");
  for(int i=0;i<arraynum;i++)
  {
    JOB_TIME.add(qyjsensing.JobTime[i]);
  }
  JsonArray PRESSURE = doc.createNestedArray("PRESSURE");
  for(int i=0;i<arraynum;i++)
  {
    PRESSURE.add(qyjsensing.Pressure[i]);
  }
  JsonArray TORQUE = doc.createNestedArray("TORQUE");
  for(int i=0;i<arraynum;i++)
  {
    TORQUE.add(qyjsensing.Torque[i]);
  }
  JsonArray INCLINATION_X = doc.createNestedArray("INCLINATION_X");
  for(int i=0;i<arraynum;i++)
  {
    INCLINATION_X.add(qyjsensing.InclinationX[i]);
  }
  JsonArray INCLINATION_Y = doc.createNestedArray("INCLINATION_Y");
  for(int i=0;i<arraynum;i++)
  {
    INCLINATION_Y.add(qyjsensing.InclinationY[i]);
  }
  JsonArray ROD_COUNT = doc.createNestedArray("ROD_COUNT");
  for(int i=0;i<arraynum;i++)
  {
    ROD_COUNT.add(qyjsensing.RodCount[i]);
  }
  JsonArray ENCODER = doc.createNestedArray("ENCODER");
  for(int i=0;i<arraynum;i++)
  {
    ENCODER.add(qyjsensing.Encoder[i]);
  }
  JsonArray MAX_DEPTH = doc.createNestedArray("MAX_DEPTH");
  for(int i=0;i<arraynum;i++)
  {
    MAX_DEPTH.add(qyjsensing.MaxDepth[i]);
  }
  JsonArray BEAT_POSITION = doc.createNestedArray("BEAT_POSITION");
  for(int i=0;i<arraynum;i++)
  {
    BEAT_POSITION.add(qyjsensing.BitPosition[i]);
  }
  JsonArray SWITCH = doc.createNestedArray("SWITCH");
  for(int i=0;i<arraynum;i++)
  {
    SWITCH.add(qyjsensing.Switch[i]);
  }
  JsonArray bottom = doc.createNestedArray("Bottom");
  for(int i=0;i<arraynum;i++)
  {
    bottom.add(qyjsensing.Bottom[i]);
  }
  JsonArray offset = doc.createNestedArray("offset");
  for(int i=0;i<arraynum;i++)
  {
    offset.add(qyjsensing.offset[i]);
  }
  serializeJson(doc, qbuf);
}

void MqttTopic::PublishTopicSSSensing(void)
{
  StaticJsonDocument<4096> doc;
  doc["MAC"] = (const char*)qsssensing.MAC;
  doc["PACKETS"] = qsssensing.Packets;
  JsonArray BASETIME = doc.createNestedArray("BASETIME");
  for(int i=0;i<8;i++)
  {
    BASETIME.add(qsssensing.BaseTime.sbuf[i]);
  }
  int arraynum = qsssensing.Packets;
  JsonArray START_TIME = doc.createNestedArray("START_TIME");
  for(int i=0;i<arraynum;i++)
  {
    START_TIME.add(qsssensing.StartTime[i]);
  }
  JsonArray END_TIME = doc.createNestedArray("END_TIME");
  for(int i=0;i<arraynum;i++)
  {
    END_TIME.add(qsssensing.EndTime[i]);
  }
  JsonArray SAMPLING_NUM = doc.createNestedArray("SAMPLING_NUM");
  for(int i=0;i<arraynum;i++)
  {
    SAMPLING_NUM.add(qsssensing.SamplingNum[i]);
  }
  JsonArray HAMMERING_FREQUENCY = doc.createNestedArray("HAMMERING_FREQUENCY");
  for(int i=0;i<arraynum;i++)
  {
    HAMMERING_FREQUENCY.add(qsssensing.HammeringFrequency[i]);
  }
  JsonArray HAMMERING_STDDIVX = doc.createNestedArray("HAMMERING_STDDIVX");
  for(int i=0;i<arraynum;i++)
  {
    HAMMERING_STDDIVX.add(qsssensing.HammeringStdDivX[i]);
  }
  JsonArray HAMMERING_STDDIVY = doc.createNestedArray("HAMMERING_STDDIVY");
  for(int i=0;i<arraynum;i++)
  {
    HAMMERING_STDDIVY.add(qsssensing.HammeringStdDivY[i]);
  }
  JsonArray ENCODER = doc.createNestedArray("ENCODER");
  for(int i=0;i<arraynum;i++)
  {
    ENCODER.add(qsssensing.Encoder[i]);
  }
  JsonArray DEPTH = doc.createNestedArray("DEPTH");
  for(int i=0;i<arraynum;i++)
  {
    DEPTH.add(qsssensing.Depth[i]);
  }
  JsonArray ROP = doc.createNestedArray("ROP");
  for(int i=0;i<arraynum;i++)
  {
    ROP.add(qsssensing.ROPData[i]);
  }
  serializeJson(doc, qbuf);
}

void MqttTopic::PublishTopicEncSensing(void)
{
  StaticJsonDocument<4096> doc;
  doc["MAC"] = (const char*)qencsensing.MAC;
  doc["PACKETS"] = qencsensing.Packets;
  JsonArray BASETIME = doc.createNestedArray("BASETIME");
  for(int i=0;i<8;i++)
  {
    BASETIME.add(qencsensing.BaseTime.sbuf[i]);
  }
  int arraynum = qencsensing.Packets;
  JsonArray TIME = doc.createNestedArray("TIME");
  for(int i=0;i<arraynum;i++)
  {
    TIME.add(qencsensing.Time[i]);
  }
  JsonArray ENCODER = doc.createNestedArray("ENCODER");
  for(int i=0;i<arraynum;i++)
  {
    ENCODER.add(qencsensing.Encoder[i]);
  }
  serializeJson(doc, qbuf);
}

void MqttTopic::PublishTopicGNSSData(void)
{
  StaticJsonDocument<4096> doc;
  doc["MAC"] = (const char*)qgnssdata.MAC;
  doc["PACKETS"] = qgnssdata.Packets;
  JsonArray BASETIME = doc.createNestedArray("BASETIME");
  for(int i=0;i<8;i++)
  {
    BASETIME.add(qgnssdata.BaseTime.sbuf[i]);
  }
  int arraynum = qgnssdata.Packets;
  JsonArray TIME = doc.createNestedArray("TIME");
  for(int i=0;i<arraynum;i++)
  {
    TIME.add(qgnssdata.Time[i]);
  }
  JsonArray LATITUDE = doc.createNestedArray("LATITUDE");
  for(int i=0;i<arraynum;i++)
  {
    LATITUDE.add(qgnssdata.Latitude[i]);
  }
  JsonArray LONGITUDE = doc.createNestedArray("LONGITUDE");
  for(int i=0;i<arraynum;i++)
  {
    LONGITUDE.add(qgnssdata.Longitude[i]);
  }
  JsonArray ALTITUDE = doc.createNestedArray("ALTITUDE");
  for(int i=0;i<arraynum;i++)
  {
    ALTITUDE.add(qgnssdata.Altitude[i]);
  }
  JsonArray Azimuth = doc.createNestedArray("AZIMUTH");
  for(int i=0;i<arraynum;i++)
  {
    Azimuth.add(qgnssdata.Azimuth[i]);
  }
  serializeJson(doc, qbuf);
}

void MqttTopic::PublishTopicShockSensing(void)
{
  StaticJsonDocument<4096> doc;
  doc["MAC"] = (const char*)qshocksensing.MAC;
  JsonArray BASETIME = doc.createNestedArray("BASETIME");
  for(int i=0;i<8;i++)
  {
    BASETIME.add(qshocksensing.BaseTime.sbuf[i]);
  }
  doc["START_TIME"] = qshocksensing.StartTime;
  doc["END_TIME"] = qshocksensing.EndTime;
  doc["START_IDX"] = qshocksensing.StartIdx;
  doc["LENGTH"] = qshocksensing.Length;

  int arraynum = qshocksensing.Length;
  if(arraynum > SHOCKDATA_MAX) arraynum = SHOCKDATA_MAX;

  JsonArray SHOCK_X = doc.createNestedArray("SHOCK_X");
  for(int i=0;i<arraynum;i++)
  {
    SHOCK_X.add(qshocksensing.ShockX[i]);
  }
  JsonArray SHOCK_Y = doc.createNestedArray("SHOCK_Y");
  for(int i=0;i<arraynum;i++)
  {
    SHOCK_Y.add(qshocksensing.ShockY[i]);
  }
  serializeJson(doc, qbuf);
}

void MqttTopic::PublishTopicNetworkStatus(void)
{
  StaticJsonDocument<256> doc;
  doc["WiFi"] = qnetstatus.IsWiFiConnected; // 와이파이 연결 상태
  doc["Server"] = qnetstatus.IsServerConnected; // mqtt 연결 상태
  doc["Controller"] = qnetstatus.IsControllerConnected; // 컨트롤러 연결상태 
  serializeJson(doc, qbuf);
}

void MqttTopic::ParsingTopicTimeMS(byte* payload, unsigned int length)
{
  char* p = (char*)malloc(length);
  memcpy(p,payload,length);

  const size_t capacity = JSON_ARRAY_SIZE(8) + JSON_OBJECT_SIZE(1) + 10;
  DynamicJsonDocument doc(capacity);
  DeserializationError error = deserializeJson(doc, p);

  JsonArray T = doc["T"];
  for(int i=0;i<8;i++)
  {
    qtimems.T.sbuf[i] = (uint8_t)T[i];
  }

  free(p);
  //Serial.printf("\n=> T : %lld",qtimems.T.llbuf);
}


void MqttTopic::ParsingNetworkData(byte* payload, unsigned int length)
{
  char* p = (char*)malloc(length);
  memcpy(p,payload,length);

  const size_t capacity = JSON_OBJECT_SIZE(4) + 120;
  DynamicJsonDocument doc(capacity);
  DeserializationError error = deserializeJson(doc, p);

  const char* pSSID = doc["SSID"];
  if(pSSID != NULL) strcpy(netdata.SSID,pSSID );
  const char* pPWD = doc["PWD"];
  if(pPWD != NULL) strcpy(netdata.PWD,pPWD );
  const char* pIP = doc["IP"];
  if(pIP != NULL) strcpy(netdata.IP,pIP );
  netdata.PORT = doc["PORT"];
  free(p);
  
  //Serial.printf("\n=> SSID(%s) PWD(%s) IP(%s) PORT(%d)",netdata.SSID,netdata.PWD,netdata.IP,netdata.PORT);
}

void MqttTopic::ParsingModelData(byte* payload, unsigned int length)
{
  char* p = (char*)malloc(length);
  memcpy(p,payload,length);

  StaticJsonDocument<256> doc;
  DeserializationError error = deserializeJson(doc, p);

  modeldata.model = doc["Model_Code"]; 
  modeldata.Encod_low = doc["Encod_low"]; 
  free(p);
}

void MqttTopic::ParsingTopicRequestLogin(byte* payload, unsigned int length)
{
  char* p = (char*)malloc(length);
  memcpy(p,payload,length);

  StaticJsonDocument<256> doc;
  DeserializationError error = deserializeJson(doc, p);

  qrequestlogin.WorkerIdx = doc["WORKER_IDX"];
  qrequestlogin.Encod_low = doc["Encod_low"];
  qrequestlogin.LastDepth = doc["depth"];
  qrequestlogin.bit_position = doc["beat"];
  qrequestlogin.hammer_len = doc["hammer_len"];
  qrequestlogin.rod_count = doc["rod_count"];
  qrequestlogin.OffsetBitPosition = doc["OffsetBitPosition"];

  free(p);
}

void MqttTopic::ParsingTopicRequestStart(byte* payload, unsigned int length)
{
  char* p = (char*)malloc(length);
  memcpy(p,payload,length);

  StaticJsonDocument<256> doc;
  DeserializationError error = deserializeJson(doc, p);

  qrequeststart.WorkerIdx = doc["WORKER_IDX"]; 
  qrequeststart.WorkUnitIdx = doc["WORKUNIT_IDX"]; 
  qrequeststart.TargetDepth = doc["TARGET_DEPTH"];
  qrequeststart.Encod_low = doc["Encod_low"];
  qrequeststart.bit_position = doc["beat"];
  qrequeststart.LastDepth = doc["depth"];
  qrequeststart.hammer_len = doc["hammer_len"];
  qrequeststart.rod_count = doc["rod_count"];
  qrequeststart.OffsetBitPosition = doc["OffsetBitPosition"];

  free(p);
}

void MqttTopic::ParsingTopicRequestStop(byte* payload, unsigned int length)
{
  char* p = (char*)malloc(length);
  memcpy(p,payload,length);

  StaticJsonDocument<256> doc;
  DeserializationError error = deserializeJson(doc, p);

  qrequeststop.WorkerIdx = doc["WORKER_IDX"]; 
  qrequeststop.WorkUnitIdx = doc["WORKUNIT_IDX"];
  qrequeststop.Encod_low = doc["Encod_low"]; 
  free(p);
}
void MqttTopic::ParsingTopicRequestGnss(byte* payload, unsigned int length)
{
  char* p = (char*)malloc(length);
  memcpy(p,payload,length);

  const size_t capacity = JSON_OBJECT_SIZE(4) + 120;
  DynamicJsonDocument doc(capacity);
  DeserializationError error = deserializeJson(doc, p);
  
  qrequestgnss.GNSS_lon = doc["Longitude"]; 
  qrequestgnss.GNSS_lat = doc["latitude"];
  qrequestgnss.GNSS_alt = doc["altitude"]; 
  qrequestgnss.Azimuth = doc["azimuth"];
  //Serial.printf("\n=> lon(%s) lat(%s) alt(%s) Azimuth(%f)",lon,lat,alt,qrequestgnss.Azimuth);
  free(p);
}

int MqttTopic::CheckQbufLength(void)
{
  int length = 0;
  for(int i=0;i<QBUF_LENGTH;i++)
  {
    if(qbuf[i] == 0x00)
    {
      length = i;
      break;
    }
  }
  return length;
}

