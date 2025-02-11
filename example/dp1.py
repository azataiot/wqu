# example/dp_1.py
from wqu.pricing.options import Option, OptionType, OptionStyle
from wqu.pricing.binomial import BinomialTree
from wqu.pricing.trinomial import TrinomialTree
from wqu.pricing.greeks import compute_vega
import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple

class ProjectCalculations:
    def __init__(self):
        # Initial parameters from the project
        self.S0 = 100
        self.r = 0.05  # 5%
        self.sigma = 0.20  # 20%
        self.T = 0.25  # 3 months
        self.n_steps = 50  # Default number of steps
        
    def verify_put_call_parity(self, K: float) -> Tuple[float, float, bool]:
        """
        Verify put-call parity for European options
        
        Args:
            K: Strike price
            
        Returns:
            Tuple of (LHS, RHS, parity_holds)
            where LHS = P + S0
                  RHS = C + K*exp(-rT)
        """
        # Create binomial tree pricer
        tree = BinomialTree(
            S0=self.S0,
            K=K,
            T=self.T,
            r=self.r,
            sigma=self.sigma,
            n_steps=self.n_steps
        )
        
        # Price European call and put
        call_price = tree.price_european(OptionType.CALL)
        put_price = tree.price_european(OptionType.PUT)
        
        # Calculate both sides of put-call parity
        lhs = put_price + self.S0
        rhs = call_price + K * np.exp(-self.r * self.T)
        
        # Check if parity holds within a small tolerance
        tolerance = 0.01
        parity_holds = abs(lhs - rhs) < tolerance
        
        return lhs, rhs, parity_holds
    
    def compare_european_american(self, K: float) -> dict:
        """
        Compare European and American option prices
        
        Args:
            K: Strike price
            
        Returns:
            Dictionary with price comparisons
        """
        tree = BinomialTree(
            S0=self.S0,
            K=K,
            T=self.T,
            r=self.r,
            sigma=self.sigma,
            n_steps=self.n_steps
        )
        
        # Price all combinations
        eu_call = tree.price_european(OptionType.CALL)
        eu_put = tree.price_european(OptionType.PUT)
        am_call = tree.price_american(OptionType.CALL)
        am_put = tree.price_american(OptionType.PUT)
        
        return {
            'european_call': eu_call,
            'european_put': eu_put,
            'american_call': am_call,
            'american_put': am_put,
            'call_difference': am_call - eu_call,
            'put_difference': am_put - eu_put
        }
    
    def compute_option_deltas(self, K: float) -> dict:
        """
        Compute deltas for all option types
        
        Args:
            K: Strike price
            
        Returns:
            Dictionary with delta values
        """
        tree = BinomialTree(
            S0=self.S0,
            K=K,
            T=self.T,
            r=self.r,
            sigma=self.sigma,
            n_steps=self.n_steps
        )
        
        deltas = {
            'european_call_delta': tree.compute_delta(OptionType.CALL, OptionStyle.EUROPEAN),
            'european_put_delta': tree.compute_delta(OptionType.PUT, OptionStyle.EUROPEAN),
            'american_call_delta': tree.compute_delta(OptionType.CALL, OptionStyle.AMERICAN),
            'american_put_delta': tree.compute_delta(OptionType.PUT, OptionStyle.AMERICAN)
        }
        
        return deltas
    
    def analyze_volatility_impact(self, K: float) -> dict:
        """
        Analyze impact of volatility change on option prices
        
        Args:
            K: Strike price
            
        Returns:
            Dictionary with price changes
        """
        # Original prices with sigma = 20%
        tree = BinomialTree(
            S0=self.S0,
            K=K,
            T=self.T,
            r=self.r,
            sigma=self.sigma,
            n_steps=self.n_steps
        )
        
        original_prices = {
            'european_call': tree.price_european(OptionType.CALL),
            'european_put': tree.price_european(OptionType.PUT),
            'american_call': tree.price_american(OptionType.CALL),
            'american_put': tree.price_american(OptionType.PUT)
        }
        
        # New prices with sigma = 25%
        tree.sigma = 0.25
        new_prices = {
            'european_call': tree.price_european(OptionType.CALL),
            'european_put': tree.price_european(OptionType.PUT),
            'american_call': tree.price_american(OptionType.CALL),
            'american_put': tree.price_american(OptionType.PUT)
        }
        
        # Calculate changes
        changes = {
            f"{key}_change": new_prices[key] - original_prices[key]
            for key in original_prices
        }
        
        return changes

def main():
    # Create calculator instance
    calc = ProjectCalculations()
    
    # Task 1-4: Put-Call Parity theoretical discussion is in the comments
    print("\nPut-Call Parity Verification for ATM options:")
    lhs, rhs, parity_holds = calc.verify_put_call_parity(K=100)
    print(f"P + S0 = {lhs:.2f}")
    print(f"C + Ke^(-rT) = {rhs:.2f}")
    print(f"Parity holds: {parity_holds}")
    
    # Task 5-7: European Options Analysis
    print("\nEuropean vs American Option Prices (ATM):")
    prices = calc.compare_european_american(K=100)
    for key, value in prices.items():
        print(f"{key}: {value:.2f}")
    
    print("\nOption Deltas:")
    deltas = calc.compute_option_deltas(K=100)
    for key, value in deltas.items():
        print(f"{key}: {value:.4f}")
    
    print("\nVolatility Impact (20% to 25%):")
    vol_impact = calc.analyze_volatility_impact(K=100)
    for key, value in vol_impact.items():
        print(f"{key}: {value:.2f}")

if __name__ == "__main__":
    main()