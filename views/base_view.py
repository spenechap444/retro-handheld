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