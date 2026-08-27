from machine import Pin, SPI, PWM
import framebuf
import time


# --------------------------------------------------
# Pins
# --------------------------------------------------

LCD_DC   = 8
LCD_CS   = 9
LCD_SCK  = 10
LCD_MOSI = 11
LCD_MISO = 12
LCD_BL   = 13
LCD_RST  = 15
TP_CS    = 16
TP_IRQ   = 17


# --------------------------------------------------
# LCD
# --------------------------------------------------

class LCD_3inch5:

    def __init__(self):

        self.RED   = 0xF800
        self.GREEN = 0x07E0
        self.BLUE  = 0x001F
        self.WHITE = 0xFFFF
        self.BLACK = 0x0000
        self.YELLOW=0xFFE0
        self.black=0x1820

        # Hochformat
        self.width = 320
        self.height = 480

        self.rotate = 90

        # Pins
        self.cs = Pin(LCD_CS, Pin.OUT)
        self.rst = Pin(LCD_RST, Pin.OUT)
        self.dc = Pin(LCD_DC, Pin.OUT)

        self.tp_cs = Pin(TP_CS, Pin.OUT)
        self.irq = Pin(TP_IRQ, Pin.IN)

        self.cs(1)
        self.dc(1)
        self.rst(1)
        self.tp_cs(1)

        # LCD SPI
        self.spi = SPI(
            1,
            baudrate=40_000_000,
            sck=Pin(LCD_SCK),
            mosi=Pin(LCD_MOSI),
            miso=Pin(LCD_MISO)
        )

        # Nur ein kleiner Buffer für Text
        self.text_buffer = None

        self.init_display()


    # --------------------------------------------------
    # LCD Kommunikation
    # --------------------------------------------------

    def write_cmd(self, cmd):

        self.cs(1)
        self.dc(0)
        self.cs(0)

        self.spi.write(bytearray([cmd]))

        self.cs(1)


    def write_data(self, data):

        self.cs(1)
        self.dc(1)
        self.cs(0)

        if isinstance(data, int):
            self.spi.write(bytearray([data]))
        else:
            self.spi.write(data)

        self.cs(1)


    # --------------------------------------------------
    # Display initialisieren
    # --------------------------------------------------

    def init_display(self):

        self.rst(1)
        time.sleep_ms(5)

        self.rst(0)
        time.sleep_ms(10)

        self.rst(1)
        time.sleep_ms(5)

        self.write_cmd(0x21)

        self.write_cmd(0xC2)
        self.write_data(0x33)

        self.write_cmd(0xC5)
        self.write_data(0x00)
        self.write_data(0x1E)
        self.write_data(0x80)

        self.write_cmd(0xB1)
        self.write_data(0xB0)

        self.write_cmd(0xE0)

        for value in (
            0x00, 0x13, 0x18, 0x04,
            0x0F, 0x06, 0x3A, 0x56,
            0x4D, 0x03, 0x0A, 0x06,
            0x30, 0x3E, 0x0F
        ):
            self.write_data(value)

        self.write_cmd(0xE1)

        for value in (
            0x00, 0x13, 0x18, 0x01,
            0x11, 0x06, 0x38, 0x34,
            0x4D, 0x06, 0x0D, 0x0B,
            0x31, 0x37, 0x0F
        ):
            self.write_data(value)

        self.write_cmd(0x3A)
        self.write_data(0x55)

        self.write_cmd(0x11)
        time.sleep_ms(120)

        self.write_cmd(0x29)

        self.write_cmd(0xB6)
        self.write_data(0x00)
        self.write_data(0x62)

        # Rotation 90°
        self.write_cmd(0x36)
        self.write_data(0xE8)


    # --------------------------------------------------
    # Zeichenbereich setzen
    # --------------------------------------------------

    def set_window(self, x0, y0, x1, y1):

        # Virtuelles Hochformat 320x480
        #
        # Der Controller liegt physisch bei 480x320.
        # Die Koordinaten werden deshalb gedreht.

        # Rotation 90°
        physical_x0 = y0
        physical_x1 = y1

        physical_y0 = 319 - x1
        physical_y1 = 319 - x0

        self.write_cmd(0x2A)

        self.write_data((physical_x0 >> 8) & 0xFF)
        self.write_data(physical_x0 & 0xFF)

        self.write_data((physical_x1 >> 8) & 0xFF)
        self.write_data(physical_x1 & 0xFF)

        self.write_cmd(0x2B)

        self.write_data((physical_y0 >> 8) & 0xFF)
        self.write_data(physical_y0 & 0xFF)

        self.write_data((physical_y1 >> 8) & 0xFF)
        self.write_data(physical_y1 & 0xFF)

        self.write_cmd(0x2C)


    # --------------------------------------------------
    # Bildschirm löschen
    # --------------------------------------------------

    def fill(self, color):

        # Ganze Fläche in kleinen Blöcken schreiben
        block_pixels = 1024

        high = (color >> 8) & 0xFF
        low = color & 0xFF

        block = bytearray(block_pixels * 2)

        for i in range(0, len(block), 2):
            block[i] = high
            block[i + 1] = low

        total_pixels = self.width * self.height

        self.set_window(
            0,
            0,
            self.width - 1,
            self.height - 1
        )

        self.cs(1)
        self.dc(1)
        self.cs(0)

        remaining = total_pixels

        while remaining > 0:

            count = min(block_pixels, remaining)

            self.spi.write(memoryview(block)[:count * 2])

            remaining -= count

        self.cs(1)


    # --------------------------------------------------
    # Rechteck
    # --------------------------------------------------

    def fill_rect(self, x, y, w, h, color):

        if x < 0:
            w += x
            x = 0

        if y < 0:
            h += y
            y = 0

        if x + w > self.width:
            w = self.width - x

        if y + h > self.height:
            h = self.height - y

        if w <= 0 or h <= 0:
            return

        high = (color >> 8) & 0xFF
        low = color & 0xFF

        row = bytearray(w * 2)

        for i in range(0, len(row), 2):
            row[i] = high
            row[i + 1] = low

        self.set_window(
            x,
            y,
            x + w - 1,
            y + h - 1
        )

        self.cs(1)
        self.dc(1)
        self.cs(0)

        for _ in range(h):
            self.spi.write(row)

        self.cs(1)


    # --------------------------------------------------
    # Text
    # --------------------------------------------------

    def text(self, string, x, y, color):

        if not string:
            return

        width = len(string) * 8
        height = 8

        buffer = bytearray(width * height * 2)

        fb = framebuf.FrameBuffer(
            buffer,
            width,
            height,
            framebuf.RGB565
        )

        # Transparenter Hintergrund
        fb.fill(self.BLACK)

        # Text zeichnen
        fb.text(string, 0, 0, color)

        # Nur tatsächlich gesetzte Textpixel übertragen
        for py in range(height):
            for px in range(width):

                pixel = fb.pixel(px, py)

                if pixel != self.BLACK:
                    self.fill_rect(
                        x + px,
                        y + py,
                        1,
                        1,
                        pixel
                    )

        del fb
        del buffer
    # --------------------------------------------------
    # Bildschirm anzeigen
    #
    # Bei dieser Version wird direkt gezeichnet.
    # show() bleibt deshalb aus Kompatibilitätsgründen.
    # --------------------------------------------------

    def show(self):
        pass


    def show_up(self):
        pass


    def show_down(self):
        pass


    # --------------------------------------------------
    # Hintergrundbeleuchtung
    # --------------------------------------------------

    def bl_ctrl(self, duty):

        pwm = PWM(Pin(LCD_BL))
        pwm.freq(1000)

        if duty >= 100:
            pwm.duty_u16(65535)
        else:
            pwm.duty_u16(655 * duty)


    # --------------------------------------------------
    # Touch
    # --------------------------------------------------

    def touch_get(self):

        if self.irq() != 0:
            return None

        self.spi = SPI(
            1,
            baudrate=4_000_000,
            sck=Pin(LCD_SCK),
            mosi=Pin(LCD_MOSI),
            miso=Pin(LCD_MISO)
        )

        self.tp_cs(0)

        X_Point = 0
        Y_Point = 0

        for _ in range(3):

            self.spi.write(bytearray([0xD0]))

            read_data = self.spi.read(2)

            time.sleep_us(10)

            X_Point += (
                ((read_data[0] << 8) + read_data[1]) >> 3
            )

            self.spi.write(bytearray([0x90]))

            read_data = self.spi.read(2)

            Y_Point += (
                ((read_data[0] << 8) + read_data[1]) >> 3
            )

        X_Point = X_Point / 3
        Y_Point = Y_Point / 3

        self.tp_cs(1)

        # LCD SPI wieder auf schnell
        self.spi = SPI(
            1,
            baudrate=40_000_000,
            sck=Pin(LCD_SCK),
            mosi=Pin(LCD_MOSI),
            miso=Pin(LCD_MISO)
        )

        # Touch-Koordinaten auf 320x480 umrechnen
        x = int((Y_Point - 430) * 480 / 3270)
        y = 320 - int((X_Point - 430) * 320 / 3270)

        # Begrenzen
        if x < 0:
            x = 0
        if x >= 480:
            x = 479

        if y < 0:
            y = 0
        if y >= 320:
            y = 319

        return [x, y]
