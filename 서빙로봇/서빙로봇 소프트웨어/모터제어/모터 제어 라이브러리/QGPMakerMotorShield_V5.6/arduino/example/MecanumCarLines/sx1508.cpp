/******************************************************************************
  sx1508.cpp
  sx1508 I/O Expander Library Source File
  Creation Date: 01-18-2022
  @ YFROBOT

  Here you'll find the Arduino code used to interface with the SX1508 I2C
  8 I/O expander. There are functions to take advantage of everything the
  SX1508 provides - input/output setting, writing pins high/low, reading
  the input value of pins, LED driver utilities.

  Distributed as-is; no warranty is given.
******************************************************************************/

#include <Wire.h>
#include "Arduino.h"
#include "sx1508.h"

SX1508::SX1508()
{
  _clkX = 0;
}

SX1508::SX1508(uint8_t address, uint8_t resetPin, uint8_t interruptPin, uint8_t oscillatorPin)
{
  // Store the received parameters into member variables
  deviceAddress = address;
  pinInterrupt = interruptPin;
  pinOscillator = oscillatorPin;
  pinReset = resetPin;
}

uint8_t SX1508::begin(uint8_t address, TwoWire &wirePort, uint8_t resetPin)
{
  // Store the received parameters into member variables
  _i2cPort = &wirePort;
  deviceAddress = address;
  pinReset = resetPin;

  return init();
}

uint8_t SX1508::init(void)
{
  // Begin I2C should be done externally, before beginning SX1508
  //Wire.begin();

  // If the reset pin is connected
  if (pinReset != 255)
    reset(1);
  else
    reset(0);

  // Communication test. We'll read from two registers with different
  // default values to verify communication.
  uint8_t testRegisters = readByte(REG_INTERRUPT_MASK); // This should return 0xFF, Interrupt mask register address 0x09

  if (testRegisters == 0xFF)
  {
    // Set the clock to a default of 2MHz using internal
    clock(INTERNAL_CLOCK_2MHZ);

    return 1;
  }

  return 0;
}

void SX1508::reset(bool hardware)
{
  // if hardware bool is set
  if (hardware) {
    // Check if bit 2 of REG_MISC is set
    // if so nReset will not issue a POR, we'll need to clear that bit first
    uint8_t regMisc = readByte(REG_MISC);
    if (regMisc & (1 << 2)) {
      regMisc &= ~(1 << 2);
      writeByte(REG_MISC, regMisc);
    }
    // Reset the SX1508, the pin is active low
    pinMode(pinReset, OUTPUT);	  // set reset pin as output
    digitalWrite(pinReset, LOW);  // pull reset pin low
    delay(1);					  // Wait for the pin to settle
    digitalWrite(pinReset, HIGH); // pull reset pin back high
  } else {
    // Software reset command sequence:
    writeByte(REG_RESET, 0x12);
    writeByte(REG_RESET, 0x34);
  }
}

void SX1508::pinDir(uint8_t pin, uint8_t inOut, uint8_t initialLevel)
{
  // The SX1508 RegDir registers: REG_DIR, REG_DIR
  //	0: IO is configured as an output
  //	1: IO is configured as an input
  uint8_t modeBit;
  if ((inOut == OUTPUT) || (inOut == ANALOG_OUTPUT)) {
    uint8_t tempRegData = readByte(REG_DATA);
    if (initialLevel == LOW) {
      tempRegData &= ~(1 << pin);
      writeByte(REG_DATA, tempRegData);
    }
    modeBit = 0;
  } else {
    modeBit = 1;
  }

  uint8_t tempRegDir = readByte(REG_DIR);
  if (modeBit)
    tempRegDir |= (1 << pin);
  else
    tempRegDir &= ~(1 << pin);
  writeByte(REG_DIR, tempRegDir);

  // If INPUT_PULLUP was called, set up the pullup too:
  if (inOut == INPUT_PULLUP)
    writePin(pin, HIGH);

  if (inOut == ANALOG_OUTPUT) {
    ledDriverInit(pin);
  }
}

void SX1508::pinMode(uint8_t pin, uint8_t inOut, uint8_t initialLevel)
{
  pinDir(pin, inOut, initialLevel);
}

bool SX1508::writePin(uint8_t pin, uint8_t highLow)
{
  uint8_t tempRegDir = readByte(REG_DIR);
  if ((0xFF ^ tempRegDir) & (1 << pin)) { // If the pin is an output, write high/low
    uint8_t tempRegData = readByte(REG_DATA);
    if (highLow)
      tempRegData |= (1 << pin);
    else
      tempRegData &= ~(1 << pin);
    return writeByte(REG_DATA, tempRegData);
  } else { // Otherwise the pin is an input, pull-up/down
    uint8_t tempPullUp = readByte(REG_PULL_UP);
    uint8_t tempPullDown = readByte(REG_PULL_DOWN);

    if (highLow) { // if HIGH, do pull-up, disable pull-down
      tempPullUp |= (1 << pin);
      tempPullDown &= ~(1 << pin);
      return writeByte(REG_PULL_UP, tempPullUp) && writeByte(REG_PULL_DOWN, tempPullDown);
    } else { // If LOW do pull-down, disable pull-up
      tempPullDown |= (1 << pin);
      tempPullUp &= ~(1 << pin);
      return writeByte(REG_PULL_UP, tempPullUp) && writeByte(REG_PULL_DOWN, tempPullDown);
    }
  }
}

bool SX1508::digitalWrite(uint8_t pin, uint8_t highLow)
{
  return writePin(pin, highLow);
}

uint8_t SX1508::readPin(uint8_t pin)
{
  uint8_t tempRegDir = readByte(REG_DIR);
  if (tempRegDir & (1 << pin)) // If the pin is an input
  {
    uint8_t tempRegData = readByte(REG_DATA);
    if (tempRegData & (1 << pin))
      return 1;
  } else {
    // log_d("Pin %d not INPUT, REG_DIR: %d", pin, tempRegDir);
  }
  return 0;
}

bool SX1508::readPin(const uint8_t pin, bool *value)
{
  uint8_t tempRegDir;
  if (readByte(REG_DIR, &tempRegDir)) {
    if (tempRegDir & (1 << pin)) { // If the pin is an input
      uint8_t tempRegData;
      if (readByte(REG_DATA, &tempRegData)) {
        *value = (tempRegData & (1 << pin)) != 0;
        return true;
      };
    }
    else
    {
      *value = false;
      return true;
    }
  }
  return false;
}

uint8_t SX1508::digitalRead(uint8_t pin)
{
  return readPin(pin);
}

bool SX1508::digitalRead(uint8_t pin, bool *value)
{
  return readPin(pin, value);
}

void SX1508::ledDriverInit(uint8_t pin, uint8_t freq /*= 1*/, bool log /*= false*/)
{
  uint8_t tempByte;

  // Disable input buffer
  // Writing a 1 to the pin bit will disable that pins input buffer
  tempByte = readByte(REG_INPUT_DISABLE);
  tempByte |= (1 << pin);
  writeByte(REG_INPUT_DISABLE, tempByte);

  // Disable pull-up
  // Writing a 0 to the pin bit will disable that pull-up resistor
  tempByte = readByte(REG_PULL_UP);
  tempByte &= ~(1 << pin);
  writeByte(REG_PULL_UP, tempByte);

  // Set direction to output (REG_DIR)
  tempByte = readByte(REG_DIR);
  tempByte &= ~(1 << pin); // 0=output
  writeByte(REG_DIR, tempByte);

  // Enable oscillator (REG_CLOCK)
  tempByte = readByte(REG_CLOCK);
  tempByte |= (1 << 6);  // Internal 2MHz oscillator part 1 (set bit 6)
  tempByte &= ~(1 << 5); // Internal 2MHz oscillator part 2 (clear bit 5)
  writeByte(REG_CLOCK, tempByte);

  // Configure LED driver clock and mode (REG_MISC)
  tempByte = readByte(REG_MISC);
  if (log) {
    tempByte |= (1 << 7); // set logarithmic mode bank B
    tempByte |= (1 << 3); // set logarithmic mode bank A
  } else {
    tempByte &= ~(1 << 7); // set linear mode bank B
    tempByte &= ~(1 << 3); // set linear mode bank A
  }

  // Use configClock to setup the clock divder
  if (_clkX == 0) { // Make clckX non-zero
    _clkX = 2000000.0 / (1 << (1 - 1)); // Update private clock variable

    uint8_t freq = (1 & 0x07) << 4; // freq should only be 3 bits from 6:4
    tempByte |= freq;
  }
  writeByte(REG_MISC, tempByte);

  // Enable LED driver operation (REG_LED_DRIVER_ENABLE)
  tempByte = readByte(REG_LED_DRIVER_ENABLE);
  tempByte |= (1 << pin);
  writeByte(REG_LED_DRIVER_ENABLE, tempByte);

  // Set REG_DATA bit low ~ LED driver started
  tempByte = readByte(REG_DATA);
  tempByte &= ~(1 << pin);
  writeByte(REG_DATA, tempByte);
}

void SX1508::pwm(uint8_t pin, uint8_t iOn)
{
  // Write the on intensity of pin
  // Linear mode: Ion = iOn
  // Log mode: Ion = f(iOn)
  writeByte(REG_I_ON[pin], iOn);
}

void SX1508::analogWrite(uint8_t pin, uint8_t iOn)
{
  pwm(pin, iOn);
}

void SX1508::blink(uint8_t pin, unsigned long tOn, unsigned long tOff, uint8_t onIntensity, uint8_t offIntensity)
{
  uint8_t onReg = calculateLEDTRegister(tOn);
  uint8_t offReg = calculateLEDTRegister(tOff);

  setupBlink(pin, onReg, offReg, onIntensity, offIntensity, 0, 0);
}

void SX1508::breathe(uint8_t pin, unsigned long tOn, unsigned long tOff, unsigned long rise, unsigned long fall, uint8_t onInt, uint8_t offInt, bool log)
{
  offInt = constrain(offInt, 0, 7);

  uint8_t onReg = calculateLEDTRegister(tOn);
  uint8_t offReg = calculateLEDTRegister(tOff);

  uint8_t riseTime = calculateSlopeRegister(rise, onInt, offInt);
  uint8_t fallTime = calculateSlopeRegister(fall, onInt, offInt);

  setupBlink(pin, onReg, offReg, onInt, offInt, riseTime, fallTime, log);
}

void SX1508::setupBlink(uint8_t pin, uint8_t tOn, uint8_t tOff, uint8_t onIntensity, uint8_t offIntensity, uint8_t tRise, uint8_t tFall, bool log)
{
  ledDriverInit(pin, log);

  // Keep parameters within their limits:
  tOn &= 0x1F;  // tOn should be a 5-bit value
  tOff &= 0x1F; // tOff should be a 5-bit value
  offIntensity &= 0x07;
  // Write the time on
  // 1-15:  TON = 64 * tOn * (255/ClkX)
  // 16-31: TON = 512 * tOn * (255/ClkX)
  writeByte(REG_T_ON[pin], tOn);

  // Write the time/intensity off register
  // 1-15:  TOFF = 64 * tOff * (255/ClkX)
  // 16-31: TOFF = 512 * tOff * (255/ClkX)
  // linear Mode - IOff = 4 * offIntensity
  // log mode - Ioff = f(4 * offIntensity)
  writeByte(REG_OFF[pin], (tOff << 3) | offIntensity);

  // Write the on intensity:
  writeByte(REG_I_ON[pin], onIntensity);

  // Prepare tRise and tFall
  tRise &= 0x1F; // tRise is a 5-bit value
  tFall &= 0x1F; // tFall is a 5-bit value

  // Write regTRise
  // 0: Off
  // 1-15:  TRise =      (regIOn - (4 * offIntensity)) * tRise * (255/ClkX)
  // 16-31: TRise = 16 * (regIOn - (4 * offIntensity)) * tRise * (255/ClkX)
  if (REG_T_RISE[pin] != 0xFF)
    writeByte(REG_T_RISE[pin], tRise);
  // Write regTFall
  // 0: off
  // 1-15:  TFall =      (regIOn - (4 * offIntensity)) * tFall * (255/ClkX)
  // 16-31: TFall = 16 * (regIOn - (4 * offIntensity)) * tFall * (255/ClkX)
  if (REG_T_FALL[pin] != 0xFF)
    writeByte(REG_T_FALL[pin], tFall);
}

void SX1508::sync(void)
{
  // First check if nReset functionality is set
  uint8_t regMisc = readByte(REG_MISC);
  if (!(regMisc & 0x04))
  {
    regMisc |= (1 << 2);
    writeByte(REG_MISC, regMisc);
  }

  // Toggle nReset pin to sync LED timers
  pinMode(pinReset, OUTPUT);	  // set reset pin as output
  digitalWrite(pinReset, LOW);  // pull reset pin low
  delay(1);					  // Wait for the pin to settle
  digitalWrite(pinReset, HIGH); // pull reset pin back high

  // Return nReset to POR functionality
  writeByte(REG_MISC, (regMisc & ~(1 << 2)));
}

void SX1508::debounceConfig(uint8_t configValue)
{
  // First make sure clock is configured
  uint8_t tempByte = readByte(REG_MISC);
  if ((tempByte & 0x70) == 0)
  {
    tempByte |= (1 << 4); // Just default to no divider if not set
    writeByte(REG_MISC, tempByte);
  }
  tempByte = readByte(REG_CLOCK);
  if ((tempByte & 0x60) == 0)
  {
    tempByte |= (1 << 6); // default to internal osc.
    writeByte(REG_CLOCK, tempByte);
  }

  configValue &= 0b111; // 3-bit value
  writeByte(REG_DEBOUNCE_CONFIG, configValue);
}

void SX1508::debounceTime(uint8_t time)
{
  if (_clkX == 0)					   // If clock hasn't been set up.
    clock(INTERNAL_CLOCK_2MHZ, 1); // Set clock to 2MHz.

  // Debounce time-to-byte map: (assuming fOsc = 2MHz)
  // 0: 0.5ms		1: 1ms
  // 2: 2ms		3: 4ms
  // 4: 8ms		5: 16ms
  // 6: 32ms		7: 64ms
  // 2^(n-1)
  uint8_t configValue = 0;
  // We'll check for the highest set bit position,
  // and use that for debounceConfig
  for (int8_t i = 7; i >= 0; i--)
  {
    if (time & (1 << i))
    {
      configValue = i + 1;
      break;
    }
  }
  configValue = constrain(configValue, 0, 7);

  debounceConfig(configValue);
}

void SX1508::debounceEnable(uint8_t pin)
{
  uint8_t debounceEnable = readByte(REG_DEBOUNCE_ENABLE);
  debounceEnable |= (1 << pin);
  writeByte(REG_DEBOUNCE_ENABLE, debounceEnable);
}

void SX1508::debouncePin(uint8_t pin)
{
  debounceEnable(pin);
}

void SX1508::debounceKeypad(uint8_t time, uint8_t numRows, uint8_t numCols)
{
  // Set up debounce time:
  debounceTime(time);

  // Set up debounce pins:
  for (uint8_t i = 0; i < numRows; i++)
    debouncePin(i);
  for (uint8_t i = 0; i < (8 + numCols); i++)
    debouncePin(i);
}

void SX1508::enableInterrupt(uint8_t pin, uint8_t riseFall)
{
  // Set REG_INTERRUPT_MASK
  uint8_t tempByte = readByte(REG_INTERRUPT_MASK);
  tempByte &= ~(1 << pin); // 0 = event on IO will trigger interrupt
  writeByte(REG_INTERRUPT_MASK, tempByte);

  uint8_t sensitivity = 0;
  switch (riseFall)
  {
    case CHANGE:
      sensitivity = 0b11;
      break;
    case FALLING:
      sensitivity = 0b10;
      break;
    case RISING:
      sensitivity = 0b01;
      break;
  }

  // Set REG_SENSE_XXX
  // Sensitivity is set as follows:
  // 00: None
  // 01: Rising
  // 10: Falling
  // 11: Both
  uint8_t pinMask = (pin & 0x07) * 2;
  uint8_t senseRegister;

  // Need to select between two words. One for bank A, one for B.
  if (pin >= 8)
    senseRegister = REG_SENSE_HIGH;
  else
    senseRegister = REG_SENSE_HIGH;

  tempByte = readByte(senseRegister);
  tempByte &= ~(0b11 << pinMask);		  // Mask out the bits we want to write
  tempByte |= (sensitivity << pinMask); // Add our new bits
  writeByte(senseRegister, tempByte);
}

uint8_t SX1508::interruptSource(bool clear /* =true*/)
{
  uint8_t intSource = readByte(REG_INTERRUPT_SOURCE);
  if (clear)
    writeByte(REG_INTERRUPT_SOURCE, 0xFF); // Clear interrupts
  return intSource;
}

bool SX1508::checkInterrupt(uint8_t pin)
{
  if (interruptSource(false) & (1 << pin))
    return true;

  return false;
}

void SX1508::clock(uint8_t oscSource, uint8_t oscDivider, uint8_t oscPinFunction, uint8_t oscFreqOut)
{
  configClock(oscSource, oscPinFunction, oscFreqOut, oscDivider);
}

void SX1508::configClock(uint8_t oscSource /*= 2*/, uint8_t oscPinFunction /*= 0*/, uint8_t oscFreqOut /*= 0*/, uint8_t oscDivider /*= 1*/)
{
  // RegClock constructed as follows:
  //	6:5 - Oscillator frequency souce
  //		00: off, 01: external input, 10: internal 2MHz, 1: reserved
  //	4 - OSCIO pin function
  //		0: input, 1 ouptut
  //	3:0 - Frequency of oscout pin
  //		0: LOW, 0xF: high, else fOSCOUT = FoSC/(2^(RegClock[3:0]-1))
  oscSource = (oscSource & 0b11) << 5;		// 2-bit value, bits 6:5
  oscPinFunction = (oscPinFunction & 1) << 4; // 1-bit value bit 4
  oscFreqOut = (oscFreqOut & 0b1111);			// 4-bit value, bits 3:0
  uint8_t regClock = oscSource | oscPinFunction | oscFreqOut;
  writeByte(REG_CLOCK, regClock);

  // Config RegMisc[6:4] with oscDivider
  // 0: off, else ClkX = fOSC / (2^(RegMisc[6:4] -1))
  oscDivider = constrain(oscDivider, 1, 7);
  _clkX = 2000000.0 / (1 << (oscDivider - 1)); // Update private clock variable
  oscDivider = (oscDivider & 0b111) << 4;		 // 3-bit value, bits 6:4

  uint8_t regMisc = readByte(REG_MISC);
  regMisc &= ~(0b111 << 4);
  regMisc |= oscDivider;
  writeByte(REG_MISC, regMisc);
}

uint8_t SX1508::calculateLEDTRegister(uint8_t ms)
{
  uint8_t regOn1, regOn2;
  float timeOn1, timeOn2;

  if (_clkX == 0)
    return 0;

  regOn1 = (float)(ms / 1000.0) / (64.0 * 255.0 / (float)_clkX);
  regOn2 = regOn1 / 8;
  regOn1 = constrain(regOn1, 1, 15);
  regOn2 = constrain(regOn2, 16, 31);

  timeOn1 = 64.0 * regOn1 * 255.0 / _clkX * 1000.0;
  timeOn2 = 512.0 * regOn2 * 255.0 / _clkX * 1000.0;

  if (abs(timeOn1 - ms) < abs(timeOn2 - ms))
    return regOn1;
  else
    return regOn2;
}

uint8_t SX1508::calculateSlopeRegister(uint8_t ms, uint8_t onIntensity, uint8_t offIntensity)
{
  uint16_t regSlope1, regSlope2;
  float regTime1, regTime2;

  if (_clkX == 0)
    return 0;

  float tFactor = ((float)onIntensity - (4.0 * (float)offIntensity)) * 255.0 / (float)_clkX;
  float timeS = float(ms) / 1000.0;

  regSlope1 = timeS / tFactor;
  regSlope2 = regSlope1 / 16;

  regSlope1 = constrain(regSlope1, 1, 15);
  regSlope2 = constrain(regSlope2, 16, 31);

  regTime1 = regSlope1 * tFactor * 1000.0;
  regTime2 = 16 * regTime1;

  if (abs(regTime1 - ms) < abs(regTime2 - ms))
    return regSlope1;
  else
    return regSlope2;
}

// readByte(uint8_t registerAddress)
//	This function reads a single byte located at the registerAddress register.
//	- deviceAddress should already be set by the constructor.
//	- Return value is the byte read from registerAddress
//		- Currently returns 0 if communication has timed out
uint8_t SX1508::readByte(uint8_t registerAddress)
{
  uint8_t readValue;
  // Commented the line as variable seems unused;
  //uint16_t timeout = RECEIVE_TIMEOUT_VALUE;

  _i2cPort->beginTransmission(deviceAddress);
  _i2cPort->write(registerAddress);
  _i2cPort->endTransmission();
  _i2cPort->requestFrom(deviceAddress, (uint8_t)1);

  readValue = _i2cPort->read();

  return readValue;
}

bool SX1508::readByte(uint8_t registerAddress, uint8_t *value)
{
  return readBytes(registerAddress, value, 1);
}

// readBytes(uint8_t firstRegisterAddress, uint8_t * destination, uint8_t length)
//	This function reads a series of bytes incrementing from a given address
//	- firstRegisterAddress is the first address to be read
//	- destination is an array of bytes where the read values will be stored into
//	- length is the number of bytes to be read
//	- Return boolean true if succesfull
bool SX1508::readBytes(uint8_t firstRegisterAddress, uint8_t *destination, uint8_t length)
{
  _i2cPort->beginTransmission(deviceAddress);
  _i2cPort->write(firstRegisterAddress);
  uint8_t endResult = _i2cPort->endTransmission();
  bool result = (endResult == I2C_ERROR_OK) && (_i2cPort->requestFrom(deviceAddress, length) == length);

  if (result)
  {
    for (uint8_t i = 0; i < length; i++)
    {
      destination[i] = _i2cPort->read();
    }
  }
  return result;
}

// writeByte(uint8_t registerAddress, uint8_t writeValue)
//	This function writes a single byte to a single register on the SX509.
//	- writeValue is written to registerAddress
//	- deviceAddres should already be set from the constructor
//	- Return value: true if succeeded, false if failed
bool SX1508::writeByte(uint8_t registerAddress, uint8_t writeValue)
{
  _i2cPort->beginTransmission(deviceAddress);
  bool result = _i2cPort->write(registerAddress) && _i2cPort->write(writeValue);
  uint8_t endResult = _i2cPort->endTransmission();
  return result && (endResult == I2C_ERROR_OK);
}

// writeBytes(uint8_t firstRegisterAddress, uint8_t * writeArray, uint8_t length)
//	This function writes an array of bytes, beggining at a specific adddress
//	- firstRegisterAddress is the initial register to be written.
//		- All writes following will be at incremental register addresses.
//	- writeArray should be an array of byte values to be written.
//	- length should be the number of bytes to be written.
//	- Return value: true if succeeded, false if failed
bool SX1508::writeBytes(uint8_t firstRegisterAddress, uint8_t *writeArray, uint8_t length)
{
  _i2cPort->beginTransmission(deviceAddress);
  bool result = _i2cPort->write(firstRegisterAddress);
  result = _i2cPort->write(writeArray, length);
  uint8_t endResult = _i2cPort->endTransmission();
  return result && (endResult == I2C_ERROR_OK);
}
