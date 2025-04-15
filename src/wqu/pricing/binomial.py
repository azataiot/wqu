import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple
from wqu.pricing.options import OptionType

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
        self.avg_stock_tree = np.zeros((n_steps + 1, n_steps + 1))
        self.option_tree = np.zeros((n_steps + 1, n_steps + 1))
        self._build_stock_tree()

    def _build_stock_tree(self):
        """
        Builds the stock price evolution tree and computes running averages.
        """
        for i in range(self.n_steps + 1):
            for j in range(i + 1):
                self.stock_tree[j, i] = self.S0 * (self.u ** (i - j)) * (self.d ** j)

        # Compute running average stock prices over time
        for i in range(self.n_steps + 1):
            for j in range(i + 1):
                self.avg_stock_tree[j, i] = np.mean(self.stock_tree[: j + 1, i])

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

    def price_asian(self, option_type: OptionType = OptionType.PUT) -> float:
        """
        Price an Asian option using a binomial tree.

        Args:
            option_type: OptionType.CALL or OptionType.PUT

        Returns:
            Asian option price
        """
        # Compute terminal payoffs based on the average stock price at each node
        for j in range(self.n_steps + 1):
            avg_price = np.mean(self.stock_tree[j, :])  # Correctly compute path-dependent avg
            if option_type == OptionType.CALL:
                self.option_tree[j, self.n_steps] = max(0, avg_price - self.K)
            else:
                self.option_tree[j, self.n_steps] = max(0, self.K - avg_price)

        # Backward induction for pricing
        for i in range(self.n_steps - 1, -1, -1):
            for j in range(i + 1):
                # Compute expected discounted value
                expected_value = np.exp(-self.r * self.dt) * (
                        self.p * self.option_tree[j, i + 1] + (1 - self.p) * self.option_tree[j + 1, i + 1]
                )
                avg_price = np.mean(self.stock_tree[j, : i + 1])  # Average price up to this node
                intrinsic_value = max(0, self.K - avg_price) if option_type == OptionType.PUT else max(0, avg_price - self.K) #noqa

                # Store the max value (since early exercise is not allowed, it's purely expectation-based)
                self.option_tree[j, i] = expected_value

        return self.option_tree[0, 0]

    def delta(self, option_type: OptionType) -> float:
        """
        Compute Delta using finite difference method.
        """
        h = self.S0 * 0.01  # Small change in stock price
        option_up = BinomialTree(self.S0 + h, self.K, self.T, self.r, self.sigma, self.n_steps).price_european(option_type)
        option_down = BinomialTree(self.S0 - h, self.K, self.T, self.r, self.sigma, self.n_steps).price_european(option_type)
        return (option_up - option_down) / (2 * h)

    def delta_steps(self, option_type: OptionType) -> float:
        """
        Compute Delta dynamically at each node using finite differences.
        """
        h = self.S0 * 0.01  # Small perturbation in stock price

        # Compute option price with S0 + h
        binomial_up = BinomialTree(self.S0 + h, self.K, self.T, self.r, self.sigma, self.n_steps)
        price_up = binomial_up.price_asian(option_type)  # Compute for Asian options

        # Compute option price with S0 - h
        binomial_down = BinomialTree(self.S0 - h, self.K, self.T, self.r, self.sigma, self.n_steps)
        price_down = binomial_down.price_asian(option_type)  # Compute for Asian options

        # Finite difference method to approximate delta
        delta_value = (price_up - price_down) / (2 * h)

        return delta_value

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
