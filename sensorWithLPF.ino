#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_ADXL345_U.h>
#include "ITG3200.h"

/* Assign a unique ID to this sensor at the same time */
Adafruit_ADXL345_Unified accel = Adafruit_ADXL345_Unified(12345);
ITG3200 gyro;

const float alpha = 0.5;
double fXa = 0;
double fYa = 0;
double fZa = 0;
double fXg = 0;
double fYg = 0;
double fZg = 0;

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

    //Low Pass Filter
    fXa = (event.acceleration.x)* alpha + (fXa * (1.0 - alpha));
    fYa = (event.acceleration.y)* alpha + (fYa * (1.0 - alpha));
    fZa = (event.acceleration.z)* alpha + (fZa * (1.0 - alpha));
    fXg = ax * alpha + (fXg * (1.0 - alpha));
    fYg = ay * alpha + (fYg * (1.0 - alpha));
    fZg = az * alpha + (fZg * (1.0 - alpha));
    
    /* Display the results (acceleration is measured in m/s^2) */
    Serial.print("{\"acc_x\":"); Serial.print(fXa); Serial.print(','); Serial.print("\"acc_y\":"); Serial.print(fYa); Serial.print(','); Serial.print("\"acc_z\":"); Serial.print(fZa);
    Serial.print(','); Serial.print("\"gyr_x\":"); Serial.print(fXg); Serial.print(','); Serial.print("\"gyr_y\":"); Serial.print(fYg); Serial.print(','); Serial.print("\"gyr_z\":"); Serial.print(fZg); Serial.println('}');
    delay(25);
  }
}
