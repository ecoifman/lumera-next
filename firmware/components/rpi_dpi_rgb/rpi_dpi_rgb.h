//
// Created by Clyde Stubbs on 29/10/2023.
//
#pragma once

// only applicable on ESP32-S3
#ifdef USE_ESP32_VARIANT_ESP32S3
#include "esphome/core/component.h"
#include "esphome/core/gpio.h"
#include "esphome/core/log.h"
#include "esphome/core/application.h"
#include "esphome/components/display/display.h"
#include "esp_lcd_panel_ops.h"

#include "esp_lcd_panel_rgb.h"
#include <algorithm>

namespace esphome::rpi_dpi_rgb {

constexpr static const char *const TAG = "rpi_dpi_rgb";

class RpiDpiRgb final : public display::Display {
 public:
  void update() override { this->do_update_(); }
  void setup() override;
  void loop() override;
  float get_setup_priority() const override { return setup_priority::HARDWARE; }
  void draw_pixels_at(int x_start, int y_start, int w, int h, const uint8_t *ptr, display::ColorOrder order,
                      display::ColorBitness bitness, bool big_endian, int x_offset, int y_offset, int x_pad) override;
  void draw_pixel_at(int x, int y, Color color) override;

  display::ColorOrder get_color_mode() { return this->color_mode_; }
  void set_color_mode(display::ColorOrder color_mode) { this->color_mode_ = color_mode; }
  void set_invert_colors(bool invert_colors) { this->invert_colors_ = invert_colors; }

  void add_data_pin(InternalGPIOPin *data_pin, size_t index) { this->data_pins_[index] = data_pin; };
  void set_de_pin(InternalGPIOPin *de_pin) { this->de_pin_ = de_pin; }
  void set_pclk_pin(InternalGPIOPin *pclk_pin) { this->pclk_pin_ = pclk_pin; }
  void set_vsync_pin(InternalGPIOPin *vsync_pin) { this->vsync_pin_ = vsync_pin; }
  void set_hsync_pin(InternalGPIOPin *hsync_pin) { this->hsync_pin_ = hsync_pin; }
  void set_enable_pin(GPIOPin *enable_pin) { this->enable_pin_ = enable_pin; }
  void set_reset_pin(GPIOPin *reset_pin) { this->reset_pin_ = reset_pin; }
  void set_width(uint16_t width) { this->width_ = width; }
  void set_dimensions(uint16_t width, uint16_t height) {
    this->width_ = width;
    this->height_ = height;
  }
  int get_width() override;
  int get_height() override;
  void set_hsync_back_porch(uint16_t hsync_back_porch) { this->hsync_back_porch_ = hsync_back_porch; }
  void set_hsync_front_porch(uint16_t hsync_front_porch) { this->hsync_front_porch_ = hsync_front_porch; }
  void set_hsync_pulse_width(uint16_t hsync_pulse_width) { this->hsync_pulse_width_ = hsync_pulse_width; }
  void set_vsync_pulse_width(uint16_t vsync_pulse_width) { this->vsync_pulse_width_ = vsync_pulse_width; }
  void set_vsync_back_porch(uint16_t vsync_back_porch) { this->vsync_back_porch_ = vsync_back_porch; }
  void set_vsync_front_porch(uint16_t vsync_front_porch) { this->vsync_front_porch_ = vsync_front_porch; }
  void set_pclk_frequency(uint32_t pclk_frequency) { this->pclk_frequency_ = pclk_frequency; }
  void set_pclk_inverted(bool inverted) { this->pclk_inverted_ = inverted; }
  void set_offsets(int16_t offset_x, int16_t offset_y) {
    this->offset_x_ = offset_x;
    this->offset_y_ = offset_y;
  }
  display::DisplayType get_display_type() override { return display::DisplayType::DISPLAY_TYPE_COLOR; }
  void dump_config() override;

 protected:
  int get_width_internal() override { return this->width_; }
  int get_height_internal() override { return this->height_; }
  void reset_display_() const;
  InternalGPIOPin *de_pin_{nullptr};
  InternalGPIOPin *pclk_pin_{nullptr};
  InternalGPIOPin *hsync_pin_{nullptr};
  InternalGPIOPin *vsync_pin_{nullptr};
  GPIOPin *enable_pin_{nullptr};
  GPIOPin *reset_pin_{nullptr};
  InternalGPIOPin *data_pins_[16] = {};
  uint16_t hsync_front_porch_ = 8;
  uint16_t hsync_pulse_width_ = 4;
  uint16_t hsync_back_porch_ = 8;
  uint16_t vsync_front_porch_ = 8;
  uint16_t vsync_pulse_width_ = 4;
  uint16_t vsync_back_porch_ = 8;
  uint32_t pclk_frequency_ = 16 * 1000 * 1000;
  bool pclk_inverted_{true};

  bool invert_colors_{};
  display::ColorOrder color_mode_{display::COLOR_ORDER_BGR};
  size_t width_{};
  size_t height_{};
  int16_t offset_x_{0};
  int16_t offset_y_{0};

  esp_lcd_panel_handle_t handle_{};

 public:
  esp_lcd_panel_handle_t get_panel_handle() const { return this->handle_; }
  // Panel colour calibration: per-channel gain (1.0 = unchanged), applied to every pixel on its way
  // to the frame buffer through a 64K lookup table in PSRAM. All 1.0 switches the table off.
  void set_color_gains(float r, float g, float b, float gamma = 1.0f, float sat = 1.0f);

 protected:
  uint16_t *lut_{nullptr};
  uint16_t *line_buf_{nullptr};
  size_t line_cap_{0};

  // Like the stock Lanbon firmware in landscape: three frame buffers, LVGL renders whole frames
  // into one that is neither on screen nor queued, and the driver switches buffers at the frame
  // boundary. The RGB output only starts once the GC9503 has been initialised (start()).
 public:
  void start();                       // begin RGB scan-out (call after the GC9503 init)
  bool started() const { return this->started_; }
  // timing probe (read and reset by the yaml perf logger)
  uint32_t prof_wait_us_{0}, prof_copy_us_{0}, prof_px_{0};
  uint32_t vsync_count() const { return this->vsyncs_; }
  uint16_t *front_buffer() const { return this->fbs_[0] ? this->fbs_[this->latest_] : nullptr; }

 protected:
  static bool on_vsync_(esp_lcd_panel_handle_t panel, const esp_lcd_rgb_panel_event_data_t *edata, void *ctx);
  void copy_into_(uint16_t *fb, int x_start, int y_start, int w, int h, const uint8_t *ptr, int x_offset,
                  int y_offset, int x_pad);
  struct Rect {
    int x0{0}, y0{0}, x1{0}, y1{0};
    bool empty() const { return x1 <= x0 || y1 <= y0; }
    void add(int x, int y, int w, int h) {
      if (empty()) { x0 = x; y0 = y; x1 = x + w; y1 = y + h; return; }
      x0 = std::min(x0, x); y0 = std::min(y0, y); x1 = std::max(x1, x + w); y1 = std::max(y1, y + h);
    }
  };
  void begin_frame_(const Rect &first);
  void end_frame_();
  // dirty areas of a frame: a few separate rectangles (merged into one when there are too many)
  struct Areas {
    static constexpr int N = 8;
    Rect r[N]{};
    int n{0};
    void clear() { n = 0; }
    void add(int x, int y, int w, int h) {
      if (n < N) { r[n] = Rect{}; r[n].add(x, y, w, h); n++; return; }
      for (int i = 1; i < N; i++) r[0].add(r[i].x0, r[i].y0, r[i].x1 - r[i].x0, r[i].y1 - r[i].y0);
      r[0].add(x, y, w, h); n = 1;
    }
  };
  Areas cur_{}, hist_[2]{};
  bool frame_open_{false};
  uint8_t back_{1};
  uint16_t *fbs_[3]{nullptr, nullptr, nullptr};
  uint8_t latest_{0};
  volatile uint32_t vsyncs_{0};
  uint32_t vsync_at_submit_{0};
  uint32_t vsync_at_prev_submit_{0xFFFFFFFF};
  bool started_{false};
  uint32_t setup_ms_{0};
};

}  // namespace esphome::rpi_dpi_rgb
#endif  // USE_ESP32_VARIANT_ESP32S3
