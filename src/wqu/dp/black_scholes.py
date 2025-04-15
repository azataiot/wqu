# src/wqu/dp/black_scholes.py
import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt

class BlackScholes:
    def __init__(self, S0:float, K:float, T:float, r:float, sigma:float, option_type:str = "call"):
        """
        Initialize the Black-Scholes model parameters.

        Parameters:
        S0 (float): Current stock price
        K (float): Option strike price
        T (float): Time to expiration in years
        r (float): Risk-free annual rate (e.g., 0.05 for 5%)
        sigma (float): Volatility of the underlying asset
        option_type (str): Type of option ('call' or 'put')
        """
        self.S0 = S0
        self.K = K
        self.T = T
        self.r = r
        self.sigma = sigma
        self.option_type = option_type.lower()

        if self.option_type not in ["call", "put"]:
            raise ValueError("option_type must be one of 'call' or 'put'")

        # Precompute d1 and d2 for efficiency
        self._d1 = (self._compute_d1())
        self._d2 = (self._compute_d2())

    def _compute_d1(self) -> float:
        return (np.log(self.S0 / self.K) + (self.r + 0.5 * self.sigma**2) * self.T) / (self.sigma * np.sqrt(self.T))

    def _compute_d2(self) -> float:
        return self._d1 - self.sigma * np.sqrt(self.T)

    def price(self) -> float:
        """
        Compute the Black-Scholes price for the option.
        """
        d1, d2 = self._d1, self._d2
        if self.option_type == "call":
            return self.S0 * norm.cdf(d1) - self.K * np.exp(-self.r * self.T) * norm.cdf(d2)
        else:
            return self.K * np.exp(-self.r * self.T) * norm.cdf(-d2) - self.S0 * norm.cdf(-d1)

    def delta(self) -> float:
        """
        Compute Delta of the option.
        """
        d1 = self._d1
        if self.option_type == "call":
            return norm.cdf(d1)
        else:
            return norm.cdf(d1) - 1

    def gamma(self) -> float:
        """
        Compute Gamma of the option.
        """
        d1 = self._d1
        return norm.pdf(d1) / (self.S0 * self.sigma * np.sqrt(self.T))

    def vega(self) -> float:
        """
        Compute Vega of the option (sensitivity to volatility).
        """
        d1 = self._d1
        return self.S0 * norm.pdf(d1) * np.sqrt(self.T)

    def theta(self) -> float:
        """
        Compute Theta of the option (sensitivity to time).
        """
        d1, d2 = self._d1, self._d2
        term1 = - (self.S0 * norm.pdf(d1) * self.sigma) / (2 * np.sqrt(self.T))
        if self.option_type == "call":
            term2 = - self.r * self.K * np.exp(-self.r * self.T) * norm.cdf(d2)
            return term1 + term2
        else:
            term2 = self.r * self.K * np.exp(-self.r * self.T) * norm.cdf(-d2)
            return term1 + term2

    def rho(self) -> float:
        """
        Compute Rho of the option (sensitivity to interest rate).
        """
        d2 = self._d2
        if self.option_type == "call":
            return self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(d2)
        else:
            return -self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(-d2)

    def to_dict(self) -> dict:
        """
        Return a dictionary with option price and all Greeks.
        """
        return {
            "price": self.price(),
            "delta": self.delta(),
            "gamma": self.gamma(),
            "vega": self.vega(),
            "theta": self.theta(),
            "rho": self.rho()
        }

    def plot_greeks(self, S_range: tuple = (50, 150), num: int = 100):
        """
        Plot Greeks over a range of stock prices.

        Parameters:
        - S_range: Tuple (min, max) for stock price range
        - num: Number of price points
        """
        S_vals = np.linspace(*S_range, num)
        delta_vals, gamma_vals, vega_vals, theta_vals, rho_vals = [], [], [], [], []

        for S in S_vals:
            tmp = BlackScholes(S, self.K, self.T, self.r, self.sigma, self.option_type)
            delta_vals.append(tmp.delta())
            gamma_vals.append(tmp.gamma())
            vega_vals.append(tmp.vega())
            theta_vals.append(tmp.theta())
            rho_vals.append(tmp.rho())

        plt.figure(figsize=(12, 8))
        plt.plot(S_vals, delta_vals, label="Delta")
        plt.plot(S_vals, gamma_vals, label="Gamma")
        plt.plot(S_vals, vega_vals, label="Vega")
        plt.plot(S_vals, theta_vals, label="Theta")
        plt.plot(S_vals, rho_vals, label="Rho")
        plt.title(f"Greeks for {self.option_type.capitalize()} Option")
        plt.xlabel("Stock Price (S)")
        plt.ylabel("Greek Value")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()