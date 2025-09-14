// #include <Wire.h>

// #define SENSOR_ADDR 0x44 // SCHT-M30 기본 I2C 주소

// const int sensorPin = 37; // ESP32의 아날로그 입력 핀
// int another_sensorValue = 0;

// const int another_sensorPin = 35;

// void setup() {
//     Serial.begin(115200);
//     Wire.begin();
// }

// void loop() {
//     Wire.beginTransmission(SENSOR_ADDR);
//     Wire.write(0x2C); // 측정 명령
//     Wire.write(0x06);
//     Wire.endTransmission();

//     // 압력 센서

//     int sensorValue = analogRead(sensorPin);
//     Serial.print("value : ");
//     Serial.println(sensorValue);
//     delay(500);

//     Wire.requestFrom(SENSOR_ADDR, 6);
//     if (Wire.available() == 6) {
//         uint16_t temp_raw = (Wire.read() << 8) | Wire.read();
//         Wire.read(); // CRC 무시
//         uint16_t hum_raw = (Wire.read() << 8) | Wire.read();
//         Wire.read(); // CRC 무시

//         float temperature = -45 + (175 * (temp_raw / 65535.0));
//         float humidity = 100 * (hum_raw / 65535.0);

//         Serial.print("Temperature: ");
//         Serial.print(temperature);
//         Serial.print(" °C, Humidity: ");
//         Serial.print(humidity);
//         Serial.println(" %");
//     }

//     // 가스 감지 센서

//     another_sensorValue = analogRead(another_sensorPin);
//     Serial.print("SEN0571 : ");
//     Serial.println(another_sensorValue);

//     delay(2000);
// }

// 같은 주기를 가지고 센서값 출력
#include <Wire.h>
#include <WiFi.h>

#define SENSOR_ADDR 0x44 // SCHT-M30 기본 I2C 주소

const int sensorPin = 34;          // 압력 센서
const int another_sensorPin = 35;  // 가스 감지 센서

unsigned long one_lastReadTime = 0;
unsigned long two_lastReadTime = 0;
unsigned long three_lastReadTime = 0;
unsigned long four_lastReadTime = 0;
const unsigned long readInterval = 1000; // 모든 센서 동일 주기로 1초마다 읽기

const int weight = 100;
const int temper = 36;
const int humid = 70;
const int gas_concentration = 1000;

void setup() {
  Serial.begin(115200);
  Wire.begin();
}
int pressureValue = 0;
float temperature = 0;
float humidity = 0;
int gasValue = 0;

void loop() {
  unsigned long currentTime = millis();

  if (currentTime - one_lastReadTime >= readInterval) {
    pressureValue = analogRead(sensorPin);
    one_lastReadTime = currentTime;
  }

  if (currentTime - two_lastReadTime >= readInterval) {
    Wire.beginTransmission(SENSOR_ADDR);
    Wire.write(0x2C);
    Wire.write(0x06);
    Wire.endTransmission();
    delay(15); // 측정 대기

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
    gasValue = analogRead(another_sensorPin);
    three_lastReadTime = currentTime;
  }

  if (currentTime - four_lastReadTime >= readInterval) {
    Serial.print("Pressure: ");
    Serial.print(pressureValue);
    Serial.print(" | Temperature: ");
    Serial.print(temperature);
    Serial.print(" °C | Humidity: ");
    Serial.print(humidity);
    Serial.print(" % | Gas: ");
    Serial.println(gasValue);
    
    if (pressureValue >= weight &&
        temperature >= temper &&
        humidity >= humid &&
        gasValue >= gas_concentration) {
      Serial.println("똥 쌈");
    }

    four_lastReadTime = currentTime;
  }
}

//처음에는 WiFi를 사용하기 위한 WiFi헤더를 포함하고 있다.
// #include <WiFi.h>
// #include <Adafruit_NeoPixel.h>
 
  // #define LED_PIN   16      // 데이터 핀 (GPIO 5)
  // #define LED_COUNT  1      // LED 하나만 사용

// Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);

// // 그 다음으로 WiFi의 SSID와 암호 변수를 저장한다. const이니까...상수인가?!
// // 잡담이지만 define이 아니라 const를 쓰는 이유는 뭘까요?? 네...pointer쓰려고.ㅎㅎ
// const char* ssid     = "AP02";
// const char* password = "Gwe1234!#@";

// // 이제 서버를 생성한다. 80은 포트번호.
// WiFiServer server(80);

// void setup()
// {
//     Serial.begin(115200);
//     pinMode(5, OUTPUT);      // set the LED pin mode

//     delay(10);

//     // We start by connecting to a WiFi network

//     Serial.println();
//     Serial.println();
//     Serial.print("Connecting to ");
//     Serial.println(ssid);

//     // WiFi 접속을 시작한다.
//     WiFi.begin(ssid, password);

//     // WiFi의 상태가 연결상태가 아니면 500ms간격으로 점 찍는다.
//     // 즉 begin을 하면 사용자가 어떤 제지를 할 때까지는 계속 접속을 시도한다.
//     while (WiFi.status() != WL_CONNECTED) {
//         delay(500);
//         Serial.print(".");
//     }

//     Serial.println("");
//     Serial.println("WiFi connected.");
//     Serial.println("IP address: ");
//     // WiFi에 연결이되고 DHCP로 IP를 받아오면 WiFi.localIP()확인할 수 있다.
//     Serial.println(WiFi.localIP());
    
//     // 위에서 선언한 서버를 시작한다.
//     server.begin();
// }

// // ESP32를 PC와 소켓(TCP/IP) 통신, 

// int value = 0;

// void loop(){
//  // 수신을 대기한다.
//  WiFiClient client = server.available();   // listen for incoming clients

//  // 만약 client가 있다면,
//   if (client) {                             // if you get a client,
//     Serial.println("New Client.");           // print a message out the serial port
//     String currentLine = "";                // make a String to hold incoming data from the client
//     while (client.connected()) {            // loop while the client's connected
//       if (client.available()) {             // if there's bytes to read from the client,
//         char c = client.read();             // read a byte, then
//         Serial.write(c);                    // print it out the serial monitor
//         if (c == '\n') {                    // if the byte is a newline character

//           // if the current line is blank, you got two newline characters in a row.
//           // that's the end of the client HTTP request, so send a response:
//           // 접속한 클라이언트에서의 명령이 없다면 헤더를 출력
//           if (currentLine.length() == 0) {
//             // HTTP headers always start with a response code (e.g. HTTP/1.1 200 OK)
//             // and a content-type so the client knows what's coming, then a blank line:
//             client.println("HTTP/1.1 200 OK");
//             client.println("Content-type:text/html");
//             client.println();

//             // the content of the HTTP response follows the header:
//             // 클라이언트 화면에 문자열 2개를 출력한다.
//             client.print("Click <a href=\"/H\">here</a> to turn the LED on pin 5 on.<br>");
//             client.print("Click <a href=\"/L\">here</a> to turn the LED on pin 5 off.<br>");

//             // The HTTP response ends with another blank line:
//             client.println();
//             // break out of the while loop:
//             break;
//           } else {    // if you got a newline, then clear currentLine:
//             currentLine = "";
//           }
//         } else if (c != '\r') {  // if you got anything else but a carriage return character,
//           currentLine += c;      // add it to the end of the currentLine
//         }

//         // Check to see if the client request was "GET /H" or "GET /L":
//         // request가 H인지 L인지에 따라 명령울 수행한다.
//         if (currentLine.endsWith("GET /H")) {
//           // 색상 3번 바꾸기
//             setColor(255, 0, 0);  // 빨강
//             delay(1000);

//             setColor(0, 255, 0);  // 초록
//             delay(1000);

//             setColor(0, 0, 255);  // 파랑
//             delay(1000);

//                 // 
//         }
//         if (currentLine.endsWith("GET /L")) {
//           setColor(0, 0, 0);              // GET /L turns the LED off
//         }
//       }
//     }
//     // close the connection:
//     // 처리가 끝나면 client와의 연결을 끊는다.
//     client.stop();
//     Serial.println("Client Disconnected.");
//   }
// }

// void setColor(uint8_t r, uint8_t g, uint8_t b) {
//   strip.setPixelColor(0, strip.Color(r, g, b));
//   strip.show();
// }

// Import required libraries
// 필수 라이브러리
// #include <WiFi.h>
// #include <AsyncTCP.h>
// #include <ESPAsyncWebServer.h>
// #include <Adafruit_NeoPixel.h>

// // Wi-Fi 설정
// const char* ssid     = "AP02";
// const char* password = "Gwe1234!#@";

// // RGB NeoPixel 설정
// #define RGB_PIN 16
// #define NUM_PIXELS 1
// Adafruit_NeoPixel rgbLed(NUM_PIXELS, RGB_PIN, NEO_GRB + NEO_KHZ800);

// bool ledState = 0;  // false = OFF, true = ON

// AsyncWebServer server(80);
// AsyncWebSocket ws("/ws");

// // 웹페이지 HTML
// const char index_html[] PROGMEM = R"rawliteral(
// <!DOCTYPE HTML><html>
// <head>
//   <title>ESP Web Server</title>
//   <meta name="viewport" content="width=device-width, initial-scale=1">
//   <link rel="icon" href="data:,">
//   <style>
//   html { font-family: Arial, sans-serif; text-align: center; }
//   h1 { font-size: 1.8rem; color: white; }
//   h2 { font-size: 1.5rem; font-weight: bold; color: #143642; }
//   .topnav { overflow: hidden; background-color: #143642; padding: 10px; color: white; }
//   body { margin: 0; background: #f4f4f4; }
//   .content { padding: 30px; max-width: 600px; margin: 0 auto; }
//   .card {
//     background-color: #F8F7F9;
//     box-shadow: 2px 2px 12px rgba(140,140,140,0.5);
//     padding: 20px;
//   }
//   .button {
//     padding: 15px 50px; font-size: 24px;
//     color: #fff; background-color: #0f8b8d; border: none;
//     border-radius: 5px; user-select: none;
//   }
//   .button:active {
//     background-color: #0f8b8d;
//     box-shadow: 2 2px #CDCDCD;
//     transform: translateY(2px);
//   }
//   .state {
//     font-size: 1.5rem;
//     color:#8c8c8c;
//     font-weight: bold;
//   }
//   </style>
// </head>
// <body>
//   <div class="topnav">
//     <h1>ESP WebSocket Server</h1>
//   </div>
//   <div class="content">
//     <div class="card">
//       <h2>Output - RGB LED(GPIO 16)</h2>
//       <p class="state">state: <span id="state">%STATE%</span></p>
//       <p><button id="button" class="button">Toggle</button></p>
//     </div>
//   </div>
// <script>
//   var gateway = `ws://${window.location.hostname}/ws`;
//   var websocket;
//   window.addEventListener('load', onLoad);
//   function initWebSocket() {
//     console.log('Trying to open a WebSocket connection...');
//     websocket = new WebSocket(gateway);
//     websocket.onopen    = onOpen;
//     websocket.onclose   = onClose;
//     websocket.onmessage = onMessage;
//   }
//   function onOpen(event) {
//     console.log('Connection opened');
//   }
//   function onClose(event) {
//     console.log('Connection closed');
//     setTimeout(initWebSocket, 2000);
//   }
//   function onMessage(event) {
//     var state = (event.data == "1") ? "ON" : "OFF";
//     document.getElementById('state').innerHTML = state;
//   }
//   function onLoad(event) {
//     initWebSocket();
//     initButton();
//   }
//   function initButton() {
//     document.getElementById('button').addEventListener('click', toggle);
//   }
//   function toggle(){
//     websocket.send('toggle');
//   }
// </script>
// </body>
// </html>
// )rawliteral";

// // 상태 전송
// void notifyClients() {
//   ws.textAll(String(ledState));
// }

// // WebSocket 메시지 처리
// void handleWebSocketMessage(void *arg, uint8_t *data, size_t len) {
//   AwsFrameInfo *info = (AwsFrameInfo*)arg;
//   if (info->final && info->index == 0 && info->len == len && info->opcode == WS_TEXT) {
//     data[len] = 0;
//     if (strcmp((char*)data, "toggle") == 0) {
//       ledState = !ledState;
//       notifyClients();
//     }
//   }
// }

// // WebSocket 이벤트
// void onEvent(AsyncWebSocket *server, AsyncWebSocketClient *client, AwsEventType type,
//              void *arg, uint8_t *data, size_t len) {
//   switch (type) {
//     case WS_EVT_CONNECT:
//       Serial.printf("WebSocket client #%u connected from %s\n", client->id(), client->remoteIP().toString().c_str());
//       client->text(String(ledState));  // 초기 상태 전송
//       break;
//     case WS_EVT_DISCONNECT:
//       Serial.printf("WebSocket client #%u disconnected\n", client->id());
//       break;
//     case WS_EVT_DATA:
//       handleWebSocketMessage(arg, data, len);
//       break;
//     default:
//       break;
//   }
// }

// void initWebSocket() {
//   ws.onEvent(onEvent);
//   server.addHandler(&ws);
// }

// String processor(const String& var){
//   if(var == "STATE"){
//     return ledState ? "ON" : "OFF";
//   }
//   return String();
// }

// void setup(){
//   Serial.begin(115200);

//   // NeoPixel 초기화
//   rgbLed.begin();
//   rgbLed.setBrightness(100);
//   rgbLed.show();

//   WiFi.begin(ssid, password);
//   while (WiFi.status() != WL_CONNECTED) {
//     delay(1000);
//     Serial.println("Connecting to WiFi..");
//   }

//   Serial.println(WiFi.localIP());

//   initWebSocket();

//   server.on("/", HTTP_GET, [](AsyncWebServerRequest *request){
//     request->send_P(200, "text/html", index_html, processor);
//   });

//   server.begin();
// }

// void loop() {
//   ws.cleanupClients();

//   // RGB LED 제어
//   if (ledState) {
//     rgbLed.setPixelColor(0, rgbLed.Color(255, 0, 0));  // ON → 빨강
//   } else {
//     rgbLed.setPixelColor(0, 0, 0, 0);  // OFF
//   }
//   rgbLed.show();
// }

// #include <WiFi.h>

// const char* ssid     = "AP02";
// const char* password = "Gwe1234!#@";

// WiFiServer server(1234);
// WiFiClient client;

// void setup() {
//   Serial.begin(115200);
//   WiFi.begin(ssid, password);

//   while (WiFi.status() != WL_CONNECTED) {
//     delay(500);
//     Serial.print(".");
//   }
//   Serial.println("\nWiFi connected");
//   Serial.print("IP address: ");
//   Serial.println(WiFi.localIP());

//   server.begin();
// }

// void loop() {
//   client = server.available();
//   if (client) {
//     Serial.println("Client connected");
//     while (client.connected()) {
//       // 예: 1초마다 값을 보냄
//       String dataToSend = "응애";
//       client.print(dataToSend);
//       Serial.println("Sent: " + dataToSend);
//       delay(1000);
//     }
//     Serial.println("Client disconnected");
//     client.stop();}
//   }