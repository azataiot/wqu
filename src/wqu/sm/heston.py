# src/wqu/sm/heston.py

import numpy as np
from scipy.integrate import quad
from scipy.optimize import brute, fmin
from scipy.optimize import brute, minimize
from numpy.fft import fft

# ------------------------------------------
# Heston Model with Fourier Transform
# This class implements the Heston model for option pricing using the Fourier transform method.
# It is based on the work of Lewis (2001).
# ------------------------------------------
class HestonFourier:
    def __init__(self, S0, K, T, r,
                 v0, theta, kappa, sigma, rho,
                 method="lewis", option_type="call", integration_limit=100):
        """
        Initialize the Heston Fourier pricer.

        Parameters:
        - S0: initial stock price
        - K: strike price
        - T: time to maturity
        - r: risk-free rate
        - v0: initial variance
        - theta: long-term variance
        - kappa: mean reversion speed
        - sigma: volatility of variance (vol of vol)
        - rho: correlation between asset and variance
        - method: only 'lewis' supported for now
        - option_type: 'call' or 'put'
        - integration_limit: upper bound for numerical integration
        """
        self.S0 = S0
        self.K = K
        self.T = T
        self.r = r
        self.v0 = v0
        self.theta = theta
        self.kappa = kappa
        self.sigma = sigma
        self.rho = rho
        self.method = method.lower()
        self.option_type = option_type.lower()
        self.integration_limit = integration_limit

        if self.option_type not in ["call", "put"]:
            raise ValueError("Only 'call' and 'put' options are supported.")
        if self.method not in ["lewis", "carr-madan"]:
            raise ValueError("Method must be 'lewis' or 'carr-madan'.")


    def characteristic_function(self, u):
        """
        Characteristic function of log(S_T) under the Heston (1993) model
        using Lewis (2001) formulation.
        """
        c1 = self.kappa * self.theta
        c2 = -np.sqrt(
            (self.rho * self.sigma * 1j * u - self.kappa) ** 2
            - self.sigma ** 2 * (-1j * u - u ** 2)
        )
        c3 = (self.kappa - self.rho * self.sigma * 1j * u + c2) / (
                self.kappa - self.rho * self.sigma * 1j * u - c2
        )

        H1 = (
                1j * u * self.r * self.T
                + (c1 / self.sigma ** 2)
                * (
                        (self.kappa - self.rho * self.sigma * 1j * u + c2) * self.T
                        - 2 * np.log((1 - c3 * np.exp(c2 * self.T)) / (1 - c3))
                )
        )

        H2 = (
                (self.kappa - self.rho * self.sigma * 1j * u + c2)
                / self.sigma ** 2
                * ((1 - np.exp(c2 * self.T)) / (1 - c3 * np.exp(c2 * self.T)))
        )

        return np.exp(H1 + H2 * self.v0)

    def _price_lewis(self):
        def heston_integrand(u):
            # Matches H93_int_func from textbook
            v = u - 1j * 0.5
            phi = self.characteristic_function(v)
            numerator = np.exp(1j * u * np.log(self.S0 / self.K)) * phi
            denominator = u**2 + 0.25
            return np.real(numerator / denominator)

        integral, _ = quad(heston_integrand, 0, 150, limit=1000, epsabs=1e-4, epsrel=1e-4)

        call_value = max(
            0,
            self.S0 - np.exp(-self.r * self.T) * np.sqrt(self.S0 * self.K) / np.pi * integral
        )

        return call_value

    def _price_carr_madan(self):
        k = np.log(self.K / self.S0)
        N = 4096
        eps = 1 / 150
        eta = 2 * np.pi / (N * eps)
        b = 0.5 * N * eps - k
        u = np.arange(1, N + 1)
        vo = eta * (u - 1)

        alpha = 1.5  # damping factor
        v = vo - (alpha + 1) * 1j

        cf_vals = self.characteristic_function(v)
        psi = np.exp(-self.r * self.T) * cf_vals / (alpha**2 + alpha - vo**2 + 1j * (2 * alpha + 1) * vo)

        delta = np.zeros(N)
        delta[0] = 1
        j = np.arange(1, N + 1)
        SimpsonW = (3 + (-1)**j - delta) / 3

        integrand = np.exp(1j * b * vo) * psi * eta * SimpsonW
        payoff = np.real(fft(integrand))
        CallValueM = np.exp(-alpha * k) / np.pi * payoff
        idx = int((k + b) / eps)
        call_price = self.S0 * CallValueM[idx]

        return call_price if self.option_type == "call" else call_price - self.S0 + self.K * np.exp(-self.r * self.T)


    def price(self):
        if self.method == "lewis":
            call_price = self._price_lewis()
        elif self.method == "carr-madan":
            call_price = self._price_carr_madan()
        else:
            raise ValueError("Unsupported pricing method")

        if self.option_type == "call":
            return call_price
        else:
            # Put-call parity
            return call_price - self.S0 + self.K * np.exp(-self.r * self.T)


class HestonCalibrator:
    def __init__(self, S0, options_df, ranges=None, method="lewis"):
        self.S0 = S0
        self.options = options_df
        self.min_mse = float("inf")
        self.counter = 0
        self.ranges = ranges
        self.method = method

    def error_function(self, params):
        kappa, theta, sigma, rho, v0 = params

        # Constraints
        if kappa < 0 or theta < 0.005 or sigma < 0 or not -1 <= rho <= 1:
            return 1e5
        if 2 * kappa * theta < sigma**2:
            return 1e5

        errors = []
        for _, opt in self.options.iterrows():
            # dynamically handle call and put types
            model = HestonFourier(
                S0=self.S0,
                K=opt["Strike"],
                T=opt["T"],
                r=opt["r"],
                v0=v0,
                theta=theta,
                kappa=kappa,
                sigma=sigma,
                rho=rho,
                method=self.method,
                option_type="call"  # Always price as call first
            )
            call_price = model.price()

            # Adjust via put-call parity if type is Put
            if opt["Type"] == "P":
                model_price = call_price - self.S0 + opt["Strike"] * np.exp(-opt["r"] * opt["T"])
            else:
                model_price = call_price
            # Compute squared errors
            errors.append((model_price - opt["Price"])**2)

        mse = np.mean(errors)
        self.min_mse = min(self.min_mse, mse)
        if self.counter % 25 == 0:
            print(f"{self.counter:4d} | {params} | MSE: {mse:.6f} | Min MSE: {self.min_mse:.6f}")
        self.counter += 1
        return mse

    def calibrate(self):
        print(">>> Starting brute-force search...")
        ranges = self.ranges
        if ranges is None:
            ranges = (
                (2.5, 10.6, 5),          # kappa
                (0.01, 0.041, 0.01),     # theta
                (0.01, 0.5, 0.05),       # sigma
                (-0.75, 0.01, 0.25),     # rho
                (0.01, 0.031, 0.01)      # v0
            )
        initial = brute(
            self.error_function,
            ranges=ranges,
            finish=None
        )
        print(">>> Refining with local search...")
        result = fmin(
            self.error_function,
            initial,
            xtol=1e-6,
            ftol=1e-6,
            maxiter=1000,
            maxfun=1500
        )
        return result


    def calibrate_auto(self):
        bounds = [(0.1, 15), (0.005, 1), (0.01, 1), (-0.999, 0.999), (0.005, 1)]
        initial_guess = [2.5, 0.05, 0.2, -0.5, 0.03]

        result = minimize(
            self.error_function, initial_guess, method='L-BFGS-B',
            bounds=bounds, options={'maxiter': 1000, 'disp': True}
        )
        return result.x

    def plot(self, calibrated_params):
        kappa, theta, sigma, rho, v0 = calibrated_params
        model_prices = []

        for _, opt in self.options.iterrows():
            model = HestonFourier(
                S0=self.S0,
                K=opt["Strike"],
                T=opt["T"],
                r=opt["r"],
                v0=v0,
                theta=theta,
                kappa=kappa,
                sigma=sigma,
                rho=rho,
                option_type="call",
                method=self.method
            )
            price = model.price()
            if opt["Type"] == "P":
                price = price - self.S0 + opt["Strike"] * np.exp(-opt["r"] * opt["T"])
            model_prices.append(price)

        self.options["ModelPrice"] = model_prices
        df = self.options.copy()
        df.set_index("Strike", inplace=True)

        import matplotlib.pyplot as plt
        plt.figure(figsize=(10, 6))
        calls = df[df["Type"] == "C"]
        puts = df[df["Type"] == "P"]

        plt.plot(calls.index, calls["Price"], 'bo', label="Market Call Price")
        plt.plot(calls.index, calls["ModelPrice"], 'b--', label="Model Call Price")

        plt.plot(puts.index, puts["Price"], 'ro', label="Market Put Price")
        plt.plot(puts.index, puts["ModelPrice"], 'r--', label="Model Put Price")

        plt.xlabel("Strike")
        plt.ylabel("Option Price")
        plt.title(f"Heston Model vs Market Prices {self.method.capitalize()}")
        plt.legend()
        plt.grid()
        plt.show()