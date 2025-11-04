import pygame
from settings import *
from state import State


class Agent(pygame.sprite.Sprite):
    def __init__(self, name, x, y, color):
        """
        Initialize the agent class as subclass of Pygame Sprite.
        Args:
            name: str, name of the agent
            x: int, x-coordinate of the agent
            y: int, y-coordinate of the agent
            color: tuple, RGB color of the agent
        """
        super().__init__()
        # Agent properties
        self.name = name
        self.controller = None  # Algorithm controlling the agent
        self.max_speed = 0  # R_v
        self.position = pygame.Vector2(x, y)
        
        # State properties
        self.active_state = None
        
        # Pygame sprite setup for rendering
        self.image = pygame.Surface((10, 10))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))

    def set_state(self, new_state):
        """
        Change the agent's state. Called from updated method after transition conditions were checked.
        Exits the current state and enters the new state.
        Args:
            new_state: state object
        """
        # Exit the current state if exists (in initialization no current state)
        if self.active_state:
            self.active_state.exit()
        
        # Set & enter new active state
        self.active_state = new_state
        self.active_state.enter(agent=self)
        return
    
    def move(self, vector: pygame.Vector2, speed=None, mode='direction'):
        """
        Move agent to the given position if within speed range, else on a vector towards it.
        Args:
            vector: pygame.Vector2, can be position to move to or direction to move in
            speed: int (optional), speed to move with, if None method uses base speed
            mode: str, 'direction' or 'position', whether vector is a direction or a position
        """
        # use given speed if specified otherwise standard speed
        velocity = speed if speed is not None else self.max_speed
        
        # If vector is a position, calculate the direction vector and 
        # move the agent in that direction 
        # (either directly to the point or as close as possible within speed)
        if mode == 'position':
            distance = self.position.distance_to(vector)
            if distance <= velocity:
                self.position = vector
            else:
                direction = pygame.Vector2(vector - self.position)
                direction.normalize_ip()
                self.position += direction * velocity
        
        # If vector is a direction, move the agent in that direction
        elif mode == 'direction':
            if vector.length() > 0:
                vector.normalize_ip()
                self.position += vector * velocity
        
        else:
            raise ValueError(f"Invalid mode: {mode}")
        
        # Keep agent within boundaries
        self.position.x = int(max(0, min(GAME_WIDTH, self.position.x)))
        self.position.y = int(max(0, min(HEIGHT, self.position.y)))

        # Update the sprite position
        self.rect.center = (self.position.x, self.position.y)
        return
    

class Searching(State):
    def __init__(self):
        super().__init__()
        
    def action(self, direction):
        # Move in random direction?
        return

    def check_transition(self):
        pass


class Working(State):
    def __init__(self):
        super().__init__()
        
    def action(self):
        # Perform work logic here
        return

    def check_transition(self):
        pass


class Helping(State):
    def __init__(self):
        super().__init__()
        
    def action(self, direction):
        # Move towards the help call location
        return

    def check_transition(self):
        pass