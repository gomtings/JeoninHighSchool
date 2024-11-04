/*
	Remeber to upload the data directory to your board!
	
	Serial baud rate in this example is 9600
*/

#include "FS.h"

#include <SPIFFSIniFile.h>

void printErrorMessage(uint8_t e, bool eol = true)
{
  switch (e) {
  case SPIFFSIniFile::errorNoError:
    Serial.print("no error");
    break;
  case SPIFFSIniFile::errorFileNotFound:
    Serial.print("file not found");
    break;
  case SPIFFSIniFile::errorFileNotOpen:
    Serial.print("file not open");
    break;
  case SPIFFSIniFile::errorBufferTooSmall:
    Serial.print("buffer too small");
    break;
  case SPIFFSIniFile::errorSeekError:
    Serial.print("seek error");
    break;
  case SPIFFSIniFile::errorSectionNotFound:
    Serial.print("section not found");
    break;
  case SPIFFSIniFile::errorKeyNotFound:
    Serial.print("key not found");
    break;
  case SPIFFSIniFile::errorEndOfFile:
    Serial.print("end of file");
    break;
  case SPIFFSIniFile::errorUnknownError:
    Serial.print("unknown error");
    break;
  default:
    Serial.print("unknown error value");
    break;
  }
  if (eol)
    Serial.println();
}

void setup()
{
  
  const size_t bufferLen = 80;
  char buffer[bufferLen];

  const char *filename = "/net.ini";
  Serial.begin(9600);
  
  //Mount the SPIFFS  
  if (!SPIFFS.begin())
    while (1)
      Serial.println("SPIFFS.begin() failed");
  
  SPIFFSIniFile ini(filename);
  if (!ini.open()) {
    Serial.print("Ini file ");
    Serial.print(filename);
    Serial.println(" does not exist");
    // Cannot do anything else
    while (1)
      ;
  }
  Serial.println("Ini file exists");

  // Check the file is valid. This can be used to warn if any lines
  // are longer than the buffer.
  if (!ini.validate(buffer, bufferLen)) {
    Serial.print("ini file ");
    Serial.print(ini.getFilename());
    Serial.print(" not valid: ");
    printErrorMessage(ini.getError());
    // Cannot do anything else
    while (1)
      ;
  }
  
  // Fetch a value from a key which is present
  if (ini.getValue("network", "mac", buffer, bufferLen)) {
    Serial.print("section 'network' has an entry 'mac' with value ");
    Serial.println(buffer);
  }
  else {
    Serial.print("Could not read 'mac' from section 'network', error was ");
    printErrorMessage(ini.getError());
  }
  
  // Try fetching a value from a missing key (but section is present)
  if (ini.getValue("network", "nosuchkey", buffer, bufferLen)) {
    Serial.print("section 'network' has an entry 'nosuchkey' with value ");
    Serial.println(buffer);
  }
  else {
    Serial.print("Could not read 'nosuchkey' from section 'network', error was ");
    printErrorMessage(ini.getError());
  }
  
  // Try fetching a key from a section which is not present
  if (ini.getValue("nosuchsection", "nosuchkey", buffer, bufferLen)) {
    Serial.print("section 'nosuchsection' has an entry 'nosuchkey' with value ");
    Serial.println(buffer);
  }
  else {
    Serial.print("Could not read 'nosuchkey' from section 'nosuchsection', error was ");
    printErrorMessage(ini.getError());
  }

  // Fetch a boolean value
  bool allowPut; // variable where result will be stored
  bool found = ini.getValue("/upload", "allow put", buffer, bufferLen, allowPut);
  if (found) {
    Serial.print("The value of 'allow put' in section '/upload' is ");
    // Print value, converting boolean to a string
    Serial.println(allowPut ? "TRUE" : "FALSE");
  }
  else {
    Serial.print("Could not get the value of 'allow put' in section '/upload': ");
    printErrorMessage(ini.getError());
  }
}


void loop()
{


}
