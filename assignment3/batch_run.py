import mesa
import pandas as pd
import os
from model import STAModel

# Parameters to be tested in the Batch Run 

params = {
    "seed": None,
    "num_workers": [1, 3, 5, 10, 20, 30],
    "num_tasks": [1],
    "protocol": "random",
    "worker_speed": [25],
    "worker_comm_range": [50],
    "worker_timeout": [1],
    "task_action_range": [50],
    "task_workers": [1],
    "task_time": [3],
}


# Batch Simulation
if __name__ == "__main__":
    results = mesa.batch_run(
        STAModel,
        parameters=params,
        iterations=100,       # Run each parameter combo 100 times
        max_steps=2000,      # Run each simulation for 2000 steps
        number_processes=None, # Use all available CPU cores
        data_collection_period=1,
        display_progress=True
    )


    # Save results to file
    folder = "logs"
    results_file = "several_worker_one_task_long.csv"
    absolute_path = os.path.dirname(__file__)
    folder = os.path.join(absolute_path, folder)
    os.makedirs(folder, exist_ok=True)
    pd.DataFrame(results).to_csv(os.path.join(folder, results_file), index=False)
    print(f"Batch run results saved to {results_file}")
