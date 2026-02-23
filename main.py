from machine import Pin, SPI
import time
import utime
from views.base_view import BodyItem
from views.main_menu import HomeScreen

import ssd1306 as ssd1306
import inputs_v2
# import views.test

# SPI0: SCK=GP2, MOSI=GP3 (most reliable)
spi = SPI(0, baudrate=10_000_000, polarity=0, phase=0,
          sck=Pin(2), mosi=Pin(3))

dc  = Pin(5, Pin.OUT)
cs  = Pin(4, Pin.OUT)
rst = Pin(6, Pin.OUT)

# Hard reset pulse (helps with "blank but no error")
rst.value(0)
time.sleep_ms(50)
rst.value(1)
time.sleep_ms(50)

oled = ssd1306.SSD1306_SPI(128, 64, spi, dc, rst, cs)

header = BodyItem(text='M E N U',
                title=True,
                selectable=False,
                x=40,
                y=0)
item1 = BodyItem(text='1. Browse songs',
                 title=False,
                 selectable=True,
                 x=0,
                 y=10)
item2 = BodyItem(text='2. Restart song',
                 title=False,
                 selectable=True,
                 x=0,
                 y=20)
item3 = BodyItem(text='3. Games',
                 title=False,
                 selectable=True,
                 x=0,
                 y=30)
item4 = BodyItem(text='4. Settings',
                 title=False,
                 selectable=True,
                 x=0,
                 y=40)

menu_items = [header, item1, item2, item3, item4]

Home = HomeScreen(menu_items)
Home.render()

inputs = inputs_v2.ButtonEvents({
    11: "UP",
    12: "SELECT",
    13: "DOWN"
}, debounce_ms=150)

while True:
    events = inputs.poll()
    if events:
        for e in events:
            if e == "UP":
                Home.move(-1)
                Home.render()
            elif e == "DOWN":
                Home.move(+1)
                Home.render()
            elif e == "SELECT":
                chosen = Home.select()
                print("Selected:", chosen)
                if chosen == "3. Games":
                    bbGame = BrickBreakerGame(display=oled)
                    bbGame.run()
                # Later: switch screen based on chosen
    utime.sleep_ms(20) # fast enough for responsiveness