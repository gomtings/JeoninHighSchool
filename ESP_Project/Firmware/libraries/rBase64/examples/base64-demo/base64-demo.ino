/*

  Easy to Use example of rBASE64 Library

  This example shows the calling convention for the various functions.

  For more information about this library please visit us at
  http://github.com/boseji/BASE64

  Created by Abhijit Bose (boseji) on 22/02/16.
  Copyright 2016 - Under creative commons license 3.0:
        Attribution-ShareAlike CC BY-SA

  @version API 1.1.0
  @author boseji - salearj@hotmail.com

*/

#include <rBase64.h>

void setup() {
  Serial.begin(115200);
}

void loop() {
  if (rbase64.encode("Hello There, I am doing Good.") == RBASE64_STATUS_OK) {
    Serial.println("\nConverted the String to Base64 : ");
    Serial.println(rbase64.result());
  }

  if (rbase64.decode("SGVsbG8gVGhlcmUsIEkgYW0gZG9pbmcgR29vZC4=") == RBASE64_STATUS_OK ) {
    Serial.println("\nConverted the String from Base64 : ");
    Serial.println(rbase64.result());
  }
  delay(2000);
}