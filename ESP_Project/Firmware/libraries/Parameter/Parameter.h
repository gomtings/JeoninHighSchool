#ifndef Parameter_h
#define Parameter_h

#include <Arduino.h>
#include <EEPROM.h>
#include <WiFi.h>
#include <BluetoothSerial.h>
#include <BoardSet.h>

#define INIT_CHECKSUM 0x1234

//////////////////////////////////////////////////////////////////////////////
// typedef
//////////////////////////////////////////////////////////////////////////////
typedef struct _ParamterData
{
  char ParVersion[12];
  char ModuleName[24];
  char ModuleType[20];
  char ModuleVersion[20];
  char HardSoftVersion[16];
  char SupplierName[20];

  char MacAddressHex[20];
  char MacAddressHexColon[20];
  uint8_t MacAddressByte[6];
  uint16_t BootCount;

  char WiFiSSID[40];
  char WiFiKey[40];

  char ServerIP[20];
  char OTAServerIP[20];
  uint16_t ConnectionPort[6];

  int16_t HassCmdNum;
  int16_t ModbusCmdNum;
  
  uint8_t HassStartCode[HASSCMD_NUM];
  uint8_t HassCmdCode[HASSCMD_NUM];
  int16_t HassDataLength[HASSCMD_NUM];
  int16_t HassDataPackets[HASSCMD_NUM];
  int32_t HassCmdSendTime[HASSCMD_NUM];
  int32_t HassCmdTimeInit[HASSCMD_NUM];

  int16_t ModbusDataPackets[MODBUSCMD_NUM];
  int32_t ModbusCmdSendTime[MODBUSCMD_NUM];
  int32_t ModbusCmdTimeInit[MODBUSCMD_NUM];
  bool ModbusCmdSendSeq[MODBUSCMD_NUM];
  // 모델별 데이터.
  int16_t Model;
  int32_t Encoder_Bottom;

  uint16_t Reserved; 
  uint16_t CheckSum;
} ParameterData;

typedef union UParameterData
{
  ParameterData data;
  uint8_t sbuf[sizeof(ParameterData)];
};

class Parameter
{
  public:
    char* ptrParVersion;
    char* ptrModuleName;
    char* ptrModuleType;
    char* ptrModuleVersion;
    char* ptrHardSoftVersion;
    char* ptrSupplierName;
    char* ptrMacAddressHex;
    char* ptrMacAddressHexColon;
    uint8_t* ptrMacAddressByte;

    char* ptrWiFiSSID;
    char* ptrWiFiKey;
    char* ptrServerIP;
    char* ptrOTAServerIP;
    uint16_t* ptrConnectionPort;

    uint8_t* ptrHassStartCode;
    uint8_t* ptrHassCmdCode;
    int16_t* ptrHassDataLength;
    int16_t* ptrHassDataPackets;
    int32_t* ptrHassCmdSendTime;
    int32_t* ptrHassCmdTimeInit;
    int16_t* ptrModbusDataPackets;
    int32_t* ptrModbusCmdSendTime;
    int32_t* ptrModbusCmdTimeInit;
    // 모델별 데이터.
    int16_t ptrModel;
    int32_t ptrEncoder_Bottom;

    bool* ptrModbusCmdSendSeq;

    Parameter();
    void InitParameter(char* version);
    void ResetParameter(void);
    void SetParameterPointer(void);
    void CopyPowerOnData(void);
    void ShowParameter(void);
    void SerialShowParameter(void);
    bool ReadParameter(void);
    void WriteParameter(void);
    void ModelParameter(void);

    BluetoothSerial* ptrBTSerial;
    BoardSet* ptrBSet;

    UParameterData UPData;
    int16_t datasize;
    uint8_t ParBuf[sizeof(ParameterData)];

  private:
    bool CheckParameter(void);
    uint16_t CalCheckSum(uint16_t *ptr, size_t sz);
    uint16_t CalParameterCheckSum(void);
};

#endif

