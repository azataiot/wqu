# src/wqu/dp/gbm.py

import numpy as np
import matplotlib.pyplot as plt

# ------------------------------------------
# Geometric Brownian Motion (GBM)
# A class representing the GBM process for simulating stock prices.
# ------------------------------------------

class GBM:
    def __init__(self, S0: float, mu: float, sigma: float, T: float = 1.0, N: int = 252, seed: int = None):
        """
        Initialize the GBM simulation parameters.

        Parameters:
        - S0: Initial stock price
        - mu: Expected return (drift)
        - sigma: Volatility
        - T: Total time in years (e.g., 1.0 for one year)
        - N: Number of time steps (e.g., 252 for daily over a year)
        - seed: Random seed for reproducibility (optional)
        """
        self.S0 = S0
        self.mu = mu
        self.sigma = sigma
        self.T = T
        self.N = N
        self.dt = T / N
        self.t = np.linspace(0, T, N + 1)
        if seed is not None:
            np.random.seed(seed)

    def simulate(self, method: str = "exact") -> np.ndarray:
        """
        Simulate a single GBM path using the specified method.

        Parameters:
        - method: 'exact' (default) or 'euler'

        Returns:
        - A NumPy array of length N+1 representing the price path: [S_0, S_1, ..., S_N]
        """
        if method == "exact":
            return self._simulate_exact()
        elif method == "euler":
            return self._simulate_euler()
        else:
            raise ValueError("Method must be 'exact' or 'euler'.")

    def _simulate_exact(self) -> np.ndarray:
        """
        Internal: Simulate GBM using the exact analytical solution.

        Returns:
        - A NumPy array of prices of length N+1 including S0
        """
        dW = np.random.randn(self.N) * np.sqrt(self.dt)
        W = np.concatenate(([0], np.cumsum(dW)))  # W_0 = 0
        S = self.S0 * np.exp((self.mu - 0.5 * self.sigma**2) * self.t + self.sigma * W)
        return S

    def _simulate_euler(self) -> np.ndarray:
        """
        Internal: Simulate GBM using Euler-Maruyama approximation.

        Returns:
        - A NumPy array of prices of length N+1 including S0
        """
        S = np.zeros(self.N + 1)
        S[0] = self.S0
        for i in range(1, self.N + 1):
            dW = np.random.randn() * np.sqrt(self.dt)
            S[i] = S[i - 1] + self.mu * S[i - 1] * self.dt + self.sigma * S[i - 1] * dW
        return S

    def plot(self, M: int = 10, method: str = "exact", alpha: float = 0.3, **kwargs):
        """
        Plot one or more simulated GBM paths.

        Parameters:
        - M: Number of paths to simulate (default: 10)
        - method: Simulation method - 'exact' or 'euler'
        - alpha: Line transparency (useful for multiple paths)
        - kwargs: Extra matplotlib arguments (e.g., color, lw, figsize)
        """
        figsize = kwargs.pop("figsize", (10, 5))
        plt.figure(figsize=figsize)

        for i in range(M):
            S = self.simulate(method=method)
            label = f"{method.capitalize()} Method" if i == 0 else None
            line_alpha = 1.0 if M == 1 else alpha
            plt.plot(self.t, S, label=label, alpha=line_alpha, **kwargs)

        plt.title(f"{M} GBM Path{'s' if M > 1 else ''} - {method.capitalize()} Method")
        plt.xlabel("Time (years)")
        plt.ylabel("Stock Price")
        plt.grid(True)
        if M == 1:
            plt.legend()
        plt.tight_layout()
        plt.show()