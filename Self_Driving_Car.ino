/*
  Minimal Esp8266 Websockets Server

  This sketch:
        1. Connects to a WiFi network
        2. Starts a websocket server on port 80
        3. Waits for connections
        4. Once a client connects, it wait for a message from the client
        5. Sends an "echo" message to the client
        6. closes the connection and goes back to step 3

  Hardware:
        For this sketch you only need an ESP8266 board.

  Created 15/02/2019
  By Gil Maimon
  https://github.com/gilmaimon/ArduinoWebsockets
*/

#include <ArduinoWebsockets.h>
#include <ESP8266WiFi.h>

char ssid[] = "LTL"; //Enter SSID
const char* password = "ProjectPassword"; //Enter Password

using namespace websockets;

WebsocketsServer server;
void setup() {
  pinMode(D2, OUTPUT);
  pinMode(D3, OUTPUT);
  Serial.begin(115200);
  // Connect to wifi
  WiFi.begin(ssid, password);

  // Wait some time to connect to wifi
  for(int i = 0; i < 15 && WiFi.status() != WL_CONNECTED; i++) {
      Serial.print(".");
      delay(1000);
  }
  
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());   //You can get IP address assigned to ESP

  server.listen(80);
  Serial.print("Is server live? ");
  Serial.println(server.available());
}

void loop() {
  WebsocketsClient client = server.accept();
  if(client.available()) {
    WebsocketsMessage msg = client.readBlocking();

    // log
    Serial.print("Got Message: ");
    Serial.println(msg.data());
    String payload = msg.data();
    if(payload == "LEFT") {
      Serial.println("LEFT ACTIVATE");
      digitalWrite(D3, LOW);
      digitalWrite(D2, HIGH);
    } else if (payload == "RIGHT") {
      Serial.println("RIGHT ACTIVATE");
      digitalWrite(D3, HIGH);
      digitalWrite(D2, LOW);
    } else if (payload == "ALONG") {
      Serial.println("CENTER ACTIVATE");
      digitalWrite(D2, LOW);
      digitalWrite(D3, LOW);
    } else {
      Serial.println("DEACTIVATE");
      digitalWrite(D2, HIGH);
      digitalWrite(D3, HIGH);
    }
  }
}
