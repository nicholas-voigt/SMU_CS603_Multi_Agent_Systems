import mesa
from state import State


class Task(mesa.Agent):
    def __init__(self, model: mesa.Model, work_range: int):
        """
        Agent class for the multi-agent system simulation.
        Args:
            model (mesa.Model): The model instance the agent belongs to.
            work_range (int): The range within which the task can be worked on.
        """
        super().__init__(model)
        self.work_range = work_range
        # Default state is instantiated from the state class
        self.active_state = IdleState() 

    def step(self):
        # Delegate all logic to the current state object.
        self.active_state.execute(self)

    def change_state(self, new_state):
        self.active_state = new_state
        # Optional: self.state.enter(self) for one-time setup logic


class IdleState(State):
    def execute(self, agent):
        # Task is idle, waiting to be assigned
        pass


class WorkingState(State):
    def execute(self, agent):
        # Task is being worked on, check for completion
        # Notify when done 
        pass # No movement logic


class CompletedState(State):
    def execute(self, agent):
        # Task is completed
        pass