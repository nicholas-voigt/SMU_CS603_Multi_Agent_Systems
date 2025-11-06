class State:
    """Base class for all agent or task states."""
    @property
    def name(self): 
        return self.__class__.__name__
    
    def execute(self, agent):
        """The main logic for this state."""
        raise NotImplementedError
