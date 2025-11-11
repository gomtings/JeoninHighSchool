/*

  Generics based example of rBASE64 Library

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

rBase64generic<250> mybase64;

void setup() {
  Serial.begin(115200);
}

void loop() {
  if (mybase64.encode("There is an electric fire in human nature tending to purify - so that among these human creatures there is  continually some birth of new heroism. The pity is that we must wonder at it, as we should at finding a pearl in rubbish.")
      == RBASE64_STATUS_OK) {
    Serial.println("\nConverted the String to Base64 : ");
    Serial.println(mybase64.result());
  }

  if (mybase64.decode("VGhlcmUgaXMgYW4gZWxlY3RyaWMgZmlyZSBpbiBodW1hbiBuYXR1cmUgdGVuZGluZyB0byBwdXJpZnkgLSBzbyB0aGF0IGFtb25nIHRoZXNlIGh1bWFuIGNyZWF0dXJlcyB0aGVyZSBpcyAgY29udGludWFsbHkgc29tZSBiaXJ0aCBvZiBuZXcgaGVyb2lzbS4gVGhlIHBpdHkgaXMgdGhhdCB3ZSBtdXN0IHdvbmRlciBhdCBpdCwgYXMgd2Ugc2hvdWxkIGF0IGZpbmRpbmcgYSBwZWFybCBpbiBydWJiaXNoLg==")
      == RBASE64_STATUS_OK) {
    Serial.println("\nConverted the String from Base64 : ");
    Serial.println(mybase64.result());
  }
  delay(2000);
}