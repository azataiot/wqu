# src/wqu/pricing/trinomial.py
import numpy as np
from typing import Tuple
from wqu.pricing.options import OptionType

class TrinomialTree:
    def __init__(self, S0: float, K: float, T: float, r: float, sigma: float, n_steps: int):
        """
        Initialize trinomial tree model for option pricing.

        Args:
            S0: Initial stock price
            K: Strike price
            T: Time to expiration in years
            r: Risk-free interest rate (annual)
            sigma: Volatility
            n_steps: Number of steps in the tree
        """
        self.S0 = S0
        self.K = K
        self.T = T
        self.r = r
        self.sigma = sigma
        self.n_steps = n_steps
        self.dt = T / n_steps

        # Compute up/down factors
        self.u = np.exp(sigma * np.sqrt(2 * self.dt))
        self.d = 1 / self.u

        # Risk-neutral probabilities
        exp_half_r_dt = np.exp(r * self.dt / 2)
        exp_sigma_sqrt_dt = np.exp(sigma * np.sqrt(self.dt / 2))
        exp_neg_sigma_sqrt_dt = np.exp(-sigma * np.sqrt(self.dt / 2))

        self.pu = ((exp_half_r_dt - exp_neg_sigma_sqrt_dt) / (exp_sigma_sqrt_dt - exp_neg_sigma_sqrt_dt)) ** 2
        self.pd = ((exp_sigma_sqrt_dt - exp_half_r_dt) / (exp_sigma_sqrt_dt - exp_neg_sigma_sqrt_dt)) ** 2
        self.pm = 1 - self.pu - self.pd

    def _build_stock_tree(self) -> np.ndarray:
        """
        Builds the stock price evolution tree.

        Returns:
            np.ndarray: A 2D array representing stock price evolution.
        """
        tree = np.zeros((2 * self.n_steps + 1, self.n_steps + 1))
        for j in range(self.n_steps + 1):
            for i in range(2 * j + 1):
                shift = j  # Center the tree
                tree[i, j] = self.S0 * (self.u ** (shift - i))

        return tree

    def price_european(self, option_type: OptionType = OptionType.CALL) -> float:
        """
        Price European option using trinomial tree.

        Args:
            option_type: OptionType.CALL or OptionType.PUT

        Returns:
            Option price
        """
        stock_tree = self._build_stock_tree()
        option_tree = np.zeros_like(stock_tree)

        # Terminal payoffs
        for i in range(2 * self.n_steps + 1):
            if option_type == OptionType.CALL:
                option_tree[i, self.n_steps] = max(0, stock_tree[i, self.n_steps] - self.K)
            else:
                option_tree[i, self.n_steps] = max(0, self.K - stock_tree[i, self.n_steps])

        # Backward induction
        for j in range(self.n_steps - 1, -1, -1):
            for i in range(2 * j + 1):
                option_tree[i, j] = np.exp(-self.r * self.dt) * (
                        self.pu * option_tree[i, j + 1] +
                        self.pm * option_tree[i + 1, j + 1] +
                        self.pd * option_tree[i + 2, j + 1]
                )

        return round(option_tree[0, 0], 4)

    def price_american(self, option_type: OptionType = OptionType.CALL) -> float:
        """
        Price American option using trinomial tree.

        Args:
            option_type: OptionType.CALL or OptionType.PUT

        Returns:
            Option price
        """
        stock_tree = self._build_stock_tree()
        option_tree = np.zeros_like(stock_tree)

        # Terminal payoffs
        for i in range(2 * self.n_steps + 1):
            if option_type == OptionType.CALL:
                option_tree[i, self.n_steps] = max(0, stock_tree[i, self.n_steps] - self.K)
            else:
                option_tree[i, self.n_steps] = max(0, self.K - stock_tree[i, self.n_steps])

        # Backward induction with early exercise
        for j in range(self.n_steps - 1, -1, -1):
            for i in range(2 * j + 1):
                hold_value = np.exp(-self.r * self.dt) * (
                        self.pu * option_tree[i, j + 1] +
                        self.pm * option_tree[i + 1, j + 1] +
                        self.pd * option_tree[i + 2, j + 1]
                )

                exercise_value = max(0, (stock_tree[i, j] - self.K) if option_type == OptionType.CALL else (self.K - stock_tree[i, j]))
                option_tree[i, j] = max(hold_value, exercise_value)

        return round(option_tree[0, 0], 4)

    def get_trees(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Returns the stored stock and option price trees for visualization.

        Returns:
            Tuple[np.ndarray, np.ndarray]: Stock and option price trees.
        """
        return self._build_stock_tree(), np.zeros_like(self._build_stock_tree())  # Placeholder for option tree