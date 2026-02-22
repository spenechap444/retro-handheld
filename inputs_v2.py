from machine import Pin
import utime

class ButtonEvents:
    def __init__(self, pin_to_name: dict, debounce_ms=150):
        self.debounce_ms = debounce_ms
        self.buttons = {}
        self.last_state = {}
        self.last_time = {}
        
        now = utime.ticks_ms()
        for pin_num, name in pin_to_name.items():
            p = Pin(pin_num, Pin.IN, Pin.PULL_DOWN)
            self.buttons[name] = p # capturing the different button's pins
            self.last_state[name] = p.value() # capturing value of last state
            self.last_time[name] = now # capturing ms since last state read
            
    def poll(self):
        ''' Call this frequently.  Returns a list of events like ["UP", "SELECT"]
            Usually 0 or 1 event, but list keeps it flexible'''
        events = []
        now = utime.ticks_ms()
        
        # iterating through the buttons
        for name, pin in self.buttons.items():
            v = pin.value()
            prev = self.last_state[name]
            
            # Rising edge = "pressed"
            if prev == 0 and v == 1:
                # Debounce gate
                if utime.ticks_diff(now, self.last_time[name]) >= self.debounce_ms:
                    events.append(name)
                    self.last_time[name] = now # updating last time
            
            self.last_state[name] = v # updating state value
        
        return events
    
    def get_button_state(self):
        ''' Returns a dict of current button states for continuous input (held buttons)
            Usage: state = inputs.get_button_state()
                   if state["UP"]: paddle moves left (while held)'''
        state = {}
        for name, pin in self.buttons.items():
            state[name] = pin.value() == 1  # True if pressed, False if released
        return state
