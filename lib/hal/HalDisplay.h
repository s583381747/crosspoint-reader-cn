#pragma once
#include <Arduino.h>
#include <EInkDisplay.h>

class HalDisplay {
 public:
  // Constructor with pin configuration
  HalDisplay();

  // Destructor
  ~HalDisplay();

  // Refresh modes
  enum RefreshMode {
    FULL_REFRESH,  // Full refresh with complete waveform
    HALF_REFRESH,  // Half refresh (1720ms) - balanced quality and speed
    FAST_REFRESH   // Fast refresh using custom LUT
  };

  // Initialize the display hardware and driver
  void begin();

  // Display dimensions — hardcoded to X3 (792x528).
  // This fork targets Xteink X3 only; rendering code uses these compile-time
  // constants for buffer stride and layout, so they MUST match the panel
  // geometry set by einkDisplay.setDisplayX3() in begin(). Using X4 (800x480)
  // here against an X3 panel produces a ~1-byte-per-row stride mismatch that
  // shows up as diagonal (~30°) tearing.
  static constexpr uint16_t DISPLAY_WIDTH = EInkDisplay::X3_DISPLAY_WIDTH;        // 792
  static constexpr uint16_t DISPLAY_HEIGHT = EInkDisplay::X3_DISPLAY_HEIGHT;      // 528
  static constexpr uint16_t DISPLAY_WIDTH_BYTES = DISPLAY_WIDTH / 8;              // 99
  static constexpr uint32_t BUFFER_SIZE = DISPLAY_WIDTH_BYTES * DISPLAY_HEIGHT;   // 52272

  // Frame buffer operations
  void clearScreen(uint8_t color = 0xFF) const;
  void drawImage(const uint8_t* imageData, uint16_t x, uint16_t y, uint16_t w, uint16_t h,
                 bool fromProgmem = false) const;
  void drawImageTransparent(const uint8_t* imageData, uint16_t x, uint16_t y, uint16_t w, uint16_t h,
                            bool fromProgmem = false) const;

  void displayBuffer(RefreshMode mode = RefreshMode::FAST_REFRESH, bool turnOffScreen = false);
  void refreshDisplay(RefreshMode mode = RefreshMode::FAST_REFRESH, bool turnOffScreen = false);

  // Power management
  void deepSleep();

  // Access to frame buffer
  uint8_t* getFrameBuffer() const;

  void copyGrayscaleBuffers(const uint8_t* lsbBuffer, const uint8_t* msbBuffer);
  void copyGrayscaleLsbBuffers(const uint8_t* lsbBuffer);
  void copyGrayscaleMsbBuffers(const uint8_t* msbBuffer);
  void cleanupGrayscaleBuffers(const uint8_t* bwBuffer);

  void displayGrayBuffer(bool turnOffScreen = false);

 private:
  EInkDisplay einkDisplay;
};
