# src/wqu/dp/vasicek.py

import numpy as np
import matplotlib.pyplot as plt

class Vasicek:
    def __init__(self, r0: float, k: float, theta: float, sigma: float, T: float = 1.0, N: int = 252, seed: int = None):
        """
        Initialize the Vasicek model parameters.

        Parameters:
        - r0: initial interest rate
        - k: speed of mean reversion
        - theta: long-term mean rate
        - sigma: volatility
        - T: total simulation time in years
        - N: number of time steps
        - seed: random seed (optional)
        """
        self.r0 = r0
        self.k = k
        self.theta = theta
        self.sigma = sigma
        self.T = T
        self.N = N
        self.dt = T / N
        self.t = np.linspace(0, T, N + 1)
        if seed is not None:
            np.random.seed(seed)

    def _simulate(self) -> np.ndarray:
        """
        Simulate a single Vasicek path.
        Returns an array of shape (N+1,)
        """
        r = np.zeros(self.N + 1)
        r[0] = self.r0
        for i in range(1, self.N + 1):
            dr = self.k * (self.theta - r[i - 1]) * self.dt + self.sigma * np.sqrt(self.dt) * np.random.randn()
            r[i] = r[i - 1] + dr
        return r

    def simulate(self, M: int = 1) -> np.ndarray:
        """
        Simulate M Vasicek paths.
        Returns a NumPy array of shape (M, N+1)
        """
        return np.array([self._simulate() for _ in range(M)])

    def plot(self, M: int = 1, alpha: float = 0.5, **kwargs):
        """
        Plot M simulated Vasicek paths.

        Parameters:
        - M: number of paths
        - alpha: line transparency
        - kwargs: passed to matplotlib.plot
        """
        paths = self.simulate(M)
        plt.figure(figsize=kwargs.pop("figsize", (10, 5)))
        for i in range(M):
            plt.plot(self.t, paths[i], alpha=alpha, **kwargs)
        plt.title(f"Vasicek Model Simulation (M={M})")
        plt.xlabel("Time (Years)")
        plt.ylabel("Interest Rate")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def compare_parameters(self, param: str, values: list, M: int = 1):
        """
        Plot paths with varying one parameter to see its effect.

        Parameters:
        - param: one of 'k', 'theta', 'sigma'
        - values: list of values to try
        - M: number of paths per parameter value
        """
        original = getattr(self, param)
        plt.figure(figsize=(10, 6))

        for val in values:
            setattr(self, param, val)
            paths = self.simulate(M)
            mean_path = paths.mean(axis=0)
            plt.plot(self.t, mean_path, label=f"{param} = {val}")

        setattr(self, param, original)  # reset original value
        plt.title(f"Effect of Changing {param} on Vasicek Mean Path")
        plt.xlabel("Time (Years)")
        plt.ylabel("Interest Rate")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def to_dict(self):
        return {
            "r0": self.r0,
            "k": self.k,
            "theta": self.theta,
            "sigma": self.sigma,
            "T": self.T,
            "N": self.N
        }