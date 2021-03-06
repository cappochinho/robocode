#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_ADXL345_U.h>
#include "ITG3200.h"

/* Assign a unique ID to this sensor at the same time */
Adafruit_ADXL345_Unified accel = Adafruit_ADXL345_Unified(12345);
ITG3200 gyro;

char transmitting = 'N';

void setup(void) 
{
  Serial.begin(9600);
  
  /* Initialise the sensor */
  if(!accel.begin())
  {
    /* There was a problem detecting the ADXL345 ... check your connections */
    Serial.println("{\"err\": \"Ooops, no ADXL345 detected ... Check your wiring!\"}");
    while(1);
  }

  /* Set the range to whatever is appropriate for your project */
  accel.setRange(ADXL345_RANGE_16_G);

  gyro.init();
  gyro.zeroCalibrate(200,10);//sample 200 times to calibrate and it will take 200*10ms
}

void loop(void) 
{
  /* Get a new sensor event */ 
  if (Serial.available())
  {
    char str = Serial.read();
    if (str == 'Y')
      transmitting = 'Y';
    else if (str == 'N')
      transmitting = 'N';
    Serial.println(transmitting);
  }
  if (transmitting == 'Y')
  {
    sensors_event_t event; 
    accel.getEvent(&event);
    float ax,ay,az;
    gyro.getAngularVelocity(&ax,&ay,&az);
    
    /* Display the results (acceleration is measured in m/s^2) */
    Serial.print("{\"acc_x\":"); Serial.print(event.acceleration.x); Serial.print(','); Serial.print("\"acc_y\":"); Serial.print(event.acceleration.y); Serial.print(','); Serial.print("\"acc_z\":"); Serial.print(event.acceleration.z);
    Serial.print(','); Serial.print("\"gyr_x\":"); Serial.print(ax); Serial.print(','); Serial.print("\"gyr_y\":"); Serial.print(ay); Serial.print(','); Serial.print("\"gyr_z\":"); Serial.print(az); Serial.println('}');
    delay(25);
  }
}