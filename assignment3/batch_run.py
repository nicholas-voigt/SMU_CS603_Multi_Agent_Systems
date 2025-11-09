import mesa
import pandas as pd
import os
from model import STAModel

# Parameters to be tested in the Batch Run 

params = {
    "seed": None,
    "num_workers": [30],
    "num_tasks": [2],
    "use_call_off": [False, True],
    "worker_speed": [25],
    "worker_comm_range": [0, 100, 200, 300, 400, 600, 1000, 1400],
    "worker_timeout": [60],
    "worker_break_time": [0],
    "task_action_range": [50],
    "task_workers": [3],
    "task_time": [1],
}


# Batch Simulation
if __name__ == "__main__":
    results = mesa.batch_run(
        STAModel,
        parameters=params,
        iterations=100,       # Run each parameter combo 100 times
        max_steps=1000,      # Run each simulation for 1000 steps
        number_processes=None, # Use all available CPU cores
        data_collection_period=1,
        display_progress=True
    )
    print("Batch run completed.")

    # Save results to file
    folder = "logs"
    results_file = "call_off_protocol.csv"
    absolute_path = os.path.dirname(__file__)
    folder = os.path.join(absolute_path, folder)
    os.makedirs(folder, exist_ok=True)
    pd.DataFrame(results).to_csv(os.path.join(folder, results_file), index=False)
    print(f"Batch run results saved to {results_file}")
