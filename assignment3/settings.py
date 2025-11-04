# Define parameters for game environment and simulation

# Pygame Settings
GAME_WIDTH = 800
PANEL_WIDTH = 300
WIDTH = GAME_WIDTH + PANEL_WIDTH
HEIGHT = 600
FPS = 10

# Game Settings
NUM_AGENTS = 10  # Number of agents to create
NUM_TASKS = 5   # Number of tasks to keep in the environment

TASK_RANGE = 50  # Range within which tasks can be performed
AGENT_SPEED = 5  # Base speed of agents
COMMUNICATION_RANGE = 200  # Range within which agents can communicate (hear help calls)