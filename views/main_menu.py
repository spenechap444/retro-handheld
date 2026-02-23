from views.base_view import Screen, BodyItem

class HomeScreen(Screen):
    def __init__(self, body: list(BodyItem), display):
        self.body = body
        self.display = display
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
        self.display.fill(0)
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
                self.display.text(">", 0, body.y + v_padding)
                text_x = body.x + 10 # sift right so it doesn't collide
            else:
                text_x = body.x
                
            self.display.text(body.text, text_x, body.y + v_padding)

            
        self.display.show()

