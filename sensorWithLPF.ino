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

    //converts accelerometer values to a value in G
    float Ax = event.acceleration.x * 0039;
    float Ay = event.acceleration.y * 0039;
    float Az = event.acceleration.z * 0039;
    
    //Low Pass Filter
    fXa = Ax * alpha + (fXa * (1.0 - alpha));
    fYa = Ay * alpha + (fYa * (1.0 - alpha));
    fZa = Az * alpha + (fZa * (1.0 - alpha));

    //gyroscope values to a value in degrees/sec
    float Gx = ax / 14.375;
    float Gy = ay / 14.375;
    float Gz = az / 14.375;
    
    /* Display the results (acceleration is measured in m/s^2) */
    Serial.print("{\"acc_x\":"); Serial.print(fXa); Serial.print(','); Serial.print("\"acc_y\":"); Serial.print(fYa); Serial.print(','); Serial.print("\"acc_z\":"); Serial.print(fZa);
    Serial.print(','); Serial.print("\"gyr_x\":"); Serial.print(Gx); Serial.print(','); Serial.print("\"gyr_y\":"); Serial.print(Gy); Serial.print(','); Serial.print("\"gyr_z\":"); Serial.print(Gz); Serial.println('}');
    delay(25);
  }
