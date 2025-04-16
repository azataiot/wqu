# notebooks/sm/merton.py

import numpy as np
from scipy.integrate import quad
from scipy.optimize import brute, fmin
import pandas as pd
import matplotlib.pyplot as plt

# ------------------------------------------
# Merton Jump-Diffusion Model
# This class implements the Merton jump-diffusion model for option pricing.
# ------------------------------------------

class MertonFourier:
    def __init__(self, S0, K, T, r, sigma, lam, mu, delta, option_type="call"):
        self.S0 = S0
        self.K = K
        self.T = T
        self.r = r
        self.sigma = sigma
        self.lam = lam
        self.mu = mu
        self.delta = delta
        self.option_type = option_type.lower()

    def characteristic_function(self, u):
        omega = self.r - 0.5 * self.sigma ** 2 - self.lam * (np.exp(self.mu + 0.5 * self.delta ** 2) - 1)
        term = (
                1j * u * omega
                - 0.5 * self.sigma ** 2 * u ** 2
                + self.lam * (np.exp(1j * u * self.mu - 0.5 * self.delta ** 2 * u ** 2) - 1)
        )
        return np.exp(term * self.T)

    def integrand(self, u):
        v = u - 0.5j
        phi = self.characteristic_function(v)
        numerator = np.exp(1j * u * np.log(self.S0 / self.K)) * phi
        denominator = u**2 + 0.25
        return np.real(numerator / denominator)

    def price(self):
        integral, _ = quad(self.integrand, 0, 50, limit=250)
        value = self.S0 - np.exp(-self.r * self.T) * np.sqrt(self.S0 * self.K) / np.pi * integral
        if self.option_type == "call":
            return value
        else:
            return value - self.S0 + self.K * np.exp(-self.r * self.T)

    def plot(self, K_range=(50, 150), num=100):
        """
        Plot call (or put) option prices across a range of strike prices.

        Parameters:
        - K_range: Tuple of (min_strike, max_strike)
        - num: Number of strike prices to evaluate
        """
        original_K = self.K
        Ks = np.linspace(K_range[0], K_range[1], num)
        prices = []

        for K in Ks:
            self.K = K
            prices.append(self.price())

        self.K = original_K  # restore original strike

        plt.figure(figsize=(10, 5))
        plt.plot(Ks, prices, label=f"{self.option_type.capitalize()} Price")
        plt.axvline(original_K, linestyle="--", color="gray", alpha=0.6, label="Original K")
        plt.title(f"Merton Model ({self.option_type.capitalize()}) via Lewis Method")
        plt.xlabel("Strike Price (K)")
        plt.ylabel("Option Price")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()


class MertonCalibrator:
    def __init__(self, S0, options_df):
        self.S0 = S0
        self.options_df = options_df.copy()
        self.min_rmse = np.inf
        self.counter = 0

    def _error_function(self, params):
        sigma, lam, mu, delta = params

        if sigma < 0 or lam < 0 or delta < 0:
            return 1e6

        squared_errors = []
        for _, row in self.options_df.iterrows():
            model = MertonFourier(
                S0=self.S0,
                K=row["Strike"],
                T=row["T"],
                r=row["r"],
                sigma=sigma,
                lam=lam,
                mu=mu,
                delta=delta,
                option_type="call"
            )
            model_price = model.price()
            market_price = row["Call"]
            squared_errors.append((model_price - market_price) ** 2)

        rmse = np.sqrt(np.mean(squared_errors))
        self.min_rmse = min(self.min_rmse, rmse)

        if self.counter % 50 == 0:
            print(f"{self.counter:4d} | {np.array(params)} | {rmse:7.3f} | {self.min_rmse:7.3f}")
        self.counter += 1

        return rmse

    def calibrate(self):
        # Stage 1: Global search
        initial_guess = brute(
            self._error_function,
            ranges=(
                (0.075, 0.201, 0.025),   # sigma
                (0.10, 0.401, 0.1),      # lam
                (-0.5, 0.01, 0.1),       # mu
                (0.10, 0.301, 0.1),      # delta
            ),
            finish=None
        )

        # Stage 2: Local optimization
        optimal = fmin(
            self._error_function,
            x0=initial_guess,
            xtol=1e-4,
            ftol=1e-4,
            maxiter=600,
            maxfun=1000
        )

        return optimal


    def plot(self, optimal_params):
        """
        Plot model vs. market call prices across maturities using calibrated parameters.
        This method will generate subplots for each maturity.
        """
        sigma, lam, mu, delta = optimal_params
        options = self.options_df.copy()
        options["Model"] = 0.0

        for idx, row in options.iterrows():
            model = MertonFourier(
                S0=self.S0,
                K=row["Strike"],
                T=row["T"],
                r=row["r"],
                sigma=sigma,
                lam=lam,
                mu=mu,
                delta=delta,
                option_type="call"
            )
            options.loc[idx, "Model"] = model.price()

        # Plot grouped by maturity
        maturities = sorted(options["Maturity"].unique())
        options = options.set_index("Strike")

        # Create subplots
        fig, axes = plt.subplots(nrows=len(maturities), ncols=1, figsize=(10, 5 * len(maturities)))

        # If there's only one subplot, axes might not be an array, so we handle that
        if len(maturities) == 1:
            axes = [axes]

        for i, mat in enumerate(maturities):
            data = options[options["Maturity"] == mat]
            ax = axes[i]
            data[["Call", "Model"]].plot(style=["b-", "ro"], ax=ax, title=f"Maturity: {str(mat)[:10]}")
            ax.set_ylabel("Option Value")
            ax.set_xlabel("Strike Price")
            ax.grid(True)

        plt.tight_layout()
        plt.show()