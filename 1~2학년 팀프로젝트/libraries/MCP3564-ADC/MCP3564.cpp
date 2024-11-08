#include <MCP3564.h>
#include <SPI.h>

MCP3564::MCP3564()
{
}

void MCP3564::writeRegisterDiffSync(void) 
{
  byte command_byte = 0;
  byte data_byte = 0;
  
  command_byte = CONFIG0_WRITE;
  data_byte = CONFIG0_REG_MASK | CONFIG0_CLK_SEL_INT;
  data_byte |= CONFIG0_ADC_MODE_CONV;
  digitalWrite(ADC_CS, LOW);
  SPI.transfer(command_byte);
  SPI.transfer(data_byte);
  digitalWrite(ADC_CS, HIGH);
  delay(10);

  command_byte = CONFIG1_WRITE;
  data_byte = CONFIG1_REG_MASK | CONFIG1_OSR_32;
  digitalWrite(ADC_CS, LOW);
  SPI.transfer(command_byte);
  SPI.transfer(data_byte);
  digitalWrite(ADC_CS, HIGH);
  delay(10);

  command_byte = CONFIG2_WRITE;
  data_byte = CONFIG2_REG_MASK;
  digitalWrite(ADC_CS, LOW);
  SPI.transfer(command_byte);
  SPI.transfer(data_byte);
  digitalWrite(ADC_CS, HIGH);
  delay(10);

  command_byte = CONFIG3_WRITE;
  data_byte = CONFIG3_REG_MASK;
  digitalWrite(ADC_CS, LOW);
  SPI.transfer(command_byte);
  SPI.transfer(data_byte);
  digitalWrite(ADC_CS, HIGH);
  delay(10);

  command_byte = IRQ_WRITE;
  data_byte = IRQ_REG_MASK;
  digitalWrite(ADC_CS, LOW);
  SPI.transfer(command_byte);
  SPI.transfer(data_byte);
  digitalWrite(ADC_CS, HIGH);
  delay(10);

  command_byte = SCAN_WRITE;
  digitalWrite(ADC_CS, LOW);
  SPI.transfer(command_byte);
  data_byte = SCAN_REG_MASK2;  
  SPI.transfer(data_byte);
  data_byte = SCAN_REG_MASK1;  
  SPI.transfer(data_byte);
  data_byte = SCAN_REG_MASK0;  
  SPI.transfer(data_byte);
  digitalWrite(ADC_CS, HIGH);

  command_byte = TIMER_WRITE;
  digitalWrite(ADC_CS, LOW);
  SPI.transfer(command_byte);
  data_byte = TIMER_REG_MASK2;  
  SPI.transfer(data_byte);
  data_byte = TIMER_REG_MASK1;  
  SPI.transfer(data_byte);
  data_byte = TIMER_REG_MASK0;  
  SPI.transfer(data_byte);
  digitalWrite(ADC_CS, HIGH);
  delay(10);
}

void MCP3564::writeRegisterSyncYJ(void) 
{
  byte command_byte = 0;
  byte data_byte = 0;
  
  command_byte = CONFIG0_WRITE;
  data_byte = CONFIG0_REG_MASK | CONFIG0_CLK_SEL_INT;
  data_byte |= CONFIG0_ADC_MODE_CONV;
  digitalWrite(ADC_CS, LOW);
  SPI.transfer(command_byte);
  SPI.transfer(data_byte);
  digitalWrite(ADC_CS, HIGH);
  delay(10);

  command_byte = CONFIG1_WRITE;
  data_byte = CONFIG1_REG_MASK | CONFIG1_OSR_32;
  digitalWrite(ADC_CS, LOW);
  SPI.transfer(command_byte);
  SPI.transfer(data_byte);
  digitalWrite(ADC_CS, HIGH);
  delay(10);

  command_byte = CONFIG2_WRITE;
  data_byte = CONFIG2_REG_MASK;
  digitalWrite(ADC_CS, LOW);
  SPI.transfer(command_byte);
  SPI.transfer(data_byte);
  digitalWrite(ADC_CS, HIGH);
  delay(10);

  command_byte = CONFIG3_WRITE;
  data_byte = CONFIG3_REG_MASK;
  digitalWrite(ADC_CS, LOW);
  SPI.transfer(command_byte);
  SPI.transfer(data_byte);
  digitalWrite(ADC_CS, HIGH);
  delay(10);

  command_byte = IRQ_WRITE;
  data_byte = IRQ_REG_MASK;
  digitalWrite(ADC_CS, LOW);
  SPI.transfer(command_byte);
  SPI.transfer(data_byte);
  digitalWrite(ADC_CS, HIGH);
  delay(10);

  command_byte = SCAN_WRITE;
  digitalWrite(ADC_CS, LOW);
  SPI.transfer(command_byte);
  data_byte = SCAN_REG_MASK2_YJ;  
  SPI.transfer(data_byte);
  data_byte = SCAN_REG_MASK1_YJ;  
  SPI.transfer(data_byte);
  data_byte = SCAN_REG_MASK0_YJ;  
  SPI.transfer(data_byte);
  digitalWrite(ADC_CS, HIGH);

  command_byte = TIMER_WRITE;
  digitalWrite(ADC_CS, LOW);
  SPI.transfer(command_byte);
  data_byte = TIMER_REG_MASK2;  
  SPI.transfer(data_byte);
  data_byte = TIMER_REG_MASK1;  
  SPI.transfer(data_byte);
  data_byte = TIMER_REG_MASK0;  
  SPI.transfer(data_byte);
  digitalWrite(ADC_CS, HIGH);
  delay(10);
}

void MCP3564::Reset(void) 
{
  //synchronization_counter = 0;
  data_counter = 0;
  data_points_to_sample = 5000;

  readRegisters();
  if(verifyRegisters() == false)
  {
    writeRegisterDiffSync();
    readRegisters();
    printRegisters();
  }
  startConversion();
}

void MCP3564::ResetYJ(void) 
{
  //synchronization_counter = 0;
  data_counter = 0;
  data_points_to_sample = 5000;

  readRegisters();
  if(verifyRegisters() == false)
  {
    writeRegisterSyncYJ();
    readRegisters();
    printRegisters();
  }
  startConversion();
}

void MCP3564::readRegisters(void) 
{
  digitalWrite(ADC_CS, LOW);
  SPI.transfer(IREAD_COMMAND);
  config0_data = SPI.transfer(0);
  config1_data = SPI.transfer(0);
  config2_data = SPI.transfer(0);
  config3_data = SPI.transfer(0);
  irq_data = SPI.transfer(0);
  irq_data &= 0x0F;
  mux_data = SPI.transfer(0);
  byte temp2 = SPI.transfer(0);
  byte temp1 = SPI.transfer(0);
  byte temp0 = SPI.transfer(0);
  scan_data = (temp2 << 16) | (temp1 << 8) | temp0;
  temp2 = SPI.transfer(0);
  temp1 = SPI.transfer(0);
  temp0 = SPI.transfer(0);
  timer_data = (temp2 << 16) | (temp1 << 8) | temp0;
  temp2 = SPI.transfer(0);
  temp1 = SPI.transfer(0);
  temp0 = SPI.transfer(0);
  offsetcal_data =  (temp2 << 16) | (temp1 << 8) | temp0;
  temp2 = SPI.transfer(0);
  temp1 = SPI.transfer(0);
  temp0 = SPI.transfer(0);
  gaincal_data = (temp2 << 16) | (temp1 << 8) | temp0;
  temp2 = SPI.transfer(0);
  temp1 = SPI.transfer(0);
  temp0 = SPI.transfer(0);
  reserved_1_data = (temp2 << 16) | (temp1 << 8) | temp0;
  reserved_2_data = SPI.transfer(0);
  lock_data = SPI.transfer(0);
  temp1 = SPI.transfer(0);
  temp0 = SPI.transfer(0);
  reserved_3_data = (temp1 << 8) | temp0;
  temp1 = SPI.transfer(0);
  temp0 = SPI.transfer(0);
  crccfg_data = (temp1 << 8) | temp0;
  digitalWrite(ADC_CS, HIGH);
  delay(10);
}

void MCP3564::startConversion(void)
{
  digitalWrite(ADC_CS, LOW);
  SPI.transfer(START_COMMAND);
  digitalWrite(ADC_CS, HIGH);
  delay(10);
}

// PARTIALLY COMPLETE. DOES NOT VERIFY ALL REGISTERS.
bool MCP3564::verifyRegisters(void) 
{
  if(config0_data == 0b00110011) config0_ok = true;
  if(config1_data == 0b00000000) config1_ok = true;
  if(config2_data == 0b10001011) config2_ok = true;
  if(config3_data == 0b11110000) config3_ok = true;
  if(irq_data == 0b00000010) irq_ok = true;

  bool all_ok = config0_ok && config1_ok && config2_ok && config3_ok && irq_ok;

  if(all_ok == true) {
    Serial.print("\r\nALL REGISTERS OK.");
    return true;
  }
  Serial.print("\r\nSOME REGISTER NOT OK. REGISTER TABLE:");
  return false;
}

void MCP3564::printRegisters(void) 
{
  Serial.print("CONFIG0: ");
  Serial.println(config0_data, BIN);
  Serial.print("CONFIG1: ");
  Serial.println(config1_data, BIN);
  Serial.print("CONFIG2: ");
  Serial.println(config2_data, BIN);
  Serial.print("CONFIG3: ");
  Serial.println(config3_data, BIN);
  Serial.print("IRQ: ");
  Serial.println(irq_data, BIN);
  Serial.print("MUX: ");
  Serial.println(mux_data, BIN);
  Serial.print("SCAN: ");
  Serial.println(scan_data, BIN);
  Serial.print("TIMER: ");
  Serial.println(timer_data, BIN);
  Serial.print("OFFSETCAL: ");
  Serial.println(offsetcal_data, BIN);
  Serial.print("GAINCAL: ");
  Serial.println(gaincal_data, BIN);
  Serial.print("RESERVED1: ");
  Serial.println(reserved_1_data, HEX);
  Serial.print("RESERVED2: ");
  Serial.println(reserved_2_data, HEX);
  Serial.print("LOCK: ");
  Serial.println(lock_data, BIN);
  Serial.print("RESERVED3: ");
  Serial.println(reserved_3_data, HEX);
  Serial.print("CRCCFG: ");
  Serial.println(crccfg_data, BIN);
  Serial.println("-----------------------------");
}

/*
void MCP3564::readADCData(void) 
{
  //Serial.print("Data Read Interrupt Activated. data_counter: ");
  //Serial.print(data_counter);
  //Serial.print("/");
  //Serial.println(Mdata_points_to_sample);
  if(data_counter < data_points_to_sample) 
  {
    digitalWrite(ADC_CS, LOW);
    SPI.transfer(SREAD_COMMAND);
    adc_data[3] = SPI.transfer(0);
    adc_data[2] = SPI.transfer(0);
    adc_data[1] = SPI.transfer(0);
    adc_data[0] = SPI.transfer(0);
    adc_sample = (adc_data[2] << 16) | (adc_data[1] << 8) | (adc_data[0]);
    digitalWrite(ADC_CS, HIGH);
    //Serial.write(adc_data, 3);
    //Serial.printf("\r%02X %d %d ",adc_data[3], adc_sample, data_counter);
    data_counter += 1;
  }
  else {
    //Serial.println("Read Complete. Detatching Interrupts.");
    Serial.printf("\r%02X %06X %d ",adc_data[3], adc_sample, data_counter);
    data_counter = 0;
    //detachInterrupt(digitalPinToInterrupt(ADC_INT));
  }
}
*/

void MCP3564::readADCData(void) 
{
  digitalWrite(ADC_CS, LOW);
  SPI.transfer(SREAD_COMMAND);
  adc_data[3] = SPI.transfer(0);
  adc_data[2] = SPI.transfer(0);
  adc_data[1] = SPI.transfer(0);
  adc_data[0] = SPI.transfer(0);
  //adc_sample = (adc_data[2] << 16) | (adc_data[1] << 8) | (adc_data[0]);
  adc_sample = (adc_data[2] << 12) | adc_data[1]<<4 | (adc_data[0]>>4);
  adc_ch = (adc_data[3] & 0xF0)>>4;
  digitalWrite(ADC_CS, HIGH);
}

void MCP3564::recordSync() 
{
  //synchronization_data[synchronization_counter] = data_counter;
  //synchronization_counter += 1;
}
