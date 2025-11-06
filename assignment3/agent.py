import mesa
from state import State


class Agent(mesa.Agent):
    def __init__(self, model: mesa.Model, protocol: str, speed: int, call_range: int, response_timeout: int):
        """
        Agent class for the multi-agent system simulation.
        Args:
            model (mesa.Model): The model instance the agent belongs to.
            protocol (str): Communication protocol ('random', 'call-out', 'auction').
            speed (int): Movement speed of the agent.
            call_range (int): Communication range for calls/auctions.
            response_timeout (int): Maximum time to respond to calls/auctions.
        """
        super().__init__(model)
        self.speed = speed
        self.comm_range = call_range
        self.response_timer_max = response_timeout
        self.protocol = protocol
        # Default state is instantiated from the state class
        self.active_state = SearchingState() 

    def step(self):
        # Delegate all logic to the current state object.
        self.active_state.execute(self)

    def change_state(self, new_state):
        self.active_state = new_state


class SearchingState(State):
    def execute(self, agent):
        # 1. Implement movement logic
        # 2. Check for tasks
        # 3. If protocol!= 'random', check for calls/auctions (within R_d)
        # 4. Handle possible state change to WorkingState, RespondingToCallState, WaitingForHelpState
        pass


class WaitingForHelpState(State):
    def execute(self, agent):
        # wait for help logic
        pass


class WorkingState(State):
    def __init__(self, task, emitting_call=False):
        self.task = task
        # Used for 'call-out' protocol
        self.emitting_call = emitting_call 
    
    def execute(self, agent):
        # Per assignment: "agent will stop and wait" 
        pass # No movement logic


class RespondingToCallState(State):
    def __init__(self, target_pos, timer):
        self.target_pos = target_pos
        self.timer = timer
    
    def execute(self, agent):
        # 1. Move towards target_pos
        # 2. Decrement self.timer
        # 3. If self.timer == 0, agent.change_state(SearchingState())
        # 4. If at target, agent.change_state(WorkingState(...))
        pass

