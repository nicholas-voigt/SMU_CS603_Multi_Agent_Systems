# Implementation of the base State class for agents' state machines

class State:
    def __init__(self):
        self.agent = None
    
    def enter(self, agent):
        """Called when an agent enters this state"""
        self.agent = agent
        
    def exit(self):
        """Called when an agent exits this state"""
        self.agent = None

    def action(self, *args, **kwargs):
        """Action logic for this state, to be implemented by subclasses"""
        pass
    
    def check_transition(self):
        """
        Check if the agent can transition to another state, to be implemented by subclasses
        Returns:
            state_object of state if transition is possible/necessary, None otherwise
        """
        pass
