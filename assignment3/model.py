import mesa
from agents import WorkerAgent, TaskAgent


class STAModel(mesa.Model):
    def __init__(self, seed: float | None, num_workers: int, num_tasks: int, use_call_off: bool,
                 worker_speed: int, worker_comm_range: int, worker_timeout: int, worker_break_time: int,
                 task_action_range: int, task_workers: int, task_time: int) -> None:
        """
        Model class for the multi-agent system simulation.
        Args:
            seed (float | None): Seed for random number generator.
            num_agents (int): Number of agents in the simulation.
            num_tasks (int): Number of tasks in the simulation.
            use_call_off (bool): Whether to use call-off protocol (if false, uses call-out without freeing of workers).
            worker_speed (int): Speed of the workers.
            worker_comm_range (int): Call range of the workers to communicate.
            worker_timeout (int): Response timeout of the workers.
            worker_break_time (int): Break time of the workers after releasing a task.
            task_action_range (int): Work range of the tasks.
            task_workers (int): Number of workers required per task.
            task_time (int): Time required to complete each task.
        """
        super().__init__(seed=seed)
        self.num_agents = num_workers
        self.num_tasks = num_tasks

        # Game Parameters
        self.speed = worker_speed
        self.comm_range = worker_comm_range
        self.worker_timeout = worker_timeout
        self.worker_break_time = worker_break_time
        self.action_range = task_action_range

        # Initialize space
        self.space = mesa.space.ContinuousSpace(x_max=1000, y_max=1000, torus=False)

        # Initialize agents and tasks
        WorkerAgent.create_agents(self, num_workers, call_off=use_call_off, speed=worker_speed, call_range=worker_comm_range, action_range=task_action_range, response_timeout=worker_timeout, break_time=worker_break_time)
        TaskAgent.create_agents(self, num_tasks, action_range=task_action_range, workers_required=task_workers, time_required=task_time)

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
