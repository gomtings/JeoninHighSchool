/*
  ReadAnalogVoltage

  Reads an analog input off channel0, converts it to voltage, and prints the
  result to the Serial Monitor. Attach the center pin of a potentiometer to pin
  A0, and the outside pins to +3V3 and ground.

*/

#include "MCP3x6x.h"
#define MCP3x6x_DEBUG 1
#define ADC_INT 35  // data ready interrupt pin. LOW = data ready.
#define ADC_CS 32
#define IRQ_PIN 8 // data ready interrupt pin. HIGH = data ready. LOW = data not ready.
#define MCLK_PIN 7
#define MISO_PIN 12
#if defined ARDUINO_AVR_PROMICRO8
MCP3564 mcp(2, 3, 10);
#elif defined ARDUINO_GRAND_CENTRAL_M4
SPIClass mySPI = SPIClass(&sercom5, 125, 126, 99, SPI_PAD_0_SCK_3, SERCOM_RX_PAD_2);
MCP3564 mcp(84, 81, 98, &mySPI);
#elif defined ADAFRUIT_METRO_M0_EXPRESS
SPIClass mySPI(&sercom1, 12, 13, 11, SPI_PAD_0_SCK_1, SERCOM_RX_PAD_3);
MCP3564 mcp(8, 7, 10, &mySPI, 11, 12, 13);
#elif defined ARDUINO_ARCH_ESP8266
MCP3564 mcp(D1, D2, SS);
// #elif
// todo: might need further cases, didn't check for all boards
#else
//MCP3564 mcp(ADC_CS, &SPI, 23, 19, 18, ADC_INT);
MCP3564 mcp(ADC_INT, 18, ADC_CS, &SPI, 23, 19, NULL);

#endif

void mcp_wrapper() { mcp.IRQ_handler(); }

void setup() {
  Serial.begin(115200);
  while (!Serial)
    ;
  Serial.println(__FILE__);

  if (!mcp.begin()) {
    Serial.println("failed to initialize MCP");
    while (1)
      ;
  }
  mcp.enableScanChannel(MCP_CH0);
  mcp.enableScanChannel(MCP_CH2);
  mcp.startContinuous();

  Serial.println("MCP setup done");
}

unsigned long previousMillis = 0;
const long interval          = 1000;

// the loop routine runs over and over again forever:
void loop() {
  unsigned long currentMillis = millis();
  Serial.println(currentMillis);
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    // read the input on default analog channel:
    int32_t adcdata0 = mcp.analogReadContinuous(MCP_CH0);
    int32_t adcdata1 = mcp.analogReadContinuous(MCP_CH2);

    // print out the value you read:
    Serial.print("voltage0: ");
    Serial.println(adcdata0, 10);
    Serial.print("voltage1: ");
    Serial.println(adcdata1, 10);
  }
}
