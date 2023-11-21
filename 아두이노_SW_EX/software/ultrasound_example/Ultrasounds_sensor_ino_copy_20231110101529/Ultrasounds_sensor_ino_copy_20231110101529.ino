// 초음파 센서 핀 설정
const int trigPin = 12;
const int echoPin = 13;

long duration;
int distance;

void setup() {
  Serial.begin(9600);

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
}

void loop() {
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  duration = pulseIn(echoPin, HIGH);

  // distance = duration * 0.0343 / 2;
  distance = duration * 17 / 1000; 

  Serial.println(distance);

  delay(100);
}
