//功能：拍照+本地保存+wifi链接服务器  稳定代码

// ===========================
// Including
// ===========================
#include "esp_camera.h"
#include <WiFi.h>
#define CAMERA_MODEL_AI_THINKER  // Has PSRAM
#include "camera_pins.h"
#include "FS.h"                // SD Card ESP32
#include "SD_MMC.h"            // SD Card ESP32
#include "soc/soc.h"           // Disable brownour problems
#include "soc/rtc_cntl_reg.h"  // Disable brownour problems
#include "driver/rtc_io.h"
#include <EEPROM.h>            // read and write from flash memory
#include "rc4.hpp"
#include <string>
#define EEPROM_SIZE 1
int pictureNumber = 0;

// ===========================
// Enter your WiFi credentials
// ===========================
// const char *ssid = "mys24";
// const char *password = "20050602";

const char *ssid = "HITSZ";
const char *password = "";
const char *key = "12345678";
const size_t key_len = 8;
void startCameraServer();
void setupLedFlash(int pin);

RC4 rc4; 

void rc4_process(uint8_t* data, size_t len) {
  if (len < 32) return;
  rc4.reset((uint8_t*)key, key_len);
  rc4.crypt(data, data, len);
}


void serial_setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.println();
}

camera_config_t config;

void camera_setup() {
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.frame_size = FRAMESIZE_UXGA;
  config.pixel_format = PIXFORMAT_JPEG;  // for streaming
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 10;
  config.fb_count = 2;
  config.grab_mode = CAMERA_GRAB_LATEST;

  // Init Camera
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }
}

void wifi_setup() {
  WiFi.begin(ssid, password);
  WiFi.setSleep(false);
  while (WiFi.status() != WL_CONNECTED) {
    delay(2000);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  startCameraServer();
  Serial.print("Camera Ready! Use 'http://");
  Serial.print(WiFi.localIP());
  Serial.println("' to connect");
}

void sd_setup()
{
  // WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0); //disable brownout detector
 
  //Serial.println("Starting SD Card");
  if(!SD_MMC.begin()){
    Serial.println("SD Card Mount Failed");
    return;
  }
  
  uint8_t cardType = SD_MMC.cardType();
  if(cardType == CARD_NONE){
    Serial.println("No SD Card attached");
    return;
  }
}

void save_jpg() {
     
  camera_fb_t * fb = NULL;
  size_t _jpg_buf_len = 0;
  uint8_t *_jpg_buf = NULL;
  // Take Picture with Camera
  // delay(1000);
  fb = esp_camera_fb_get();  
  rc4_process(fb->buf, fb->len);
  if(!fb) {
    Serial.printf("Camera capture failed");
    return;
  } else {
    if(fb->width > 400){
      if(fb->format != PIXFORMAT_JPEG){
        bool jpeg_converted = frame2jpg(fb, 80, &_jpg_buf, &_jpg_buf_len);
        esp_camera_fb_return(fb);
        fb = NULL;
        if(!jpeg_converted){
          Serial.printf("JPEG compression failed");
          // res = ESP_FAIL;
        } else {
          Serial.printf("Camera compression success");
        }
      } else {
        Serial.printf("Camera capture is jpeg\n");
        _jpg_buf_len = fb->len;
        _jpg_buf = fb->buf;
      }
    } else {
      Serial.printf("Camera capture is too small");
      esp_camera_fb_return(fb);
      return;
      // return;
    }
  }
  // initialize EEPROM with predefined size
  EEPROM.begin(EEPROM_SIZE);
  pictureNumber = EEPROM.read(0) + 1;
 
  // Path where new picture will be saved in SD Card
  String path = "/picture" + String(pictureNumber) +".bin";
 
  fs::FS &fs = SD_MMC; 
  Serial.printf("Picture file name: %s\n", path.c_str());
  
  File file = fs.open(path.c_str(), FILE_WRITE);
  if(!file){
    Serial.println("Failed to open file in writing mode");
  } 
  else {
    file.write(_jpg_buf, _jpg_buf_len); // payload (image), payload length
    Serial.printf("Saved file to path: %s\n", path.c_str());
    EEPROM.write(0, pictureNumber);
    EEPROM.commit();
  }
  file.close();
  esp_camera_fb_return(fb); 
  
  if(fb){
    esp_camera_fb_return(fb);
    fb = NULL;
    _jpg_buf = NULL;
  } else if(_jpg_buf){
    free(_jpg_buf);
    _jpg_buf = NULL;
  }
}

void led_setup()
{
  pinMode(4, OUTPUT);
  digitalWrite(4, LOW);
  // rtc_gpio_hold_en(GPIO_NUM_4);
}

bool has_saved = false;
void setup() {
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0); //disable brownout detector
  serial_setup();
  camera_setup();
  sd_setup();
  // led_setup();
  
  wifi_setup();
  has_saved = false;
}

void loop() {
  Serial.write("hi\n");
  delay(10000);
  if (!has_saved) {
    save_jpg();
    has_saved = true;
    led_setup();
  }
}