////////////////////////////////////////////////////////////////////////////////////
// Programmed by LDH 2022.06.01
// Edit by LSW 2023.06.13 ~ 
////////////////////////////////////////////////////////////////////////////////////
#include <Arduino.h>
#include <CANModule.h>
#include <mcp_can.h>
#include <MCP3564.h>
#include <Ticker.h>
////////////////////////////////////////////////////////////////////////////////////


////////////////////////////////////////////////////////////////////////////////////
// Module data
////////////////////////////////////////////////////////////////////////////////////
MCP3564 ADC;
MCP_CAN CAN0(CAN0_CS);
CANModule AriCAN;
bool IsCANActive = false;
bool CANPreStatus = false;
bool CANOpStatus = false;



#define PRESS_READ_TIME 1000
int32_t pressReadTime = 0;
bool IspressReadTime = false;

#define TORQ_READ_TIME 2700
int32_t troeqReadTime = 0;
bool IstroeqReadTime = false;
int32_t seqcount =0 ;
int32_t ADCData[3];
bool ADCStatus[3];
float Pressure = 0;
float Torque = 0;
////////////////////////////////////////////////////////////////////////////////////
// Timer Interrupt
////////////////////////////////////////////////////////////////////////////////////
Ticker mainTicker;
////////////////////////////////////////////////////////////////////////////////////


////////////////////////////////////////////////////////////////////////////////////
// Function define
////////////////////////////////////////////////////////////////////////////////////
bool Torque_ReadADC(void);
bool Pressure_ReadADC(void);
void InitHardwares(void);
void InitCAN(void);
void InitTimer(void);
void mainTimer(void);

bool Torque_ReadADC(void) // 190ms
{
  //if(digitalRead(ADC_INT) == 0)
  //{
    ADC.readADCData(); 
    if(ADC.adc_ch == 0)
    {
      ADCData[0] = ADC.adc_sample;
      ADCStatus[0] = true;
      //Serial.printf("\r\n adc_ch(%d) adc_sample(%d)",ADC.adc_ch,ADC.adc_sample);
    }
  //}
  if((ADCStatus[0]==true))
  {
    // Torque = Pressure * 9520/628  /  Pressure * 100 *15.159/100 = 0.159....
    // at 1V : 0x0001B000
    // at 5V : 0x00095000
    // 0.5~ 2.5v 입력...
    int32_t adata, rdata;
    float fdata;
    if(ADCData[0] < 0x0001B000) adata = 0; // 1V 이하 이면.. 0..
    else
    {
      if(ADCData[0] > 0x000F0000) adata = 0; // 오버플로우 방지..?
      else adata = ADCData[0]-0x0001B000; // 여기가 정상 범위 임...  442368 = 500 / 0~2v 변환... 
    }
    rdata = (adata*500)/4997;
    if(rdata > 50000) fdata = 50000; // Pressure 의 최대 값 제한. = 50000 * 0.01 == 500
    else fdata = (float)rdata;
    Pressure = fdata * 0.01;

    ADCStatus[0] = false;
    return true;
  }
}
bool Pressure_ReadADC(void) // 170ms
{
  //if(digitalRead(ADC_INT) == 0)
  //{
    seqcount++;
    ADC.readADCData();
    if(ADC.adc_ch == 2)
    {
      ADCData[2] = ADC.adc_sample;
      ADCStatus[2] = true;
      
    }Serial.printf("\r\nseqcount(%d) ",seqcount);
  //}
  if((ADCStatus[2]==true))
  {
    // Pressure = (Vout-1)/4*500
    // at 1V : 0x0001B000
    // at 5V : 0x00095000
    // 0.5~ 2.5v 입력...
    int32_t adata, rdata;
    float fdata;
    
    if(ADCData[2] < 0x0001B000) adata = 0; // 
    else
    {
      if(ADCData[2] > 0x000F0000) adata = 0; //
      else adata = ADCData[2]-0x0001B000;//
    }
    rdata = (adata*500)/4997;
    if(rdata > 50000) fdata = 50000; // Torque 의 최대 값 제한. = 50000 * 0.15159236 == 7579.618
    else fdata = (float)rdata;
    Torque = fdata*0.15159236;

    ADCStatus[2] = false;
    //Serial.printf("\r\nADCData[0](%08X) ADCData[2](%08X)Pressure(%f) Torque(%f)",ADCData[0],ADCData[2],Pressure,Torque);
    return true;
  }
  return true;
}

////////////////////////////////////////////////////////////////////////////////////
// 1msec Timer, setup, loop
////////////////////////////////////////////////////////////////////////////////////
void mainTimer(void)
{
  if(IspressReadTime == false)
  {
    pressReadTime++;
    if(pressReadTime >= PRESS_READ_TIME) IspressReadTime = true; // 170ms - ADC PRESS
  }
  
  /*if(IstroeqReadTime == false)
  {
    troeqReadTime++;
    if(troeqReadTime >= TORQ_READ_TIME) IstroeqReadTime = true; // 190ms - ADC TORQ
  }*/
}

void setup()
{
  Serial.begin(115200);
  InitHardwares();
  InitTimer();
  //Serial.printf("\r\n setup");
}

void loop()
{
  if(IspressReadTime == true) // 170ms
  {
    if(Pressure_ReadADC() == true)
    {
      pressReadTime = 0;
      IspressReadTime = false;
    }
  }
  else if(IstroeqReadTime == true) // 190ms
  {
    if(Torque_ReadADC() == true)
    {
      troeqReadTime = 0;
      IstroeqReadTime = false;
    }
  }
}
////////////////////////////////////////////////////////////////////////////////////


////////////////////////////////////////////////////////////////////////////////////
// Initialize function
////////////////////////////////////////////////////////////////////////////////////
void InitHardwares(void)
{
  InitCAN();  
  pinMode(ADC_CS, OUTPUT);
  pinMode(ADC_INT, INPUT);  
  SPI.begin();
  delay(500); // I think we need an initial delay.
  ADC.ResetYJ();
  //ADC.printRegisters();
}

void InitCAN(void)
{
  AriCAN.ptrcan = &CAN0;
  //Serial.printf("\r\nCAN Initialization");
  if(AriCAN.YJModuleInit()==true)
  //if(AriCAN.ModuleInit125kbps()==true)
  {
    IsCANActive = true;
    delay(3000);
    CANPreStatus = AriCAN.SendPreoperationSet();
    delay(1000);
    CANOpStatus = AriCAN.SendOperationSet();
    delay(1000);
  }
}
void InitTimer(void)
{
  mainTicker.attach_ms(1, mainTimer);
}
////////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////////////////
