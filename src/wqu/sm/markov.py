# src/wqu/sm/markov.py
import numpy as np
import matplotlib.pyplot as plt

class StateMarkovChain:
    def __init__(self, states, transition_matrix, initial_state=None):
        """
        Initialize an N-state Markov chain.
        :param states: states: list or array of state values (e.g. [-1, 0, 1])
        :param transition_matrix: NxN matrix of transition probabilities
        :param initial_state: a valid state (optional); if None, chosen randomly
        """
        self.states = np.array(states)
        self.P = np.array(transition_matrix)
        self.N = len(states)

        # validations
        assert self.P.shape == (self.N, self.N), "Transition matrix shape must match number of states"
        assert np.allclose(self.P.sum(axis=1), 1), "Each row of transition matrix must sum to 1"

        # Allows converting from state values (e.g., -1,1) to matrix indices.
        self.index_map = {state: i for i, state in enumerate(self.states)}
        self.current_state = initial_state if initial_state else np.random.choice(self.states)
        self.states_indices = {state: i for i, state in enumerate(self.states)}

    def reset(self, to_state=None):
        """
        Reset the current state. If no state is given, choose randomly.
        :param to_state: state to reset to (optional)
        """
        if to_state is None:
            self.current_state = np.random.choice(self.states)
        else:
            assert to_state in self.states, "Given state is not valid, Reset state must be one of the defined states"
            self.current_state = to_state

    def step(self, rand_value=None):
        """
        Simulates $s_t$ to $s_{t+1}$
        """
        i = self.index_map[self.current_state]
        if rand_value is None:
            rand_value = np.random.rand()
        # Manual branching like original code (mimicking textbook logic)
        if rand_value < self.P[i, i]:
            return self.current_state  # stay
        else:
            for j in range(self.N):
                if j != i:
                    self.current_state = self.states[j]
                    break
            return self.current_state

    def simulate(self, steps):
        """
        Simulate a trajectory of states over given number of steps.
        $\text{Trajectory} = [s_0, s_1, \dots, s_T]$
        """
        trajectory = [self.current_state]
        for _ in range(steps):
            self.step()
            trajectory.append(self.current_state)
        return trajectory

    def conditional_expectation(self):
        """
        Return expected next state values (P @ state values)
        """
        return self.P @ self.states.reshape(-1, 1)

    def get_transition_prob(self, from_state, to_state):
        """
        Return the probability of transitioning from one state to another.
        """
        i = self.states_indices[from_state]
        j = self.states_indices[to_state]
        return self.P[i, j]
    def plot_trajectory(self, steps=50):
        """
        Simulate and plot a trajectory of the process.
        """
        path = self.simulate(steps)
        plt.figure(figsize=(10, 4))
        plt.plot(range(steps + 1), path, marker='o')
        plt.title("State Markov Chain Trajectory")
        plt.xlabel("Time Step")
        plt.ylabel("State")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def simulate_X_t(self, steps=50, x0=75, seed=12345):
        np.random.seed(seed)
        randarray = np.random.rand(steps)
        X = [x0]
        states_used = [self.current_state]
        transition_counts = np.zeros((self.N, self.N))

        for t in range(1, steps):
            prev_state = self.current_state
            prev_index = self.index_map[prev_state]
            next_state = self.step(rand_value=randarray[t])
            next_index = self.index_map[next_state]

            X.append(X[-1] + next_state)
            states_used.append(next_state)
            transition_counts[prev_index, next_index] += 1

        return X, states_used, transition_counts

    def simulate_X_t_process(self, steps, x0=0):
        """
        Simulate a process $X_t = X_{t-1} + s_t$,
        where s_t is drawn from the Markov Chain.

        Returns both (X_t values, state path)
        """
        Xt = [x0]
        path = [self.current_state]

        for _ in range(steps):
            next_state = self.step()
            Xt.append(Xt[-1] + next_state)
            path.append(next_state)

        return Xt, path

    def __str__(self):
        return f"States: {self.states}\nTransition Matrix:\n{self.P}"
