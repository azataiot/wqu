# src/wqu/pricing/greeks.py
from typing import Callable

def compute_vega(pricing_func: Callable, sigma: float, 
                delta_vol: float = 0.05, **kwargs) -> float:
    """
    Compute option vega using finite differences
    
    Args:
        pricing_func: Option pricing function
        sigma: Current volatility
        delta_vol: Change in volatility for finite difference
        **kwargs: Additional arguments for pricing function
        
    Returns:
        Option vega
    """
    # Price with sigma + delta_vol
    price_up = pricing_func(sigma=sigma + delta_vol, **kwargs)
    
    # Price with sigma - delta_vol
    price_down = pricing_func(sigma=sigma - delta_vol, **kwargs)
    
    # Central difference approximation
    vega = (price_up - price_down)/(2 * delta_vol)
    
    return round(vega, 4)

def compute_delta(pricing_func: Callable, S0: float, 
                 delta_S: float = None, **kwargs) -> float:
    """
    Compute option delta using finite differences
    
    Args:
        pricing_func: Option pricing function
        S0: Current stock price
        delta_S: Change in stock price for finite difference
        **kwargs: Additional arguments for pricing function
        
    Returns:
        Option delta
    """
    if delta_S is None:
        delta_S = S0 * 0.01
        
    # Price with S0 + delta_S
    price_up = pricing_func(S0=S0 + delta_S, **kwargs)
    
    # Price with S0 - delta_S
    price_down = pricing_func(S0=S0 - delta_S, **kwargs)
    
    # Central difference approximation
    delta = (price_up - price_down)/(2 * delta_S)
    
    return round(delta, 4)
