#include <SoftwareSerial.h>
SoftwareSerial bluetooth(2, 3);
void setup() 
{
  pinMode(12,OUTPUT);
  digitalWrite(12,LOW);
  pinMode(11,OUTPUT);
  digitalWrite(11,LOW);
  Serial.begin(9600);
  bluetooth.begin(9600);
  String data;
  char buff[10];
  int cnt = 0;
  delay(100);
  bluetooth.print("AT");
  delay(1000);
  cnt = 0;
  while(bluetooth.available()) {
    char c = bluetooth.read();
    buff[cnt] = c;
    cnt ++;
  }
  buff[cnt] = '\0';
  data = buff;
  if(data == "OK"){
    digitalWrite(12,HIGH);
    delay(100);
    digitalWrite(12,LOW);
    Serial.println("yes");
  }else{
    digitalWrite(11,HIGH);
    while(1);
  }
  
  bluetooth.print("AT+ROLE=S");
  delay(1000);
  cnt = 0;
  while(bluetooth.available()) {
    char c = bluetooth.read();
    buff[cnt] = c;
    cnt ++;
  }
  buff[cnt] = '\0';
  data = buff;
  if(data == "OK+ROLE:S"){
    digitalWrite(12,HIGH);
    delay(100);
    digitalWrite(12,LOW);
    Serial.println("yes");
  }
  else{
    digitalWrite(11,HIGH);
    while(1);
  }
  
  bluetooth.print("AT+NAMEHC-06");
  delay(1000);
  cnt = 0;
  while(bluetooth.available()) {
    char c = bluetooth.read();
    buff[cnt] = c;
    cnt ++;
  }
  buff[cnt] = '\0';
  data = buff;
  if(data == "OKsetname"){
    digitalWrite(12,HIGH);
    delay(100);
    digitalWrite(12,LOW);
    Serial.println("yes");
  }
  else{
    digitalWrite(11,HIGH);
    while(1);
  }
  
  bluetooth.print("AT+PIN1234");
  delay(1000);
  cnt = 0;
  while(bluetooth.available()) {
    char c = bluetooth.read();
    buff[cnt] = c;
    cnt ++;
  }
  buff[cnt] = '\0';
  data = buff;
  if(data == "OKsetPIN"){
    digitalWrite(12,HIGH);
    delay(100);
    digitalWrite(12,LOW);
    Serial.println("yes");
  }else{
    digitalWrite(11,HIGH);
    while(1);
  }
}
void loop()
{
  digitalWrite(12,HIGH);
  delay(100);
  digitalWrite(12,LOW);
  delay(100);
}
