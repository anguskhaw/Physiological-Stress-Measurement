#include <ArduinoBLE.h>

#define BLE_UUID_DATA_SERVICE                  "180F"
#define BLE_UUID_DATA_LEVEL                    "2A19"

#define BLE_MAX_PERIPHERALS 2
#define BLE_SCAN_INTERVALL 1000

BLEDevice peripherals[BLE_MAX_PERIPHERALS];
BLECharacteristic dataCharacteristics[BLE_MAX_PERIPHERALS];

int peripheralsConnected = 0;
const int buttonPin = 4;
int buttonState = 0; 

void setup() {
    Serial.begin(9600);
  pinMode(buttonPin, INPUT_PULLUP);

  // begin initialization
  BLE.begin();
  if (!BLE.begin()) {
    Serial.println("starting BLE failed!");

    while (1);
  }

  Serial.println("BLE Central - Receiver");
  Serial.println("Make sure to turn on the device.");

  // start scanning for peripheral
  BLE.scan();
  BLE.scanForUuid( BLE_UUID_DATA_SERVICE );
  
  int peripheralCounter = 0;
  unsigned long startMillis = millis();
  while ( millis() - startMillis < BLE_SCAN_INTERVALL && peripheralCounter < BLE_MAX_PERIPHERALS )
  {
    BLEDevice peripheral = BLE.available();

    if ( peripheral )
    {
      if ( peripheral.localName() == "GDPsensor" )
      {
        boolean peripheralAlreadyFound = false;
        for ( int i = 0; i < peripheralCounter; i++ )
        {
          if ( peripheral.address() == peripherals[i].address() )
          {
            peripheralAlreadyFound = true;
          }
        }
        if ( !peripheralAlreadyFound )
        {
          peripherals[peripheralCounter] = peripheral;
          peripheralCounter++;
        }
      }
    }
  }
  
  BLE.stopScan();

  for ( int i = 0; i < peripheralCounter; i++ )
  {
    peripherals[i].connect();
    peripherals[i].discoverAttributes();
    BLECharacteristic dataCharacteristic = peripherals[i].characteristic( BLE_UUID_DATA_LEVEL );
    if ( dataCharacteristic )
    {
      dataCharacteristics[i] = dataCharacteristic;
      dataCharacteristics[i].subscribe();
    }
  }
  peripheralsConnected = peripheralCounter;

}

void loop() {
  uint8_t sensordatas[BLE_MAX_PERIPHERALS];
  bool newDataPrint = false;

  for ( int i = 0; i < peripheralsConnected; i++ )
  {
    while (digitalRead(buttonPin) == LOW){
    if ( dataCharacteristics[i].valueUpdated() )
    {
      newDataPrint = true;
      uint8_t data;
      dataCharacteristics[i].readValue( data );
      sensordatas[i] = data;
    }
  
  if ( newDataPrint )
  {
    for ( int i = 0; i < peripheralsConnected; i++ )
    {
      Serial.print( sensordatas[i] );
      Serial.print( "," );  
    }
    Serial.print( "\n" );
  }
    }
}

}
