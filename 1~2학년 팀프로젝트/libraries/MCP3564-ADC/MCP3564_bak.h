#ifndef MCP3564_h
#define MCP3564_h

#define DEVICE_ADDRESS 0b01
#define DEVICE_ADDRESS_MASK (DEVICE_ADDRESS << 6)
#define COMMAND_ADDR_POS 2

// USEFUL MASKS FOR ADC COMMUNICATION
#define DATA_READY_MASK 0b00000100 // Tells us whether data is ready from an SPI transaction
#define ADDRESS_MASK 0b00111000
#define WRITE_COMMAND_MASK 0b00000010
#define WRITE_COMMAND WRITE_COMMAND_MASK | DEVICE_ADDRESS_MASK
#define IREAD_COMMAND_MASK 0b00000011 // Incremental read command
#define IREAD_COMMAND IREAD_COMMAND_MASK | DEVICE_ADDRESS_MASK
#define SREAD_COMMAND_MASK 0b1 // Static read command
#define SREAD_DATA_COMMAND SREAD_COMMAND_MASK | DEVICE_ADDRESS_MASK

#define CONFIG0_ADDR 0x01
#define CONFIG0_WRITE (CONFIG0_ADDR << COMMAND_ADDR_POS) | WRITE_COMMAND
#define CONFIG0_CLK_SEL_MASK 0b00110000
#define CONFIG0_CLK_SEL_POS 4
#define CONFIG0_CLK_SEL_INT 0b11 << CONFIG0_CLK_SEL_POS
#define CONFIG0_CLK_SEL_EXT 0b00 << CONFIG0_CLK_SEL_POS
#define CONFIG0_ADC_MODE_POS 0
#define CONFIG0_ADC_MODE_CONV 0b11 << CONFIG0_ADC_MODE_POS

#define CONFIG1_ADDR 0x02
#define CONFIG1_WRITE (CONFIG1_ADDR << COMMAND_ADDR_POS) | WRITE_COMMAND
#define CONFIG1_OSR_POS 2
#define CONFIG1_OSR_32 0b0000 << CONFIG1_OSR_POS
#define CONFIG1_OSR_256 0b0011 << CONFIG1_OSR_POS

#define CONFIG3_ADDR 0x04
#define CONFIG3_WRITE (CONFIG3_ADDR << COMMAND_ADDR_POS) | WRITE_COMMAND
#define CONFIG3_CONV_MODE_POS 6
#define CONFIG3_CONV_MODE_CONTINUOUS 0b11 << CONFIG3_CONV_MODE_POS

#define IRQ_ADDR 0x05
#define IRQ_WRITE (IRQ_ADDR << COMMAND_ADDR_POS) | WRITE_COMMAND
#define IRQ_MODE_POS 2
#define IRQ_MODE_HIGH 0b01110111

#define CS_PIN 9
#define IRQ_PIN 8 // data ready interrupt pin. HIGH = data ready. LOW = data not ready.
#define MCLK_PIN 7
#define MISO_PIN 12
#define EXTERNAL_SYNC_PIN 5
#define MAX_SYNCHRONIZATION_POINTS 5000

// USEFUL FAST COMMANDS AND OTHER COMMANDS
// Resets the device registers to their default  values
#define DEVICE_RESET_COMMAND DEVICE_ADDRESS_BYTE | 0b111000

class MCP3564 {
  public: 
    // Class methods
    void readRegisters(void);
    void verifyRegisters(void);
    void writeRegisterDefaults(void);
    void writeRegisterDiffSync(void);
    void printRegisters(void);
    void Reset(void);
    static void readADCData(void);
    static void recordSync(void);

    // Static class variables used in interrupts
    static uint32_t data_counter;
    static uint32_t data_points_to_sample;
    static byte adc_data[3];
    static uint32_t adc_sample;
    static uint32_t synchronization_data[MAX_SYNCHRONIZATION_POINTS];
    static uint32_t synchronization_counter;

    // Class variables
    byte config0_data;
    byte config1_data;
    byte config2_data;
    byte config3_data;
    byte irq_data;
    byte mux_data;
    uint32_t scan_data; // A 24-bit register
    uint32_t timer_data; // A 24-bit register
    uint32_t offsetcal_data; // A 24-bit register
    uint32_t gaincal_data; // A 24-bit register
    uint32_t reserved_1_data;
    byte reserved_2_data;
    byte lock_data;
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


uint32_t MCP3564::data_counter;
uint32_t MCP3564::data_points_to_sample = 1;
byte MCP3564::adc_data[3];
uint32_t MCP3564::adc_sample = 0;
uint32_t MCP3564::synchronization_data[MAX_SYNCHRONIZATION_POINTS];
uint32_t MCP3564::synchronization_counter = 0;

#endif