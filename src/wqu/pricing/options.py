from enum import Enum, auto
from dataclasses import dataclass
from typing import Union, Optional

class OptionType(Enum):
    CALL = auto()
    PUT = auto()

class OptionStyle(Enum):
    EUROPEAN = auto()
    AMERICAN = auto()
    ASIAN = auto()

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
