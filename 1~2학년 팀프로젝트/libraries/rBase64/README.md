# rBASE64 Library for Arduino

Real Base64 library is a speed optimized flexible implementations of BASE64
Encoding and Decoding logic.

There are native as well as object oriented functions.

## Example 1 : Using the Standard Object

***NOTE: Read the [Limitations](https://github.com/boseji/rBASE64#limitations) Carefully***

```c
#include <rBase64.h>

void setup() {
  Serial.begin(115200);
}

void loop() {

  rbase64.encode("Hello There, I am doing Good.");
  
  Serial.println(rbase64.result());
  
  rbase64.decode("SGVsbG8gVGhlcmUsIEkgYW0gZG9pbmcgR29vZC4=");
  
  Serial.println(rbase64.result());
  
  delay(2000);
}
```

## Example 2 : Using the Generic Class to create a special instance

```c
#include <rBase64.h>

rBase64generic<250> mybase64;

void setup() {
  Serial.begin(115200);
}

void loop() {
  mybase64.encode("There is an electric fire in human nature tending to purify - so that among these human creatures there is  continually some birth of new heroism. The pity is that we must wonder at it, as we should at finding a pearl in rubbish.");

  Serial.println(mybase64.result());
  mybase64.decode("VGhlcmUgaXMgYW4gZWxlY3RyaWMgZmlyZSBpbiBodW1hbiBuYXR1cmUgdGVuZGluZyB0byBwdXJpZnkgLSBzbyB0aGF0IGFtb25nIHRoZXNlIGh1bWFuIGNyZWF0dXJlcyB0aGVyZSBpcyAgY29udGludWFsbHkgc29tZSBiaXJ0aCBvZiBuZXcgaGVyb2lzbS4gVGhlIHBpdHkgaXMgdGhhdCB3ZSBtdXN0IHdvbmRlciBhdCBpdCwgYXMgd2Ugc2hvdWxkIGF0IGZpbmRpbmcgYSBwZWFybCBpbiBydWJiaXNoLg==");

  Serial.println(mybase64.result());

  delay(2000);
}
```

### Tip : How to test base64 in Python

At the Python terminal prompt (get this by executing `python.exe` on *Windows* or `python` on *Linux* terminal) :

```python
>>> import base64
>>> base64.b64encode("Hello There, I am doing Good.")
'SGVsbG8gVGhlcmUsIEkgYW0gZG9pbmcgR29vZC4='
>>> base64.b64decode("SGVsbG8gVGhlcmUsIEkgYW0gZG9pbmcgR29vZC4=")
'Hello There, I am doing Good.'
>>>
```

This way one can also verify other strings.

## API

### Native Implementation

Here is the List of the Native Functions for those who want more Control:

  - `size_t rbase64_encode(char *output, char *input, size_t inputLen)`

This function helps to Encode the Stream of Bytes provided at the *input* to *output*
User needs to ensure that that the Output buffer is adequacy sized.

  - `size_t rbase64_decode(char *output, char *input, size_t inputLen)`

This function helps to Decode the Stream ob Bytes provided at the *input* to *output*  
User needs to ensure that that the Output buffer is adequacy sized.

  - `size_t rbase64_enc_len(size_t inputLen)`
  
This function can be used to ascertain the maximum size of buffer needed to accommodate  
the converted BASE64 output 

  - `size_t rbase64_dec_len(char *input, size_t inputLen)`
  
This function can be used to find out the maximum size of the buffer needed to accommodate  
the converted original string from BASE64

### OO Default Implementation

*Note:* The default implementation uses the `rBase64generic<100>`.

Here is the List of the OO Function in `rbase64` object:

  - `size_t rbase64.encode(uint8_t *data, size_t length)` - For Direct byte Stream

  - `size_t rbase64.encode(const char *data)` - For NULL Terminated character Array as shown in the [**Example 1**](https://github.com/boseji/rBASE64#example-1--using-the-standard-object)
  
  - `size_t rbase64.encode(String text)` - String containing the source
  
Function to Convert into BASE64 encoded string else returns the Error Codes detailed below

  - `size_t rbase64.decode(uint8_t *data, size_t length)` - For Direct byte Stream
  
  - `size_t rbase64::decode(const char *data)` - For NULL Terminated character Array as shown in the [**Example 1**](https://github.com/boseji/rBASE64#example-1--using-the-standard-object)
  
  - `size_t rbase64::decode(String text)` - String containing the source
  
Function to Convert from BASE64 encoded string else returns the [Error Codes](https://github.com/boseji/rBASE64#error-codes) detailed below

The Result for all the above conversion function is received by:
  
  - `char * rbase64.result()`

### Error Codes

  - `RBASE64_STATUS_OK = 0` - If Every thing is alright.

  - `RABSE64_STATUS_SIZE = 1` - If there is buffer size overflow detected

### Macro

  - `RBASE64_ENC_SIZECALC(x)` this can be used to calculate the Constant size of array needed to store the string of size `x`


## Dependencies
 WString Library
 Thread Safe: No
 Extendable: Yes

**Note:** The API version 1.1.0 breaks backward compatibility. Please update accordingly. 

## Limitations

### OO Implementation Limits (`rbase64`):
  - Can't take Encoding strings more than "100 Characters".
  - Can't Decode the BASE64 strings beyond "136 Characters".
  - Memory usage is approximately 280Bytes in RAM.

### The **Native Implementation** & **C++ Generic implementation** (`rBase64generic`) has no such Limitations.

For more information about this library please view the code at
http://github.com/boseji/rBASE64


## License

<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0 International License</a>.

