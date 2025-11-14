#ifndef CANModule_h
#define CANModule_h

#include <Arduino.h>
#include <mcp_can.h>
#include <Typedef_Ari.h>

#define CAN0_INT 4  
#define CAN0_CS 5
#define CAN1_CS 25

//////////////////////////////////////////////////////////////////////////////
// typedef
//////////////////////////////////////////////////////////////////////////////
typedef struct _CANData
{
  uint32_t Identifier;
  uint8_t DLC;
  uint8_t Command;
  uint8_t Data[8];
}CANData;

typedef union UCANData
{
  CANData data;
  uint8_t sbuf[sizeof(CANData)];
};

class CANModule 
{
  public:
    bool ModuleInit(void);
    bool YJModuleInit(void);
    bool SSModuleInit(void);
    bool ModuleInit125kbps(void);
    bool ModuleInit250kbps(void);
    bool SendPreoperationSet(void);
    bool SendOperationSet(void);
    bool SendSyncMsg(void);
    bool SendBaudrateSet(void);
    void ReadSDOMsg(void);
    bool ChkRecvMsg(void);
    void ML5_Test(void);
    byte geterrorCountRX(void);
    byte geterrorCountTX(void);
    byte getmcpStatus(void);

    UCANData UCData;
    MCP_CAN* ptrcan;
    int16_t cencoder;

    long unsigned int rxId;
    unsigned char len;
    unsigned char rxBuf[8];
    char msgString[128];

    long unsigned int idbuf;
    unsigned char lenbuf;
    unsigned char databuf[8];

    int can_seq;

    uint32_t can_id;
    byte can_data[8];

    uint32_t id_index = 1;

  private:
};

#endif
