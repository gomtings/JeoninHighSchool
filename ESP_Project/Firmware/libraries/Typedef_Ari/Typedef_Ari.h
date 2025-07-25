#ifndef Typedef_Ari_h
#define Typedef_Ari_h

typedef union _UInt16Data
{
  uint16_t ibuf;
  uint8_t sbuf[2];
}UInt16Data;

typedef union _Int16Data
{
  int16_t ibuf;
  uint8_t sbuf[2];
}Int16Data;

typedef union _UInt32Data
{
  uint32_t lbuf;
//  uint16_t ibuf[2];
  uint8_t sbuf[4];
}UInt32Data;

typedef union _Int32Data
{
  int32_t lbuf;
//  uint16_t ibuf[2];
  uint8_t sbuf[4];
}Int32Data;

typedef union _UInt64Data
{
  uint64_t llbuf;
//  uint32_t lbuf[2];
//  uint16_t ibuf[4];
  uint8_t sbuf[8];
}UInt64Data;

typedef union _Int64Data
{
  int64_t llbuf;
//  uint32_t lbuf[2];
//  uint16_t ibuf[4];
  uint8_t sbuf[8];
}Int64Data;

typedef union _FloatData
{
  float fbuf;
//  uint16_t ibuf[2];
  uint8_t sbuf[4];
}FloatData;

typedef union _DoubleData
{
  double dbuf;
//  uint32_t lbuf[2];
//  uint16_t ibuf[4];
  uint8_t sbuf[8];
}DoubleData;

#endif
