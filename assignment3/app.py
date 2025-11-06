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
    seed=1234,
    num_agents=1,
    num_tasks=1,
    protocol='random',
    agent_speed=25,
    agent_call_range=50,
    agent_response_timeout=1,
    task_work_range=50,
    task_workers=1,
    task_time=2
)

# Model Parameters for interactive testing
model_params = {
    "seed": 1234,
    "num_agents": Slider("Number of Agents", min=1, max=50, step=1, value=1, dtype=int),
    "num_tasks": Slider("Number of Tasks", min=1, max=50, step=1, value=1, dtype=int),
    "protocol": "random",
    "agent_speed": Slider("Agent Speed", min=5, max=50, step=5, value=25, dtype=int),
    "agent_call_range": 50,
    "agent_response_timeout": 1,
    "task_work_range": 50,
    "task_workers": Slider("Task Workers", min=1, max=10, step=1, value=1, dtype=int),
    "task_time": 2,
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
