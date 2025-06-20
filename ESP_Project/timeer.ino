#include <Arduino.h>
#include <esp_task_wdt.h>
#include <WiFi.h>
#include <Ticker.h>

// 변수들...
#define WDT_TIMEOUT 60
bool wdt_rst_flag = false;

// 함수선언 부 
void InitTimer(void);
void mainTimer(void);
////////////////////////////////////////////////////////////////////////////////////
// 1msec Timer, setup, loop
////////////////////////////////////////////////////////////////////////////////////
void InitTimer(void)
{
  mainTicker.attach_ms(1, mainTimer);

  esp_task_wdt_init(WDT_TIMEOUT, true);
  esp_task_wdt_add(NULL);
}
void mainTimer(void)
{
    // 여기서 타이머를 제어 합니다.
    wdt_rst_flag = true;
}
void setup() {
    Serial.begin(115200);
     InitTimer();
}
void loop() {
    sensorValue = analogRead(sensorPin);
    Serial.print("SEN0571 : ");
    Serial.println(sensorValue);
    delay(1000);

  if(wdt_rst_flag == true)
  {
    esp_task_wdt_reset();
    wdt_rst_flag = false;
  }
}