# src/wqu/sm/__init__.py
# -*- coding: utf-8 -*-

"""
This module provides a set of classes and functions for working with Stochastic Modeling, including:
- BlackScholes model closed-form solution
- Lewis's approach for pricing options with a semi-analytical method using the Fourier transform, which requires:
    - a characteristic function
    - a Fourier transform of the payoff function
    - a Fourier transform of the characteristic function

"""