#include <Adafruit_BNO055.h>
#include <Adafruit_Sensor.h>
#include <ArduinoBLE.h>
#include <Wire.h>

// BNO055 (NDOF 모드): 지자기+자이로+가속도 융합으로 자북 기준 절대 방위(0~360°)를 출력
Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x28);
bool bnoConnected = false;
float yaw = 0;
unsigned long lastImuTime = 0;
const unsigned long IMU_INTERVAL = 50; // 50ms (20Hz)

// [센서 1] 핀 변경 (D9, D10)
const int trigPin1 = 9;
const int echoPin1 = 10;

// [센서 2] 핀 변경 (D11, D12)
const int trigPin2 = 11;
const int echoPin2 = 12;

float pre_ch1, pre_ch2;
float ch1, ch2;

unsigned long lastSensorTime = 0;
const unsigned long sensorInterval = 100; // 100ms (10Hz) 고속 측정 주기로 개선

bool bleAvailable = false;

// 로봇 상태 변수
float robotX = 0.0;
float robotY = 0.0;
float robotYaw = 0.0;
// 메가가 POS: 3번째 필드로 알려주는 이상 상태 코드
// 0=정상 1=모터스톨 2=헤딩보정포화 3=바퀴편차
int robotFault = 0;

// BLE 설정
BLEService myService("12345678-1234-1234-1234-1234567890ab");
BLEStringCharacteristic myChar("abcdefab-1234-5678-1234-abcdefabcdef",
                               BLERead | BLEWrite | BLENotify, 100);

// 센서 상태 머신
enum SensorState {
  SENSOR_IDLE,
  SENSOR_TRIG_HIGH,
  SENSOR_WAIT_ECHO,
  SENSOR_MEASURING,
  SENSOR_DONE
};

struct UltrasonicSensor {
  int trigPin;
  int echoPin;
  volatile unsigned long echoStart;
  volatile unsigned long echoEnd;
  volatile bool echoReceived;
  SensorState state;
  unsigned long trigStartTime;
  unsigned long timeoutStart;
  float distance;
};

UltrasonicSensor sensor1;
UltrasonicSensor sensor2;

volatile int activeSensorIndex = 0;

void echoISR1() {
  if (digitalRead(sensor1.echoPin) == HIGH) {
    sensor1.echoStart = micros();
  } else {
    sensor1.echoEnd = micros();
    sensor1.echoReceived = true;
  }
}

void echoISR2() {
  if (digitalRead(sensor2.echoPin) == HIGH) {
    sensor2.echoStart = micros();
  } else {
    sensor2.echoEnd = micros();
    sensor2.echoReceived = true;
  }
}

void startMeasurement(UltrasonicSensor &sensor) {
  sensor.echoReceived = false;
  sensor.echoStart = 0;
  sensor.echoEnd = 0;
  sensor.distance = -1;

  digitalWrite(sensor.trigPin, LOW);
  sensor.state = SENSOR_TRIG_HIGH;
  sensor.trigStartTime = micros();
}

bool updateSensor(UltrasonicSensor &sensor) {
  unsigned long now = micros();

  switch (sensor.state) {
  case SENSOR_IDLE:
    return true;

  case SENSOR_TRIG_HIGH:
    if (now - sensor.trigStartTime >= 2) {
      digitalWrite(sensor.trigPin, HIGH);
      sensor.trigStartTime = now;
      sensor.state = SENSOR_WAIT_ECHO;
    }
    return false;

  case SENSOR_WAIT_ECHO:
    if (now - sensor.trigStartTime >= 10) {
      digitalWrite(sensor.trigPin, LOW);
      sensor.timeoutStart = now;
      sensor.state = SENSOR_MEASURING;
    }
    return false;

  case SENSOR_MEASURING:
    if (sensor.echoReceived) {
      unsigned long duration = sensor.echoEnd - sensor.echoStart;
      sensor.distance = duration * 0.034 / 2.0;
      sensor.state = SENSOR_DONE;
      return true;
    }
    if (now - sensor.timeoutStart > 20000) {
      sensor.distance = -1;
      sensor.state = SENSOR_DONE;
      return true;
    }
    return false;

  case SENSOR_DONE:
    return true;
  }
  return true;
}

enum MeasurePhase { PHASE_IDLE, PHASE_SENSOR1, PHASE_SENSOR2, PHASE_COMPLETE };

MeasurePhase measurePhase = PHASE_IDLE;

void requestMeasurement() {
  if (measurePhase == PHASE_IDLE) {
    measurePhase = PHASE_SENSOR1;
    startMeasurement(sensor1);
  }
}

bool updateMeasurement() {
  switch (measurePhase) {
  case PHASE_IDLE:
    return false;

  case PHASE_SENSOR1:
    if (updateSensor(sensor1)) {
      measurePhase = PHASE_SENSOR2;
      startMeasurement(sensor2);
    }
    return false;

  case PHASE_SENSOR2:
    if (updateSensor(sensor2)) {
      measurePhase = PHASE_COMPLETE;
      return true;
    }
    return false;

  case PHASE_COMPLETE:
    return true;
  }
  return false;
}

void finishMeasurement() {
  measurePhase = PHASE_IDLE;
  sensor1.state = SENSOR_IDLE;
  sensor2.state = SENSOR_IDLE;
}

void handleCommand(String command) { Serial1.println(command); }

void sendCombinedData() {
  if (bleAvailable) {
    BLEDevice central = BLE.central();
    if (central && central.connected()) {
      // 6번째 필드 = 이상 상태 코드.
      // PC 파서는 len(nums) >= 5 로 앞 5개만 쓰므로 구버전 PC 와도 깨지지 않는다.
      String msg = String(robotX, 3) + "," + String(robotY, 3) + "," +
                   String(yaw, 1) + "," + String(ch1, 1) + "," +
                   String(ch2, 1) + "," + String(robotFault) + "\n";
      myChar.writeValue(msg);
    }
  }
}

void readMegaSerial() {
  static String inputBuffer = "";
  while (Serial1.available() > 0) {
    char c = Serial1.read();
    if (c == '\n') {
      inputBuffer.trim();
      if (inputBuffer.length() > 0) {
        Serial.print("Mega 수신 데이터: ");
        Serial.println(inputBuffer);

        if (inputBuffer.startsWith("POS:")) {
          int comma1 = inputBuffer.indexOf(',', 4);
          if (comma1 != -1) {
            // 3번째 필드(이상 상태 코드)는 있을 수도, 없을 수도 있다.
            // toFloat() 은 쉼표에서 멈추므로 tempY 파싱은 양쪽 포맷 다 안전하다.
            int comma2 = inputBuffer.indexOf(',', comma1 + 1);
            float tempX = inputBuffer.substring(4, comma1).toFloat();
            float tempY = inputBuffer.substring(comma1 + 1).toFloat();

            if (!isnan(tempX) && !isinf(tempX) && !isnan(tempY) &&
                !isinf(tempY)) {
              robotX = tempX;
              robotY = tempY;
              if (comma2 != -1) {
                int f = inputBuffer.substring(comma2 + 1).toInt();
                if (f != robotFault) {
                  Serial.print("[FAULT] 메가 이상 상태 코드: ");
                  Serial.println(f);
                }
                robotFault = f;
              }
              sendCombinedData();
            }
          }
        }
      }
      inputBuffer = "";
    } else if (c != '\r') {
      inputBuffer += c;
    }
  }
}

// ── BLE 수신 명령 처리 ────────────────────────────────
void handleBLECommand() {
  if (!myChar.written())
    return;

  String command = myChar.value();
  command.trim();
  if (command.length() == 0)
    return;

  Serial.print("BLE 수신 데이터: ");
  Serial.println(command);
  handleCommand(command);
}

void updateIMUAndSend() {
  unsigned long now = millis();
  if (now - lastImuTime >= IMU_INTERVAL) {
    lastImuTime = now;
    if (bnoConnected) {
      // orientation.x = 헤딩(0~360°, 시계방향 증가) — 기존 yaw 규약과 동일
      sensors_event_t event;
      bno.getEvent(&event);
      float next_yaw = event.orientation.x;
      if (!isnan(next_yaw) && !isinf(next_yaw) && next_yaw >= 0.0 &&
          next_yaw < 360.0) {
        yaw = next_yaw;

        // 메가로 실시간 각도 전송 (115200bps이므로 오버헤드 미미)
        Serial1.print("YAW:");
        Serial1.println(yaw, 1);
      }

      // PC 디버깅용 출력 (USB 시리얼 모니터)
      static uint32_t lastDebugTime = 0;
      if (millis() - lastDebugTime >= 500) {
        lastDebugTime = millis();
        uint8_t sys, gyro, accel, mag;
        sys = gyro = accel = mag = 0;
        bno.getCalibration(&sys, &gyro, &accel, &mag); // 0:미보정 ~ 3:완료
        Serial.print("[IMU] YAW: ");
        Serial.print(yaw, 1);
        Serial.print(" [Calib Sys:");
        Serial.print(sys);
        Serial.print(" G:");
        Serial.print(gyro);
        Serial.print(" A:");
        Serial.print(accel);
        Serial.print(" M:");
        Serial.print(mag);
        Serial.println("]");
      }
    }
  }
}

void setup() {
  Serial.begin(9600);
  Serial1.begin(115200); // 메가와 고속 통신 설정

  // ★ 나노 33 BLE는 네이티브 USB라 부팅이 아주 빨라서 시리얼 모니터를 켜기 전에
  // setup()이 끝나버립니다. 시리얼 모니터가 연결될 때까지 최대 3초간 기다려주는
  // 코드를 추가합니다.
  unsigned long startWait = millis();
  while (!Serial && (millis() - startWait < 3000))
    ;
  delay(500);

  Wire.begin();
  Wire.setClock(50000);

  // ★ I2C 스캐너 기능 추가: 연결된 모든 I2C 장치 주소 찾기
  Serial.println("--- I2C 장치 스캔 시작 ---");
  byte i2cCount = 0;
  for (byte addr = 8; addr < 120; addr++) {
    Wire.beginTransmission(addr);
    byte error = Wire.endTransmission();
    if (error == 0) {
      Serial.print("-> I2C 장치 발견! 주소: 0x");
      Serial.println(addr, HEX);
      i2cCount++;
    } else if (error == 4) {
      Serial.print("-> 주소 0x");
      Serial.print(addr, HEX);
      Serial.println("에서 에러 4 발생");
    }
  }
  if (i2cCount == 0) {
    Serial.println("[경고] 발견된 I2C 장치가 없습니다! (배선, GND 공통 연결, "
                   "SDA/SCL 확인 필요)");
  }
  Serial.println("--------------------------");

  // 0x28 주소로 먼저 시도하고, 실패하면 0x29 주소(ADR 핀 HIGH)로 재시도
  bnoConnected = bno.begin();
  if (!bnoConnected) {
    Serial.println("주소 0x28 연결 실패. 주소 0x29로 재시도합니다...");
    bno = Adafruit_BNO055(55, 0x29);
    bnoConnected = bno.begin();
  }

  if (!bnoConnected) {
    Serial.println("BNO055 최종 연결 실패! (SDA/SCL 배선과 주소 확인 필요)");
  } else {
    bno.setExtCrystal(true); // 외부 크리스탈 사용으로 정밀도 향상
    Serial.println("BNO055 연결 성공! (NDOF 절대 방위 모드)");
    Serial.println("Calib M:3 이 될 때까지 8자를 그리며 움직이면 방위가 정확해집니다.");
  }

  if (!BLE.begin()) {
    Serial.println("BLE 초기화 실패! BLE 없이 주행 테스트를 계속 진행합니다.");
    bleAvailable = false;
  } else {
    Serial.println("BLE 초기화 성공.");
    bleAvailable = true;
  }

  pinMode(trigPin1, OUTPUT);
  pinMode(echoPin1, INPUT);
  pinMode(trigPin2, OUTPUT);
  pinMode(echoPin2, INPUT);

  sensor1.trigPin = trigPin1;
  sensor1.echoPin = echoPin1;
  sensor1.state = SENSOR_IDLE;
  sensor1.echoReceived = false;

  sensor2.trigPin = trigPin2;
  sensor2.echoPin = echoPin2;
  sensor2.state = SENSOR_IDLE;
  sensor2.echoReceived = false;

  attachInterrupt(digitalPinToInterrupt(echoPin1), echoISR1, CHANGE);
  attachInterrupt(digitalPinToInterrupt(echoPin2), echoISR2, CHANGE);

  if (bleAvailable) {
    BLE.setLocalName("Nano_BLE");
    BLE.setAdvertisedService(myService);
    myService.addCharacteristic(myChar);
    BLE.addService(myService);

    myChar.writeValue(""); // 초기값 클리어
    myChar.written();      // written() 플래그 소모

    BLE.advertise();
    Serial.println("PC 연결 대기 중...");
  } else {
    Serial.println("BLE가 비활성화된 상태로 주행 대기 중...");
  }
}

void loop() {
  if (bleAvailable) {
    BLE.poll();
  }

  updateIMUAndSend(); // IMU 갱신 및 메가 송신

  if (Serial && Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    if (command.length() > 0) {
      Serial.print("USB 수신 데이터: ");
      Serial.println(command);
      handleCommand(command);
    }
  }

  readMegaSerial();

  if (bleAvailable) {
    BLEDevice central = BLE.central();

    if (central) {
      Serial.print("PC 연결됨: ");
      Serial.println(central.address());

      while (central.connected()) {
        BLE.poll();
        // Serial.println("------------------");
        if (Serial && Serial.available() > 0) {
          String command = Serial.readStringUntil('\n');
          command.trim();
          if (command.length() > 0) {
            Serial.print("USB 수신 데이터: ");
            Serial.println(command);
            handleCommand(command);
          }
        }

        readMegaSerial();
        updateIMUAndSend(); // BLE 기기가 연결되어 작동할 때도 계속 YAW를 메가에
                            // 전송

        unsigned long currentMillis = millis();

        if (measurePhase == PHASE_IDLE &&
            currentMillis - lastSensorTime >= sensorInterval) {
          lastSensorTime = currentMillis;
          pre_ch1 = ch1;
          pre_ch2 = ch2;
          requestMeasurement();
        }

        if (updateMeasurement()) {
          ch1 = sensor1.distance;
          ch2 = sensor2.distance;
          // Serial.println(ch2);
          sendCombinedData();
          finishMeasurement();
        }

        handleBLECommand(); // ← 별도 함수로 분리 및 필터링 적용
      }

      // 연결 종료 시 플래그 클리어
      myChar.writeValue("");
      myChar.written();
      Serial.println("연결 종료");
    }
  }
}