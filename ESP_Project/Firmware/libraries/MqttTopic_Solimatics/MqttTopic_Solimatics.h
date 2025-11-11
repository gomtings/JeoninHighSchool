#ifndef MqttTopic_Solimatics_h
#define MqttTopic_Solimatics_h

#include <Arduino.h>
#include <ArduinoJson.h>
#include <rBase64.h>
#include <Typedef_Ari.h>

typedef struct _TopicInfo
{
  char MAC[20];
  char AP_MAC[20];
  char IOT_SPPL_CD[12];
  char IOT_MODEL[12];
  char MCIP[20];
  char STS[12];
  char VER[12];
  char MCID[12];
}TopicInfo;

typedef struct _TopicVersion
{
  char MAC[20];
  char ProgramVer[20];
  char HardSoftVer[20];
  char Type[20];
  uint16_t BootCount;
  uint32_t PowerOnTime;
  char Message[100];
}TopicVersion;

typedef struct _TopicTimeMS
{
  Int64Data T;
}TopicTimeMS;

typedef struct _NetworkData
{
  char SSID[50];
  char PWD[50];
  char IP[50];
  int PORT;
}NetworkData;

typedef struct _AnalysisData
{
  int32_t MaxDepth;
  int32_t Encod_low;
  int32_t BitPosition;
  uint8_t RodCount;
  uint8_t Holl;
}AnalysisData;

typedef struct _ModelData
{
  int16_t model;
  int32_t Encod_low;
  int16_t D1_LOW;
  int16_t D1_MAX;
  int16_t D2_LOW;
  int16_t D2_MAX;
}ModelData;

typedef struct _TopicTMDSLogin
{
  uint32_t WorkerIdx;
  int32_t Encod_low;
  int16_t model;
}TopicTMDSLogin;

typedef struct _TopicTMDSStart
{
  uint32_t WorkerIdx;
  uint32_t WorkUnitIdx;
  int32_t TargetDepth;
  int32_t Encod_low;
  int16_t model;
}TopicTMDSStart;

typedef struct _TopicTMDSStop
{
  uint32_t WorkerIdx;
  uint32_t WorkUnitIdx;
  int32_t Encod_low;
}TopicTMDSStop;

typedef struct _TopicGNSSData
{
  float GNSS_lon;
  float GNSS_lat; 
  float GNSS_alt;
  float Azimuth;
}TopicGNSSData;

#define YJSENSING_MAX 20
typedef struct _TopicTMDSYJSensing
{
  char MAC[20];  
  uint32_t WorkerIdx;
  uint32_t WorkUnitIdx;
  int32_t TargetDepth;
  int Packets;
  Int64Data BaseTime;
  int32_t Time[YJSENSING_MAX];
  int32_t JobTime[YJSENSING_MAX];
  float Pressure[YJSENSING_MAX];
  float Torque[YJSENSING_MAX];
  int32_t InclinationX[YJSENSING_MAX];
  int32_t InclinationY[YJSENSING_MAX];
  int8_t RodCount[YJSENSING_MAX];
  int32_t Encoder[YJSENSING_MAX];
  int32_t MaxDepth[YJSENSING_MAX];
  int32_t BitPosition[YJSENSING_MAX];
  int8_t Switch[YJSENSING_MAX];
  int32_t Bottom[YJSENSING_MAX];
  int32_t Holl[YJSENSING_MAX];
}TopicTMDSYJSensing;

#define SSSENSING_MAX 20
typedef struct _TopicTMDSSSSensing
{
  char MAC[20];  
  int Packets;
  Int64Data BaseTime;
   int32_t StartTime[SSSENSING_MAX];
  int32_t EndTime[SSSENSING_MAX];
  int16_t SamplingNum[SSSENSING_MAX];
  float HammeringFrequency[SSSENSING_MAX];
  float HammeringStdDivX[SSSENSING_MAX];
  float HammeringStdDivY[SSSENSING_MAX];
  int32_t Encoder[SSSENSING_MAX];
  int32_t Depth[SSSENSING_MAX];
  float ROPData[SSSENSING_MAX];
}TopicTMDSSSSensing;

#define ENCSENSING_MAX 20
typedef struct _TopicTMDSEncSensing
{
  char MAC[20];  
  int Packets;
  Int64Data BaseTime;
  int32_t Time[ENCSENSING_MAX];
  int32_t Encoder[ENCSENSING_MAX];
}TopicTMDSEncSensing;

#define GNSSDATA_MAX 10
typedef struct _TopicTMDSGNSSData
{
  char MAC[20];  
  int Packets;
  Int64Data BaseTime;
  int32_t Time[GNSSDATA_MAX];
  int32_t Latitude[GNSSDATA_MAX];
  int32_t Longitude[GNSSDATA_MAX];
  int32_t Altitude[GNSSDATA_MAX];
  float Azimuth[GNSSDATA_MAX];
}TopicTMDSGNSSData;

#define SHOCKDATA_MAX 100  // 더크면문제생김
typedef struct _TopicTMDSShockSensing
{
  char MAC[20];  
  Int64Data BaseTime;
  int32_t StartTime;
  int32_t EndTime;
  int16_t StartIdx;
  int16_t Length;
  int16_t ShockX[SHOCKDATA_MAX];
  int16_t ShockY[SHOCKDATA_MAX];
}TopicTMDSShockSensing;

typedef struct _TopicNetworkStatus
{
  bool IsWiFiConnected;
  bool IsServerConnected;
  bool IsControllerConnected;
}TopicNetworkStatus;

#define QBUF_LENGTH 512

class MqttTopic
{
  public:

    MqttTopic();

    void PublishTopicInit(void);
    void PublishTopicVersion(void);
    void PublishTopicResponseLogin(void);
    void PublishTopicResponseStart(void);
    void PublishTopicResponseStop(void);
    void PublishTopicYJSensing(void);
    void PublishTopicSSSensing(void);
    void PublishTopicEncSensing(void);
    void PublishTopicGNSSData(void);
    void PublishTopicShockSensing(void);
    void PublishTopicResponseModel(void);
    void PublishTopicNetworkStatus(void);

    void ParsingTopicTimeMS(byte* payload, unsigned int length);    
    void ParsingNetworkData(byte* payload, unsigned int length);
    void ParsingModelData(byte* payload, unsigned int length);
    void ParsingTopicAnalysisData(byte* payload, unsigned int length);
    void ParsingTopicRequestLogin(byte* payload, unsigned int length);
    void ParsingTopicRequestStart(byte* payload, unsigned int length);
    void ParsingTopicRequestStop(byte* payload, unsigned int length);
    void ParsingTopicRequestGnss(byte* payload, unsigned int length);

    int CheckQbufLength(void);

    char qbuf[QBUF_LENGTH];

    TopicInfo qinfo;
    TopicVersion qversion;
    TopicTMDSLogin qresponselogin;
    TopicTMDSStart qresponsestart;
    TopicTMDSStop qresponsestop;
    TopicTMDSYJSensing qyjsensing;
    TopicTMDSSSSensing qsssensing;
    TopicTMDSGNSSData qgnssdata;
    TopicTMDSShockSensing qshocksensing;
    TopicTMDSEncSensing qencsensing;
    TopicNetworkStatus qnetstatus;

    TopicTMDSLogin qrequestlogin;
    TopicTMDSStart qrequeststart;
    TopicTMDSStop qrequeststop;
    TopicGNSSData qrequestgnss;
    TopicTimeMS qtimems;
    NetworkData netdata;
    ModelData modeldata;
    AnalysisData analysisdata;

  private:
};

#endif
