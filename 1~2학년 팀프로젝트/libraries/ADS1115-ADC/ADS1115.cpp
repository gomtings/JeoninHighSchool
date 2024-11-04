#include <ADS1115.h>
#include <Wire.h> // I2C 라이브러리

ADS1115::ADS1115()
{
  Wire.begin(21,22);
  ScanI2CDevice();
}

void ADS1115::ScanI2CDevice(void) // I2C 주소 검색 
{
  byte error, address;
  int nDevices;

  Serial.print("\nScanning...");

  nDevices = 0;
  for(address = 1; address < 127; address++ ) 
  {
    Wire.beginTransmission(address);// I2C 장치 주소 설정 
    error = Wire.endTransmission(); //데이터 전송 , 데이터 전달 성공 여부를 반환 한다.
    /*0 :전송성공 1 : 버퍼의 크기가 허용된 범위 초과 2 : 해당 주소값을 가진 기기가 없을경우 3 : 데이터 전송이 실패 4: 0~3번 이 아닌 다른 오류 발생 */

    if (error == 0)
    {
      Serial.print("\nI2C device found at address 0x"); // 디바이스 검색 성공? 
      if (address<16) 
        Serial.print("0");
      Serial.print(address,HEX); // 검색된 주소 출력 
      Serial.print("  !");
      nDevices++;
    }
    else if (error==4) 
    {
      Serial.print("\nUnknow error at address 0x"); // 알수없는 디바이스 
      if (address<16) 
        Serial.print("0");
      Serial.print(address,HEX);
    }    
  }
  if (nDevices == 0)
    Serial.print("\nNo I2C devices found"); // 디바이스 장치 없음.
  else
    Serial.print("\ndone");
}
