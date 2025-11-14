#ifndef ADS1115_h
#define ADS1115_h

#include <Arduino.h>

#define RESET_COMMAND 0b01101000  // ADC Reset comm

class ADS1115 {
  public: 
    ADS1115();
    void ScanI2CDevice(void);
};

#endif