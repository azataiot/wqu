# src/wqu/pricing/utils.py

import numpy as np
from scipy.stats import norm

def black_scholes_call(S, K, T, r, sigma):
    """
    Calculate Black-Scholes price for a European call option

    Parameters:
    S: Current stock price
    K: Strike price
    T: Time to maturity (in years)
    r: Risk-free interest rate (annual)
    sigma: Volatility of the stock
    """
    d1 = (np.log(S/K) + (r + sigma**2/2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)

    call_price = S*norm.cdf(d1) - K*np.exp(-r*T)*norm.cdf(d2)
    return round(call_price, 2)

def black_scholes_put(S, K, T, r, sigma):
    """Calculate Black-Scholes price for a European put option"""
    d1 = (np.log(S/K) + (r + sigma**2/2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)

    put_price = K*np.exp(-r*T)*norm.cdf(-d2) - S*norm.cdf(-d1)
    return round(put_price, 2)

def monte_carlo_gbm(S0, r, sigma, T, n_steps, n_sims):
    """
    Generate Monte Carlo paths using Geometric Brownian Motion
    """
    dt = T/n_steps
    paths = np.zeros((n_sims, n_steps+1))
    paths[:,0] = S0

    for t in range(1, n_steps+1):
        z = np.random.standard_normal(n_sims)
        paths[:,t] = paths[:,t-1] * np.exp((r - 0.5*sigma**2)*dt + sigma*np.sqrt(dt)*z)

    return paths