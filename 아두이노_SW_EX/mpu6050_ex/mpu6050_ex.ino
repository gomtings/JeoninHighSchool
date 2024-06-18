#include <Wire.h>

const int MPU = 0x68;
int AcX, AcY, AcZ, Tmp, GyX, GyY, GyZ;

void setup() {
  Wire.begin();
  Wire.beginTransmission(MPU);
  Wire.write(0x6B);
  Wire.write(0);
  Wire.endTransmission(true);
  Serial.begin(9600);
}

void loop() {
  get6050();
  
  // 가속도계의 XYZ축 출력 (0부터 360도로 변환)
  Serial.print("AcX: ");
  Serial.print(map(AcX, -32768, 32767, 0, 360));
  Serial.print(", AcY: ");
  Serial.print(map(AcY, -32768, 32767, 0, 360));
  Serial.print(", AcZ: ");
  Serial.println(map(AcZ, -32768, 32767, 0, 360));

  delay(15);
}

void get6050() {
  Wire.beginTransmission(MPU);
  Wire.write(0x3B);
  Wire.endTransmission(false);
  Wire.requestFrom(MPU, 14, true);
  AcX = Wire.read() << 8 | Wire.read();
  AcY = Wire.read() << 8 | Wire.read();
  AcZ = Wire.read() << 8 | Wire.read();
  Tmp = Wire.read() << 8 | Wire.read();
  GyX = Wire.read() << 8 | Wire.read();
  GyY = Wire.read() << 8 | Wire.read();
  GyZ = Wire.read() << 8 | Wire.read();
  delay(1000);
}