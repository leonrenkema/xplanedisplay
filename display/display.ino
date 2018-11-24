/*
** MCP23017 16 bit Port Expander
** Example code to flash LED on GPB0
** Created 06 Aug 2012
**
** This example code is in the public domain.
** www.hobbytronics.co.uk
*/

#include <Wire.h>

const byte  GPIOA=0x12;            // Register Address of Port A
const byte  GPIOB=0x13;            // Register Address of Port B

const byte  chip1=0x20;

const byte IODIRA = 0x00;
const byte IODIRB = 0x01;

const byte statePortA = 0x00;
const byte statePortB = 0x00;

// Configuration
byte Volts[] = { chip1,IODIRA, 0x01 };
byte Oil_Pressure[] = { chip1,IODIRA, 0x02 };
byte Low_Fuel[] = { chip1,IODIRA, 0x03 };

void setup()
{
  //Send settings to MCP device
  Wire.begin();              // join i2c bus (address optional for master)

  // IOCON.BANK defaults to 0 which is what we want.
  // So we are using Table 1-4 on page 9 of datasheet
  
  Wire.beginTransmission(chip1);
  Wire.write(IODIRA); // IODIRA register
  Wire.write((byte)0x00); // set all of bank A to outputs
  Wire.write(IODIRB); // IODIRB register
  Wire.write((byte)0x00); // set all of bank B to outputs 
  Wire.endTransmission();
  
}

void loop()
{

  turnOn(Volts);
  
  Wire.beginTransmission(chip1);
  Wire.write(GPIOB);      // address bank B
  Wire.write((byte)0xFF);  // value to send - all HIGH
  
  Wire.endTransmission();

  send_byte(chip1, GPIOA, 0xFF);
  
  delay(500);

  Wire.beginTransmission(chip1);
  Wire.write(GPIOB);    // address bank B
  Wire.write((byte)0x00);  // value to send - all LOW
  Wire.endTransmission();

  send_byte(chip1, GPIOA, 0x00);
  
  delay(500);
}


void turnOff(byte light[]) {
  send_byte(light[0], light[1], light[2]);
}

void turnOn(byte light[]) {
  send_byte(light[0], light[1], light[2]);
}

void send_byte(byte address, byte bank, byte value) {
  Wire.beginTransmission(address);
  Wire.write(bank);      // address bank B
  Wire.write(value);  // value to send - all HIGH
  Wire.endTransmission();
}
