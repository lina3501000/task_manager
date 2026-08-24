from screen import LCD_3inch5
import time


LCD = LCD_3inch5()
LCD.bl_ctrl(100)

LCD.fill(LCD.WHITE)

# 4 Bereiche
LCD.fill_rect(0, 0, 320, 120, LCD.RED)
LCD.fill_rect(0, 120, 320, 120, LCD.GREEN)
LCD.fill_rect(0, 240, 320, 120, LCD.BLUE)
LCD.fill_rect(0, 360, 320, 120, LCD.BLACK)
# if you want black text, you need to use black instead of BLACK
LCD.text("OBEN", 20, 20, LCD.black)
LCD.text("MITTE OBEN", 20, 140, LCD.WHITE)
LCD.text("MITTE UNTEN", 20, 260, LCD.WHITE)
LCD.text("UNTEN", 20, 380, LCD.WHITE)

#while True:
#    time.sleep(1)