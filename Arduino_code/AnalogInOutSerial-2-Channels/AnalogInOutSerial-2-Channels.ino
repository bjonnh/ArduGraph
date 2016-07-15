/*
  Analog input, analog output, serial output

  Reads an analog input pin, maps the result to a range from 0 to 255
  and uses the result to set the pulsewidth modulation (PWM) of an output pin.
  Also prints the results to the serial monitor.

  The circuit:
   potentiometer connected to analog pin 0.
   Center pin of the potentiometer goes to the analog pin.
   side pins of the potentiometer go to +5V and ground
   LED connected from digital pin 9 to ground

  created 29 Dec. 2008
  modified 9 Apr 2012
  by Tom Igoe

  This example code is in the public domain.

*/

// These constants won't change.  They're used to give names
// to the pins used:
const int analogInPin = A0;  // Analog input pin that the potentiometer is attached to
const int analogInPin2 = A1;  // Analog input pin that the potentiometer is attached to

int sensorValue = 0;        // value read from the pot
int sensorValue2 = 0;        // value read from the pot
float dgh_1 = 0;
float dgh_2 = 0;
void setup() {
  // initialize serial communications at 9600 bps:
  Serial.begin(9600);
  Serial3.begin(9600, SERIAL_8N1);
}
char buffer[64];

float get_value_from_dgh(char* id) {
  char command[4];
  sprintf(command,"$%sRD",id);
Serial3.print(command);
  Serial3.write(13);
  Serial3.write(0);
  delay(100);
  int i = 0;
  for (int j=0;j<=63;j++) {
    buffer[j]=0;
  }
  while (Serial3.available() > 0) {
    // read the incoming byte:
    buffer[i] = Serial3.read();
    if (i==6) {
    if (strncmp(buffer,command,4)==0) {
      i=-1;
    }
    }
    i++;
  }
  return atof(buffer);
}

void loop() {
  dgh_1 = get_value_from_dgh((char *) "1");
  dgh_2 = get_value_from_dgh((char *) "2");
  Serial.print(dgh_1);
  Serial.print(",");
  Serial.println(dgh_2);
  
  
  // read the analog in value:
  //sensorValue = analogRead(analogInPin);
  //sensorValue2 = analogRead(analogInPin2);

  // print the results to the serial monitor:
  //Serial.print(sensorValue);
  //Serial.print(",");
  //Serial.println(sensorValue2);

  // wait 2 milliseconds before the next loop
  // for the analog-to-digital converter to settle
  // after the last reading:
  delay(100);
}
