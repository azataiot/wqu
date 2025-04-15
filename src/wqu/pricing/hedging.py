# src/wqu/pricing/hedging.py
import numpy as np
from typing import List
from dataclasses import dataclass

@dataclass
class HedgingPosition:
    time_step: int
    stock_price: float
    delta: float
    shares_traded: float
    cash_account: float

class DeltaHedging:
    def __init__(self, S0: float, K: float, T: float, r: float, 
                 sigma: float, n_steps: int):
        """
        Initialize delta hedging simulation
        
        Args:
            S0: Initial stock price
            K: Strike price
            T: Time to expiration in years
            r: Risk-free interest rate (annual)
            sigma: Volatility
            n_steps: Number of steps in tree
        """
        self.S0 = S0
        self.K = K
        self.T = T
        self.r = r
        self.sigma = sigma
        self.n_steps = n_steps
        self.dt = T/n_steps
        
    def simulate_path(self, path: List[str], option_price: float, 
                     deltas: List[float]) -> List[HedgingPosition]:
        """
        Simulate delta hedging along a specific path
        
        Args:
            path: List of 'u' (up) or 'd' (down) moves
            option_price: Initial option price
            deltas: List of deltas at each node
            
        Returns:
            List of HedgingPosition objects
        """
        positions = []
        current_price = self.S0
        current_delta = deltas[0]
        cash_account = -current_delta * self.S0 + option_price
        
        # Initial position
        positions.append(HedgingPosition(
            time_step=0,
            stock_price=current_price,
            delta=current_delta,
            shares_traded=current_delta,
            cash_account=cash_account
        ))
        
        # Simulate hedging along path
        for i, move in enumerate(path, 1):
            # Update stock price
            if move == 'u':
                current_price *= np.exp(self.sigma * np.sqrt(self.dt))
            else:
                current_price *= np.exp(-self.sigma * np.sqrt(self.dt))
            
            # Update delta hedge
            new_delta = deltas[i] if i < len(deltas) else 0
            shares_traded = new_delta - current_delta
            
            # Update cash account
            cash_account = (cash_account * np.exp(self.r * self.dt) - 
                          shares_traded * current_price)
            
            positions.append(HedgingPosition(
                time_step=i,
                stock_price=current_price,
                delta=new_delta,
                shares_traded=shares_traded,
                cash_account=cash_account
            ))
            
            current_delta = new_delta
            
        return positions
