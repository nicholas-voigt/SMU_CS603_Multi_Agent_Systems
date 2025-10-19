import numpy as np
import matplotlib.pyplot as plt
import argparse


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Beachgoers Optimization")
    parser.add_argument('--agents', type=int, default=100, help="Number of agents in the simulation (default: 100)")
    parser.add_argument('--beach_capacity', type=int, default=20, help="Optimal capacity of the beach (default: 20)")
    args = parser.parse_args()

    # Calculate utility with the given parameters
    n = args.agents
    c = args.beach_capacity
    x = np.arange(0, n + 1) # Actual number of agents on the beach
    utility = x * np.minimum(1.0, c / x) + (n - x) * 0.5

    # Find the optimal number of agents on the beach
    optimal_x = np.argmax(utility)
    optimal_utility = utility[optimal_x]

    # Create Plot for the utility function
    plt.figure(figsize=(10, 6))
    plt.plot(x, utility, label='Utility Function', color='blue')
    plt.axvline(float(optimal_x), color='red', linestyle='--', label='Optimal Agents on Beach: {}'.format(optimal_x))
    plt.axhline(optimal_utility, color='green', linestyle='--', label='Optimal Utility: {:.2f}'.format(optimal_utility))
    plt.xlabel('Number of Agents on Beach')
    plt.ylabel('Utility')
    plt.title('Utility Function for Beachgoers at (N={}, C={})'.format(n, c))
    plt.legend()
    plt.grid()

    # Show the plot
    print("Displaying plot in a window...")
    plt.show()
