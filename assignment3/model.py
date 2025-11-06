import mesa
from agent import Agent
from task import Task


class Model(mesa.Model):
    def __init__(self, seed: float | None, num_agents: int, num_tasks: int, activation: str, 
                 agent_speed: int, agent_call_range: int, agent_response_timeout: int, task_work_range: int) -> None:
        """
        Model class for the multi-agent system simulation.
        Args:
            seed (float | None): Seed for random number generator.
            num_agents (int): Number of agents in the simulation.
            num_tasks (int): Number of tasks in the simulation.
            activation (str): Activation schedule type ('random', 'sequential', etc.).
            agent_speed (int): Speed of the agents.
            agent_call_range (int): Call range of the agents.
            agent_response_timeout (int): Response timeout of the agents.
            task_work_range (int): Work range of the tasks.
        """
        super().__init__(seed)
        self.num_agents = num_agents
        self.num_tasks = num_tasks
        self.activation = activation

        # Initialize grid
        self.grid = mesa.space.ContinuousSpace(x_max=1000, y_max=1000, torus=True)

        # Initialize agents and tasks
        Agent.create_agents(self, num_agents, protocol='random', speed=agent_speed, call_range=agent_call_range, response_timeout=agent_response_timeout)
        Task.create_agents(self, num_tasks, work_range=task_work_range)

        # Data Collection
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Completed_Tasks": lambda m: sum(1 for task in m.tasks if task.state.name == "CompletedState"),
            },
            agent_reporters={
                "Agent_State": lambda a: a.active_state.name,
            }
        )


    def step(self) -> None:
        """
        Advance the model by one step. 
        """