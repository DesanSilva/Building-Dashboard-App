from machine import Pin, SoftI2C
from micropython import const
import framebuf
import time


# register definitions
SET_CONTRAST        = const(0x81)
SET_ENTIRE_ON       = const(0xa4)
SET_NORM_INV        = const(0xa6)
SET_DISP            = const(0xae)
SET_MEM_ADDR        = const(0x20)
SET_COL_ADDR        = const(0x21)
SET_PAGE_ADDR       = const(0x22)
SET_DISP_START_LINE = const(0x40)
SET_SEG_REMAP       = const(0xa0)
SET_MUX_RATIO       = const(0xa8)
SET_COM_OUT_DIR     = const(0xc0)
SET_DISP_OFFSET     = const(0xd3)
SET_COM_PIN_CFG     = const(0xda)
SET_DISP_CLK_DIV    = const(0xd5)
SET_PRECHARGE       = const(0xd9)
SET_VCOM_DESEL      = const(0xdb)
SET_CHARGE_PUMP     = const(0x8d)

class SSD1306:
    def __init__(self, width, height, external_vcc):
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        self.pages = self.height // 8
        self.buffer = bytearray(self.pages * self.width)
        fb = framebuf.FrameBuffer(self.buffer, self.width, self.height, framebuf.MONO_VLSB)
        self.framebuf = fb
        # Provide methods for accessing FrameBuffer graphics primitives. This is a
        # workround because inheritance from a native class is currently unsupported.
        # http://docs.micropython.org/en/latest/pyboard/library/framebuf.html
        self.fill = fb.fill
        self.pixel = fb.pixel
        self.hline = fb.hline
        self.vline = fb.vline
        self.line = fb.line
        self.rect = fb.rect
        self.fill_rect = fb.fill_rect
        self.text = fb.text
        self.scroll = fb.scroll
        self.blit = fb.blit
        self.init_display()

    def init_display(self):
        for cmd in (
            SET_DISP | 0x00, # off
            # address setting
            SET_MEM_ADDR, 0x00, # horizontal
            # resolution and layout
            SET_DISP_START_LINE | 0x00,
            SET_SEG_REMAP | 0x01, # column addr 127 mapped to SEG0
            SET_MUX_RATIO, self.height - 1,
            SET_COM_OUT_DIR | 0x08, # scan from COM[N] to COM0
            SET_DISP_OFFSET, 0x00,
            SET_COM_PIN_CFG, 0x02 if self.height == 32 else 0x12,
            # timing and driving scheme
            SET_DISP_CLK_DIV, 0x80,
            SET_PRECHARGE, 0x22 if self.external_vcc else 0xf1,
            SET_VCOM_DESEL, 0x30, # 0.83*Vcc
            # display
            SET_CONTRAST, 0xff, # maximum
            SET_ENTIRE_ON, # output follows RAM contents
            SET_NORM_INV, # not inverted
            # charge pump
            SET_CHARGE_PUMP, 0x10 if self.external_vcc else 0x14,
            SET_DISP | 0x01): # on
            self.write_cmd(cmd)
        self.fill(0)
        self.show()

    def poweroff(self):
        self.write_cmd(SET_DISP | 0x00)

    def poweron(self):
        self.write_cmd(SET_DISP | 0x01)

    def contrast(self, contrast):
        self.write_cmd(SET_CONTRAST)
        self.write_cmd(contrast)

    def invert(self, invert):
        self.write_cmd(SET_NORM_INV | (invert & 1))

    def show(self):
        x0 = 0
        x1 = self.width - 1
        if self.width == 64:
            # displays with width of 64 pixels are shifted by 32
            x0 += 32
            x1 += 32
        self.write_cmd(SET_COL_ADDR)
        self.write_cmd(x0)
        self.write_cmd(x1)
        self.write_cmd(SET_PAGE_ADDR)
        self.write_cmd(0)
        self.write_cmd(self.pages - 1)
        self.write_data(self.buffer)


class SSD1306_I2C(SSD1306):
    def __init__(self, width, height, scl, sda, addr=0x3c, external_vcc=False):
        self.i2c = SoftI2C(scl=Pin(scl), sda=Pin(sda))
        self.addr = addr
        self.temp = bytearray(2)
        super().__init__(width, height, external_vcc)

    def write_cmd(self, cmd):
        self.temp[0] = 0x80 # Co=1, D/C#=0
        self.temp[1] = cmd
        self.i2c.writeto(self.addr, self.temp)

    def write_data(self, buf):
        self.temp[0] = self.addr << 1
        self.temp[1] = 0x40 # Co=0, D/C#=1
        self.i2c.start()
        self.i2c.write(self.temp)
        self.i2c.write(buf)
        self.i2c.stop()

def display_text(display, message):
    print(message)
    display.fill(0)
    
    words = message.split()
    lines = []
    current_line = ""
    
    for word in words:
        while len(word) > 16:
            lines.append(word[:16])
            word = word[16:]

        if len(current_line) + len(word) + 1 <= 16:
            current_line += (" " if current_line else "") + word
        else:
            lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)

    for i, line in enumerate(lines[:8]):
        display.text(line, 0, i * 9)

    display.show()

def display_data(display, message, ac_status, lights_status):
    print(message)
    display.fill(0)

    data = eval(message)

    datetime_str = data.pop("time", "")
    date, time = datetime_str.split()

    display.text("time:"+ date, 0, 0)
    display.text(time, 40, 9)
    display.text(f"temp     : {data["temperature"]}", 0, 18)
    display.text(f"humidity : {data["humidity"]}", 0, 27)
    display.text(f"luminance: {data["luminance"]}", 0, 36)
    display.text(f"AC       : {'ON' if ac_status else 'OFF'}", 0, 46)
    display.text(f"LIGHTS   : {'ON' if lights_status else 'OFF'}", 0, 56)

    display.show()