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

	delay(100);
}
