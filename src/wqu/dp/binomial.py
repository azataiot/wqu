# src/wqu/dp/binomial.py
# -*- coding: utf-8 -*-
# Author: Azat
# Date: 2025-04-13

"""
This module implements the binomial tree for the options pricing model.
"""
import numpy as np


# A Class represents the binomial tree
# ------------------------------------------
# Binomial Tree for Options Pricing
# Main class: BinomialTree
# Note: 'asian' style treated as European-style Asian option (exercise at maturity only)
# ------------------------------------------

class BinomialTree:
    """
    A class representing a binomial tree for option pricing.
    Attributes:
    - S0 : float : Initial stock price
    - K  : float : Strike price
    - T  : float : Time to maturity (in years)
    - r  : float : Risk-free interest rate (annualized)
    - u  : float : Up factor (stock price increase)
    - d  : float : Down factor (stock price decrease)
    - N  : int   : Number of time steps
    - option_type : str : 'call' or 'put'
    - option_style : str : 'european', 'american', or 'asian'
    """
    def __init__(self,
                    S0: float,
                    K: float,
                    T: float,
                    r: float,
                    u: float,
                    d: float,
                    N: int,
                    option_type: str = 'call',
                    option_style: str = 'european', # 'american' or 'european' or 'asian'
                 ):
        self.S0 = S0
        self.K = K
        self.T = T
        self.r = r
        self.u = u
        self.d = d
        self.N = N
        self.dt = T / N
        self.option_type = option_type.lower()
        self.option_style = option_style.lower()
        self.p = (np.exp(r * self.dt) - d) / (u - d)
        self.discount = np.exp(-r * self.dt) # Discount factor for one time step

        self.stock_tree = None
        self.option_tree = None
        self.delta_tree = None


    def build_stock_tree(self):
        S = np.zeros((self.N + 1, self.N + 1))
        for t in range(self.N + 1):
            for i in range(t + 1):
                S[t, i] = self.S0 * (self.u ** i) * (self.d ** (t - i))
        self.stock_tree = S
        return S

    def _build_asian_option_tree(self):
        from collections import defaultdict

        values = defaultdict(list)  # key: (t, i), value: list of (sum, prob)
        values[(0, 0)].append((self.S0, 1))

        for t in range(1, self.N + 1):
            for i in range(t + 1):
                if i < t:
                    for sum_s, prob in values[(t - 1, i)]:
                        S = self.S0 * (self.u ** i) * (self.d ** (t - 1 - i))
                        new_sum = sum_s + S * self.d
                        values[(t, i)].append((new_sum, prob * (1 - self.p)))
                if i > 0:
                    for sum_s, prob in values[(t - 1, i - 1)]:
                        S = self.S0 * (self.u ** (i - 1)) * (self.d ** (t - i))
                        new_sum = sum_s + S * self.u
                        values[(t, i)].append((new_sum, prob * self.p))

        payoff = 0
        for i in range(self.N + 1):
            for sum_s, prob in values[(self.N, i)]:
                avg = sum_s / (self.N + 1)
                if self.option_type == 'call':
                    payoff += prob * max(avg - self.K, 0)
                else:
                    payoff += prob * max(self.K - avg, 0)

        self.option_tree = np.zeros_like(self.build_stock_tree())
        self.option_tree[0, 0] = payoff * np.exp(-self.r * self.T)
        return self.option_tree

    def build_option_tree(self):
        if self.option_style == 'asian':
            return self._build_asian_option_tree()

        if self.stock_tree is None:
            self.build_stock_tree()

        C = np.zeros_like(self.stock_tree)

        # Terminal values
        for i in range(self.N + 1):
            ST = self.stock_tree[self.N, i]
            if self.option_type == 'call':
                C[self.N, i] = max(0, ST - self.K)
            elif self.option_type == 'put':
                C[self.N, i] = max(0, self.K - ST)
            else:
                raise ValueError("option_type must be either 'call' or 'put'")

        # Backward induction
        for t in reversed(range(self.N)):
            for i in range(t+1):
                expected = self.discount * (self.p * C[t + 1, i + 1] + (1 - self.p) * C[t + 1, i])
                if self.option_style == 'european':
                    C[t, i] = expected
                elif self.option_style == 'american':
                    ST = self.stock_tree[t, i]
                    if self.option_type == 'call':
                        immediate = max(0, ST - self.K)
                    elif self.option_type == 'put':
                        immediate = max(0, self.K - ST)
                    else:
                        raise ValueError("option_type must be either 'call' or 'put'")
                    C[t, i] = max(expected, immediate)
                else:
                    raise ValueError("option_style must be either 'european' or 'american'")
        self.option_tree = C
        return C

    def build_delta_tree(self):
        if self.option_tree is None:
            self.build_option_tree()

        delta = np.zeros_like(self.stock_tree)

        for t in range(self.N):
            for i in range(t + 1):
               Su = self.stock_tree[t + 1, i + 1]
               Sd = self.stock_tree[t + 1, i]
               Cu = self.option_tree[t + 1, i + 1]
               Cd = self.option_tree[t + 1, i]
               delta[t, i] = (Cu - Cd) / (Su - Sd)
        self.delta_tree = delta
        return delta

    def simulate_delta_hedge(self, path: str, verbose: bool = True):
        """
        Simulates a delta hedge over a single path (e.g., 'udu').

        Parameters:
        - path : str : Sequence of 'u' and 'd' (e.g., 'udu' means up → down → up)
        - verbose : bool : If True, prints detailed step-by-step hedge info

        Returns:
        - final_hedge_value : float : Portfolio value at maturity
        - option_payoff     : float : Actual payoff of the option
        - hedge_error       : float : Difference between hedge and actual payoff
        """

        if self.delta_tree is None:
            self.build_delta_tree()

        if self.stock_tree is None:
            self.build_stock_tree()

        if self.option_tree is None:
            self.build_option_tree()

        shares_held = 0
        cash = 0
        t, i = 0, 0  # start at root
        # initial hedge
        stock_now = self.stock_tree[t, i]
        delta_now = self.delta_tree[t, i]
        shares_held = delta_now
        cash = -delta_now * stock_now  # borrow/lend to initiate hedge

        if verbose:
            total_value = shares_held * stock_now + cash
            print("Initial Hedge:")
            print(f"Stock: {stock_now:.2f}, Delta: {delta_now:.2f}, Shares: {shares_held:.2f}, Cash: {cash:.2f}, Total: {total_value:.2f}")
            print("\nStep | Stock  | Delta  | Shares Δ | Stock Value | Cash | Total")

        for move in path:
            delta_now = self.delta_tree[t, i]
            stock_now = self.stock_tree[t, i]

            # Determine next step
            if move == 'u':
                i += 1
            elif move == 'd':
                i += 0
            else:
                raise ValueError("Path must be a sequence of 'u' and 'd' only.")

            t += 1

            # Next stock price
            stock_next = self.stock_tree[t, i]
            delta_next = self.delta_tree[t, i] if t < self.N else 0  # No hedge at final step

            # Hedge adjustment
            delta_change = delta_next - delta_now
            cash -= delta_change * stock_now
            shares_held = delta_next

            if verbose:
                total_value = shares_held * stock_next + cash
                print(f" {t:<4} | {stock_next:<7.2f} | {delta_next:<6.2f} | {delta_change:<8.2f} | {shares_held * stock_next:<11.2f} | {cash:<6.2f} | {total_value:.2f}")

        # Final portfolio value
        stock_final = self.stock_tree[t, i]
        hedge_value = shares_held * stock_final + cash

        # Option payoff
        if self.option_type == 'call':
            option_payoff = max(0, stock_final - self.K)
        else:
            option_payoff = max(0, self.K - stock_final)

        hedge_error = hedge_value - option_payoff

        if verbose:
            print("\nFinal Results:")
            print(f"  Hedged Portfolio Value : {hedge_value:.4f}")
            print(f"  Option Payoff          : {option_payoff:.4f}")
            print(f"  Hedging Error          : {hedge_error:.4f}")

        return hedge_value, option_payoff, hedge_error

    def price(self):
        if self.option_tree is None:
            self.build_option_tree()
        return self.option_tree[0, 0]

    def summary(self):
        print(f"Option Style: {self.option_style.capitalize()}")
        print(f"Option Type: {self.option_type.capitalize()}")
        print(f"Price at t=0: {self.price():.4f}")
        print(f"Risk-neutral p: {self.p:.4f}")
        print(f"Discount factor: {self.discount:.4f}")


    def plot_tree(self, tree=None, title="Binomial Tree", cmap="viridis"):
        import matplotlib.pyplot as plt
        if tree is None:
            raise ValueError("A tree matrix must be provided for plotting (e.g., stock_tree or option_tree or delta tree).")
        plt.figure(figsize=(10, 6))
        for t in range(tree.shape[0]):
            for i in range(t + 1):
                plt.scatter(t, i, c='black')
                plt.text(t, i, f"{tree[t, i]:.2f}", fontsize=8, ha='center', va='center', bbox=dict(boxstyle="round,pad=0.3", fc="lightyellow", ec="black", lw=0.5))
        plt.title(title)
        plt.xlabel("Time Step t")
        plt.ylabel("Node i")
        plt.gca().invert_yaxis()
        plt.grid(True)
        plt.show()

    def check_put_call_parity(self, verbose=False):
        """
        Check Put-Call Parity: C + K*e^(-rT) ≈ P + S
        verbose : bool : If True, print the details of the check.
        """
        if self.option_type != 'call':
            raise ValueError("Put-Call Parity check is only valid for call options.")

        # Price the put with same inputs
        put = BinomialTree(S0=self.S0,K=self.K,T=self.T,r=self.r,u=self.u,d=self.d,N=self.N,option_type='put')
        P0 = put.price()
        C0 = self.price()
        lhs = C0 + self.K * np.exp(-self.r * self.T)
        rhs = P0 + self.S0
        diff = abs(lhs - rhs)

        if verbose:
            print("Put-Call Parity Check:")
            print(f"P0 = {P0:.4f}")
            print(f"C0 = {C0:.4f}")
            print(f"PV of K = K*e^(-rT) = {self.K * np.exp(-self.r * self.T):.4f}")
            print(f"Call + K*e^(-rT) = {lhs:.4f}")
            print(f"Put + S0        = {rhs:.4f}")
            print(f"Difference       = {diff:.6f}")

        return bool(np.isclose(lhs, rhs, atol=1e-4))
