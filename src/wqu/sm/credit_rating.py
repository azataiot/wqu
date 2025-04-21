# src/wqu/sm/credit_rating.py

from typing import List, Union, Optional, Dict
import numpy as np
import matplotlib.pyplot as plt
from graphviz import Digraph
from IPython.display import HTML
import matplotlib.animation as animation

class CreditRatingMarkovChain:
    """
    Simulates credit rating transitions using a Markov Chain.

    Example usage:
    >>> states = ["AAA", "AA", "A", "BBB", "BB", "B", "CCC/C", "D"]
    >>> P = normalized_matrix  # Preprocessed and normalized transition matrix (8x8)
    >>> crm = CreditRatingMarkovChain(states, P, initial_state="BBB")
    >>> crm.simulate_path()
    >>> crm.plot_path()
    >>> crm.simulate_multiple_paths(steps=20, num_simulations=10000)
    >>> crm.get_matrix_power(200)  # Check long-term convergence
    >>> crm.simulate_histories(num_paths=1000, num_steps=100)
    >>> crm.average_time_to_default()
    """

    def __init__(
            self,
            states: list[str],
            transition_matrix: np.ndarray,
            initial_state: str | int | None = None,
    ):
        self.states = states
        self.P = np.array(transition_matrix, dtype=float)
        self.n = len(states)
        assert self.P.shape == (self.n, self.n), "Transition matrix must be square"
        assert np.allclose(self.P.sum(axis=1), 1), "Rows must sum to 1"

        # For example, if we start from 'AAA', the initial_index will be 0, if we start from 'D', then it will be '7'
        self.initial_index: int = (
            self._get_index(initial_state) if initial_state is not None else 0
        )
        self.path: List[int] = []
        self.histories: np.ndarray = np.empty((0, 0))

    def _get_index(self, state: str | int) -> int:
        """
        For example: AAA->0, AA->1, A->2, BBB->3, 'CCC/C'-> 6
        Or can be 6 which represents the 'CCC/C'
        """
        return self.states.index(state) if isinstance(state, str) else state

    def simulate_path(self, steps=20):
        """
        Simulates a single path for the given steps.

        Example:
        Suppose self.n is 3, then the transition matrix self.P is something like:
        [[0.2, 0.5, 0.3],
         [0.1, 0.6, 0.3],
         [0.4, 0.4, 0.2]]
        If current is 0 (state A), then self.P[0] is [0.2, 0.5, 0.3].
        np.random.choice(3, p=[0.2, 0.5, 0.3]) will randomly select 0, 1, or 2 based on these probabilities.
        Suppose the result is 1 (state B). Then current is updated to 1.
        """
        current = self.initial_index
        self.path = [current]  # [0]
        for _ in range(steps):
            current = np.random.choice(self.n, p=self.P[current])
            self.path.append(current)
            if self.P[current, current] == 1:
                break
        return [self.states[i] for i in self.path]

    def simulate_multiple_paths(self, steps=20, num_simulations=1000):
        """
        Generate multiple-path simulations.

        Parameters:
        -----------
        steps: int
            The number of time steps for each simulation.
        num_simulations: int
            The number of simulations to run

        Returns:
        --------
            dict: A dictionary containing the total number of simulations, the number of defaulted simulations,
                and the default rate.
        """
        # In many Markov models (espacially in credit risk or default modeling), the last state in the transision matrix is often observed for an absorbing
        # state -- in this case, "default.". Once the process enters this state, it cannot leave.
        # Example: If we have 4 states, ['A', 'B', 'C', 'D'], meaning that (self.n = 4), the states are indexed as 0, 1, 2, 3. The index of
        # last state (self.n -1 = 3) is the 'default'.
        default_index = self.n - 1
        default_counts = 0
        for _ in range(num_simulations):
            current = self.initial_index
            for _ in range(steps):
                current = np.random.choice(self.n, p=self.P[current])
                if current == default_index:
                    default_counts += 1
                    break
        return {
            "simulations": num_simulations,
            "defaulted": default_counts,
            "default_rate": default_counts / num_simulations,
        }

    def plot_path(
            self,
            figsize=(10, 4),
            color="navy",
            marker="o",
            linestyle="-",
            title=None,
            xlabel="Step",
            ylabel="Credit Rating",
            grid=True,
            **kwargs,
    ):
        """
        Plots the simulated credit rating path.

        Parameters:
        -----------
        figsize : tuple, optional
            Size of the figure (default is (10, 4)).
        color : str, optional
            Line color (default is 'navy').
        marker : str, optional
            Marker style (default is 'o').
        linestyle : str, optional
            Line style (default is '-').
        title : str, optional
            Plot title (default is "Credit Rating Transition Path").
        xlabel : str, optional
            X-axis label (default is "Step").
        ylabel : str, optional
            Y-axis label (default is "Credit Rating").
        grid : bool, optional
            Whether to show grid (default is True).
        **kwargs : dict
            Additional keyword arguments passed to plt.plot().
        """
        if not self.path:
            raise ValueError("Run simulate_path() first")
        plt.figure(figsize=figsize)
        plt.plot(
            range(len(self.path)),
            self.path,
            marker=marker,
            linestyle=linestyle,
            color=color,
            **kwargs,
        )
        plt.yticks(range(self.n), self.states)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title or "Credit Rating Transition Path")
        if grid:
            plt.grid(True)
        plt.tight_layout()
        plt.show()

    def graphviz_chain(self) -> Digraph:
        dot = Digraph()
        dot.attr(rankdir="LR")
        # self.states is a list of state names (e.g., ["AAA", "AA", "A", "BBB", "BB", "B", "CCC/C", "D"]).
        # enumerate(self.states) returns pairs of (index, value) for each element in the list.
        for i, state in enumerate(self.states):
            color = "#fdd" if self.P[i, i] == 1 else "white"
            dot.node(str(i), state, style="filled", fillcolor=color)
        for i in range(self.n):
            for j in range(self.n):
                if self.P[i, j] > 0:
                    label = f"{self.P[i, j]:.2f}"
                    dot.edge(str(i), str(j), label=label)
        return dot

    def animate_path(self, save_as: Optional[str] = None) -> Union[str, HTML]:
        """
        Animate the credit rating transition path(a single path).

        This method creates an animated visualization of the credit rating path
        using matplotlib's animation functionality. The animation shows the
        progression of credit ratings over time.

        Parameters
        ----------
        save_as : str, optional
            If provided, saves the animation to a file. Supported formats:
            - '.gif' (saved using a pillow writer)
            - '.mp4' (saved using ffmpeg writer, requires ffmpeg executable installed.)
            If not provided, returns an HTML animation.

        Returns
        -------
        Union[str, HTML]
            - If save_as is provided: Returns a confirmation message
            - If save_as is not provided: Returns an HTML animation object

        Raises
        ------
        ValueError
            If simulate_path() hasn't been run before calling this method.

        Notes
        -----
        The animation shows:
        - X-axis: Time steps
        - Y-axis: Credit ratings
        - Blue line with markers showing the rating path
        - Grid for better readability
        - Automatic scaling of axes
        """
        if not self.path:
            """In case there is no simulated path yet."""
            raise ValueError("Run simulate_path() first")
        # fig: the Figure object, which is the overall window or page that everything is drawn on.
        # ax: the Axes object, which is the area on which data is plotted (the actual plot)
        fig, ax = plt.subplots(figsize=(10, 4))
        xdata, ydata = [], []
        (ln,) = plt.plot([], [], marker="o", linestyle="-", color="navy")

        def init():
            ax.set_xlim(0, len(self.path))
            ax.set_ylim(-0.5, self.n - 0.5)
            ax.set_yticks(range(self.n))
            ax.set_yticklabels(self.states)
            ax.set_title("Credit Rating Path Animation")
            ax.set_xlabel("Step")
            ax.set_ylabel("Rating")
            ax.grid(True)
            return (ln,)

        def update(frame):
            xdata.append(frame)
            ydata.append(self.path[frame])
            ln.set_data(xdata, ydata)
            return (ln,)

        # animation.FuncAnimation: creates animations by repeatedly calling a function (in this case, `update`)
        # to update the plot.
        # `frames=range(len(self.path))`: This tells the animation how many frames to create. It will call `update`
        # once for each value in this range (so as many times as there are elements in `self.path`).
        # `blit=True`: This makes the animation more effficently by only re-drawing the parts that have changed.
        ani = animation.FuncAnimation(
            fig,
            update,
            frames=range(len(self.path)),
            init_func=init,
            blit=True,
            repeat=False,
        )
        if save_as:
            if save_as.endswith(".gif"):
                ani.save(save_as, writer="pillow", fps=5)
            elif save_as.endswith(".mp4"):
                ani.save(save_as, writer="ffmpeg", fps=5)
            return f"Saved to {save_as}"
        plt.close(fig)
        return HTML(ani.to_jshtml())


    def get_matrix_power(self, power: int = 200) -> np.ndarray:
        """
        Returns the matrix raised to a given power (useful for long-run behavior).
        """
        return np.linalg.matrix_power(self.P, power)


    def simulate_histories(self, num_paths: int = 1000, num_steps: int = 100) -> np.ndarray:
        """
        Simulates multiple credit rating paths over time.

        Differences from simulate_multiple_paths:
        - `simulate_multiple_paths` only tracks whether each simulation hits the absorbing state (default), and calculates the default rate.
        - `simulate_histories` records the full sequence of states for each simulation, so one can see the entire path for each one.
        Parameters:
        -----------
        num_paths : int, optional
            Number of rating paths to simulate (default: 1000)
        num_steps : int, optional
            Maximum number of steps (time periods) to simulate for each path (default: 100)

        Returns:
        --------
        np.ndarray
            Array of shape (num_paths, num_steps) containing the simulated rating paths.
            Each row represents one path, and each column represents a time step.
            The ratings are stored as integer indices corresponding to the states.

        Notes:
        ------
        - The simulation stops early for a path if it reaches an absorbing state (like default)
        - The initial state for all paths is set to self.initial_index
        - The results are stored in self.histories for later use
        """
        # Initialize the array to store the full rating history for each path, where each row corresponds to a single path and
        # each column corresponds to a time step. The data type is integer, because the states are represented by their indices.
        self.histories = np.zeros((num_paths, num_steps), dtype=int)
        # Set the initial state for all paths
        self.histories[:, 0] = self.initial_index
        # Simulate each path one by one
        for i in range(num_paths):
            # Start from the second time step, as the first one is already set to the initial state
            for j in range(1, num_steps):
                # The current state is determined by the previous state
                current = self.histories[i, j - 1]
                # Choose the next state based on the transition probabilities
                # For example np.random.choice(3, p=[0.1, 0.6, 0.3]),
                # this will randomly return 0 (with 10% chance), 1 (with 60% chance), or 2 (with 30% chance).
                # if the first argument of the np.random.choice is an integer n, it always chooses from
                # 0 up to n-1 (the upper boundary is not included).
                self.histories[i, j] = np.random.choice(self.n, p=self.P[current])
                # If the next state is an absorbing state (like default), stop the simulation for this path
                if self.P[self.histories[i, j], self.histories[i, j]] == 1.0:
                    # The simulation stops early for this path because it reached an absorbing state
                    # TODO: we might want to fill the rest of the path with the last state, to make it more informative
                    # rather than just giving it the default 0s created with np.zeros((num_paths, num_steps), dtype=int),
                    # as 0 actually means something in this context (it's a state).
                    break
        return self.histories

    def average_time_to_default(self) -> float:
        """
        Calculate the average time (in steps) it takes for a credit rating to reach default.

        This method analyzes the simulated rating paths to determine how long it takes
        on average for a credit rating to transition to the default state (D).

        Returns:
        --------
        float
            The average number of steps taken to reach default. Returns 0.0 if no paths
            reached default in the simulations.

        Raises:
        -------
        ValueError
            If simulate_histories() has not been run first

        Notes:
        ------
        - Only considers paths that actually reached default
        - The time is measured in discrete steps (e.g., years)
        - The default state is assumed to be the last state in the transition matrix (in our case, it's 'D')
        """
        if self.histories.size == 0:
            raise ValueError("Run simulate_histories() first")

        default_index = self.n - 1
        default_times = []

        for path in self.histories:
            if default_index in path:
                # If path=[0,1,2,3,0,0] and default_index=3, then path== default_index is [False, False, False, True, False, False]
                # np.where(condition) returns the indices of the elements in the array that satisfy the condition
                # So np.where(path == default_index) returns [3]
                # [0] is used to get the first (and only) element of the array (the index of the first default) -> 3
                # So first_default = 3 step is the first time the rating defaults
                first_default = np.where(path == default_index)[0][0]
                default_times.append(first_default)

        return float(np.mean(default_times)) if default_times else 0.0

    def summary(self) -> Dict[str, Union[List[str], List[int], int, str, bool, Dict[str, int], int, List[float]]]:
        """
        Returns a summary of the most recent simulated path.

        Returns
        -------
        dict with keys:
            - path_labels: List of state names for the path
            - path_indices: List of state indices for the path
            - initial_state: Name of the initial state
            - steps: Number of steps taken (excluding initial state)
            - final_state: Name of the final state
            - absorbing: Whether the final state is absorbing
            - state_counts: Dictionary of how many times each state was visited
            - absorbing_step: The time step at which an absorbing state was reached (if any, else None)
            - final_state_probs: Transition probabilities from the final state
        """
        if not self.path:
            raise ValueError("Run simulate_path() first")
        path_labels = [self.states[i] for i in self.path]
        path_indices = self.path
        state_counts = {state: path_labels.count(state) for state in self.states}
        final_state = self.states[self.path[-1]]
        absorbing = self.P[self.path[-1], self.path[-1]] == 1
        absorbing_step = None
        for idx, i in enumerate(self.path):
            if self.P[i, i] == 1:
                absorbing_step = idx
                break
        return {
            "path_labels": path_labels,
            "path_indices": path_indices,
            "initial_state": path_labels[0],
            "steps": len(self.path) - 1,
            "final_state": final_state,
            "absorbing": absorbing,
            "state_counts": state_counts,
            "absorbing_step": absorbing_step,
            "final_state_probs": list(self.P[self.path[-1]])
        }
