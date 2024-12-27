#include <Parameter.h>

Parameter::Parameter()
{
}

void Parameter::InitParameter(char* version)
{
  SetParameterPointer();
  datasize = sizeof(ParameterData);
  Serial.printf("\r\nParameter size : %d",datasize);
  
  if(ReadParameter() == false)
  {
    Serial.print("\r\nParameter checksum error! -> Reset Parameter");
    ResetParameter();
    strcpy(ptrHardSoftVersion,version);
    WriteParameter();
  }
  else if(strcmp(ptrModuleName,ptrBSet->ptrModuleName) != 0)
  {
    Serial.print("\r\nModuleName is different! -> Reset Parameter");
    ResetParameter();
    strcpy(ptrHardSoftVersion,version);
    WriteParameter();
  }
  else if(strcmp(ptrParVersion,PARAMETER_VERSION) != 0)
  {
    Serial.print("\r\nParameter Version is different! -> Reset Parameter");
    ResetParameter();
    strcpy(ptrHardSoftVersion,version);
    WriteParameter();
  }
  else if(strcmp(ptrHardSoftVersion,version) != 0)
  {
    Serial.print("\r\nHardSoftVersion is different! -> Update Parameter");
    strcpy(ptrHardSoftVersion,version);
    UPData.data.BootCount++;
    WriteParameter();
  }
  else
  {
    UPData.data.BootCount++;
    WriteParameter();
  }
  SetParameterPointer();
}

void Parameter::SetParameterPointer(void)
{
  ptrParVersion = UPData.data.ParVersion;
  ptrModuleName = UPData.data.ModuleName;
  ptrModuleType = UPData.data.ModuleType;
  ptrModuleVersion = UPData.data.ModuleVersion;
  ptrHardSoftVersion = UPData.data.HardSoftVersion;
  ptrSupplierName = UPData.data.SupplierName;
  ptrMacAddressHex = UPData.data.MacAddressHex;
  ptrMacAddressHexColon = UPData.data.MacAddressHexColon;
  ptrMacAddressByte = UPData.data.MacAddressByte;
  ptrWiFiSSID = UPData.data.WiFiSSID;
  ptrWiFiKey = UPData.data.WiFiKey;
  ptrServerIP = UPData.data.ServerIP;
  ptrOTAServerIP = UPData.data.OTAServerIP;
  ptrConnectionPort = UPData.data.ConnectionPort;
  ptrHassStartCode = UPData.data.HassStartCode;
  ptrHassCmdCode = UPData.data.HassCmdCode;
  ptrHassDataLength = UPData.data.HassDataLength;
  ptrHassDataPackets = UPData.data.HassDataPackets;
  ptrHassCmdSendTime = UPData.data.HassCmdSendTime;
  ptrHassCmdTimeInit = UPData.data.HassCmdTimeInit;
  ptrModbusDataPackets = UPData.data.ModbusDataPackets;
  ptrModbusCmdSendTime = UPData.data.ModbusCmdSendTime;
  ptrModbusCmdTimeInit = UPData.data.ModbusCmdTimeInit;
  ptrModbusCmdSendSeq = UPData.data.ModbusCmdSendSeq;
  // 모델 별파라메터
  ptrModel = UPData.data.Model;
  ptrEncoder_Bottom = UPData.data.Encoder_Bottom;
}

void Parameter::ResetParameter(void)
{
  for(int i=0;i<datasize;i++) UPData.sbuf[i] = 0x00;

  strcpy(UPData.data.ParVersion,PARAMETER_VERSION);
  strcpy(UPData.data.ModuleName, ptrBSet->ptrModuleName); 
  strcpy(UPData.data.ModuleType , ptrBSet->ptrModuleType); 
  strcpy(UPData.data.ModuleVersion , ptrBSet->ptrModuleVersion); 
  strcpy(UPData.data.HardSoftVersion, ptrBSet->ptrHardSoftVersion); 
  strcpy(UPData.data.SupplierName, ptrBSet->ptrSupplierName); 

  uint8_t macnum[6];
  WiFi.macAddress(macnum);
  sprintf(UPData.data.MacAddressHex,"%02X%02X%02X%02X%02X%02X",macnum[0],macnum[1],macnum[2],macnum[3],macnum[4],macnum[5]);
  sprintf(UPData.data.MacAddressHexColon,"%02X:%02X:%02X:%02X:%02X:%02X",macnum[0],macnum[1],macnum[2],macnum[3],macnum[4],macnum[5]);
  for(int i=0;i<6;i++) UPData.data.MacAddressByte[i] = macnum[i];
  UPData.data.BootCount = 1;
  strcpy(UPData.data.WiFiSSID, ptrBSet->ptrWiFiSSID); 
  strcpy(UPData.data.WiFiKey, ptrBSet->ptrWiFiKey); 
  strcpy(UPData.data.ServerIP, ptrBSet->ptrServerIP);
  strcpy(UPData.data.OTAServerIP, ptrBSet->ptrOTAServerIP);
  UPData.data.ConnectionPort[0] = ptrBSet->ServerCheckPort;
  UPData.data.ConnectionPort[1]  = ptrBSet->DataSendPort;
  UPData.data.ConnectionPort[2] = ptrBSet->MQTTPort;
  UPData.data.ConnectionPort[3] = ptrBSet->UpdatePort;
  UPData.data.ConnectionPort[4] = ptrBSet->FileLoadPort;
  
  // 모델 파라메터
  UPData.data.Model = ptrBSet->MODEL_Code;
  UPData.data.Encoder_Bottom = ptrBSet->Encoder;

  UPData.data.HassCmdNum = ptrBSet->HassCmdNum;
  UPData.data.ModbusCmdNum = ptrBSet->ModbusCmdNum;
  if(UPData.data.HassCmdNum > 0)
  {
    for(int i=0;i<HASSCMD_NUM;i++)
    {
      UPData.data.HassStartCode[i] = ptrBSet->ptrHassStartCode[i];
      UPData.data.HassCmdCode[i] = ptrBSet->ptrHassCmdCode[i];
      UPData.data.HassDataLength[i] = ptrBSet->ptrHassDataLength[i];
      UPData.data.HassDataPackets[i] = ptrBSet->ptrHassDataPackets[i];
      UPData.data.HassCmdSendTime[i] = ptrBSet->ptrHassCmdSendTime[i];
      UPData.data.HassCmdTimeInit[i] = ptrBSet->ptrHassCmdTimeInit[i];
    }
  }
  if(UPData.data.ModbusCmdNum > 0)
  {
    for(int i=0;i<MODBUSCMD_NUM;i++)
    {
      UPData.data.ModbusDataPackets[i] = ptrBSet->ptrModbusDataPackets[i];
      UPData.data.ModbusCmdSendTime[i] = ptrBSet->ptrModbusCmdSendTime[i];
      UPData.data.ModbusCmdTimeInit[i] = ptrBSet->ptrModbusCmdTimeInit[i];
      UPData.data.ModbusCmdSendSeq[i] = ptrBSet->ptrModbusCmdSendSeq[i];
    }
  }
}

void Parameter::ShowParameter(void)
{
  ptrBTSerial->printf("\r\nParameter Version : %s",ptrParVersion);
  ptrBTSerial->printf("\r\nModuleName: %s",ptrModuleName);
  ptrBTSerial->printf("\r\nModuleType: %s",ptrModuleType );
  ptrBTSerial->printf("\r\nModuleVersion: %s",ptrModuleVersion);
  ptrBTSerial->printf("\r\nHardSoftVersion: %s",ptrHardSoftVersion);
  ptrBTSerial->printf("\r\nSupplierName: %s",ptrSupplierName);

  ptrBTSerial->printf("\r\nMacHex : %s",ptrMacAddressHex);
  ptrBTSerial->printf("  MacHexColon: %s  MacByte: ",ptrMacAddressHexColon);
  for(int i=0;i<6;i++) ptrBTSerial->printf("%02X",ptrMacAddressByte[i]);
  ptrBTSerial->printf("\r\nBootCount : %d",UPData.data.BootCount);

  ptrBTSerial->printf("\r\nWiFiSSID: %s",ptrWiFiSSID);
  ptrBTSerial->printf("\r\nWiFiKey: %s",ptrWiFiKey);
  ptrBTSerial->printf("\r\nServerIP: %s",ptrServerIP);
  ptrBTSerial->printf("\r\nOTAServerIP: %s",ptrOTAServerIP);
  ptrBTSerial->printf("\r\nServerCheckPort: %d",ptrConnectionPort[0]);
  ptrBTSerial->printf("\r\nDataSendPort: %d",ptrConnectionPort[1]);
  ptrBTSerial->printf("\r\nMQTTPort: %d",ptrConnectionPort[2]);
  ptrBTSerial->printf("\r\nUpdatePort: %d",ptrConnectionPort[3]);
  ptrBTSerial->printf("\r\nFileLoadPort: %d",ptrConnectionPort[4]);

  ptrBTSerial->printf("\r\nHassCmdNum : %d",UPData.data.HassCmdNum);
  ptrBTSerial->printf("\r\nModbusCmdNum : %d",UPData.data.ModbusCmdNum);
  ptrBTSerial->printf("\r\nHassStartCode : ");
  for(int i=0;i<HASSCMD_NUM;i++) ptrBTSerial->printf("%d, ",ptrHassStartCode[i]);
  ptrBTSerial->printf("\r\nHassCmdCode : ");
  for(int i=0;i<HASSCMD_NUM;i++) ptrBTSerial->printf("%d, ",ptrHassCmdCode[i]);
  ptrBTSerial->printf("\r\nHassDataLength : ");
  for(int i=0;i<HASSCMD_NUM;i++) ptrBTSerial->printf("%d, ",ptrHassDataLength[i]);
  ptrBTSerial->printf("\r\nHassDataPackets : ");
  for(int i=0;i<HASSCMD_NUM;i++) ptrBTSerial->printf("%d, ",ptrHassDataPackets[i]);
  ptrBTSerial->printf("\r\nHassCmdSendTime : ");
  for(int i=0;i<HASSCMD_NUM;i++) ptrBTSerial->printf("%d, ",ptrHassCmdSendTime[i]);
  ptrBTSerial->printf("\r\nHassCmdTimeInit : ");
  for(int i=0;i<HASSCMD_NUM;i++) ptrBTSerial->printf("%d, ",ptrHassCmdTimeInit[i]);
  ptrBTSerial->printf("\r\nModbusDataPackets : ");
  for(int i=0;i<MODBUSCMD_NUM;i++) ptrBTSerial->printf("%d, ",ptrModbusDataPackets[i]);
  ptrBTSerial->printf("\r\nModbusCmdSendTime : ");
  for(int i=0;i<MODBUSCMD_NUM;i++) ptrBTSerial->printf("%d, ",ptrModbusCmdSendTime[i]);
  ptrBTSerial->printf("\r\nModbusCmdTimeInit : ");
  for(int i=0;i<MODBUSCMD_NUM;i++) ptrBTSerial->printf("%d, ",ptrModbusCmdTimeInit[i]);
  ptrBTSerial->printf("\r\nModbusCmdSendSeq : ");
  for(int i=0;i<MODBUSCMD_NUM;i++) ptrBTSerial->printf("%d, ",ptrModbusCmdSendSeq[i]);

  ptrBTSerial->printf("\r\nCheckSum : %04X",UPData.data.CheckSum);
}

void Parameter::SerialShowParameter(void)
{
  Serial.printf("\r\nParameter Version : %s",ptrParVersion);
  Serial.printf("\r\nModuleName: %s",ptrModuleName);
  Serial.printf("\r\nModuleType: %s",ptrModuleType );
  Serial.printf("\r\nModuleVersion: %s",ptrModuleVersion);
  Serial.printf("\r\nHardSoftVersion: %s",ptrHardSoftVersion);
  Serial.printf("\r\nSupplierName: %s",ptrSupplierName);

  Serial.printf("\r\nMacHex : %s",ptrMacAddressHex);
  Serial.printf("  MacHexColon: %s  MacByte: ",ptrMacAddressHexColon);
  for(int i=0;i<6;i++) Serial.printf("%02X",ptrMacAddressByte[i]);
  Serial.printf("\r\nBootCount : %d",UPData.data.BootCount);

  Serial.printf("\r\nWiFiSSID: %s",ptrWiFiSSID);
  Serial.printf("\r\nWiFiKey: %s",ptrWiFiKey);
  Serial.printf("\r\nServerIP: %s",ptrServerIP);
  Serial.printf("\r\nOTAServerIP: %s",ptrOTAServerIP);
  Serial.printf("\r\nServerCheckPort: %d",ptrConnectionPort[0]);
  Serial.printf("\r\nDataSendPort: %d",ptrConnectionPort[1]);
  Serial.printf("\r\nMQTTPort: %d",ptrConnectionPort[2]);
  Serial.printf("\r\nUpdatePort: %d",ptrConnectionPort[3]);
  Serial.printf("\r\nFileLoadPort: %d",ptrConnectionPort[4]);

  Serial.printf("\r\nHassCmdNum : %d",UPData.data.HassCmdNum);
  Serial.printf("\r\nModbusCmdNum : %d",UPData.data.ModbusCmdNum);
  Serial.printf("\r\nHassStartCode : ");
  for(int i=0;i<HASSCMD_NUM;i++) Serial.printf("%d, ",ptrHassStartCode[i]);
  Serial.printf("\r\nHassCmdCode : ");
  for(int i=0;i<HASSCMD_NUM;i++) Serial.printf("%d, ",ptrHassCmdCode[i]);
  Serial.printf("\r\nHassDataLength : ");
  for(int i=0;i<HASSCMD_NUM;i++) Serial.printf("%d, ",ptrHassDataLength[i]);
  Serial.printf("\r\nHassDataPackets : ");
  for(int i=0;i<HASSCMD_NUM;i++) Serial.printf("%d, ",ptrHassDataPackets[i]);
  Serial.printf("\r\nHassCmdSendTime : ");
  for(int i=0;i<HASSCMD_NUM;i++) Serial.printf("%d, ",ptrHassCmdSendTime[i]);
  Serial.printf("\r\nHassCmdTimeInit : ");
  for(int i=0;i<HASSCMD_NUM;i++) Serial.printf("%d, ",ptrHassCmdTimeInit[i]);
  Serial.printf("\r\nModbusDataPackets : ");
  for(int i=0;i<MODBUSCMD_NUM;i++) Serial.printf("%d, ",ptrModbusDataPackets[i]);
  Serial.printf("\r\nModbusCmdSendTime : ");
  for(int i=0;i<MODBUSCMD_NUM;i++) Serial.printf("%d, ",ptrModbusCmdSendTime[i]);
  Serial.printf("\r\nModbusCmdTimeInit : ");
  for(int i=0;i<MODBUSCMD_NUM;i++) Serial.printf("%d, ",ptrModbusCmdTimeInit[i]);
  Serial.printf("\r\nModbusCmdSendSeq : ");
  for(int i=0;i<MODBUSCMD_NUM;i++) Serial.printf("%d, ",ptrModbusCmdSendSeq[i]);

  // 모델별 데이터...
  Serial.printf("\r\nModel Code: %d",ptrModel);
  Serial.printf("\r\nEncoder_Bottom: %d",ptrEncoder_Bottom);

  Serial.printf("\r\nCheckSum : %04X",UPData.data.CheckSum);
}

bool Parameter::ReadParameter(void)
{
  EEPROM.begin(datasize);
  for(int i=0;i<datasize;i++)
  {
    UPData.sbuf[i] = EEPROM.read(i);
  }
  EEPROM.end();
  if(CheckParameter() == true) return true;
  return false;
}

void Parameter::WriteParameter(void)
{
  EEPROM.begin(datasize);
  UPData.data.CheckSum = CalParameterCheckSum();
  for(int i=0;i<datasize;i++)
  {
    EEPROM.write(i,UPData.sbuf[i]);
  }
  EEPROM.end();
}

bool Parameter::CheckParameter(void)
{
  uint16_t checksum = CalParameterCheckSum();
  if(checksum == UPData.data.CheckSum) return true;
  return false;
}

uint16_t Parameter::CalParameterCheckSum(void)
{
  uint16_t *iptr = (uint16_t *)UPData.sbuf;
  size_t isz = datasize/2;
  uint16_t checksumdata;

  checksumdata = CalCheckSum(iptr, isz-1);
  return checksumdata;
}

uint16_t Parameter::CalCheckSum(uint16_t *ptr, size_t sz)
{
  uint16_t chk =  INIT_CHECKSUM;

  while(sz-- !=0)
    chk -= *ptr++;

  return chk;
}
void Parameter::ModelParameter(void)
{
  // 모델 별파라메터
  UPData.data.Model = ptrModel;
  UPData.data.Encoder_Bottom = ptrEncoder_Bottom;
  WriteParameter();
}

