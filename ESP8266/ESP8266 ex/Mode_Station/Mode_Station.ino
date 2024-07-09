#include <SoftwareSerial.h>
#include <TimerOne.h> // TimerOne 라이브러리
#define FILTER_SIZE 5
SoftwareSerial esp8266(2, 3); // RX, TX
// AP의 위치를 나타내는 구조체
struct AP {
  char* ssid;
  double x; // AP의 x 좌표
  double y; // AP의 y 좌표
};
// AP 위치 정보 (예시)
AP aps[] = {
  {"Jeonin01", 0.0, 0.0},
  {"Jeonin02", 0.0, 10.0},
  {"Jeonin03", 10.0, 0.0},
  {"Jeonin04", 10.0, 10.0}
};
//char* ssids[] = {"Solimatics", "Solimatics", "Solimatics", "Solimatics"};
char* ssids[] = {"Jeonin01", "Jeonin02", "Jeonin03", "Jeonin04"};
char Receive_Mgs[512]; // 충분한 크기의 버퍼를 할당합니다.
char lastCommand[32]; // 최근에 보낸 명령을 저장할 변수
double distances[sizeof(ssids)/sizeof(ssids[0])];// 메인 루프 또는 함수 내에서
// 이동 평균 필터
int rssiFilterIndex = 0;
int rssiValues[FILTER_SIZE] = {0};
bool validDistances = false; // 값 존재 여부 체크

#define TEST_COMM_TIME 100 // 통신 테스트
int32_t TestTime = 0;
bool IsTestTime = false;
#define CHANGE_MODE_TIME 1000 // 스테이션 모드 전환
int32_t ChangeModeTime = 0;
bool IsChangemodeTime = false;
#define SEARCH_TIME 1000 // 스테이션 모드 전환
int32_t SearchTime = 0;
bool IsSearchTime = false;

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
    }else{
      if(SearchTime >= SEARCH_TIME) {
        Sand_Search();
        SearchTime = 0;
        IsSearchTime = true;
      }
      SearchTime++;
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
    Serial.println(" 스테이션 모드로 전환 완료");
  } else if (strcmp(lastCommand, "AT+CWLAP") == 0) {
    // 메인 루프 또는 함수 내에서
    for (int i = 0; i < sizeof(ssids)/sizeof(ssids[0]); i++) {
      char* ssidPtr = strstr(response, ssids[i]);
      if (ssidPtr != NULL) { // 원하는 AP를 찾았다면...
        char* rssiStartPtr = strchr(ssidPtr, ',') + 1;
        char* rssiEndPtr = strchr(rssiStartPtr, ',');
        char rssiStr[10];
        strncpy(rssiStr, rssiStartPtr, rssiEndPtr - rssiStartPtr);
        rssiStr[rssiEndPtr - rssiStartPtr] = '\0'; // 문자열 종료
        int rssi = atoi(rssiStr);
        // RSSI 값을 필터링
        int filteredRssi = filterRssi(rssi);
        // 각 AP로부터의 거리를 계산하고 배열에 저장
        distances[i] = calculateDistance(filteredRssi);
      }
    }
    validDistances = distances[0] != 0.00 && distances[1] != 0.00 && distances[2] != 0.00 && distances[3] != 0.00;
    if (validDistances) {
      double userX, userY;
      calculatePosition(&userX, &userY, aps, distances, sizeof(aps)/sizeof(aps[0]));
      Serial.print("User position: X=");
      Serial.print(userX);
      Serial.print(", Y=");
      Serial.println(userY);
    } else {
      Serial.println("Error: Not all distances are valid.");
    }
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
}

void Disconnect(void){ // AP 연결 해제
  sendCommand("AT+CWQAP");
}

void GetVersion(void){ // ESP01 의 FW 버전을 조회함.
  sendCommand("AT+GMR");
}

void GetVersion(void){ // AP 연결 해제
  sendCommand("AT+GMR");
}

void Reboot(void){ // AP 연결 해제
  sendCommand("AT+RST");
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
// RSSI 값을 필터링하는 함수
int filterRssi(int newRssi) {
  // 새로운 RSSI 값을 배열에 추가
  rssiValues[rssiFilterIndex] = newRssi;
  
  // 이동 평균 계산
  int sum = 0;
  for (int i = 0; i < FILTER_SIZE; i++) {
    sum += rssiValues[i];
  }
  int filteredRssi = sum / FILTER_SIZE;
  
  // 인덱스 업데이트
  rssiFilterIndex = (rssiFilterIndex + 1) % FILTER_SIZE;
  
  return filteredRssi;
}
// AP의 위치와 사용자로부터의 거리를 바탕으로 사용자의 위치를 계산하는 함수
void calculatePosition(double* userX, double* userY, AP* aps, double* distances, int numAps) {
  // 여기서는 간단한 2차원 삼각 측량법을 사용합니다.
  // 실제 구현에서는 더 정교한 알고리즘이 필요할 수 있습니다.
  
  // AP 위치와 거리를 바탕으로 두 원의 교차점 계산
  // AP1과 AP2를 사용하여 첫 번째 교차점 계산
  double A = 2 * (aps[1].x - aps[0].x);
  double B = 2 * (aps[1].y - aps[0].y);
  double C = pow(distances[0], 2) - pow(distances[1], 2) - pow(aps[0].x, 2)
             + pow(aps[1].x, 2) - pow(aps[0].y, 2) + pow(aps[1].y, 2);
  // AP2와 AP3를 사용하여 두 번째 교차점 계산
  double D = 2 * (aps[2].x - aps[1].x);
  double E = 2 * (aps[2].y - aps[1].y);
  double F = pow(distances[1], 2) - pow(distances[2], 2) - pow(aps[1].x, 2)
             + pow(aps[2].x, 2) - pow(aps[1].y, 2) + pow(aps[2].y, 2);
  
  // 교차점 계산
  *userX = (C * E - F * B) / (A * E - B * D);
  *userY = (C * D - A * F) / (B * D - A * E);
}