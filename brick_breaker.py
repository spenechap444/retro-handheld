"""
Brick Breaker Game - MicroPython Edition
A classic old-school brick breaker game inspired by BlackBerry games.
Designed for Raspberry Pi Pico with a display.
"""

import machine
import math
import random
from time import sleep

class Brick:
    """Represents a single brick in the game"""
    def __init__(self, x, y, width, height, value=1):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.active = True  # Whether the brick is still unbroken
        self.value = value

class Game:
    def __init__(self, width=125, height=50, display=None):
        self.width = width
        self.height = height
        self.ceiling = 8
        self.display = display  # Store display reference for immediate refreshes

        # Game state
        self.running = True
        self.score = 0
        self.level = 1
        self.lives = 3

        # Paddle
        self.paddle_width = 15
        self.paddle_height = 3
        self.paddle_x = (width - self.paddle_width) // 2 # paddle starts centered
        self.paddle_y = height - 5  # setting paddle height above bottom edge
        self.paddle_speed = 3

        # Ball
        self.ball_x = width / 2 # ball starts above paddle
        self.ball_y = height - 15 # ball starts above paddle
        self.ball_radius = 2 # small ball for better radius
        self.ball_speed = 2
        self.ball_vx = 2 # initial velocity x
        self.ball_vy = -2 # initial velocity y (upwards)
        self.ball_active = False # ball starts inactive until launched

        # Bricks
        self.bricks = []
        self.brick_width = 12
        self.brick_height = 4
        self.brick_padding = 1
        self.rows = 4
        self.cols = 14
        self.start_x = 2
        self.create_bricks(rows=self.rows, cols=self.cols, start_x=self.start_x, start_y=self.ceiling)

        # Input state
        self.left_pressed = False
        self.right_pressed = False

    def create_bricks(self, rows, cols, start_x, start_y):
        """Creating initial brick layout"""
        self.bricks = []
        for row in range(rows): # avoiding divideby zero
            for col in range(cols):
                x = start_x + col * (self.brick_width + self.brick_padding)
                y = start_y + row * (self.brick_height + self.brick_padding)
                if x + self.brick_width < self.width - 2:
                    self.bricks.append(Brick(x=x,
                                            y=y,
                                            width=self.brick_width,
                                            height=self.brick_height,
                                            value = int(12 / (row+1)) * self.level)) # higher rows worth more points
        
    def update(self):
        """Updating game state based on input and collisions"""
        if not self.running:
            return
        
        # Updating paddle position based on input
        if self.left_pressed:
            self.paddle_x = max(0, self.paddle_x - self.paddle_speed)
        if self.right_pressed:
            self.paddle_x = min(self.width - self.paddle_width, 
                               self.paddle_x + self.paddle_speed)
            
        # Launch ball from paddle if not active
        if not self.ball_active:
            self.ball_x = self.paddle_x + self.paddle_width // 2
            self.ball_y = self.paddle_y - self.ball_radius - 1
            if self.left_pressed or self.right_pressed:
                self.ball_active = True
                # Give ball a slight angle based on paddle position
                angle = ((self.paddle_x + self.paddle_width // 2) / self.width - 0.5) * 60
                self.ball_vx = self.ball_speed * math.sin(math.radians(angle))
                self.ball_vy = -abs(self.ball_speed * math.cos(math.radians(angle)))

        if self.ball_active:
            # Update ball position
            self.ball_x += self.ball_vx
            self.ball_y += self.ball_vy

            # Ball collision with walls
            if self.ball_x - self.ball_radius < 0 or self.ball_x + self.ball_radius >= self.width:
                self.ball_vx *= -1 # mirror the oposite velocity
                self.ball_x = max(self.ball_radius, # prevnts ball from going off left of screen
                                  min(self.width - self.ball_radius - 1, self.ball_x)) # prevent ball from going off right of screen
            
            # Ball collision with ceiling
            if self.ball_y - self.ball_radius < self.ceiling:
                self.ball_vy *= -1
                self.ball_y = self.ceiling + self.ball_radius

            # Ball collision with paddle
            if (self.ball_y + self.ball_radius >= self.paddle_y and
                self.ball_y - self.ball_radius <= self.paddle_y + self.paddle_height and
                self.ball_x >= self.paddle_x and
                self.ball_x <= self.paddle_x + self.paddle_width):

                self.ball_vy *= -1 # reverse vertical velocity
                self.ball_y = self.paddle_y - self.ball_radius - 1 # position ball above paddle

                # Add spin based on where ball hits the paddle
                hit_pos = (self.ball_x - self.paddle_x) / self.paddle_width # 0 to 1
                self.ball_vx = (hit_pos - 0.5) * 4 

            # Ball collision with bricks
            for brick in self.bricks:
                if not brick.active:
                    continue

                if self.check_brick_collision(brick):
                    brick.active = False
                    self.score += brick.value
                    self.ball_vy *= -1 # reverse vertical velocity on hit
                    # Force a display buffer refresh to prevent ghosting
                    if self.display:
                        self.display.show()
                    break

            # Ball out of bounds
            if self.ball_y > self.height:
                self.ball_active = False
                self.lives -= 1
                if self.lives <= 0:
                    self.running = False

        # Check for win state (all bricks destroyed)
        if all(not brick.active for brick in self.bricks):
            self.level += 1
            self.ball_active = False
            self.ball_speed *= 1.1 # increase ball speed for next level
            self.create_bricks(rows=self.rows,
                               cols = self.cols,
                               start_x = self.start_x,
                               start_y = self.ceiling) # reset bricks for next level
    
    def check_brick_collision(self, brick):
        """Check if ball collides with brick"""
        closest_x = max(brick.x, min(self.ball_x, brick.x + self.brick_width))
        closest_y = max(brick.y, min(self.ball_y, brick.y + self.brick_height))
        
        distance = math.sqrt((self.ball_x - closest_x)**2 + (self.ball_y - closest_y)**2)
        return distance < self.ball_radius
    
    def draw(self, display):
        """Draw game to display"""
        display.fill(0)

        # Draw bricks
        for brick in self.bricks:
            if brick.active:
                # Draw brick filled rectangle instead of outline to ensure pixels are written
                x, y = int(brick.x), int(brick.y)
                display.fill_rect(x, y, self.brick_width, self.brick_height, 1)
        
        # Draw paddle (filled)
        display.fill_rect(int(self.paddle_x), int(self.paddle_y), 
                         self.paddle_width, self.paddle_height, 1)
        
        # Draw ball (filled)
        display.fill_rect(int(self.ball_x), int(self.ball_y), self.ball_radius, self.ball_radius, 1)
        
        # Draw score and lives at top
        display.text(f"{self.score}", 0, 0, 1)
        step = 5
        for i in range(0, self.lives * step, step):
            self.draw_tiny_heart(display, i, 50)
        # display.text(f"Lives:{self.lives}", 0, 50, 1)
        display.text(f"L:{self.level}", 80, 0, 1)
        
        # Draw game over
        if not self.running:
            display.text("GAME OVER", 20, 30, 1)
            display.text(f"Final score:", 13, 38, 1)
            display.text(str(self.score), 45, 48, 1)
        
        display.show()
        
    def draw_tiny_heart(self, display, x, y):
        """Draw a tiny heart (3x3 pixels) at position x, y"""
        # Simple heart pattern for a 3x3 grid
        display.pixel(x, y, 1)        # top left bump
        display.pixel(x + 2, y, 1)    # top right bump
        display.pixel(x + 1, y + 1, 1) # middle
        display.pixel(x, y + 1, 1) # middle left
        display.pixel(x + 2, y + 1, 1) # middle right
        display.pixel(x + 1, y + 2, 1) # bottom point
    
    def set_input(self, left, right):
        """Update input state"""
        self.left_pressed = left
        self.right_pressed = right


class BrickBreakerGame:
    """Main game controller"""
    
    def __init__(self, display):
        self.display = display
        self.game = Game(display.width, display.height)
    
    def run(self):
        """Main game loop"""
        while True:
            # In a real implementation, you would read actual input here
            # For now, this is a simulation loop
            self.game.update()
            self.game.draw(self.display)
            sleep(0.05)  # ~20 FPS
            
            if not self.game.running:
                sleep(2)
                break

