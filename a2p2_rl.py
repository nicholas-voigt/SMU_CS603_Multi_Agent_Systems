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
        if init_type == 'zeros':
            self.q_table = np.zeros((n, states, actions), dtype=float)
        elif init_type == 'random':
            self.q_table = np.random.rand(n, states, actions)
        elif init_type == 'optimistic':
            self.q_table = np.ones((n, states, actions), dtype=float) * 5  # optimistic initial values
        else:
            raise ValueError("Invalid initialization type. Choose from 'zeros', 'random', or 'optimistic'.")

    def update(self, experience: np.ndarray, episode: int):
        """
        Update the Q-table with a new experience.
        Args:
            experience: np.ndarray - array of shape (n, states, actions) containing the experience for each agent
            episode: int - the current episode number
        """
        self.q_table = self.q_table + (1 / (episode + 1)) * (experience - self.q_table)

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
        States: 0 (0 - c beachgoers), 1 (c+1 - equilibrium beachgoers), 2 (> equilibrium beachgoers)
        Actions: 0 (stay home), 1 (go to beach)
        Args:
            n: int - number of agents
            c: int - optimal capacity of the beach
            epsilon: float - initial exploration rate for epsilon-greedy strategy
            epsilon_decay: float - decay rate for exploration
        """
        self.n = n  # Number of agents
        self.c = c  # Beach capacity
        self.epsilon = epsilon  # Exploration rate for epsilon-greedy
        self.epsilon_decay = epsilon_decay  # Decay rate for exploration

        self.equilibrium = int(c * 2)  # Equilibrium point (utility is equal for going to beach or staying home)
        self.previous_state = int(0)  # Previous state (depending on the number of beachgoers, 0 in first episode)
        self.memory = Memory(n=n, states=3, actions=2, init_type=state_init)
        self.logger = {'beachgoers': [], 'social_welfare': [], 'epsilon': []}

    def get_state(self, num_beachgoers: int) -> int:
        # Determine state based on number of beachgoers
        if num_beachgoers <= self.c:
            return 0
        elif num_beachgoers <= self.equilibrium:
            return 1
        else:
            return 2

    def run_simulation(self, episodes: int):
        # Simulation Loop
        for episode in range(episodes):
            self.logger['epsilon'].append(self.epsilon * 100)
            self.run_episode(episode)
            # Decay exploration rate
            self.epsilon *= self.epsilon_decay

    def run_episode(self, episode: int):
        # Evaluate if exploration or exploitation for each agent individually
        exploration_mask = (np.random.rand(self.n) < self.epsilon)

        # Choose random actions based on exploration mask
        actions = np.zeros(self.n, dtype=int)
        actions[exploration_mask] = np.random.randint(0, 2, size=exploration_mask.sum(), dtype=int)

        # For agents not exploring, use the Q-table to choose actions
        actions[~exploration_mask] = np.argmax(self.memory.q_table[~exploration_mask, self.previous_state, :], axis=1)

        # Calculate current state based on number of beachgoers
        num_beachgoers = actions.sum()
        beach_utility = np.minimum(1.0, self.c / (num_beachgoers + 1e-8))
        self.previous_state = self.get_state(num_beachgoers)

        # Update Q-table in memory
        experience = np.zeros((self.n, 3, 2), dtype=float)
        experience[:, self.previous_state, 0] = 0.5 
        experience[:, self.previous_state, 1] = beach_utility
        self.memory.update(experience, episode)

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
    print(f"Total simulation time: {end_time - start_time:.2f} seconds")

    # Print average Q-Table values
    print("Average Q-Table Values:")
    print(simulator.memory.q_table.mean(axis=0))

    # Plotting the results
    plt.figure(figsize=(12, 6))
    plt.plot(simulator.logger['beachgoers'], label='Number of Beachgoers', color='blue')
    plt.plot(simulator.logger['social_welfare'], label='Social Welfare', color='green')
    plt.plot(simulator.logger['epsilon'], label='Epsilon [%]', color='red')
    plt.ylim(0, args.n)
    plt.xlabel('Episode')
    plt.title('Beachgoers Over Episodes (N={}, C={})'.format(args.n, args.c))
    plt.legend()
    plt.grid()
    print("Plotting simulation results...")
    plt.show()