int pwmValue = 0;

void setup() {
  Serial.begin(115200);
  pinMode(13, OUTPUT);  // PWM pin
}

void loop() {
  if (Serial.available()) {
    String data = Serial.readStringUntil('\n');
    pwmValue = data.toInt();

    // Apply PWM to LED
    analogWrite(13, pwmValue);
  }
}