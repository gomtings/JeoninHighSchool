#include <Wire.h>
#define slave_addr 0x01
char MsgBuf[1024]; //Master로 부터 전송받은 데이터를 저장할 버퍼
volatile byte pos;
volatile boolean Print_Int = false;

void setup() {
  Serial.begin(9600);
  Wire.begin(slave_addr); //slave_addr의 주소값을 갖는 slave로 동작
  Wire.onReceive(Receive_Int); //Master에서 보낸 데이터를 수신했을때 호출할 함수를 등록
}

void loop() {
  if(Print_Int){
    MsgBuf[pos] = 0;
    Serial.print(MsgBuf);
    pos =0 ;
    Print_Int = false;
  }
}


void Receive_Int() { //Master에서 보낸 데이터가 수신되면 호출되는 함수
  byte m;
  while(Wire.available()){ //읽어올 데이터가 있다면
    m = Wire.read(); 
    if(m =='\n'){ //'\n'문자를 만나면 
      Print_Int = true; //Print_Int를 true로 바꿔주고 loop()문에서 데이터를 출력합니다. 
      pos = 0; // pos를 0으로 초기화하여 버퍼를 비웁니다.
    } else if(pos < sizeof(MsgBuf)){
      MsgBuf[pos++] = m; //데이터를 버퍼에 저장합니다.
    }
    Serial.print((char)m);
  } 
}





