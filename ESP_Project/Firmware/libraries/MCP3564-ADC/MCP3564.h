#ifndef MCP3564_h
#define MCP3564_h

#include <Arduino.h>

// 8_ADC = CH0 - CH1, 9_ADC = CH3-CH2
// 0xB40000 at 2.7V : Max ADC Value
// 0x800000 at 2.0V
// 0x600000 at 1.5V

// USEFUL MASKS FOR ADC COMMUNICATION
#define DATA_READY_MASK 0b00000100 // Tells us whether data is ready from an SPI transaction
#define REG_ADDRESS_MASK 0b00011100

// USEFUL FAST COMMANDS AND OTHER COMMANDS
// Resets the device registers to their default  values
#define DEVICE_RESET_COMMAND 0b01111000

#define COMMAND_ADDR_POS 2
#define START_COMMAND 0b01101000  // ADC conversion start/restart fast command
#define SREAD_COMMAND 0b01000001  // Static read of register address
#define WRITE_COMMAND 0b01000010  // Write command
#define IREAD_COMMAND 0b01000111  // Incremental read from 0x01 address(CONFIG0)

#define CONFIG0_ADDR 0x01
#define CONFIG0_WRITE (CONFIG0_ADDR << COMMAND_ADDR_POS) | WRITE_COMMAND
#define CONFIG0_REG_MASK 0b00000000
#define CONFIG0_CLK_SEL_INT 0b00110000
#define CONFIG0_CLK_SEL_EXT 0b00000000
#define CONFIG0_ADC_MODE_CONV 0b00000011
#define CONFIG0_ADC_MODE_SHUTDOWN 0b00000000

#define CONFIG1_ADDR 0x02
#define CONFIG1_WRITE (CONFIG1_ADDR << COMMAND_ADDR_POS) | WRITE_COMMAND
#define CONFIG1_REG_MASK 0b00000000
#define CONFIG1_OSR_32 0b00000000
#define CONFIG1_OSR_256 0b00001100

#define CONFIG2_ADDR 0x03
#define CONFIG2_WRITE (CONFIG2_ADDR << COMMAND_ADDR_POS) | WRITE_COMMAND
#define CONFIG2_REG_MASK 0b10001011

#define CONFIG3_ADDR 0x04
#define CONFIG3_WRITE (CONFIG3_ADDR << COMMAND_ADDR_POS) | WRITE_COMMAND
#define CONFIG3_REG_MASK 0b11110000

#define IRQ_ADDR 0x05
#define IRQ_WRITE (IRQ_ADDR << COMMAND_ADDR_POS) | WRITE_COMMAND
#define IRQ_REG_MASK 0b00000010

#define SCAN_ADDR 0x07
#define SCAN_WRITE (SCAN_ADDR << COMMAND_ADDR_POS) | WRITE_COMMAND

#define SCAN_REG_MASK0 0b00000000
#define SCAN_REG_MASK1 0b00000011  //CHO-1 Diff, CH2-3 Diff Sel, SooSan
#define SCAN_REG_MASK2 0b00000000

#define SCAN_REG_MASK0_YJ 0b00000101  //CHO, CH2 Sel, YoungJin
#define SCAN_REG_MASK1_YJ 0b00000000
#define SCAN_REG_MASK2_YJ 0b00000000

#define TIMER_ADDR 0x08
#define TIMER_WRITE (TIMER_ADDR << COMMAND_ADDR_POS) | WRITE_COMMAND
#define TIMER_REG_MASK0 0x00
#define TIMER_REG_MASK1 0x00
#define TIMER_REG_MASK2 0x00

#define ADC_INT 35  // data ready interrupt pin. LOW = data ready.
#define ADC_CS 32
//#define MAX_SYNCHRONIZATION_POINTS 5000

class MCP3564 {
  public: 
    MCP3564();
    void readRegisters(void);
    bool verifyRegisters(void);
    void startConversion(void);
    void writeRegisterDiffSync(void);
    void writeRegisterSyncYJ(void);
    void printRegisters(void);
    void Reset(void);
    void ResetYJ(void);
    
    void readADCData(void);
    void recordSync(void);

    uint32_t data_counter;
    uint32_t data_points_to_sample;
    uint8_t adc_data[4];
    uint8_t adc_ch;
    uint32_t adc_sample;
//    uint32_t synchronization_data[MAX_SYNCHRONIZATION_POINTS];
//  uint32_t synchronization_counter;

    uint8_t config0_data;
    uint8_t config1_data;
    uint8_t config2_data;
    uint8_t config3_data;
    uint8_t irq_data;
    uint8_t mux_data;
    uint32_t scan_data; // A 24-bit register
    uint32_t timer_data; // A 24-bit register
    uint32_t offsetcal_data; // A 24-bit register
    uint32_t gaincal_data; // A 24-bit register
    uint32_t reserved_1_data;
    uint8_t reserved_2_data;
    uint8_t lock_data;
    uint16_t reserved_3_data;
    uint16_t crccfg_data;
    
    bool config0_ok = false; 
    bool config1_ok = false;
    bool config2_ok = false;
    bool config3_ok = false;
    bool irq_ok = false;
    bool mux_ok = false;
    bool scan_ok = false;
    bool timer_ok = false;
    bool offsetcal_ok = false;
    bool gaincal_ok = false;
    bool reserved1_ok = false;
    bool reserved2_ok = false;
    bool lock_ok = false;
    bool reserved3_ok = false;
    bool crccfg_ok = false;
};

#endif