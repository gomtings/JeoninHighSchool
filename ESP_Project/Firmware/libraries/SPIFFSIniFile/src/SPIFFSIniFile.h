#ifndef _SPIFFSINIFILE_H
#define _SPIFFSINIFILE_H

#define SPIFFSINIFILE_VERSION "1.0.0"

// Maximum length for filename, excluding NULL char
#define SPIFFSINI_FILE_MAX_FILENAME_LEN 31

#include "FS.h"
#include "IPAddress.h"

class SPIFFSIniFileState;

class SPIFFSIniFile {
public:
	enum error_t {
		errorNoError = 0,
		errorFileNotFound,
		errorFileNotOpen,
		errorBufferTooSmall,
		errorSeekError,
		errorSectionNotFound,
		errorKeyNotFound,
		errorEndOfFile,
		errorUnknownError,
	};

	static const uint8_t maxFilenameLen;

	// Create an SPIFFSIniFile object. It isn't opened until open() is called on it.
	SPIFFSIniFile(const char* filename, char* mode = "r",
			bool caseSensitive = false);
	~SPIFFSIniFile();

	inline bool open(void); // Returns true if open succeeded
	inline void close(void);

	inline bool isOpen(void) const;

	inline error_t getError(void) const;
	inline void clearError(void) const;
	// Get the file mode (FILE_READ/FILE_WRITE)
	inline char* getMode(void) const;

	// Get the filename asscoiated with the ini file object
	inline const char* getFilename(void) const;

	bool validate(char* buffer, size_t len) const;

	// Get value from the file, but split into many short tasks. Return
	// value: false means continue, true means stop. Call getError() to
	// find out if any error
	bool getValue(const char* section, const char* key,
				  char* buffer, size_t len, SPIFFSIniFileState &state) const;

	// Get value, as one big task. Return = true means value is present
	// in buffer
	bool getValue(const char* section, const char* key,
				  char* buffer, size_t len) const;

	// Get the value as a string, storing the result in a new buffer
	// (not the working buffer)
	bool getValue(const char* section, const char* key,
				  char* buffer, size_t len, char *value, size_t vlen) const;

	// Get a boolean value
	bool getValue(const char* section, const char* key,
				  char* buffer, size_t len, bool& b) const;

	// Get an integer value
	bool getValue(const char* section, const char* key,
				  char* buffer, size_t len, int& val) const;

	// Get a uint16_t value
	bool getValue(const char* section, const char* key,
				  char* buffer, size_t len, uint16_t& val) const;

	// Get a long value
	bool getValue(const char* section, const char* key,
				  char* buffer, size_t len, long& val) const;

	bool getValue(const char* section, const char* key,
				  char* buffer, size_t len, unsigned long& val) const;

	// Get a float value
	bool getValue(const char* section, const char* key,
				  char* buffer, size_t len, float& val) const;

	bool getIPAddress(const char* section, const char* key,
					  char* buffer, size_t len, uint8_t* ip) const;

#if defined(ARDUINO) && ARDUINO >= 100
	bool getIPAddress(const char* section, const char* key,
					  char* buffer, size_t len, IPAddress& ip) const;
#endif

	bool getMACAddress(const char* section, const char* key,
					   char* buffer, size_t len, uint8_t mac[6]) const;

	// Utility function to read a line from a file, make available to all
	//static int8_t readLine(File &file, char *buffer, size_t len, uint32_t &pos);
	static error_t readLine(File &file, char *buffer, size_t len, uint32_t &pos);
	static bool isCommentChar(char c);
	static char* skipWhiteSpace(char* str);
	static void removeTrailingWhiteSpace(char* str);

	bool getCaseSensitive(void) const;
	void setCaseSensitive(bool cs);

protected:
	// True means stop looking, false means not yet found
	bool findSection(const char* section, char* buffer, size_t len,
					 SPIFFSIniFileState &state) const;
	bool findKey(const char* section, const char* key, char* buffer,
				 size_t len, char** keyptr, SPIFFSIniFileState &state) const;


private:
	char _filename[SPIFFSINI_FILE_MAX_FILENAME_LEN];
	char* _mode;
	mutable error_t _error;
	mutable File _file;
	bool _caseSensitive;
};

bool SPIFFSIniFile::open(void)
{
	if (_file)
		_file.close();
	_file = SPIFFS.open(_filename, _mode);
	if (isOpen()) {
		_error = errorNoError;
		return true;
	}
	else {
		_error = errorFileNotFound;
		return false;
	}
}

void SPIFFSIniFile::close(void)
{
	if (_file)
		_file.close();
}

bool SPIFFSIniFile::isOpen(void) const
{
	return (_file == true);
}

SPIFFSIniFile::error_t SPIFFSIniFile::getError(void) const
{
	return _error;
}

void SPIFFSIniFile::clearError(void) const
{
	_error = errorNoError;
}

char* SPIFFSIniFile::getMode(void) const
{
	return _mode;
}

const char* SPIFFSIniFile::getFilename(void) const
{
	return _filename;
}



class SPIFFSIniFileState {
public:
	SPIFFSIniFileState();

private:
	enum {funcUnset = 0,
		  funcFindSection,
		  funcFindKey,
	};

	uint32_t readLinePosition;
	uint8_t getValueState;

	friend class SPIFFSIniFile;
};


#endif

