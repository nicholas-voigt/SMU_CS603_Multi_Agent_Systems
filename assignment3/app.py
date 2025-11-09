import mesa
from mesa.visualization import Slider, SolaraViz, SpaceRenderer
from mesa.visualization.components import AgentPortrayalStyle
from model import STAModel
from agents import WorkerAgent, TaskAgent


def agent_portrayal(agent):
    """
    Defines how to draw each agent on the visualization grid.
    """
    if agent is None:
        return

    color_codes = {
        "WorkerSearching": "green",
        "WorkerWaiting": "grey",
        "WorkerResponding": "yellow",
        "WorkerWorking": "blue",
        "TaskIdle": "orange",
        "TaskInProgress": "red",
        "TaskCompleted": "purple",
    }
    # --- WorkerAgent Portrayal ---
    if isinstance(agent, WorkerAgent):
        return AgentPortrayalStyle(
            color=color_codes.get(agent.active_state.name, "black"),
            marker="o",
            size=15
        )

    # --- TaskAgent Portrayal ---
    elif isinstance(agent, TaskAgent):
        return AgentPortrayalStyle(
            color=color_codes.get(agent.active_state.name, "black"),
            marker="x",
            size=10
        )

# Create initial model instance
sta_model = STAModel(
    seed=None,
    num_workers=1,
    num_tasks=1,
    use_call_off=True,
    worker_speed=25,
    worker_comm_range=50,
    worker_timeout=1,
    worker_break_time=0,
    task_action_range=50,
    task_workers=1,
    task_time=2
)

# Model Parameters for interactive testing
model_params = {
    "seed": None,
    "num_workers": Slider("Number of Workers", min=1, max=50, step=1, value=1, dtype=int),
    "num_tasks": Slider("Number of Tasks", min=1, max=50, step=1, value=1, dtype=int),
    "use_call_off": True,
    "worker_speed": Slider("Worker Speed", min=5, max=50, step=5, value=25, dtype=int),
    "worker_comm_range": Slider("Worker Communication Range", min=100, max=1000, step=100, value=100, dtype=int),
    "worker_timeout": 60,
    "worker_break_time": Slider("Worker Break Time", min=0, max=60, step=5, value=0, dtype=int),
    "task_action_range": 50,
    "task_workers": Slider("Task Workers", min=1, max=10, step=1, value=1, dtype=int),
    "task_time": 3,
}

# Visualization Grid
renderer = SpaceRenderer(model=sta_model, backend="matplotlib").render(
    agent_portrayal=agent_portrayal
)

page = SolaraViz(
    sta_model,
    renderer,
    model_params=model_params,
    name="STA Simulation",
)
