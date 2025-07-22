#include <CANModule.h>

bool CANModule::ModuleInit(void)
{
  can_seq = 0;

  if(ptrcan->begin(MCP_STDEXT, CAN_125KBPS, MCP_8MHZ) == CAN_OK)
  {
    ptrcan->setMode(MCP_NORMAL);
    pinMode(CAN0_INT, INPUT);
    return true;
  }
  return false;
}

bool CANModule::YJModuleInit(void)
{
  can_seq = 0;

  if(ptrcan->begin(MCP_STDEXT, CAN_250KBPS, MCP_8MHZ) == CAN_OK)
  {
    ptrcan->setMode(MCP_NORMAL);
    pinMode(CAN0_INT, INPUT);
    return true;
  }
  return false;
}

bool CANModule::SSModuleInit(void)
{
  can_seq = 0;

  if(ptrcan->begin(MCP_STDEXT, CAN_125KBPS, MCP_8MHZ) == CAN_OK)
  {
    ptrcan->setMode(MCP_NORMAL);
    pinMode(CAN0_INT, INPUT);
    return true;
  }
  return false;
}

bool CANModule::ModuleInit125kbps(void)
{
  can_seq = 0;

  if(ptrcan->begin(MCP_STDEXT, CAN_125KBPS, MCP_8MHZ) == CAN_OK)
  {
    ptrcan->setMode(MCP_NORMAL);
    pinMode(CAN0_INT, INPUT);
    return true;
  }
  return false;
}

bool CANModule::ModuleInit250kbps(void)
{
  can_seq = 0;

  if(ptrcan->begin(MCP_STDEXT, CAN_250KBPS, MCP_8MHZ) == CAN_OK)
  {
    ptrcan->setMode(MCP_NORMAL);
    pinMode(CAN0_INT, INPUT);
    return true;
  }
  return false;
}

bool CANModule::SendPreoperationSet(void)
{
  can_id = 0;
  can_data[0] = 0x80;
  can_data[1] = 0;
  
  byte sndStat = ptrcan->sendMsgBuf(can_id, 0, 2, can_data);
  if(sndStat == CAN_OK) return true;

  return false;
}

bool CANModule::SendOperationSet(void)
{
  can_id = 0;
  can_data[0] = 0x01;
  can_data[1] = 0;
  
  byte sndStat = ptrcan->sendMsgBuf(can_id, 0, 2, can_data);
  if(sndStat == CAN_OK) return true;

  return false;
}

bool CANModule::SendSyncMsg(void)
{
  can_id = 0x80;
  byte sndStat = ptrcan->sendMsgBuf(can_id, 0, 0, can_data);
  if(sndStat == CAN_OK) return true;
  return false;
}

bool CANModule::SendBaudrateSet(void)
{
/*
  can_id = 0x60B;  // 0x600 + node ID
  can_data[0] = 0x22;  // Command
  can_data[1] = 0x01;  // Low byte Index
  can_data[2] = 0x20;  // High byte Index
  can_data[3] = 0x00;  // Sub Index
  can_data[4] = 0xFA;  // Data[0]
  can_data[5] = 0x00;  // Data[1]
  can_data[6] = 0x00;  // Data[2]
  can_data[7] = 0x00;  // Data[3]
 
 byte sndStat = ptrcan->sendMsgBuf(can_id, 0, 8, can_data);
  if(sndStat == CAN_OK) return true;
  return false;
*/

  can_id = 0x60A;  // 0x600 + node ID
  can_data[0] = 0x22;  // Command
  can_data[1] = 0x01;  // Low byte Index
  can_data[2] = 0x20;  // High byte Index
  can_data[3] = 0x00;  // Sub Index
  can_data[4] = 0x7D;  // Data[0]
  can_data[5] = 0x00;  // Data[1]
  can_data[6] = 0x00;  // Data[2]
  can_data[7] = 0x00;  // Data[3]
 
 byte sndStat = ptrcan->sendMsgBuf(can_id, 0, 8, can_data);
  if(sndStat == CAN_OK) return true;

  return false;
}

void CANModule::ML5_Test(void)
{
  can_id = 0x00000600+id_index;
  Serial.printf("\n(%d)",can_id);
  id_index++;  
  if(id_index>126) id_index=1;
  can_data[0] = 0x40;
  can_data[1] = 0x0B;
  can_data[2] = 0x10;
  can_data[3] = 0x00;
  can_data[4] = 0x00;
  can_data[5] = 0x00;
  can_data[6] = 0x00;
  can_data[7] = 0x00;
  ptrcan->sendMsgBuf(can_id, 0, 8, can_data);
}

void CANModule::ReadSDOMsg(void)
{
  can_id = 0x0000060B;
  can_data[0] = 0x40;
  can_data[1] = 0x00;
  can_data[2] = 0x00;
  can_data[3] = 0x00;
  can_data[4] = 0x00;
  can_data[5] = 0x00;
  can_data[6] = 0x00;
  can_data[7] = 0x00;

  can_seq++;
  if(can_seq == 1)
  {
    can_data[1] = 0x00;
    can_data[2] = 0x20;
  }
  else if(can_seq == 2)
  {
    can_data[1] = 0x01;
    can_data[2] = 0x20;
  }
  else if(can_seq == 3)
  {
    can_data[1] = 0x10;
    can_data[2] = 0x61;
  }
  else if(can_seq >= 4)
  {
    can_data[1] = 0x20;
    can_data[2] = 0x61;
    can_seq = 0;
  }
  ptrcan->sendMsgBuf(can_id, 0, 8, can_data);
}


bool CANModule::ChkRecvMsg(void)
{
  if(!digitalRead(CAN0_INT))                         
  {
    ptrcan->readMsgBuf(&rxId, &len, rxBuf);
    idbuf = rxId;
    lenbuf = len;
    for(int i=0;i<lenbuf;i++) databuf[i] = rxBuf[i];
    return true;
    
    /*
    if((rxId & 0x80000000) == 0x80000000) sprintf(msgString, "\r\nExtended ID: 0x%.8lX  DLC: %1d  Data:", (rxId & 0x1FFFFFFF), len);
    else sprintf(msgString, "\r\nStandard ID: 0x%.3lX  DLC: %1d  Data:", rxId, len);
    Serial.print(msgString);
  
    if((rxId & 0x40000000) == 0x40000000)
    {
      sprintf(msgString, " REMOTE REQUEST FRAME");
      Serial.print(msgString);
    } 
    else 
    {
      for(byte i = 0; i<len; i++)
     {
        sprintf(msgString, " 0x%.2X", rxBuf[i]);
        Serial.print(msgString);
      }
    }
    return true;
    */
  }
  return false;
}

byte CANModule::geterrorCountRX(void)
{
  byte count;
  count = ptrcan->errorCountRX();
  return count;
}

byte CANModule::geterrorCountTX(void)
{
  byte count;
  count = ptrcan->errorCountTX();
  return count;
}

byte CANModule::getmcpStatus(void)
{
  byte status;
  status = ptrcan->mcp2515_readStatus();
  return status;
}

