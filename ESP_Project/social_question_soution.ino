#include <Wire.h>
#include <WiFi.h>
#include <Arduino.h>
#include <esp_task_wdt.h>
#include <Ticker.h>

#define WDT_TIMEOUT 60
bool wdt_rst_flag = false;

Ticker mainTicker;

void InitTimer(void);
void mainTimer(void);

const char* ssid     = "AP02";  
const char* password = "Gwe1234!#@";

// Wi-Fi 소켓 서버
WiFiServer server(1234);
WiFiClient client;

// 센서 주소 및 핀 설정
#define SENSOR_ADDR 0x44 // SCHT-M30 I2C 주소
const int pressurePin = 34;         // 압력 센서
const int gasPin = 35;              // 가스 센서

// 센서 판별 기준값
const int weight = 100;
const int temper = 3;
const int humid = 70;
const int gas_concentration = 1000;

// 센서 측정 간격 (1초)
const unsigned long readInterval = 1000;
unsigned long one_lastReadTime = 0;
unsigned long two_lastReadTime = 0;
unsigned long three_lastReadTime = 0;
unsigned long four_lastReadTime = 0;

// 센서 측정값 변수
int pressureValue = 0;
float temperature = 0;
float humidity = 0;
int gasValue = 0;

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
  Wire.begin();
  InitTimer();
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  server.begin();
}

void loop() {
  client = server.available();

  if (client) {
    Serial.println("Client connected");

    while (client.connected()) {
      unsigned long currentTime = millis();

      // 주기마다 센서 값 갱신
      if (currentTime - one_lastReadTime >= readInterval) {
        pressureValue = analogRead(pressurePin);
        one_lastReadTime = currentTime;
      }

      if (currentTime - two_lastReadTime >= readInterval) {
        Wire.beginTransmission(SENSOR_ADDR);
        Wire.write(0x2C);
        Wire.write(0x06);
        Wire.endTransmission();
        delay(15);

        Wire.requestFrom(SENSOR_ADDR, 6);
        if (Wire.available() == 6) {
          uint16_t temp_raw = (Wire.read() << 8) | Wire.read();
          Wire.read(); // CRC
          uint16_t hum_raw = (Wire.read() << 8) | Wire.read();
          Wire.read(); // CRC

          temperature = -45 + (175 * (temp_raw / 65535.0));
          humidity = 100 * (hum_raw / 65535.0);
        }

        two_lastReadTime = currentTime;
      }

      if (currentTime - three_lastReadTime >= readInterval) {
        gasValue = analogRead(gasPin);
        three_lastReadTime = currentTime;
      }

      

      if (currentTime - four_lastReadTime >= readInterval) {
        String dataToSend;

        Serial.print("weight : ");
        Serial.print(pressureValue);
        Serial.print(" Temperature: ");
        Serial.print(temperature);
        Serial.print(" °C, Humidity: ");
        Serial.print(humidity);
        Serial.print(" %");
        Serial.print(" gas : ");
        Serial.println(gasValue);
        

        if (pressureValue >= weight &&
            temperature >= temper &&
            humidity >= humid &&
            gasValue >= gas_concentration) {
          dataToSend = "똥 쌈";
        } else {
          dataToSend = "똥 안쌈";
        }

        client.print(dataToSend);
        Serial.println("Sent: " + dataToSend);
        four_lastReadTime = currentTime;
      }
    }

    Serial.print("Client disconnected");
    client.stop();
  }

  if(wdt_rst_flag == true)
  {
    esp_task_wdt_reset();
    wdt_rst_flag = false;
  }
}

