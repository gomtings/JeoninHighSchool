#include <SoftwareSerial.h>
#include <TimerOne.h> // TimerOne 라이브러리

SoftwareSerial esp8266(2, 3); // RX, TX

//char* ssids[] = {"Solimatics", "Solimatics", "Solimatics", "Solimatics"};
char* ssids[] = {"Jeonin01", "Jeonin02", "Jeonin03", "Jeonin04"};
char Receive_Mgs[512]; // 충분한 크기의 버퍼를 할당합니다.
char lastCommand[32]; // 최근에 보낸 명령을 저장할 변수

#define TEST_COMM_TIME 100 // 통신 테스트
int32_t TestTime = 0;
bool IsTestTime = false;
#define CHANGE_MODE_TIME 1000 // 스테이션 모드 전환
int32_t ChangeModeTime = 0;
bool IsChangemodeTime = false;

double calculateDistance(int rssi);
void mainTimer(void);
void setup(){
  Serial.begin(9600);
  esp8266.begin(9600);
  // 타이머 인터럽트 선언...
  Timer1.initialize(1000); // 1ms마다 인터럽트 발생
  Timer1.attachInterrupt(mainTimer); // 인터럽트 함수 지정
}
void loop(){
  if (esp8266.available()) {
    esp8266.readBytesUntil('\n', Receive_Mgs, sizeof(Receive_Mgs)); // '\n' 문자가 나타날 때까지 읽습니다.
    handleResponse(Receive_Mgs);
  }
}
void mainTimer(void){
  if(IsTestTime){// 통신이 연결됨.
    if(!IsChangemodeTime){
      if(ChangeModeTime >= CHANGE_MODE_TIME) {
        Sand_Change_Mode(1);
        ChangeModeTime = 0;
        IsChangemodeTime = true;
      }
      ChangeModeTime++;
    }
  }else{
    if(TestTime >= TEST_COMM_TIME) {
      Sand_AT();
      TestTime = 0;
      IsTestTime = true;
    }
    TestTime++;
  }
}

void handleResponse(char* response) {
    // "OK" 응답을 처리하는 코드
  if (strcmp(lastCommand, "AT") == 0) { // 통신 테스트 진행.
    if (strstr(response, "OK") != NULL) {
      Serial.println("통신 테스트 성공");
      IsTestTime = true;
    }else{
      IsTestTime = false;
    }
  } else if (strcmp(lastCommand, "AT+CWMODE=1") == 0) { // 이후 모드를 스테이션 모드로 전환 한다.
    if(strstr(response, "OK") != NULL) {
      IsChangemodeTime = true;
    }else if(strstr(response, "no change") != NULL){
      IsChangemodeTime = true;
    }else{
      IsChangemodeTime = false;
    }
    if(IsChangemodeTime)Sand_Search();
    Serial.println(" 스테이션 모드로 전환 완료");
  } else if (strcmp(lastCommand, "AT+CWLAP") == 0) {
    for (int i = 0; i < sizeof(ssids)/sizeof(ssids[0]); i++) {
      char* ssidPtr = strstr(response, ssids[i]);
      if (ssidPtr != NULL) { // 원하는 AP를 찾았다면...
        char* rssiStartPtr = strchr(ssidPtr, ',') + 1;
        char* rssiEndPtr = strchr(rssiStartPtr, ',');
        char rssi[10];
        strncpy(rssi, rssiStartPtr, rssiEndPtr - rssiStartPtr);
        rssi[rssiEndPtr - rssiStartPtr] = '\0'; // 문자열 종료
        double dist = calculateDistance(atoi(rssi));
        Serial.print("Distance to ");
        Serial.print(rssi);
        Serial.print(": ");
        Serial.println(dist);
      }
    }Sand_Search();
  }
}

void Sand_AT(void){ // 통신 테스트...
  sendCommand("AT");
}

void Sand_Chk_Mode(void){ // 현재 모드 확인.
  sendCommand("AT+CWMODE?");
}

void Sand_Change_Mode(int mode){ // Station 모드 전환.
  if(mode == 1){
    sendCommand("AT+CWMODE=1");
  }else{
    sendCommand("AT+CWMODE=2");
  }
}

void Sand_Search(void){ // 주변 AP 검색..
  sendCommand("AT+CWLAP");
  Serial.println("AT+CWLAP");
}

double calculateDistance(int rssi) {
  int txPower = -30; //1미터 거리에서 RSSI 값
  double n = 2.0; // 이것은 경로 손실 지수이며, 일반적으로 2.7에서 4.3 사이의 범위
  return pow(10, ((double)txPower - rssi) / (10 * n));
}

void sendCommand(const char* command) {
  strncpy(lastCommand, command, sizeof(lastCommand)); // 최근에 보낸 명령을 저장합니다.
  esp8266.write(command);
  esp8266.write("\r\n");
}