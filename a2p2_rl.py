import argparse
import matplotlib.pyplot as plt
import numpy as np
from time import time

class Memory:
    def __init__(self, n: int, states: int, actions: int, init_type: str):
        """
        Initialize the memory buffer for Q-table storage.
        Args:
            n: int - number of agents
            states: int - number of states
            actions: int - number of actions
            init_type: str - type of initialization ('zeros', 'random', 'optimistic')
        """
        self.update_counts = np.zeros((n, states, actions), dtype=int)
        if init_type == 'zeros':
            self.q_table = np.zeros((n, states, actions), dtype=float)
        elif init_type == 'random':
            self.q_table = np.random.rand(n, states, actions)
        elif init_type == 'optimistic':
            self.q_table = np.ones((n, states, actions), dtype=float) * 5
        else:
            raise ValueError("Invalid initialization type. Choose from 'zeros', 'random', or 'optimistic'.")

    def update(self, state: int, actions: np.ndarray, rewards: np.ndarray):
        """
        Update the Q-table for the specific state-action pairs experienced.
        Args:
            state: int - The state that was observed by all agents.
            actions: np.ndarray - The action taken by each agent. Shape (n,).
            rewards: np.ndarray - The reward received by each agent for their action. Shape (n,).
        """
        agent_indices = np.arange(self.q_table.shape[0])
        # Track the number of updates for each agent-action-state triplet
        self.update_counts[agent_indices, state, actions] += 1
        # Update Q-values using incremental mean formula
        current_q_values = self.q_table[agent_indices, state, actions]
        self.q_table[agent_indices, state, actions] = current_q_values + (1 / self.update_counts[agent_indices, state, actions]) * (rewards - current_q_values)

    def retrieve(self) -> np.ndarray:
        """
        Retrieve Q-table from memory.
        Returns:
            q_table: np.ndarray - array of shape (n, states, actions) containing current Q-values
        """
        return self.q_table


class Simulator:
    def __init__(self, n: int, c: int, epsilon: float, epsilon_decay: float, state_init: str):
        """
        Initialize the Simulator for beachgoers optimization. Implements epsilon-greedy reinforcement learning with 3 states and 2 actions.
        States: 0 (0 -> c beachgoers), 1 (c+1 -> equilibrium beachgoers), 2 (> equilibrium beachgoers)
        Actions: 0 (stay home), 1 (go to beach)
        Args:
            n: int - number of agents
            c: int - optimal capacity of the beach
            epsilon: float - initial exploration rate for epsilon-greedy strategy
            epsilon_decay: float - decay rate for exploration
            state_init: str - type of state initialization for Q-table ('zeros', 'random', 'optimistic')
        """
        self.n = n
        self.c = c
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay

        self.equilibrium = int(c * 2)  # Equilibrium point (utility is equal for going to beach or staying home)
        self.state = int(0)  # State (depending on the number of beachgoers, 0 in first episode)
        self.memory = Memory(n=n, states=3, actions=2, init_type=state_init)
        self.logger = {'beachgoers': [], 'social_welfare': [], 'epsilon': []}

    def get_state(self, num_beachgoers: int) -> int:
        """
        Get the state based on the number of beachgoers.
        Args:
            num_beachgoers: int - number of agents that went to the beach
        Returns:
            state: int - resulting state (0, 1, or 2)
        """
        if num_beachgoers <= self.c:
            return 0
        elif num_beachgoers <= self.equilibrium:
            return 1
        else:
            return 2

    def run_simulation(self, episodes: int):
        """
        Run the simulation for a specified number of episodes.
        """
        for _ in range(episodes):
            self.logger['epsilon'].append(self.epsilon * 100)
            self.run_episode()
            # Decay exploration rate
            self.epsilon *= self.epsilon_decay

    def run_episode(self):
        """
        Run a single episode of the simulation.
        """
        # Evaluate if exploration or exploitation for each agent individually
        exploration_mask = np.random.rand(self.n) < self.epsilon
        actions = np.zeros(self.n, dtype=int)

        # Choose random actions based on exploration mask
        actions[exploration_mask] = np.random.randint(0, 2, size=exploration_mask.sum(), dtype=int)

        # For agents not exploring, use the Q-table entry of the previous state to choose actions
        actions[~exploration_mask] = np.argmax(self.memory.q_table[~exploration_mask, self.state, :], axis=1)

        # Observe outcome and calculate rewards
        num_beachgoers = actions.sum()
        beach_utility = np.minimum(1.0, self.c / (num_beachgoers + 1e-8))
        rewards = np.where(actions == 1, beach_utility, 0.5)

        # Update Q-table
        self.memory.update(self.state, actions, rewards)

        # Update state based on new number of beachgoers
        self.state = self.get_state(num_beachgoers)

        # Log metrics
        self.logger['beachgoers'].append(num_beachgoers)
        self.logger['social_welfare'].append(num_beachgoers * beach_utility + (self.n - num_beachgoers) * 0.5)


if __name__ == "__main__":

    # Set up argument parser
    parser = argparse.ArgumentParser(description="Beachgoers Optimization")
    parser.add_argument('--n', type=int, default=100, help="Number of agents in the simulation (default: 100)")
    parser.add_argument('--c', type=int, default=20, help="Optimal capacity of the beach (default: 20)")
    parser.add_argument('--epsilon', type=float, default=1.0, help="Initial exploration rate (default: 1.0)")
    parser.add_argument('--epsilon_decay', type=float, default=0.9, help="Exploration decay rate per episode (default: 0.9)")
    parser.add_argument('--state_init', type=str, default='optimistic', choices=['zeros', 'random', 'optimistic'], help="State initialization type (default: optimistic)")
    parser.add_argument('--e', type=int, default=50, help="Number of episodes to simulate (default: 50)")
    args = parser.parse_args()

    # Configure Simulation environment
    start_time = time()
    simulator = Simulator(n=args.n, c=args.c, epsilon=args.epsilon, epsilon_decay=args.epsilon_decay, state_init=args.state_init)
    simulator.run_simulation(episodes=args.e)
    end_time = time()

    # Print final results
    print(f"Simulation completed with {args.e} episodes.")
    print(f"Total simulation time: {end_time - start_time:.4f} seconds")

    # Print average Q-Table values
    print("Average Q-Table Values:")
    print(simulator.memory.q_table.mean(axis=0))

    # Calculate optimum for reference
    x = np.arange(1, args.n + 1)
    optimum = np.max(x * np.minimum(1.0, args.c / x) + (args.n - x) * 0.5)

    # Plotting the results
    plt.figure(figsize=(12, 6))
    plt.plot(simulator.logger['beachgoers'], label='Number of Beachgoers', color='blue')
    plt.plot(simulator.logger['social_welfare'], label='Social Welfare', color='green')
    plt.plot(simulator.logger['epsilon'], label='Epsilon [%]', color='red')
    plt.axhline(y=simulator.equilibrium, color='orange', linestyle='--', label=f'Equilibrium (={simulator.equilibrium})')
    plt.axhline(y=optimum, color='purple', linestyle='--', label=f'Social Optimum (={int(optimum)})')
    plt.ylim(0, args.n)
    plt.xlabel('Episode')
    plt.title('Beachgoers Over Episodes (N={}, C={}, Init-E={}, E-Decay={})'.format(args.n, args.c, args.epsilon, args.epsilon_decay))
    plt.legend()
    plt.grid()
    print("Plotting simulation results...")
    plt.show()
