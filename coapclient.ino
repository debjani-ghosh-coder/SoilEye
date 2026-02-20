#include <WiFi.h>
#include <WiFiUdp.h>
#include <coap-simple.h>
#include <ModbusMaster.h>


const char* ssid = "iQOO Z9x 5G";
const char* password = "Srish@6315";


IPAddress serverIP(10, 81, 251, 55);
int serverPort = 5683;


#define RE 27
#define DE 4
#define RXD2 16
#define TXD2 17

ModbusMaster node;
WiFiUDP udp;
Coap coap(udp);

uint8_t token[] = {0x01};


void preTransmission() {
  digitalWrite(RE, HIGH);
  digitalWrite(DE, HIGH);
  delay(3);
}

void postTransmission() {
  digitalWrite(DE, LOW);
  digitalWrite(RE, LOW);
  delay(3);
}

void setup() {
  Serial.begin(115200);

  pinMode(RE, OUTPUT);
  pinMode(DE, OUTPUT);
  digitalWrite(RE, LOW);
  digitalWrite(DE, LOW);

  Serial2.begin(9600, SERIAL_8N1, RXD2, TXD2);

  node.begin(1, Serial2);  
  node.preTransmission(preTransmission);
  node.postTransmission(postTransmission);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi Connected");
  Serial.println(WiFi.localIP());

  coap.start();
}

void loop() {

  float moisture = 0;
  float temperature = 0;
  uint16_t ec = 0;
  float ph = 0;

  
  if (node.readHoldingRegisters(0x0012, 1) == node.ku8MBSuccess)
    moisture = node.getResponseBuffer(0) / 10.0;

  
  if (node.readHoldingRegisters(0x0013, 1) == node.ku8MBSuccess)
    temperature = node.getResponseBuffer(0) / 10.0;

  
  if (node.readHoldingRegisters(0x0015, 1) == node.ku8MBSuccess)
    ec = node.getResponseBuffer(0);

  
  if (node.readHoldingRegisters(0x0006, 1) == node.ku8MBSuccess)
    ph = node.getResponseBuffer(0) / 10.0;

  Serial.println("----- SENSOR DATA -----");
  Serial.print("Moisture: "); Serial.println(moisture);
  Serial.print("Temperature: "); Serial.println(temperature);
  Serial.print("EC: "); Serial.println(ec);
  Serial.print("pH: "); Serial.println(ph);

  char payload[160];
  snprintf(payload, sizeof(payload),
    "{\"moisture\": %.2f, \"temp\": %.2f, \"ec\": %d, \"ph\": %.2f}",
    moisture, temperature, ec, ph
  );

  coap.send(
    serverIP,
    serverPort,
    "soil",
    COAP_CON,
    COAP_POST,
    token,
    sizeof(token),
    (uint8_t*)payload,
    strlen(payload)
  );

  Serial.println("Data sent to server");

  coap.loop();
  delay(5000);
}