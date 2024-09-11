// /*
//  *  This sketch sends random data over UDP on a ESP32 device
//  *
//  */
// // #include <ETH.h>
// // #include <Ethernet.h>
// // #include <EthernetUdp.h>
// #include <WiFi.h>
// #include <WiFiUdp.h>

// // WiFi network name and password:
// const char * networkName = "HITSZ";
// const char * networkPswd = "";

// //IP address to send UDP data to:
// // either use the ip address of the server or 
// // a network broadcast address
// const char * udpAddress = "10.250.145.73";
// const int udpPort = 3333;

// //Are we currently connected?
// boolean connected = false;

// //The udp library class
// WiFiUDP udp;
// char packetBuffer[100];  // buffer to hold incoming packet
// char ReplyBuffer[] = "acknowledged";        // a string to send back

// void WiFiEvent(WiFiEvent_t event);
// void connectToWiFi(const char * ssid, const char * pwd);
// void setup(){
//   // Initilize hardware serial:
//   Serial.begin(115200);
  
//   //Connect to the WiFi network
//   connectToWiFi(networkName, networkPswd);
// }

// void loop(){
//   //only send data when connected
//   if(connected){
//     Serial.println("Sending packet...");
//     //Send a packet
//     udp.beginPacket(udpAddress,udpPort);
//     udp.printf("Seconds since boot: %lu", millis()/1000);
//     udp.endPacket();

//   }

//   int packetSize = udp.parsePacket();
//   if (packetSize) {
//     Serial.print("Received packet of size ");
//     Serial.println(packetSize);
//     Serial.print("From ");
//     IPAddress remote = udp.remoteIP();
//     for (int i=0; i < 4; i++) {
//       Serial.print(remote[i], DEC);
//       if (i < 3) {
//         Serial.print(".");
//       }
//     }
//     Serial.print(", port ");
//     Serial.println(udp.remotePort());

//     // read the packet into packetBufffer
//     udp.read(packetBuffer, 100);
//     Serial.println("Contents:");
//     Serial.println(packetBuffer);

//     // send a reply to the IP address and port that sent us the packet we received
//     udp.beginPacket(udp.remoteIP(), udp.remotePort());
//     udp.write((uint8_t*)&ReplyBuffer[0], 5);
//     udp.endPacket();
//   }
//   delay(10);

//   //Wait for 1 second
//   delay(1000);
// }

// void connectToWiFi(const char * ssid, const char * pwd){
//   Serial.println("Connecting to WiFi network: " + String(ssid));

//   // delete old config
//   WiFi.disconnect(true);
//   //register event handler
//   WiFi.onEvent(WiFiEvent);
  
//   //Initiate connection
//   WiFi.begin(ssid, pwd);

//   Serial.println("Waiting for WIFI connection...");
// }

// //wifi event handler
// void WiFiEvent(WiFiEvent_t event){
//     switch(event) {
//       case ARDUINO_EVENT_WIFI_STA_GOT_IP:
//           //When connected set 
//           Serial.print("WiFi connected! IP address: ");
//           Serial.println(WiFi.localIP());  
//           //initializes the UDP state
//           //This initializes the transfer buffer
//           udp.begin(WiFi.localIP(),udpPort);
//           connected = true;
//           break;
//       case ARDUINO_EVENT_WIFI_STA_DISCONNECTED:
//           Serial.println("WiFi lost connection");
//           connected = false;
//           break;
//       default: break;
//     }
// }