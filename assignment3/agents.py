import mesa
import numpy as np


# --- AGENT CLASSES ---
# Implements WorkerAgent and TaskAgent.
# Agents use a state machine to manage their behavior, they don't implement logic directly.

class WorkerAgent(mesa.Agent):
    """
    The WorkerAgent that moves and performs tasks.
    """
    def __init__(self, model: mesa.Model, speed: int, call_range: int, action_range: int, response_timeout: int, break_time: int):
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
        self.break_time = break_time
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
    def __init__(self, model: mesa.Model, action_range: int, workers_required: int, time_required: int):
        """
        Args:
            model (mesa.Model): The model instance the agent belongs to.
            action_range (int): The action range for the task.
            workers_required (int): The number of workers required to complete the task.
            time_required (int): The time required to complete the task.
        """
        super().__init__(model)
        self.action_range = action_range
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
    def __init__(self, break_time: int = 0):
        self.break_time = break_time

    def execute(self, agent):
        # --- Task Search Logic ---
        neighbors = agent.model.space.get_neighbors(
            agent.pos,
            radius=agent.action_range,
            include_center=False
        )
        tasks = list(filter(lambda a: isinstance(a, TaskAgent) and a.active_state.name == "TaskIdle", neighbors))

        if len(tasks) == 0 or self.break_time > 0:
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
            # Decrease break time if on break
            self.break_time = max(0, self.break_time - 1)

        else:
            task = min(tasks, key=lambda t: agent.model.space.get_distance(agent.pos, t.pos))
            if task.workers_required > 1:
                # Notify other workers in range
                neighbors = agent.model.space.get_neighbors(
                    agent.pos,
                    radius=agent.call_range,
                    include_center=False
                )
                workers = filter(lambda a: isinstance(a, WorkerAgent) and a != agent and a.active_state.name == "WorkerSearching", neighbors)
                for worker in workers:
                    worker.change_state(WorkerResponding(task, worker.response_timeout))

            # Set worker into waiting for execution state
            agent.change_state(WorkerWaiting(task, agent.response_timeout))


class WorkerWaiting(State):
    def __init__(self, task, timer):
        self.task = task
        self.timer = timer

    def execute(self, agent):
        # Check Task Status
        if self.task.active_state.name == "TaskExecuting":
            if agent in self.task.active_state.workers:
                agent.change_state(WorkerWorking(self.task))
            else:
                agent.change_state(WorkerSearching())

        # Check if timer has expired
        elif self.timer == 0:
            agent.change_state(WorkerSearching(agent.break_time))
        else:
            self.timer -= 1


class WorkerResponding(State):
    def __init__(self, task, timer):
        self.target_pos = task.pos
        self.task = task
        self.timer = timer
    
    def execute(self, agent):
        # Check if agent reached target
        direction = np.array(self.target_pos) - np.array(agent.pos)
        distance_to_target = np.linalg.norm(direction)
        
        if distance_to_target <= agent.action_range:
            agent.change_state(WorkerWaiting(self.task, self.timer))

        # Check timer expiry
        elif self.timer == 0:
            agent.change_state(WorkerSearching(agent.break_time))

        # Move towards target and decrement timer
        else:
            direction /= distance_to_target  # Normalize
            new_pos = agent.pos + direction * min(agent.speed, distance_to_target)
            agent.model.space.move_agent(agent, new_pos)
            self.timer -= 1


class WorkerWorking(State):
    def __init__(self, task):
        self.task = task

    def execute(self, agent):
        # Check Task Status
        if self.task.active_state.name == "TaskCompleted":
            agent.change_state(WorkerSearching())


# --- STATE CLASSES FOR TASK ---
class TaskIdle(State):
    """
    The state for a task existing and waiting for execution.
    Handles search logic to find and assign workers.
    """
    def execute(self, agent):
        # Check if enough workers are within action range to perform the task
        neighbors = agent.model.space.get_neighbors(
            agent.pos,
            radius=agent.action_range,
            include_center=False
        )
        workers = list(filter(lambda a: isinstance(a, WorkerAgent) and a.active_state.name == "WorkerWaiting" and a.active_state.task == agent, neighbors)) # type: ignore
        if len(workers) >= agent.workers_required:
            agent.change_state(TaskExecuting(workers[:agent.workers_required], agent.time_required))


class TaskExecuting(State):
    """
    The state for a task being executed by assigned workers. Tracks progress and completion.
    """
    def __init__(self, workers, time_required):
        self.workers = workers
        self.timer = time_required

    def execute(self, agent):
        # Reduce time required with each step until 0 then change state to Completed
        # If completed, change to completed state and create a new task
        if self.timer == 0:
            agent.create_agents(agent.model, 1, agent.action_range, agent.workers_required, agent.time_required)
            agent.change_state(TaskCompleted())

        else:
            self.timer -= 1


class TaskCompleted(State):
    def execute(self, agent):
        # Task is completed
        pass

