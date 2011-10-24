// Shreyans Bhansali and Jenny Kortina <http://treatchewie.com>
// via BARRAGAN <http://barraganstudio.com> 
// This code is in the public domain.

#include <Servo.h> 

Servo treater;  // create servo object to control a the gumball machine

void setup() 
{
  treater.attach(9);  // attaches the servo on pin 9 to the servo object
} 

void loop()
{
  // one full rotation
  // speed and time based on trial and error
  treater.write(60);
  delay(1410);
  // writing 94 stops the servo, which we learnt through trial and error
  treater.write(94);
  // do nothing
  while(1) {}
}
