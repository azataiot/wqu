# src/wqu/pricing/binomial.py
import numpy as np
from typing import Tuple
from wqu.pricing.options import OptionType, OptionStyle

class BinomialTree:
    # noinspection PyPep8Naming
    def __init__(self, S0: float, K: float, T: float, r: float, sigma: float, n_steps: int):
        """
        Initialize binomial tree model for option pricing
        
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
        self.dt = T/n_steps
        
        # Calculate up/down factors and probability
        self.u = np.exp(sigma * np.sqrt(self.dt))
        self.d = 1/self.u
        self.p = (np.exp(r * self.dt) - self.d)/(self.u - self.d)
        
    def _build_stock_tree(self) -> np.ndarray:
        """Build the stock price tree"""
        tree = np.zeros((self.n_steps + 1, self.n_steps + 1))
        tree[0,0] = self.S0
        
        for i in range(1, self.n_steps + 1):
            for j in range(i+1):
                tree[j,i] = self.S0 * (self.u ** (i-j)) * (self.d ** j)
        return tree
    
    def price_european(self, option_type: OptionType = OptionType.CALL) -> float:
        """
        Price European option using binomial tree
        
        Args:
            option_type: OptionType.CALL or OptionType.PUT
            
        Returns:
            Option price
        """
        tree = self._build_stock_tree()
        option_tree = np.zeros((self.n_steps + 1, self.n_steps + 1))
        
        # Initialize terminal payoffs
        for i in range(self.n_steps + 1):
            if option_type == OptionType.CALL:
                option_tree[i,self.n_steps] = max(0, float(tree[i,self.n_steps]) - self.K)
            else:
                option_tree[i,self.n_steps] = max(0, self.K - float(tree[i,self.n_steps]))
        
        # Backward induction
        for j in range(self.n_steps-1, -1, -1):
            for i in range(j+1):
                option_tree[i,j] = np.exp(-self.r * self.dt) * (
                    self.p * option_tree[i,j+1] + 
                    (1-self.p) * option_tree[i+1,j+1]
                )
                
        return round(option_tree[0,0], 2)
    
    def price_american(self, option_type: OptionType = OptionType.CALL) -> float:
        """
        Price American option using binomial tree
        
        Args:
            option_type: OptionType.CALL or OptionType.PUT
            
        Returns:
            Option price
        """
        tree = self._build_stock_tree()
        option_tree = np.zeros((self.n_steps + 1, self.n_steps + 1))
        
        # Initialize terminal payoffs
        for i in range(self.n_steps + 1):
            if option_type == OptionType.CALL:
                option_tree[i,self.n_steps] = max(0, float(tree[i,self.n_steps]) - self.K)
            else:
                option_tree[i,self.n_steps] = max(0, self.K - float(tree[i,self.n_steps]))
        
        # Backward induction with early exercise
        for j in range(self.n_steps-1, -1, -1):
            for i in range(j+1):
                hold_value = np.exp(-self.r * self.dt) * (
                    self.p * option_tree[i,j+1] + 
                    (1-self.p) * option_tree[i+1,j+1]
                )
                
                if option_type == OptionType.CALL:
                    exercise_value = max(0, float(tree[i,j]) - self.K)
                else:
                    exercise_value = max(0, self.K - float(tree[i,j]))
                    
                option_tree[i,j] = max(hold_value, exercise_value)
                
        return round(option_tree[0,0], 2)
    
    def compute_delta(self, option_type: OptionType = OptionType.CALL, 
                     style: OptionStyle = OptionStyle.EUROPEAN) -> float:
        """
        Compute option delta at t=0
        
        Args:
            option_type: OptionType.CALL or OptionType.PUT
            style: OptionStyle.EUROPEAN or OptionStyle.AMERICAN
            
        Returns:
            Option delta
        """
        price_func = self.price_european if style == OptionStyle.EUROPEAN else self.price_american
        
        # Small change in stock price
        h = self.S0 * 0.01
        
        # Original price
        original_S0 = self.S0
        
        # Price with S0 + h
        self.S0 = original_S0 + h
        price_up = price_func(option_type)
        
        # Price with S0 - h
        self.S0 = original_S0 - h
        price_down = price_func(option_type)
        
        # Reset S0
        self.S0 = original_S0
        
        # Central difference approximation
        delta = (price_up - price_down)/(2*h)
        
        return round(delta, 4)
