import time
import board
import supervisor
import alarm
import digitalio
import displayio
import terminalio
import adafruit_ssd1680
from adafruit_bus_device.i2c_device import I2CDevice
from adafruit_display_text import label

default_text = "Jmeno,Prijmeni,Firma/Projekt"

# --- Init NFC ---

# normal IO is used for power of NFC chip
nfc_pwr = digitalio.DigitalInOut(board.D6)
nfc_gnd = digitalio.DigitalInOut(board.D7)
nfc_pwr.direction = digitalio.Direction.OUTPUT
nfc_gnd.direction = digitalio.Direction.OUTPUT
nfc_pwr.value = True
nfc_gnd.value = False

i2c = board.I2C()
nfc = I2CDevice(i2c, 0x55)

# --- Init display ---

# Define board pinout
board_spi = board.SPI()
board_epd_cs = board.D41
board_epd_dc = board.D40
board_epd_reset = board.D39
board_epd_busy = board.D42

# Define ePaper display colors value
display_black = 0x000000
display_white = 0xFFFFFF

# Define ePaper display resolution
display_width = 250
display_height = 122

# Prepare ePaper display
displayio.release_displays()
display_bus = displayio.FourWire(
    board_spi, command = board_epd_dc, chip_select = board_epd_cs, reset = board_epd_reset, baudrate = 1000000
)
time.sleep(1)
display = adafruit_ssd1680.SSD1680(
    display_bus, width = display_width, height = display_height, rotation = 270, busy_pin = board_epd_busy, seconds_per_frame = 10.0
)
display_data = displayio.Group()
display_background = displayio.Bitmap(display_width, display_height, 1)
display_color_palette = displayio.Palette(1)
display_color_palette[0] = display_white

# Append tilegrid with the background to the display data
display_data.append(displayio.TileGrid(display_background, pixel_shader = display_color_palette))

print("Init done")


# ---


def read_tag_into(buffer):
    for i in range(len(buffer) // 16):        
        with nfc:
            nfc.write(bytes([i+1]))
            nfc.readinto(buffer, start = i*16, end = (i+1)*16)


def nfc_get_text():
    try:
        buf = bytearray(64)
        read_tag_into(buf)
        text = parse_text(buf)
        print(text)
        return text    
    except Exception as ex:
        print(ex)
        return default_text


def print_buffer(buffer):
    print("".join("{:02X} ".format(x) for x in buffer))


def parse_text(buf):
    # Super hacky NDEF parser
    # it will parse only text message from Text record on short NDEF message stored on NFC Tag Type 2

    if (buf[0] != 0x03):
        raise Exception("Unsupported NFC type 2 TVL tag")
    
    if (buf[2] != 0xD1):
        raise Exception("Unknown NDEF Record")

    rec_type_len = buf[3]

    if (buf[3] != 0x01):
        raise Exception("Unsupported type length")

    rec_data_len = buf[4]
    rec_type = chr(buf[5])
    #print("Type: {}".format(rec_type))

    if (rec_type != "T"): 
        raise Exception("Unsupported type")

    txt_rec_flag = buf[6]

    if (txt_rec_flag != 0x02):
        raise Exception("Unsupported txt encoding or lang size")
    
    text = buf[9 : (rec_data_len + 9 - 3)]
    return text.decode("utf-8")


def refresh():
    while True:    
        try:
            print("Refresh")
            display.refresh()
            while display.busy:
                pass
            print("refresh done")
            return
        except RuntimeError as ex:
            print(ex)
            time.sleep(5)


# Parse NFC
def set_text(text):
    print("Text: {}".format(text))
    lines = text.split(",");
    n = len(lines)
        
    label1.text = lines[0].strip() if n >= 1 else ""
    label2.text = lines[1].strip() if n >= 2 else ""
    label3.text = lines[2].strip() if n >= 3 else ""
        
    refresh()


# Function for append text to the display data
def _addLabel(scale, color, x_cord, y_cord):
    text_label = label.Label(terminalio.FONT, color = color, scale = scale)
    text_label.anchor_point = (0.5, 0.0)
    text_label.anchored_position = (x_cord, y_cord)
    display_data.append(text_label)
    return text_label


# Render namecard to display
x = 125
label1 = _addLabel(3, display_black, x, 5)
label2 = _addLabel(3, display_black, x, 50)
label3 = _addLabel(2, display_black, x, 95)
display.show(display_data)

text = nfc_get_text()
set_text(text)

print("done")
        
# go to deep sleep and wait for NFC field detect
pin_alarm = alarm.pin.PinAlarm(pin=board.D10, value=False, pull=True)
alarm.exit_and_deep_sleep_until_alarms(pin_alarm)
