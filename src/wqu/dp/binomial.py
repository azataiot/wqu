# src/wqu/dp/binomial.py
# -*- coding: utf-8 -*-
# Author: Azat
# Date: 2025-04-13

"""
This module implements the binomial tree for the options pricing model.
"""
import numpy as np

def binomial_call(S0, K, T, r, u, d, N):
    """
    Computes the price of a European call option using the binomial tree model.

    Args:
        S0 (float): Initial stock price.
        K (float): Strike price of the option.
        T (float): Time to maturity (in years).
        r (float): Risk-free interest rate (annualized).
        u (float): Upward movement factor for the stock price.
        d (float): Downward movement factor for the stock price.
        N (int): Number of time steps in the binomial tree.

    Returns:
        float: The price of the European call option.
    """
    dt = T / N  # Time step size
    disc = np.exp(-r * dt)  # Discount factor for one time step
    q = (np.exp(r * dt) - d) / (u - d)  # Risk-neutral probability

    # Initialize trees for stock prices and option values
    S = np.zeros((N + 1, N + 1))  # Stock price tree
    C = np.zeros((N + 1, N + 1))  # Option value tree

    # Compute terminal stock prices and option payoffs
    for i in range(N + 1):
        S[N, i] = S0 * (u ** i) * (d ** (N - i))  # Stock price at maturity
        C[N, i] = max(S[N, i] - K, 0)  # Payoff for a call option at maturity

    # Perform backward induction to calculate option values at earlier nodes
    for j in range(N - 1, -1, -1):  # Iterate over time steps in reverse
        for i in range(j + 1):  # Iterate over nodes at each time step
            S[j, i] = S0 * (u ** i) * (d ** (j - i))  # Stock price at node
            # Option value is the discounted expected value of future payoffs
            C[j, i] = disc * (q * C[j + 1, i + 1] + (1 - q) * C[j + 1, i])

    # Return the call option price
    return C[0, 0]


# A function to calculate the price of a European put option using the put-call parity
def binomial_put(S0, K, T, r, u, d, N):
    """
    Computes the price of a European put option using the binomial tree model.

    Args:
        S0 (float): Initial stock price.
        K (float): Strike price of the option.
        T (float): Time to maturity (in years).
        r (float): Risk-free interest rate (annualized).
        u (float): Upward movement factor for the stock price.
        d (float): Downward movement factor for the stock price.
        N (int): Number of time steps in the binomial tree.

    Returns:
        float: The price of the European put option.
    """
    call_price, _, _ = binomial_call(S0, K, T, r, u, d, N)
    return call_price - S0 * np.exp(-r * T) + K * np.exp(-r * T)


# A function to calculate the price of a European put option using the put-call parity given the call price
def binomial_put_from_call(S0, K, T, r, call_price):
    """
    Computes the price of a European put option using the put-call parity.

    Args:
        S0 (float): Initial stock price.
        K (float): Strike price of the option.
        T (float): Time to maturity (in years).
        r (float): Risk-free interest rate (annualized).
        call_price (float): Price of the European call option.

    Returns:
        float: The price of the European put option.
    """
    return call_price - S0 * np.exp(-r * T) + K * np.exp(-r * T)