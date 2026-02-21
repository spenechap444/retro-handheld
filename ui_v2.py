from machine import Pin, SPI
import time
import ssd1306 as ssd1306
import inputs_v2
import utime
import views.test

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

class Screen:
    def on_enter(self): pass
    def on_exist(self): pass
    def handle(self): pass
    def render(self): pass
    
class BodyItem:
    def __init__(self, text: str, title: bool, selectable: bool, x: float, y: float):
        self.text = text
        self.title = title
        self.selectable = selectable
        self.x = x
        self.y = y
    
class HomeScreen(Screen):
    def __init__(self, body: list(BodyItem)):
        self.body = body
        self.selectable_indices = [i for i, it in enumerate(body) if it.selectable]
        self.sel_pos = 0 # position with selectable_indices
        
    def move(self, delta):
        if not self.selectable_indices:
            return
        self.sel_pos = (self.sel_pos + delta) % len(self.selectable_indices)
        
    def current_item(self):
        if not self.selectable_indices:
            return None
        return self.body[self.selectable_indices[self.sel_pos]]
    
    def select(self):
        item = self.current_item()
        if item:
            # for now just return the text; later you can change screen/state
            return item.text
        return None
        
    def _clamp(self):
        pass
        # max y val = 45, if > 45, change visible UI items
    def _text_2x(self, item):
        self.body.append(BodyItem(text=item.text, title=False, selectable=item.selectable, x=item.x+1, y=item.y))
        self.body.append(BodyItem(text=item.text, title=False, selectable=item.selectable, x=item.x, y=item.y+1))
        self.body.append(BodyItem(text=item.text, title=False, selectable=item.selectable, x=item.x+1, y=item.y+1))
        
        
    def render(self):
        oled.fill(0)
        v_padding=0
        
        selected_global_index = None
        if self.selectable_indices:
            selected_global_index = self.selectable_indices[self.sel_pos]
        
        # iterate through the body items
        for i, body in enumerate(self.body):
            if body.title:
                v_padding += 10
                self._text_2x(body)
            
            # Draw cursor for selected selectable item
            if i == selected_global_index:
                oled.text(">", 0, body.y + v_padding)
                text_x = body.x + 10 # sift right so it doesn't collide
            else:
                text_x = body.x
                
            oled.text(body.text, text_x, body.y + v_padding)

            
        oled.show()

import brick_breaker as bb
from utime import sleep

class BrickBreakerGame:
    """Main game controller"""
    
    def __init__(self, display):
        self.display = display
        self.game = bb.Game(display.width, display.height)
    
    def run(self):
        """Main game loop"""
        self.game.draw(self.display)
        while True:
            events = inputs.poll()
            if events:
                for e in events:
                    if e == "UP":
                        self.game.set_input(left=True, right=False)
                    elif e == "DOWN":
                        self.game.set_input(left=False, right=True)
            # In a real implementation, you would read actual input here
            # For now, this is a simulation loop
            self.game.update()
            self.game.draw(self.display)
            sleep(0.05)  # ~20 FPS
            
            if not self.game.running:
                sleep(2)
                break

def run_brick_breaker():
    bbGame = BrickBreakerGame(display=oled)
    bbGame.run()


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
