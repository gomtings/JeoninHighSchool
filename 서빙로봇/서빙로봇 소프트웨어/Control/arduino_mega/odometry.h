#ifndef _ODOMETRY_H_
#define _ODOMETRY_H_

// =====================================================================
//  odometry.h  —  메카넘 휠 오도메트리 (엔코더 + BNO055 IMU 융합)
//
//  현재 코드 구조에 맞춘 설계:
//   - 엔코더: RISING 단방향 카운트 (부호 없음 → 방향은 isTurning으로 판별)
//   - IMU yaw: BNO055(나노 33 BLE)에서 0~360도로 이미 계산된 값 사용
//   - 호출 위치: loop()의 100ms 엔코더 처리 블록 내부
// =====================================================================

// ── 물리 상수 (config.h와 동일) ──────────────────────────────────────
static const float ODO_R = 0.03f;    // 바퀴 반지름 (m)
static const float ODO_CPR = 411.3f; // Counts Per Revolution 보정 CPR = 617 ×
                                     // (시리얼 X값 / 실제 이동거리)
// 1펄스당 이동 거리 (m) = 2pi * r / CPR    // f=플로트인데 굳이 한번 더 하는
// 이유는 변수가 확실하게 뭔지 구별하기 위해
static const float ODO_DIST_PER_PULSE = (2.0f * PI * ODO_R) / ODO_CPR;

// ── 위치 구조체 ───────────────────────────────────────────────────────
struct OdoPose {
  float x = 0.0f;     // 월드 X 좌표 (m)
  float y = 0.0f;     // 월드 Y 좌표 (m)
  float theta = 0.0f; // 방향각 (라디안), IMU yaw에서 변환
};

OdoPose pose;

// ── 리셋 함수 ─────────────────────────────────────────────────────────
void resetOdometry() {
  pose.x = 0.0f;
  pose.y = 0.0f;
  pose.theta = 0.0f;
}

// =====================================================================
//  updateOdometry()
//
//  [호출 위치]
//    loop()의 "if (!isTurning && (now - lastSpeedTime >= 100))" 블록에서
//    cA/cB/cC/cD 복사 직후에 호출하세요. (encXX 리셋 전)
//
//  [매개변수]
//    pA, pB, pC, pD  : 100ms 동안 누적된 각 바퀴의 펄스 수 (전진 +, 후진 -)
//    currentYawDeg   : BNO055에서 계산된 현재 yaw 값 (0~360도)
//    turning         : 제자리 회전 중이면 true
// =====================================================================
void updateOdometry(long pA, long pB, long pC, long pD, float currentYawDeg,
                    bool turning) {

  // 제자리 회전 중에는 슬립 오차를 피하기 위해 갱신하지 않음
  if (turning)
    return;

  // ── ① 각 바퀴 이동 거리 (m) ──────────────────────────────────────
  float dA = pA * ODO_DIST_PER_PULSE;
  float dB = pB * ODO_DIST_PER_PULSE;
  float dC = pC * ODO_DIST_PER_PULSE;
  float dD = pD * ODO_DIST_PER_PULSE;

  // ── ② 메카넘 순기구학 → 로봇 로컬 변위 (m) ──────────────────────
  //  바퀴 레이아웃 (config.h 기준):
  //    A(앞좌)  B(앞우)
  //    C(뒤좌)  D(뒤우)
  float dx_local = (dA + dB + dC + dD) / 4.0f;
  float dy_local = (dA - dB - dC + dD) / 4.0f;

  // ── ③ IMU yaw → 라디안 변환 ──────────────────────────────────────
  // 현재 코드: 시계방향이 yaw 증가 → 수학적 반시계 기준으로 부호 반전
  float thetaRad = -currentYawDeg * DEG_TO_RAD;

  // ── ④ 로컬 변위 → 월드 좌표계 변환 ──────────────────────────────
  float cosT = cos(thetaRad);
  float sinT = sin(thetaRad);

  pose.x += dx_local * cosT - dy_local * sinT;
  pose.y += dx_local * sinT + dy_local * cosT;
  pose.theta = thetaRad; // 각도는 IMU 값을 직접 사용 (더 정확)
}

// ── 시리얼 출력 헬퍼 ──────────────────────────────────────────────────
void printOdometry() {
  Serial.print(F("ODO | X: "));
  Serial.print(pose.x, 3);
  Serial.print(F("m  Y: "));
  Serial.print(pose.y, 3);
  Serial.print(F("m  Heading: "));
  Serial.print(pose.theta * RAD_TO_DEG, 1);
  Serial.println(F("deg"));
}

#endif // _ODOMETRY_H_
