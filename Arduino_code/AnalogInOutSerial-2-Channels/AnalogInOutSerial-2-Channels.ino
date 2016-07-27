// These constants won't change.  They're used to give names
// to the pins used:
const int analogInPin = A0;  // Analog input pin that the potentiometer is attached to
const int analogInPin2 = A1;  // Analog input pin that the potentiometer is attached to

int sensorValue = 0;        // value read from the pot
int sensorValue2 = 0;        // value read from the pot

void setup() {
	Serial.begin(9600);
}

void loop() {
	
	sensorValue = analogRead(analogInPin);
	sensorValue2 = analogRead(analogInPin2);
	
	Serial.print(sensorValue);
	Serial.print(",");
	Serial.println(sensorValue2);
	
	delay(100);
}
