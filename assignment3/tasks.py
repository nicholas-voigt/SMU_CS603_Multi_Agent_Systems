import pygame
from settings import *
from state import State

class Task(pygame.sprite.Sprite):
    def __init__(self, name, radius, x, y, color):
        """
        Initialize the task class as subclass of Pygame Sprite.
        Args:
            name: str, name of the task
            radius: int, radius of the task in which it can be performed
            x: int, x-coordinate of the task
            y: int, y-coordinate of the task
            color: tuple, RGB color of the task
        """
        super().__init__()
        # Task properties
        self.name = name
        self.position = pygame.Vector2(x, y)
        self.radius = radius

        # Pygame sprite setup for rendering
        self.image = pygame.Surface((10, 10))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.range = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA).fill((color[0], color[1], color[2], 50))
    
    def set_state(self, new_state):
        """
        Change the task's state. Called from updated method after transition conditions were checked.
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
    

class Idle(State):
    def __init__(self):
        super().__init__()
        
    def action(self):
        # Perform work logic here
        return

    def check_transition(self):
        pass


class InProgress(State):
    def __init__(self):
        super().__init__()
        
    def action(self):
        # Perform work logic here
        return

    def check_transition(self):
        pass


class Completed(State):
    def __init__(self):
        super().__init__()
        
    def action(self):
        # Perform work logic here
        return

    def check_transition(self):
        pass