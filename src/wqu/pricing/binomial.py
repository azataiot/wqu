import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple
from wqu.pricing.options import OptionType, OptionStyle

class BinomialTree:
    def __init__(self, S0: float, K: float, T: float, r: float, sigma: float, n_steps: int):
        """
        Initialize binomial tree model for option pricing.
        """
        self.S0 = S0
        self.K = K
        self.T = T
        self.r = r
        self.sigma = sigma
        self.n_steps = n_steps
        self.dt = T / n_steps

        # Calculate up/down factors and probability
        self.u = np.exp(sigma * np.sqrt(self.dt))
        self.d = 1 / self.u
        self.p = (np.exp(r * self.dt) - self.d) / (self.u - self.d)

        # Store tree structures
        self.stock_tree = np.zeros((n_steps + 1, n_steps + 1))
        self.option_tree = np.zeros((n_steps + 1, n_steps + 1))
        self._build_stock_tree()

    def _build_stock_tree(self):
        """
        Builds the stock price evolution tree.
        """
        for i in range(self.n_steps + 1):
            for j in range(i + 1):
                self.stock_tree[j, i] = self.S0 * (self.u ** (i - j)) * (self.d ** j)

    def price_european(self, option_type: OptionType) -> float:
        """
        Compute European option price using backward induction.
        """
        for j in range(self.n_steps + 1):
            self.option_tree[j, self.n_steps] = max(0, (self.stock_tree[j, self.n_steps] - self.K) if option_type == OptionType.CALL else (self.K - self.stock_tree[j, self.n_steps]))

        for i in range(self.n_steps - 1, -1, -1):
            for j in range(i + 1):
                self.option_tree[j, i] = np.exp(-self.r * self.dt) * (self.p * self.option_tree[j, i + 1] + (1 - self.p) * self.option_tree[j + 1, i + 1])

        return self.option_tree[0, 0]

    def price_american(self, option_type: OptionType) -> float:
        """
        Compute American option price using backward induction.
        """
        for j in range(self.n_steps + 1):
            self.option_tree[j, self.n_steps] = max(0, (self.stock_tree[j, self.n_steps] - self.K) if option_type == OptionType.CALL else (self.K - self.stock_tree[j, self.n_steps]))

        for i in range(self.n_steps - 1, -1, -1):
            for j in range(i + 1):
                hold_value = np.exp(-self.r * self.dt) * (self.p * self.option_tree[j, i + 1] + (1 - self.p) * self.option_tree[j + 1, i + 1])
                intrinsic_value = max(0, (self.stock_tree[j, i] - self.K) if option_type == OptionType.CALL else (self.K - self.stock_tree[j, i]))
                self.option_tree[j, i] = max(hold_value, intrinsic_value)

        return self.option_tree[0, 0]

    def delta(self, option_type: OptionType) -> float:
        """
        Compute Delta using finite difference method.
        """
        h = self.S0 * 0.01  # Small change in stock price
        option_up = BinomialTree(self.S0 + h, self.K, self.T, self.r, self.sigma, self.n_steps).price_european(option_type)
        option_down = BinomialTree(self.S0 - h, self.K, self.T, self.r, self.sigma, self.n_steps).price_european(option_type)
        return (option_up - option_down) / (2 * h)

    def vega(self, option_type: OptionType, dv: float = 0.01) -> float:
        """
        Compute Vega using finite difference method.
        """
        option_original = self.price_european(option_type)
        option_higher_vol = BinomialTree(self.S0, self.K, self.T, self.r, self.sigma + dv, self.n_steps).price_european(option_type)
        return (option_higher_vol - option_original) / dv

    def get_trees(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Returns the stored stock and option price trees for visualization.
        """
        return self.stock_tree, self.option_tree

    def plot_tree(self):
        """
        Plots the binomial tree for stock prices.
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        for i in range(self.n_steps + 1):
            for j in range(i + 1):
                ax.text(i, self.stock_tree[j, i], f'{self.stock_tree[j, i]:.2f}', ha='center', va='center', fontsize=10, color='blue')
        ax.set_title("Binomial Stock Price Tree")
        ax.set_xlabel("Time Step")
        ax.set_ylabel("Stock Price")
        plt.show()
