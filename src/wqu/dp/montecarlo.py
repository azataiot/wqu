# src/wqu/dp/montecarlo.py

import numpy as np

# A Class represents the Monte Carlo method for solving the Option pricing problem.
# ------------------------------------------
# Monte Carlo for Options Pricing
# Main class: MonteCarlo
# Note: can price European and Asian options using either binomial-hybrid or continuous GBM simulation
# ------------------------------------------

class MonteCarlo:
    def __init__(self,
                 S0: float,
                 K: float,
                 T: float,
                 r: float,
                 sigma: float,
                 N: int = 2500,
                 M: int = 10000,
                 option_type: str = 'call',  # 'call' or 'put'
                 option_style: str = 'european',  # 'european' or 'asian'
                 method: str = 'continuous'  # 'binomial' or 'continuous'
                 ):
        self.S0 = S0
        self.K = K
        self.T = T
        self.r = r
        self.sigma = sigma
        self.N = N
        self.M = M
        self.option_type = option_type.lower()
        self.option_style = option_style.lower()
        self.method = method.lower()

    def price(self):
        if self.option_style == 'european':
            return self._price_european()
        elif self.option_style == 'asian':
            return self._price_asian()
        else:
            raise ValueError("option_style must be 'european' or 'asian'")

    def _price_european(self):
        if self.method == 'continuous':
            Z = np.random.randn(self.M)
            ST = self.S0 * np.exp((self.r - 0.5 * self.sigma ** 2) * self.T + self.sigma * np.sqrt(self.T) * Z)
        elif self.method == 'binomial':
            dt = self.T / self.N
            u = np.exp(self.sigma * np.sqrt(dt))
            d = np.exp(-self.sigma * np.sqrt(dt))
            p = (np.exp(self.r * dt) - d) / (u - d)
            ST = np.zeros(self.M)
            for j in range(self.M):
                rand = np.random.binomial(1, p, self.N + 1)
                S = self.S0
                for i in range(1, self.N + 1):
                    S *= u if rand[i] == 1 else d
                ST[j] = S
        else:
            raise ValueError("method must be 'continuous' or 'binomial'")

        if self.option_type == 'call':
            payoff = np.maximum(ST - self.K, 0)
        elif self.option_type == 'put':
            payoff = np.maximum(self.K - ST, 0)
        else:
            raise ValueError("option_type must be 'call' or 'put'")

        return np.exp(-self.r * self.T) * np.mean(payoff)

    def _price_asian(self):
        if self.method == 'continuous':
            dt = self.T / self.N
            paths = np.zeros((self.M, self.N + 1))
            paths[:, 0] = self.S0
            for t in range(1, self.N + 1):
                Z = np.random.randn(self.M)
                paths[:, t] = paths[:, t - 1] * np.exp((self.r - 0.5 * self.sigma ** 2) * dt + self.sigma * np.sqrt(dt) * Z)
            averages = np.mean(paths, axis=1)

        elif self.method == 'binomial':
            dt = self.T / self.N
            u = np.exp(self.sigma * np.sqrt(dt))
            d = np.exp(-self.sigma * np.sqrt(dt))
            p = (np.exp(self.r * dt) - d) / (u - d)
            averages = np.zeros(self.M)

            for j in range(self.M):
                rand = np.random.binomial(1, p, self.N + 1)
                total = self.S0
                S = self.S0
                for i in range(1, self.N + 1):
                    S *= u if rand[i] == 1 else d
                    total += S
                averages[j] = total / (self.N + 1)

        else:
            raise ValueError("method must be 'continuous' or 'binomial'")

        if self.option_type == 'call':
            payoff = np.maximum(averages - self.K, 0)
        elif self.option_type == 'put':
            payoff = np.maximum(self.K - averages, 0)
        else:
            raise ValueError("option_type must be 'call' or 'put'")

        return np.exp(-self.r * self.T) * np.mean(payoff)

    def plot_convergence(self, M_values):
        """
        Plot the convergence of the Monte Carlo option price with increasing simulations.

        Parameters:
            M_values (list[int]): List of different simulation sizes to test
        """
        import matplotlib.pyplot as plt
        prices = []
        for M in M_values:
            self.M = M
            prices.append(self.price())

        plt.figure(figsize=(10, 6))
        plt.plot(M_values, prices, marker='o')
        plt.title(f'Monte Carlo Convergence for {self.option_style.capitalize()} Option Pricing')
        plt.xlabel('Number of Simulations (M)')
        plt.ylabel('Estimated Option Price')
        plt.grid(True)
        plt.show()