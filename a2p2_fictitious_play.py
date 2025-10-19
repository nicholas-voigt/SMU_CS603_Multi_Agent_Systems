import argparse
import matplotlib.pyplot as plt
import numpy as np


class Memory:
    def __init__(self, limit: int, action_size: int):
        self.limit = limit
        self.position = 0
        self.size = 0
        # Pre-allocate memory on the target device
        self.actions = np.zeros((limit, action_size), dtype=bool)

    def append(self, actions: np.ndarray):
        """
        Appends a batch of experiences to the buffer.
        Args:
            actions: np.ndarray - array of shape (action_size, ) containing actions taken
        """
        # Generate indices for insertion using modulo arithmetic
        indices = np.arange(self.position, self.position + 1) % self.limit
        # Vectorized assignment
        self.actions[indices] = actions
        # Update position and size
        self.position = (self.position + 1) % self.limit
        self.size = min(self.size + 1, self.limit)

    def retrieve(self) -> np.ndarray:
        """
        Retrieve all experiences from the buffer.
        Returns:
            actions: np.ndarray - array of shape (size, *action_shape) containing stored actions
        """
        return self.actions[:self.size]
    
    def __len__(self):
        return self.size


class Simulator:
    def __init__(self, n: int, c: int, k: int, choice: str):
        self.n = n  # Number of agents
        self.c = c  # Beach capacity
        self.stochastic = (choice == 'stochastic')

        self.memory = Memory(limit=k, action_size=n)
        self.logger = {'beachgoers': [], 'social_welfare': [], 'exp_utility': []}

    def run_episode(self):
        if self.memory.size == 0:
            # Randomly generate actions (agents deciding to go to the beach or not)
            actions = np.random.randint(0, 2, size=self.n).astype(bool)
            self.logger['exp_utility'].append(0.0)

        else:
            # Retrieve experiences from memory
            actions_replay = self.memory.retrieve()

            # For each agent, calculate the past average number of agents going to the beach (except himself)
            mask = ~np.eye(self.n, dtype=bool)
            actions_excl_self = actions_replay[:, np.newaxis, :] * mask
            # [T, N, N] where actions_excl_self[t, i, j] = 1 if agent j went at time t, and i != j

            # Calculate past average number of agents going to the beach (excluding self)
            past_crowd = actions_excl_self.sum(axis=2).mean(axis=0)  # Shape (n,)

            # Calculate expected utility for going to the beach based on the average past crowd (and myself)
            exp_utility = np.minimum(1.0, c / (past_crowd + 1))
            self.logger['exp_utility'].append(exp_utility.mean() * 100)

            # Choose actions based on expected utility
            if self.stochastic:
                actions = np.random.rand(self.n) < (exp_utility / (exp_utility + 0.5))  # Stochastic choice
            else:
                actions = exp_utility > 0.5  # Deterministic choice

        # Calculate utility for each agent
        x = actions.sum()  # Total number of agents going to the beach
        social_welfare = x * np.minimum(1.0, self.c / (x + 1e-8)) + (self.n - x) * 0.5

        # Append experience to memory & log results
        self.memory.append(actions)
        self.logger['beachgoers'].append(x)
        self.logger['social_welfare'].append(social_welfare)


if __name__ == "__main__":

    # Set up argument parser
    parser = argparse.ArgumentParser(description="Beachgoers Optimization")
    parser.add_argument('--choice', type=str, choices=['deterministic', 'stochastic'], default='stochastic', help="Strategy for agents choosing actions (default: stochastic)")
    parser.add_argument('--n', type=int, default=100, help="Number of agents in the simulation (default: 100)")
    parser.add_argument('--c', type=int, default=20, help="Optimal capacity of the beach (default: 20)")
    parser.add_argument('--k', type=int, default=10, help="Maximum number of experiences for replay (default: 10)")
    parser.add_argument('--e', type=int, default=50, help="Number of episodes to simulate (default: 50)")
    args = parser.parse_args()

    # Configure Simulation environment
    simulator = Simulator(n=args.n, c=args.c, k=args.k, choice=args.choice)

    # Simulation Loop
    for episode in range(args.e):
        simulator.run_episode()
        print(f"Episode {episode + 1} completed.")
        print(f"  Number of Beachgoers: {simulator.logger['beachgoers'][-1]}")
        print(f"  Social Welfare: {simulator.logger['social_welfare'][-1]:.2f}")
        print(f"  Expected Utility: {simulator.logger['exp_utility'][-1]:.2f}")

    # Print final results
    print(f"Simulation completed with {args.e} episodes.")

    # Plotting the results
    plt.figure(figsize=(12, 6))
    plt.plot(simulator.logger['beachgoers'], label='Number of Beachgoers', color='blue')
    plt.plot(simulator.logger['social_welfare'], label='Social Welfare', color='green')
    plt.plot(simulator.logger['exp_utility'], label='Expected Utility [%]', color='red')
    plt.ylim(0, n)
    plt.xlabel('Episode')
    plt.title('Beachgoers Over Episodes (N={}, C={}, K={})'.format(n, c, k))
    plt.legend()
    plt.grid()
    print("Displaying plot in a window...")
    plt.show()