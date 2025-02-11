# src/wqu/pricing/options.py
from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional, List

class OptionType(Enum):
    CALL = auto()
    PUT = auto()

class OptionStyle(Enum):
    EUROPEAN = auto()
    AMERICAN = auto()
    ASIAN = auto()

class PricingMethod(Enum):
    BINOMIAL = auto()
    TRINOMIAL = auto()
    MONTE_CARLO = auto()

@dataclass
class Option:
    """Base class for option contracts"""
    S0: float  # Initial stock price
    K: float   # Strike price
    T: float   # Time to expiration in years
    r: float   # Risk-free interest rate (annual)
    sigma: float  # Volatility
    option_type: OptionType = OptionType.CALL
    option_style: OptionStyle = OptionStyle.EUROPEAN
    pricing_method: PricingMethod = PricingMethod.BINOMIAL
    n_steps: Optional[int] = None  # Number of steps for tree methods

    def __post_init__(self):
        """Validate option parameters"""
        if self.S0 <= 0:
            raise ValueError("Initial stock price must be positive")
        if self.K <= 0:
            raise ValueError("Strike price must be positive")
        if self.T <= 0:
            raise ValueError("Time to expiration must be positive")
        if self.sigma <= 0:
            raise ValueError("Volatility must be positive")
        if self.n_steps is not None and self.n_steps <= 0:
            raise ValueError("Number of steps must be positive")

    def payoff(self, stock_price: float) -> float:
        """Calculate option payoff at expiration"""
        if self.option_type == OptionType.CALL:
            return max(0, stock_price - self.K)
        else:
            return max(0, self.K - stock_price)

    def price(self) -> float:
        """Calculate option price based on the selected pricing method"""
        from wqu.pricing.binomial import BinomialTree
        from wqu.pricing.trinomial import TrinomialTree

        if self.n_steps is None:
            self.n_steps = 50

        if self.pricing_method == PricingMethod.BINOMIAL:
            tree = BinomialTree(
                S0=self.S0, K=self.K, T=self.T, r=self.r, sigma=self.sigma, n_steps=self.n_steps
            )
            return tree.price_european(self.option_type) if self.option_style == OptionStyle.EUROPEAN else tree.price_american(self.option_type)
        elif self.pricing_method == PricingMethod.TRINOMIAL:
            tree = TrinomialTree(
                S0=self.S0, K=self.K, T=self.T, r=self.r, sigma=self.sigma, n_steps=self.n_steps
            )
            return tree.price_european(self.option_type) if self.option_style == OptionStyle.EUROPEAN else tree.price_american(self.option_type)
        elif self.pricing_method == PricingMethod.MONTE_CARLO:
            raise NotImplementedError("Monte Carlo pricing not implemented")
        else:
            raise ValueError("Invalid pricing method")

    def deltas(self) -> List[float]:
        """Calculate option deltas at each node"""
        if self.n_steps is None:
            self.n_steps = 50

        dt = self.T / self.n_steps
        deltas = []

        for i in range(self.n_steps + 1):
            t = i * dt
            remaining_T = self.T - t
            if remaining_T <= 0:
                deltas.append(0.0)  # At expiration
                continue

            # Calculate delta using finite differences
            h = self.S0 * 0.01
            price_up = self.price()

            # Temporarily modify S0 for down price
            original_S0 = self.S0
            self.S0 = self.S0 - h
            price_down = self.price()
            self.S0 = original_S0  # Restore original S0

            delta = (price_up - price_down) / (2 * h)
            deltas.append(delta)

        return deltas
