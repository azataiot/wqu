# src/wqu/dp/binomial.py
# -*- coding: utf-8 -*-
# Author: Azat
# Date: 2025-04-13

"""
This module implements the binomial tree for the options pricing model.
"""
import numpy as np

def binomial_tree(S0: float, T: float, u: float, d: float, N: int) -> np.ndarray:
    """
    Constructs a binomial tree of stock prices.

    :param S0: Initial stock price
    :param T: Time to maturity (not used in this basic tree, included for completeness)
    :param u: Up factor per step
    :param d: Down factor per step
    :param N: Number of steps
    :return: 2D array of stock prices [time_step][up_moves]
    """
    S = np.zeros((N + 1, N + 1))

    for j in range(N + 1):      # time step j
        for i in range(j + 1):  # number of up moves i
            S[j, i] = S0 * (u ** i) * (d ** (j - i))

    return S


