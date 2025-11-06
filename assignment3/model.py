import mesa
from agents import WorkerAgent, TaskAgent


class STAModel(mesa.Model):
    def __init__(self, seed: float | None, num_agents: int, num_tasks: int, protocol: str,
                 agent_speed: int, agent_call_range: int, agent_response_timeout: int, 
                 task_work_range: int, task_workers: int, task_time: int) -> None:
        """
        Model class for the multi-agent system simulation.
        Args:
            seed (float | None): Seed for random number generator.
            num_agents (int): Number of agents in the simulation.
            num_tasks (int): Number of tasks in the simulation.
            protocol (str): Protocol used by agents (e.g., 'random', 'call_out', 'call_off').
            agent_speed (int): Speed of the agents.
            agent_call_range (int): Call range of the agents.
            agent_response_timeout (int): Response timeout of the agents.
            task_work_range (int): Work range of the tasks.
            task_workers (int): Number of workers required per task.
            task_time (int): Time required to complete each task.
        """
        super().__init__(seed=seed)
        self.num_agents = num_agents
        self.num_tasks = num_tasks

        # Game Parameters
        self.agent_speed = agent_speed
        self.agent_call_range = agent_call_range
        self.agent_response_timeout = agent_response_timeout
        self.task_work_range = task_work_range

        # Initialize space
        self.space = mesa.space.ContinuousSpace(x_max=1000, y_max=1000, torus=False)

        # Initialize agents and tasks
        WorkerAgent.create_agents(self, num_agents, speed=agent_speed, call_range=agent_call_range, action_range=task_work_range, response_timeout=agent_response_timeout)
        TaskAgent.create_agents(self, num_tasks, workers_required=task_workers, time_required=task_time)

        # Data Collection
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Completed_Tasks": lambda m: sum(1 for agent in m.agents if isinstance(agent, TaskAgent) and agent.active_state.name == "TaskCompleted"),
                "Active_Tasks": lambda m: sum(1 for agent in m.agents if isinstance(agent, TaskAgent) and agent.active_state.name != "TaskCompleted"),
            },
            agent_reporters={
                "Agent_State": lambda a: a.active_state.name,
            }
        )


    def step(self) -> None:
        """
        Advance the model by one step. 
        """
        # Advance all agents randomly within their types to prevent race conditions
        for agent_class in self.agent_types:
            self.agents_by_type[agent_class].shuffle_do("step")
        
        # Collect data
        self.datacollector.collect(self)
