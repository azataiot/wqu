# src/wqu/dp/binomial.py
# -*- coding: utf-8 -*-
# Author: Azat
# Date: 2025-04-13

"""
This module implements the binomial tree for the options pricing model.
"""
import numpy as np

def binomial_tree(initial_price:float, maturity:float, up_factor:float, down_factor:float, steps:int):
    prices = np.zeros((steps + 1, steps + 1))
    for j in range(steps + 1):  # time steps
        for i in range(j + 1):  # up moves
            prices[j, i] = initial_price * (up_factor ** i) * (down_factor ** (j - i))
    return prices