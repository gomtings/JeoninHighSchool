1. BNO055 3D 각도(오일러 각도) 및 칼리브레이션 테스트 지자기와
    자이로가 융합된 Yaw,
    Pitch,
    Roll 값과 센서의 캘리브레이션 단계(0 ~3) 를 실시간 확인하는 코드입니다.

#include <Adafruit_BNO055.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>

    // BNO055 기본 I2C 주소 0x28
    Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x28);

void setup() {
  Serial.begin(9600);
  while (!Serial)
    ;

  if (!bno.begin()) {
    Serial.println("BNO055 감지 실패! 배선(SDA/SCL)과 주소를 확인하세요.");
    while (1)
      ;
  }

  bno.setExtCrystal(true); // 외부 크리스탈 사용으로 정밀도 향상
  Serial.println("BNO055 오일러 각도 및 칼리브레이션 테스트 시작");
}

void loop() {
  // 1. 각도 데이터 읽기
  sensors_event_t event;
  bno.getEvent(&event);

  // 2. 캘리브레이션 상태 읽기 (Sys, Gyro, Accel, Mag / 0:미보정 ~ 3:완료)
  uint8_t system, gyro, accel, mag;
  system = gyro = accel = mag = 0;
  bno.getCalibration(&system, &gyro, &accel, &mag);

  // 시리얼 출력
  Serial.print("Yaw: ");
  Serial.print(event.orientation.x, 1);
  Serial.print(" | Pitch: ");
  Serial.print(event.orientation.y, 1);
  Serial.print(" | Roll: ");
  Serial.print(event.orientation.z, 1);

  Serial.print(" [Calib -> Sys:");
  Serial.print(system);
  Serial.print(" G:");
  Serial.print(gyro);
  Serial.print(" A:");
  Serial.print(accel);
  Serial.print(" M:");
  Serial.print(mag);
  Serial.println("]");

  delay(100);
}

2. BNO055 순수 가속도(Linear Acceleration) 측정 테스트중력
    가속도(1g) 를 제외하고,
    로봇이 실제로 가속 / 감속할 때의 순수 움직임만 측정하는 테스트입니다.

#include <Adafruit_BNO055.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>

                         Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x28);

void setup() {
  Serial.begin(9600);
  if (!bno.begin()) {
    Serial.println("BNO055 연결 실패!");
    while (1)
      ;
  }
  bno.setExtCrystal(true);
  Serial.println("BNO055 순수 가속도(Linear Accel) 테스트 시작");
}

void loop() {
  // 중력(Gravitational Vector)이 제거된 선형 가속도 벡터 읽기 (m/s^2)
  imu::Vector<3> linAccel = bno.getVector(Adafruit_BNO055::VECTOR_LINEARACCEL);

  Serial.print("Accel X: ");
  Serial.print(linAccel.x(), 2);
  Serial.print(" m/s^2 | Y: ");
  Serial.print(linAccel.y(), 2);
  Serial.print(" m/s^2 | Z: ");
  Serial.print(linAccel.z(), 2);
  Serial.println(" m/s^2");

  delay(100);
}

3. BNO055 쿼터니언(Quaternion)
데이터 테스트 라디안 / 오일러 각도의 Gimbal Lock(짐벌락)
문제를 방지하고,
    ROS나 고급 제어 알고리즘으로 데이터를 넘길 때 사용하는 사원수(w, x, y, z)
출력 코드입니다.

#include <Adafruit_BNO055.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>

    Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x28);

void setup() {
  Serial.begin(9600);
  if (!bno.begin()) {
    Serial.println("BNO055 연결 실패!");
    while (1)
      ;
  }
  bno.setExtCrystal(true);
  Serial.println("BNO055 쿼터니언(Quaternion) 테스트 시작");
}

void loop() {
  // 쿼터니언 읽기
  imu::Quaternion quat = bno.getQuat();

  Serial.print("W: ");
  Serial.print(quat.w(), 4);
  Serial.print(" | X: ");
  Serial.print(quat.x(), 4);
  Serial.print(" | Y: ");
  Serial.print(quat.y(), 4);
  Serial.print(" | Z: ");
  Serial.println(quat.z(), 4);

  delay(100);
}

4. BMP280 기압, 온도 및 수직 고도(Altitude)
테스트
모듈에 함께 포함된 BMP280을 사용하여 현재 기온, 기압,
    상대 고도를 정밀 측정하는 코드입니다.

#include <Adafruit_BMP280.h>
#include <Wire.h>

    // 모듈에 따라 I2C 주소가 0x76 또는 0x77 입니다.
    Adafruit_BMP280 bmp;

void setup() {
  Serial.begin(9600);
  Serial.println("BMP280 기압/고도 센서 테스트 시작");

  // 기본 주소 0x76으로 시도
  if (!bmp.begin(0x76)) {
    // 실패 시 0x77로 재시도
    if (!bmp.begin(0x77)) {
      Serial.println("BMP280 감지 실패! I2C 배선 및 주소를 확인하세요.");
      while (1)
        ;
    }
  }

  /* 서빙로봇/실내 고도 측정용 튜닝 설정 */
  bmp.setSampling(
      Adafruit_BMP280::MODE_NORMAL,    // 노말 측정 모드
      Adafruit_BMP280::SAMPLING_X2,    // 온도 오버샘플링
      Adafruit_BMP280::SAMPLING_X16,   // 기압 오버샘플링 (정밀도 향상)
      Adafruit_BMP280::FILTER_X16,     // IIR 필터 적용 (진동 노이즈 제거)
      Adafruit_BMP280::STANDBY_MS_63); // 63ms 대기시간
}

void loop() {
  float temp = bmp.readTemperature();
  float pressure = bmp.readPressure() / 100.0F; // Pa -> hPa 변환
  // 해수면 표준 기압 1013.25hPa 기준 고도 계산
  float altitude = bmp.readAltitude(1013.25);

  Serial.print("온도: ");
  Serial.print(temp, 1);
  Serial.print(" °C | ");
  Serial.print("기압: ");
  Serial.print(pressure, 2);
  Serial.print(" hPa | ");
  Serial.print("추정 고도: ");
  Serial.print(altitude, 2);
  Serial.println(" m");

  delay(200);
}