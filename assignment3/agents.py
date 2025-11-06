import mesa
import numpy as np

# --- BASE STATE CLASS ---
class State:
    """Base class for all agent states."""
    @property
    def name(self):
        return self.__class__.__name__
    
    def execute(self, agent):
        """The main logic for this state."""
        raise NotImplementedError


# --- STATE CLASSES FOR WORKER ---
class WorkerSearching(State):
    """
    The state for a worker randomly walking around and searching for tasks.
    """
    def execute(self, agent):
        # --- Task Search Logic ---
        neighbors = agent.model.space.get_neighbors(
            agent.pos,
            radius=agent.action_range,
            include_center=False
        )
        tasks = list(filter(lambda a: isinstance(a, TaskAgent) and a.active_state.name == "TaskIdle", neighbors))

        if len(tasks) == 0:
            # --- Random Walk Logic ---
            # Agent picks a random direction and speed within speed limit
            angle = agent.random.uniform(0, 2 * np.pi)
            speed = agent.random.uniform(0, agent.speed)
            new_x = agent.pos[0] + np.cos(angle) * speed
            new_y = agent.pos[1] + np.sin(angle) * speed
            # Enforce the boundaries of the grid & walk
            new_x = max(0, min(agent.model.space.x_max - 1, new_x))
            new_y = max(0, min(agent.model.space.y_max - 1, new_y))
            agent.model.space.move_agent(agent, (new_x, new_y))

        else:
            task = min(tasks, key=lambda t: agent.model.space.get_distance(agent.pos, t.pos))
            if task.workers_required == 1:
                # Found a task to work on alone
                task.change_state(TaskExecuting([agent]))
                agent.change_state(WorkerWorking(task))
        
            else:
                # Found a task that needs more workers, notify in range and change to WaitingState
                neighbors = agent.model.space.get_neighbors(
                    agent.pos,
                    radius=agent.call_range,
                    include_center=False
                )
                workers = filter(lambda a: isinstance(a, WorkerAgent) and a != agent and a.active_state.name == "WorkerSearching", neighbors)
                for worker in workers:
                    worker.change_state(WorkerResponding(task, worker.response_timeout))
                agent.change_state(WorkerWaiting(task, agent.response_timeout))


class WorkerWaiting(State):
    def __init__(self, task, timer):
        self.task = task
        self.timer = timer

    def execute(self, agent):
        # Check if timer has expired
        if self.timer == 0:
            agent.change_state(WorkerSearching())
            return
        else:
            self.timer -= 1


class WorkerResponding(State):
    def __init__(self, task, timer):
        self.target_pos = task.pos
        self.task = task
        self.timer = timer
    
    def execute(self, agent):
        # Check timer expiry
        if self.timer == 0:
            agent.change_state(WorkerSearching())
            return
        
        self.timer -= 1

        # Check position
        direction = np.array(self.target_pos) - np.array(agent.pos)
        distance_to_target = np.linalg.norm(direction)
        
        if distance_to_target <= agent.action_range:
            agent.change_state(WorkerWaiting(self.task, self.timer))
        else:
            direction /= distance_to_target  # Normalize
            new_pos = agent.pos + direction * min(agent.speed, distance_to_target)
            agent.model.space.move_agent(agent, new_pos)


class WorkerWorking(State):
    def __init__(self, task):
        self.task = task

    def execute(self, agent):
        # Perform work logic
        pass


# --- STATE CLASSES FOR TASK ---
class TaskIdle(State):
    """
    The state for a task existing and waiting for execution.
    Handles search logic to find and assign workers.
    """
    def execute(self, agent):
        # Task is idle, waiting to be assigned
        pass


class TaskExecuting(State):
    """
    The state for a task being executed by assigned workers. Tracks progress and completion.
    """
    def __init__(self, workers):
        self.workers = workers

    def execute(self, agent):
        # Reduce time required with each step until 0 then change state to Completed
        # If completed, notify workers to return to searching, change to completed state and create a new task
        if agent.time_required == 0:
            for worker in self.workers:
                worker.change_state(WorkerSearching())
            agent.create_agents(agent.model, 1, agent.workers_required, agent.time_required)
            agent.change_state(TaskCompleted())

        else:
            agent.time_required -= 1


class TaskCompleted(State):
    def execute(self, agent):
        # Task is completed
        pass


# --- AGENT CLASSES ---
# Implements WorkerAgent and TaskAgent.
# Agents use a state machine to manage their behavior, they don't implement logic directly.

class WorkerAgent(mesa.Agent):
    """
    The WorkerAgent that moves and performs tasks.
    """
    def __init__(self, model: mesa.Model, speed: int, call_range: int, action_range: int, response_timeout: int):
        """
        Args:
            model (mesa.Model): The model instance the agent belongs to.
            speed (int): Movement speed of the agent.
            call_range (int): Communication range for calls/auctions.
            action_range (int): Action range for performing tasks.
            response_timeout (int): Maximum time to respond to calls/auctions.
        """
        super().__init__(model)
        self.speed = speed
        self.call_range = call_range
        self.action_range = action_range
        self.response_timeout = response_timeout
        self.active_state = WorkerSearching()

        # Place agent at random position in space
        x = self.random.uniform(0, self.model.space.x_max) # type: ignore
        y = self.random.uniform(0, self.model.space.y_max) # type: ignore
        self.model.space.place_agent(self, (x, y)) # type: ignore

    def change_state(self, new_state):
        self.active_state = new_state

    def step(self):
        self.active_state.execute(self)


class TaskAgent(mesa.Agent):
    """
    The TaskAgent that is placed on the grid.
    """
    def __init__(self, model: mesa.Model, workers_required: int, time_required: int):
        """
        Args:
            model (mesa.Model): The model instance the agent belongs to.
            workers_required (int): The number of workers required to complete the task.
            time_required (int): The time required to complete the task.
        """
        super().__init__(model)
        self.workers_required = workers_required
        self.time_required = time_required
        self.active_state = TaskIdle()

        # Place task at random position in space
        x = self.random.uniform(0, self.model.space.x_max) # type: ignore
        y = self.random.uniform(0, self.model.space.y_max) # type: ignore
        self.model.space.place_agent(self, (x, y)) # type: ignore

    def step(self):
        self.active_state.execute(self)

    def change_state(self, new_state):
        self.active_state = new_state
