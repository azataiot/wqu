# src/wqu/sm/heston.py

import numpy as np
from scipy.integrate import quad
from scipy.optimize import brute, fmin

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
        if self.method != "lewis":
            raise NotImplementedError("Only Lewis (2001) method is currently implemented.")


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

        integral, _ = quad(heston_integrand, 0, 100, limit=500, epsabs=1e-5)

        call_value = max(
            0,
            self.S0 - np.exp(-self.r * self.T) * np.sqrt(self.S0 * self.K) / np.pi * integral
        )

        return call_value

    def price(self):
        """
        Price a European call or put using the Lewis (2001) Fourier method.
        """
        call_price = self._price_lewis()

        if self.option_type == "call":
            return call_price
        else:
            return call_price - self.S0 + self.K * np.exp(-self.r * self.T)  # Put-call parity


class HestonCalibrator:
    def __init__(self, S0, options_df, ranges=None):
        self.S0 = S0
        self.options = options_df
        self.min_mse = float("inf")
        self.counter = 0
        self.ranges = ranges

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
                method="lewis",
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

    def calibrate(self, ranges=None):
        print(">>> Starting brute-force search...")
        if self.ranges is None:
            self.ranges=(
                (2.5, 10.6, 5),          # kappa
                (0.01, 0.041, 0.01),     # theta
                (0.01, 0.5, 0.05),       # sigma
                (-0.75, 0.01, 0.25),     # rho
                (0.01, 0.031, 0.01)      # v0
            )
        initial = brute(
            self.error_function,
            ranges=self.ranges,
            finish=None
        )
        print(">>> Refining with local search...")
        result = fmin(self.error_function, initial, xtol=1e-6, ftol=1e-6, maxiter=1000, maxfun=1500)
        return result

