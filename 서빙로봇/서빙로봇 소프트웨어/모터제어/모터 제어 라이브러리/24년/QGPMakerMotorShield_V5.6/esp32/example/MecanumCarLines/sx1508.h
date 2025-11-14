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

#include "Arduino.h"

#ifndef SX1508_H
#define SX1508_H

#ifndef I2C_ERROR_OK
#define I2C_ERROR_OK 0
#endif

#define RECEIVE_TIMEOUT_VALUE 1000 // Timeout for I2C receive

// These are used for setting LED driver to linear or log mode:
#define LINEAR 0
#define LOGARITHMIC 1

// These are used for clock config:
#define INTERNAL_CLOCK_2MHZ 2
#define EXTERNAL_CLOCK 1

#define SOFTWARE_RESET 0
#define HARDWARE_RESET 1

#define ANALOG_OUTPUT 0x3 // To set a pin mode for PWM output

#define   REG_INPUT_DISABLE   0x00  //  RegInputDisableA Input buffer disable register _ I/O[7_0] (Bank A) 0000 0000
#define   REG_LONG_SLEW     0x01  //  RegLongSlewA Output buffer long slew register _ I/O[7_0] (Bank A) 0000 0000
#define   REG_LOW_DRIVE     0x02  //  RegLowDriveA Output buffer low drive register _ I/O[7_0] (Bank A) 0000 0000
#define   REG_PULL_UP       0x03  //  RegPullUpA Pull_up register _ I/O[7_0] (Bank A) 0000 0000
#define   REG_PULL_DOWN     0x04  //  RegPullDownA Pull_down register _ I/O[7_0] (Bank A) 0000 0000
#define   REG_OPEN_DRAIN      0x05  //  RegOpenDrainA Open drain register _ I/O[7_0] (Bank A) 0000 0000
#define   REG_POLARITY      0x06  //  RegPolarityA Polarity register _ I/O[7_0] (Bank A) 0000 0000
#define   REG_DIR         0x07  //  RegDirA Direction register _ I/O[7_0] (Bank A) 1111 1111
#define   REG_DATA        0x08  //  RegDataA Data register _ I/O[7_0] (Bank A) 1111 1111*
#define   REG_INTERRUPT_MASK    0x09  //  RegInterruptMaskA Interrupt mask register _ I/O[7_0] (Bank A) 1111 1111
#define   REG_SENSE_HIGH      0x0A  //  RegSenseHighA Sense register for I/O[7:4] 0000 0000
#define   REG_SENSE_LOW     0x0B  //  RegSenseLowA Sense register for I/O[3:0] 0000 0000
#define   REG_INTERRUPT_SOURCE  0x0C  //  RegInterruptSourceA Interrupt source register _ I/O[7_0] (Bank A) 0000 0000
#define   REG_EVENT_STATUS    0x0D  //  RegEventStatusA Event status register _ I/O[7_0] (Bank A) 0000 0000
#define   REG_LEVEL_SHIFTER   0x0E  //  RegLevelShifter1 Level shifter register 0000 0000
#define   REG_CLOCK       0x0F  //  RegClock Clock management register 0000 0000
#define   REG_MISC        0x10  //  RegMisc Miscellaneous device settings register 0000 0000
#define   REG_LED_DRIVER_ENABLE 0x11  //  RegLEDDriverEnableA LED driver enable register _ I/O[7_0] (Bank A) 0000 0000
// Debounce and Keypad Engine
#define   REG_DEBOUNCE_CONFIG   0x12  //  RegDebounceConfig Debounce configuration register 0000 0000
#define   REG_DEBOUNCE_ENABLE   0x13  //  RegDebounceEnableA Debounce enable register _ I/O[7_0] (Bank A) 0000 0000
#define   REG_KEY_CONFIG      0x14  //  RegKeyConfig1 Key scan configuration register 0000 0000
#define   REG_KEY_DATA      0x15  //  RegKeyData1 Key value 1111 1111
// LED Driver (PWM, blinking, breathing)
#define   REG_I_ON_0        0x16  //  RegIOn0 ON intensity register for I/O[0] 1111 1111
#define   REG_I_ON_1        0x17  //  RegIOn1 ON intensity register for I/O[1] 1111 1111
#define   REG_T_ON_2        0x18  //  RegTOn2 ON time register for I/O[2] 0000 0000
#define   REG_I_ON_2        0x19  //  RegIOn2 ON intensity register for I/O[2] 1111 1111
#define   REG_OFF_2       0x1A  //  RegOff2 OFF time/intensity register for I/O[2] 0000 0000
#define   REG_T_ON_3        0x1B  //  RegTOn3 ON time register for I/O[3] 0000 0000
#define   REG_I_ON_3        0x1C  //  RegIOn3 ON intensity register for I/O[3] 1111 1111
#define   REG_OFF_3       0x1D  //  RegOff3 OFF time/intensity register for I/O[3] 0000 0000
#define   REG_T_RISE_3      0x1E  //  RegTRise3 Fade in register for I/O[3] 0000 0000
#define   REG_T_FALL_3      0x1F  //  RegTFall3 Fade out register for I/O[3] 0000 0000
#define   REG_I_ON_4        0x20  //  RegIOn4 ON intensity register for I/O[4] 1111 1111
#define   REG_I_ON_5        0x21  //  RegIOn5 ON intensity register for I/O[5] 1111 1111
#define   REG_T_ON_6        0x22  //  RegTOn6 ON time register for I/O[6] 0000 0000
#define   REG_I_ON_6        0x23  //  RegIOn6 ON intensity register for I/O[6] 1111 1111
#define   REG_OFF_6       0x24  //  RegOff6 OFF time/intensity register for I/O[6] 0000 0000
#define   REG_T_ON_7        0x25  //  RegTOn7 ON time register for I/O[7] 0000 0000
#define   REG_I_ON_7        0x26  //  RegIOn7 ON intensity register for I/O[7] 1111 1111
#define   REG_OFF_7       0x27  //  RegOff7 OFF time/intensity register for I/O[7] 0000 0000
#define   REG_T_RISE_7      0x28  //  RegTRise7 Fade in register for I/O[7] 0000 0000
#define   REG_T_FALL_7      0x29  //  RegTFall7 Fade out register for I/O[7] 0000 0000
//  Miscellaneous
#define   REG_HIGH_INPUT      0x2A  //  RegHighInputA High input enable register _ I/O[7_0] (Bank A) 0000 0000
//  Software Reset
#define   REG_RESET       0x7D  //  RegReset Software reset register 0000 0000
#define   REG_TEST_1        0x7E  //  RegTest1 Test register 0000 0000
#define   REG_TEST_2        0x7F  //  RegTest2 Test register 0000 0000

class SX1508
{
  private:

    byte REG_I_ON[8] = {REG_I_ON_0, REG_I_ON_1, REG_I_ON_2, REG_I_ON_3,
                        REG_I_ON_4, REG_I_ON_5, REG_I_ON_6, REG_I_ON_7
                       };

    byte REG_T_ON[8] = {0xFF, 0xFF, REG_T_ON_2, REG_T_ON_3,
                        0xFF, 0xFF, REG_T_ON_6, REG_T_ON_7
                       };

    byte REG_OFF[8] = {0xFF, 0xFF, REG_OFF_2, REG_OFF_3,
                       0xFF, 0xFF, REG_OFF_6, REG_OFF_7
                      };

    byte REG_T_RISE[8] = {0xFF, 0xFF, 0xFF, REG_T_RISE_3,
                          0xFF, 0xFF, 0xFF, REG_T_RISE_7
                         };

    byte REG_T_FALL[8] = {0xFF, 0xFF, 0xFF, REG_T_FALL_3,
                          0xFF, 0xFF, 0xFF, REG_T_FALL_7
                         };

    // These private functions are not available to Arduino sketches.
    // If you need to read or write directly to registers, consider
    // putting the writeByte, readByte functions in the public section
    TwoWire *_i2cPort;
    uint8_t deviceAddress; // I2C Address of SX1508
    // Pin definitions:
    uint8_t pinInterrupt;
    uint8_t pinOscillator;
    uint8_t pinReset;
    // Misc variables:
    unsigned long _clkX;
    // Read Functions:
    uint8_t readByte(uint8_t registerAddress);

    // Read Functions returning success or failure:
    bool readBytes(uint8_t firstRegisterAddress, uint8_t *destination, uint8_t length);
    bool readByte(uint8_t registerAddress, uint8_t *value);

    // Write functions, returning success or failure:
    bool writeByte(uint8_t registerAddress, uint8_t writeValue);
    bool writeBytes(uint8_t firstRegisterAddress, uint8_t *writeArray, uint8_t length);

    // Helper functions:
    // calculateLEDTRegister - Try to estimate an LED on/off duration register,
    // given the number of milliseconds and LED clock frequency.
    uint8_t calculateLEDTRegister(uint8_t ms);
    // calculateSlopeRegister - Try to estimate an LED rise/fall duration
    // register, given the number of milliseconds and LED clock frequency.
    uint8_t calculateSlopeRegister(uint8_t ms, uint8_t onIntensity, uint8_t offIntensity);

  public:
    // -----------------------------------------------------------------------------
    // Constructor - SX1508: This function sets up the pins connected to the
    //		SX1508, and sets up the private deviceAddress variable.
    // -----------------------------------------------------------------------------
    SX1508();
    // Legacy below. Use 0-parameter constructor, and set these parameters in the
    // begin function:
    SX1508(uint8_t address, uint8_t resetPin = 255, uint8_t interruptPin = 255, uint8_t oscillatorPin = 255);

    // -----------------------------------------------------------------------------
    // begin(uint8_t address, uint8_t resetPin): This function initializes the SX1508.
    //  	It requires wire to already be begun (previous versions did not do this), resets the IC, and tries to read some
    //  	registers to prove it's connected.
    // Inputs:
    //		- address: should be the 7-bit address of the SX1508. This should be
    //		 one of four values - 0x3E, 0x3F, 0x70, 0x71 - all depending on what the
    //		 ADDR0 and ADDR1 pins ar se to. This variable is required.
    //		- resetPin: This is the Arduino pin tied to the SX1508 RST pin. This
    //		 pin is optional. If not declared, the library will attempt to
    //		 software reset the SX1508.
    // Output: Returns a 1 if communication is successful, 0 on error.
    // -----------------------------------------------------------------------------
    uint8_t begin(uint8_t address = 0x3E, TwoWire &wirePort = Wire, uint8_t resetPin = 0xFF);
    uint8_t init(void); // Legacy -- use begin now

    // -----------------------------------------------------------------------------
    // reset(bool hardware): This function resets the SX1508 - either a hardware
    //		reset or software. A hardware reset (hardware parameter = 1) pulls the
    //		reset line low, pausing, then pulling the reset line high. A software
    //		reset writes a 0x12 then 0x34 to the REG_RESET as outlined in the
    //		datasheet.
    //
    //  Input:
    //	 	- hardware: 0 executes a software reset, 1 executes a hardware reset
    // -----------------------------------------------------------------------------
    void reset(bool hardware);

    // -----------------------------------------------------------------------------
    // pinMode(uint8_t pin, uint8_t inOut): This function sets one of the SX1508's 16
    //		outputs to either an INPUT or OUTPUT.
    //
    //	Inputs:
    //	 	- pin: should be a value between 0 and 15
    //	 	- inOut: The Arduino INPUT and OUTPUT constants should be used for the
    //		 inOut parameter. They do what they say!
    // -----------------------------------------------------------------------------
    void pinMode(uint8_t pin, uint8_t inOut, uint8_t initialLevel = HIGH);
    void pinDir(uint8_t pin, uint8_t inOut, uint8_t initialLevel = HIGH); // Legacy - use pinMode

    // -----------------------------------------------------------------------------
    // digitalWrite(uint8_t pin, uint8_t highLow): This function writes a pin to either high
    //		or low if it's configured as an OUTPUT. If the pin is configured as an
    //		INPUT, this method will activate either the PULL-UP	or PULL-DOWN
    //		resistor (HIGH or LOW respectively).
    //
    //	Inputs:
    //		- pin: The SX1508 pin number. Should be a value between 0 and 15.
    //		- highLow: should be Arduino's defined HIGH or LOW constants.
    // -----------------------------------------------------------------------------
    bool digitalWrite(uint8_t pin, uint8_t highLow);
    bool writePin(uint8_t pin, uint8_t highLow); // Legacy - use digitalWrite

    // -----------------------------------------------------------------------------
    // digitalRead(uint8_t pin): This function reads the HIGH/LOW status of a pin.
    //		The pin should be configured as an INPUT, using the pinDir function.
    //
    //	Inputs:
    //	 	- pin: The SX1508 pin to be read. should be a value between 0 and 15.
    //  Outputs:
    //		This function returns a 1 if HIGH, 0 if LOW
    // -----------------------------------------------------------------------------
    uint8_t digitalRead(uint8_t pin);
    bool digitalRead(uint8_t pin, bool *value);
    uint8_t readPin(uint8_t pin); // Legacy - use digitalRead
    bool readPin(const uint8_t pin, bool *value);

    // -----------------------------------------------------------------------------
    // ledDriverInit(uint8_t pin, uint8_t freq, bool log): This function initializes LED
    //		driving on a pin. It must be called if you want to use the pwm or blink
    //		functions on that pin.
    //
    //	Inputs:
    //		- pin: The SX1508 pin connected to an LED. Should be 0-15.
    //   	- freq: Sets LED clock frequency divider.
    //		- log: selects either linear or logarithmic mode on the LED drivers
    //			- log defaults to 0, linear mode
    //			- currently log sets both bank A and B to the same mode
    //	Note: this function automatically decides to use the internal 2MHz osc.
    // -----------------------------------------------------------------------------
    void ledDriverInit(uint8_t pin, uint8_t freq = 1, bool log = false);

    // -----------------------------------------------------------------------------
    // analogWrite(uint8_t pin, uint8_t iOn):	This function can be used to control the intensity
    //		of an output pin connected to an LED.
    //
    //	Inputs:
    //		- pin: The SX1508 pin connecte to an LED.Should be 0-15.
    //		- iOn: should be a 0-255 value setting the intensity of the LED
    //			- 0 is completely off, 255 is 100% on.
    //
    //	Note: ledDriverInit should be called on the pin before calling this.
    // -----------------------------------------------------------------------------
    void analogWrite(uint8_t pin, uint8_t iOn);
    void pwm(uint8_t pin, uint8_t iOn); // Legacy - use analogWrite

    // -----------------------------------------------------------------------------
    // setupBlink(uint8_t pin, uint8_t tOn, uint8_t tOff, uint8_t offIntensity, uint8_t tRise, uint8_t
    //		tFall):  blink performs both the blink and breath LED driver functions.
    //
    // 	Inputs:
    //  	- pin: the SX1508 pin (0-15) you want to set blinking/breathing.
    //		- tOn: the amount of time the pin is HIGH
    //			- This value should be between 1 and 31. 0 is off.
    //		- tOff: the amount of time the pin is at offIntensity
    //			- This value should be between 1 and 31. 0 is off.
    //		- offIntensity: How dim the LED is during the off period.
    //			- This value should be between 0 and 7. 0 is completely off.
    //		- onIntensity: How bright the LED will be when completely on.
    //			- This value can be between 0 (0%) and 255 (100%).
    //		- tRise: This sets the time the LED takes to fade in.
    //			- This value should be between 1 and 31. 0 is off.
    //			- This value is used with tFall to make the LED breath.
    //		- tFall: This sets the time the LED takes to fade out.
    //			- This value should be between 1 and 31. 0 is off.
    // 	 Notes:
    //		- The breathable pins are 4, 5, 6, 7, 12, 13, 14, 15 only. If tRise and
    //			tFall are set on 0-3 or 8-11 those pins will still only blink.
    // 		- ledDriverInit should be called on the pin to be blinked before this.
    // -----------------------------------------------------------------------------
    void setupBlink(uint8_t pin, uint8_t tOn, uint8_t toff, uint8_t onIntensity = 255, uint8_t offIntensity = 0, uint8_t tRise = 0, uint8_t tFall = 0, bool log = false);

    // -----------------------------------------------------------------------------
    // blink(uint8_t pin, unsigned long tOn, unsigned long tOff, uint8_t onIntensity, uint8_t offIntensity);
    //  	Set a pin to blink output for estimated on/off millisecond durations.
    //
    // 	Inputs:
    //  	- pin: the SX1508 pin (0-15) you want to set blinking
    //   	- tOn: estimated number of milliseconds the pin is LOW (LED sinking current will be on)
    //   	- tOff: estimated number of milliseconds the pin is HIGH (LED sinking current will be off)
    //   	- onIntensity: 0-255 value determining LED on brightness
    //   	- offIntensity: 0-255 value determining LED off brightness
    // 	 Notes:
    //		- The breathable pins are 4, 5, 6, 7, 12, 13, 14, 15 only. If tRise and
    //			tFall are set on 0-3 or 8-11 those pins will still only blink.
    // 		- ledDriverInit should be called on the pin to be blinked before this.
    // -----------------------------------------------------------------------------
    void blink(uint8_t pin, unsigned long tOn, unsigned long tOff, uint8_t onIntensity = 255, uint8_t offIntensity = 0);

    // -----------------------------------------------------------------------------
    // breathe(uint8_t pin, unsigned long tOn, unsigned long tOff, unsigned long rise, unsigned long fall, uint8_t onInt, uint8_t offInt, bool log);
    //  	Set a pin to breathe output for estimated on/off millisecond durations, with
    //  	estimated rise and fall durations.
    //
    // 	Inputs:
    //  	- pin: the SX1508 pin (0-15) you want to set blinking
    //   	- tOn: estimated number of milliseconds the pin is LOW (LED sinking current will be on)
    //   	- tOff: estimated number of milliseconds the pin is HIGH (LED sinking current will be off)
    //   	- rise: estimated number of milliseconds the pin rises from LOW to HIGH
    //   	- falll: estimated number of milliseconds the pin falls from HIGH to LOW
    //   	- onIntensity: 0-255 value determining LED on brightness
    //   	- offIntensity: 0-255 value determining LED off brightness
    // 	 Notes:
    //		- The breathable pins are 4, 5, 6, 7, 12, 13, 14, 15 only. If tRise and
    //			tFall are set on 0-3 or 8-11 those pins will still only blink.
    // 		- ledDriverInit should be called on the pin to be blinked before this,
    //  	  Or call pinMode(<pin>, ANALOG_OUTPUT);
    // -----------------------------------------------------------------------------
    void breathe(uint8_t pin, unsigned long tOn, unsigned long tOff, unsigned long rise, unsigned long fall, uint8_t onInt = 255, uint8_t offInt = 0, bool log = LINEAR);

    // -----------------------------------------------------------------------------
    // sync(void): this function resets the PWM/Blink/Fade counters, syncing any
    //		blinking LEDs. Bit 2 of REG_MISC is set, which alters the functionality
    //		of the nReset pin. The nReset pin is toggled low->high, which should
    //		reset all LED counters. Bit 2 of REG_MISC is again cleared, returning
    //		nReset pin to POR functionality
    // -----------------------------------------------------------------------------
    void sync(void);

    // -----------------------------------------------------------------------------
    // debounceConfig(uint8_t configValue): This method configures the debounce time of
    //		every input.
    //
    //	Input:
    //		- configValue: A 3-bit value configuring the debounce time.
    //			000: 0.5ms * 2MHz/fOSC
    //			001: 1ms * 2MHz/fOSC
    //			010: 2ms * 2MHz/fOSC
    //			011: 4ms * 2MHz/fOSC
    //			100: 8ms * 2MHz/fOSC
    //			101: 16ms * 2MHz/fOSC
    //			110: 32ms * 2MHz/fOSC
    //			111: 64ms * 2MHz/fOSC
    //
    //	Note: fOSC is set with the configClock function. It defaults to 2MHz.
    // -----------------------------------------------------------------------------
    void debounceConfig(uint8_t configVaule);

    // -----------------------------------------------------------------------------
    // debounceTime(uint8_t configValue): This method configures the debounce time of
    //		every input to an estimated millisecond time duration.
    //
    //	Input:
    //		- time: A millisecond duration estimating the debounce time. Actual
    //		  debounce time will depend on fOSC. Assuming it's 2MHz, debounce will
    //		  be set to the 0.5, 1, 2, 4, 8, 16, 32, or 64 ms (whatever's closest)
    //
    //	Note: fOSC is set with the configClock function. It defaults to 2MHz.
    // -----------------------------------------------------------------------------
    void debounceTime(uint8_t time);

    // -----------------------------------------------------------------------------
    // debouncePin(uint8_t pin): This method enables debounce on SX1508 input pin.
    //
    //	Input:
    //		- pin: The SX1508 pin to be debounced. Should be between 0 and 15.
    // -----------------------------------------------------------------------------
    void debouncePin(uint8_t pin);
    void debounceEnable(uint8_t pin); // Legacy, use debouncePin

    // -----------------------------------------------------------------------------
    // debounceKeypad(uint8_t pin): This method enables debounce on all pins connected
    //  to a row/column keypad matrix.
    //
    //	Input:
    //		- time: Millisecond time estimate for debounce (see debounceTime()).
    //		- numRows: The number of rows in the keypad matrix.
    //		- numCols: The number of columns in the keypad matrix.
    // -----------------------------------------------------------------------------
    void debounceKeypad(uint8_t time, uint8_t numRows, uint8_t numCols);

    // -----------------------------------------------------------------------------
    // enableInterrupt(uint8_t pin, uint8_t riseFall): This function sets up an interrupt
    //		on a pin. Interrupts can occur on all SX1508 pins, and can be generated
    //		on rising, falling, or both.
    //
    //	Inputs:
    //		-pin: SX1508 input pin that will generate an input. Should be 0-15.
    //		-riseFall: Configures if you want an interrupt generated on rise fall or
    //			both. For this param, send the pin-change values previously defined
    //			by Arduino:
    //			#define CHANGE 1	<-Both
    //			#define FALLING 2	<- Falling
    //			#define RISING 3	<- Rising
    //
    //	Note: This function does not set up a pin as an input, or configure	its
    //		pull-up/down resistors! Do that before (or after).
    // -----------------------------------------------------------------------------
    void enableInterrupt(uint8_t pin, uint8_t riseFall);

    // -----------------------------------------------------------------------------
    // interruptSource(void): Returns an uint16_t representing which pin caused
    //		an interrupt.
    //
    //	Output: 16-bit value, with a single bit set representing the pin(s) that
    //		generated an interrupt. E.g. a return value of	0x0104 would mean pins 8
    //		and 3 (bits 8 and 3) have generated an interrupt.
    //  Input:
    //  	- clear: boolean commanding whether the interrupt should be cleared
    //  	  after reading or not.
    // -----------------------------------------------------------------------------
    uint8_t interruptSource(bool clear = true);

    // -----------------------------------------------------------------------------
    // checkInterrupt(void): Checks if a single pin generated an interrupt.
    //
    //	Output: Boolean value. True if the requested pin has triggered an interrupt/
    //  Input:
    //  	- pin: Pin to be checked for generating an input.
    // -----------------------------------------------------------------------------
    bool checkInterrupt(uint8_t pin);

    // -----------------------------------------------------------------------------
    // configClock(uint8_t oscSource, uint8_t oscPinFunction, uint8_t oscFreqOut, uint8_t oscDivider)
    //		This function configures the oscillator source/speed
    //		and the clock, which is used to drive LEDs and time debounces.
    //
    //	Inputs:
    //	- oscSource: Choose either internal 2MHz oscillator or an external signal
    //		applied to the OSCIO pin.
    //		- INTERNAL_CLOCK and EXTERNAL_CLOCK are defined in the header file.
    //			Use those.
    //		- This value defaults to internal.
    //	- oscDivider: Sets the clock divider in REG_MISC.
    //		- ClkX = fOSC / (2^(RegMisc[6:4] -1))
    //		- This value defaults to 1.
    //	- oscPinFunction: Allows you to set OSCIO as an input or output.
    //		- You can use Arduino's INPUT, OUTPUT defines for this value
    //		- This value defaults to input
    //	- oscFreqOut: If oscio is configured as an output, this will set the output
    //		frequency
    //		- This should be a 4-bit value. 0=0%, 0xF=100%, else
    //			fOSCOut = FOSC / (2^(RegClock[3:0]-1))
    //		- This value defaults to 0.
    // -----------------------------------------------------------------------------
    void configClock(uint8_t oscSource = 2, uint8_t oscPinFunction = 0, uint8_t oscFreqOut = 0, uint8_t oscDivider = 1); // Legacy, use clock();

    // -----------------------------------------------------------------------------
    // clock(uint8_t oscSource, uint8_t oscDivider, uint8_t oscPinFunction, uint8_t oscFreqOut)
    //		This function configures the oscillator source/speed
    //		and the clock, which is used to drive LEDs and time debounces.
    //  	This is just configClock in a bit more sane order.
    //
    // -----------------------------------------------------------------------------
    void clock(uint8_t oscSource = 2, uint8_t oscDivider = 1, uint8_t oscPinFunction = 0, uint8_t oscFreqOut = 0);
};

#endif // SX1508_library_H
