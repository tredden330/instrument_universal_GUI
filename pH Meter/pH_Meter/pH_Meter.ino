
//states:
//1 = waiting for connection
//2 = spit out values
int state = 1;
int incomingByte = 0; // for incoming serial data

void setup() {
  Serial.begin(115200);
  pinMode(2,OUTPUT);
  digitalWrite(2, LOW);
}

void loop() {

  if (state == 1) {
    
    if (Serial.available() > 0) {
      // read the incoming byte:
      incomingByte = Serial.read();
      digitalWrite(2, HIGH);

      Serial.println("pH Meter");

      state = 2;
    }
  }

  if (state == 2) {
    digitalWrite(2, HIGH);
    int val = analogRead(34);
    Serial.println(val);
    delay(10);
  }
}