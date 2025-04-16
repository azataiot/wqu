# src/wqu/sm/bates.py

import numpy as np
from numpy.fft import fft
import matplotlib.pyplot as plt
from scipy.optimize import brute, fmin
from scipy.integrate import quad
from scipy.optimize import minimize

# ------------------------------------------
# Bates Model with Fourier Transform
# This class implements the Bates model for option pricing using the Fourier transform method.
# It combines the Heston model with Merton's jump-diffusion model.
# Approaches: Lewis (2001) and Carr-Madan (1999).
# ------------------------------------------
class BatesFourier:
    def __init__(
            self,
            S0, K, T, r, sigma,
            kappa, theta, v0, rho, lam, mu, delta,
            method="carr-madan", option_type="call", alpha=1.5
    ):
        self.S0 = S0
        self.K = K
        self.T = T
        self.r = r
        self.sigma = sigma
        self.kappa = kappa
        self.theta = theta
        self.v0 = v0
        self.rho = rho
        self.lam = lam
        self.mu = mu
        self.delta = delta
        self.alpha = alpha
        self.option_type = option_type.lower()
        self.method = method.lower()

        self.integration_limit = 100

        if self.option_type not in ["call", "put"]:
            raise ValueError("Only 'call' or 'put' option_type supported.")
        if self.method not in ["lewis", "carr-madan"]:
            raise ValueError("Method must be 'lewis' or 'carr-madan'.")

    def characteristic_function(self, u):
        """
        Combined Heston + Merton (Bates) characteristic function φ(u)
        """
        c1 = self.kappa * self.theta
        d = np.sqrt((self.rho * self.sigma * 1j * u - self.kappa)**2 + self.sigma**2 * (1j * u + u**2))
        g = (self.kappa - self.rho * self.sigma * 1j * u - d) / (self.kappa - self.rho * self.sigma * 1j * u + d)

        term1 = 1j * u * (self.r - self.lam * (np.exp(self.mu + 0.5 * self.delta**2) - 1)) * self.T
        term2 = c1 / self.sigma**2 * (
                (self.kappa - self.rho * self.sigma * 1j * u - d) * self.T
                - 2 * np.log((1 - g * np.exp(-d * self.T)) / (1 - g))
        )
        term3 = (self.v0 / self.sigma**2) * (self.kappa - self.rho * self.sigma * 1j * u - d) * (
                1 - np.exp(-d * self.T)
        ) / (1 - g * np.exp(-d * self.T))
        term4 = self.lam * self.T * (np.exp(1j * u * self.mu - 0.5 * self.delta**2 * u**2) - 1)

        return np.exp(term1 + term2 + term3 + term4)

    def _price_lewis(self):
        """
        Lewis (2001) approach: numerical integration
        """
        def integrand(u):
            v = u - 0.5j
            phi = self.characteristic_function(v)
            numerator = np.exp(1j * u * np.log(self.S0 / self.K)) * phi
            denominator = u**2 + 0.25
            return np.real(numerator / denominator)

        integral, _ = quad(integrand, 0, self.integration_limit)
        call_price = max(0, self.S0 - np.exp(-self.r * self.T) * np.sqrt(self.S0 * self.K) / np.pi * integral)

        return call_price if self.option_type == "call" else self._put_from_call(call_price)

    def _price_carr_madan(self):
        """
        Carr-Madan FFT approach
        """
        k = np.log(self.K / self.S0)
        N = 4096
        eps = 1 / 150
        eta = 2 * np.pi / (N * eps)
        b = 0.5 * N * eps - k
        u = np.arange(1, N + 1)
        vo = eta * (u - 1)

        alpha = self.alpha
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

        return call_price if self.option_type == "call" else self._put_from_call(call_price)

    def _put_from_call(self, call_price):
        return call_price - self.S0 + self.K * np.exp(-self.r * self.T)

    def price(self):
        if self.method == "lewis":
            return self._price_lewis()
        elif self.method == "carr-madan":
            return self._price_carr_madan()


# BatesCalibrator class
class BatesCalibratorLegacy:
    def __init__(self, S0, options_df, method="lewis"):
        self.S0 = S0
        self.options = options_df.copy()
        self.i = 0
        self.min_rmse = np.inf
        self.best_params = None
        self.method = method

    def _model_call_price(self, strike, T, r, sigma, lam, mu, delta, kappa, theta, v0, rho):
        """
        Computes model price using Lewis (2001) formulation for Bates (1996).
        """
        def integrand(u):
            # Bates (1996) characteristic function under Lewis integral
            c1 = kappa * theta
            d = np.sqrt((rho * sigma * 1j * u - kappa) ** 2 + sigma ** 2 * (1j * u + u ** 2))
            g = (kappa - rho * sigma * 1j * u - d) / (kappa - rho * sigma * 1j * u + d)

            drift = r - lam * (np.exp(mu + 0.5 * delta**2) - 1)
            phi = np.exp(
                1j * u * drift * T
                + (c1 / sigma ** 2) * ((kappa - rho * sigma * 1j * u - d) * T
                                       - 2 * np.log((1 - g * np.exp(-d * T)) / (1 - g)))
                + (v0 / sigma ** 2) * (kappa - rho * sigma * 1j * u - d)
                * (1 - np.exp(-d * T)) / (1 - g * np.exp(-d * T))
                + lam * T * (np.exp(1j * u * mu - 0.5 * delta ** 2 * u ** 2) - 1)
            )

            numerator = np.exp(1j * u * np.log(self.S0 / strike)) * phi
            return np.real(numerator / (u ** 2 + 0.25))

        integral, _ = quad(integrand, 0, 100)
        return max(0, self.S0 - np.exp(-r * T) * np.sqrt(self.S0 * strike) / np.pi * integral)

    def error_function(self, p):
        sigma, lam, mu, delta, kappa, theta, v0, rho = p

        if sigma < 0 or lam < 0 or delta < 0 or v0 < 0 or theta < 0 or not -1 <= rho <= 1:
            return 1e3
        if 2 * kappa * theta < sigma ** 2:
            return 1e3

        errors = []
        for _, opt in self.options.iterrows():
            model_price = self._model_call_price(
                strike=opt["Strike"], T=opt["T"], r=opt["r"],
                sigma=sigma, lam=lam, mu=mu, delta=delta,
                kappa=kappa, theta=theta, v0=v0, rho=rho
            )
            if opt["Type"] == "P":
                model_price = model_price - self.S0 + opt["Strike"] * np.exp(-opt["r"] * opt["T"])
            errors.append((model_price - opt["Price"]) ** 2)

        rmse = np.sqrt(np.mean(errors))
        if rmse < self.min_rmse:
            self.min_rmse = rmse
            self.best_params = p

        if self.i % 25 == 0:
            print(f"{self.i:4d} | RMSE: {rmse:8.4f} | Best: {self.min_rmse:8.4f} | Params: {np.round(p, 4)}")
        self.i += 1
        return rmse

    def calibrate(self):
        """
        Perform brute-force + local search calibration for Bates model
        """
        self.i = 0
        self.min_rmse = np.inf

        p0 = brute(
            self.error_function,
            ranges=(
                (0.10, 0.30, 0.05),   # sigma
                (0.1, 0.5, 0.1),      # lambda
                (-0.4, 0.0, 0.1),     # mu
                (0.05, 0.2, 0.05),    # delta
                (1.0, 3.0, 0.5),      # kappa
                (0.01, 0.05, 0.01),   # theta
                (0.01, 0.05, 0.01),   # v0
                (-0.9, 0.1, 0.2),     # rho
            ),
            finish=None
        )

        result = fmin(self.error_function, p0, xtol=1e-5, ftol=1e-5, maxiter=500, maxfun=800)
        return result

    def calibrate_auto(self):
        bounds = [
            (0.01, 1.0),     # sigma
            (0.01, 1.0),     # lambda
            (-1.0, 0.5),     # mu
            (0.01, 1.0),     # delta
            (0.5, 10.0),     # kappa
            (0.005, 0.5),    # theta
            (0.005, 0.5),    # v0
            (-0.999, 0.999)  # rho
        ]
        initial_guess = np.array([0.2, 0.2, -0.2, 0.1, 2.0, 0.02, 0.02, -0.3])

        result = minimize(
            self.error_function,
            initial_guess,
            method='L-BFGS-B',
            bounds=bounds,
            options={'maxiter': 1000, 'disp': True}
        )
        return result.x


    def plot_legacy(self, calibrated_params):
        """
        Plot market vs model prices using calibrated parameters
        """
        sigma, lam, mu, delta, kappa, theta, v0, rho = calibrated_params

        # Compute model prices using internal method
        self.options["Model"] = self.options.apply(
            lambda row: self._model_call_price(
                strike=row["Strike"], T=row["T"], r=row["r"],
                sigma=sigma, lam=lam, mu=mu, delta=delta,
                kappa=kappa, theta=theta, v0=v0, rho=rho
            ),
            axis=1
        )

        # Plot grouped by maturity
        maturities = sorted(self.options["Maturity"].unique())
        n = len(maturities)

        fig, axes = plt.subplots(1, n, figsize=(6 * n, 5), sharey=True)

        if n == 1:
            axes = [axes]

        for ax, mat in zip(axes, maturities):
            subset = self.options[self.options["Maturity"] == mat].set_index("Strike")
            subset[["Call", "Model"]].plot(ax=ax, style=["b-", "ro"], title=f"Maturity: {mat.date()}")
            ax.set_ylabel("Option Price")
            ax.grid(True)

        plt.suptitle("Market vs Bates Model Prices", fontsize=14)
        plt.tight_layout()
        plt.show()

    def plot(self, calibrated_params):
        sigma, lam, mu, delta, kappa, theta, v0, rho = calibrated_params
        model_prices = []

        for _, opt in self.options.iterrows():
            model_price = self._model_call_price(
                strike=opt["Strike"], T=opt["T"], r=opt["r"],
                sigma=sigma, lam=lam, mu=mu, delta=delta,
                kappa=kappa, theta=theta, v0=v0, rho=rho
            )
            if opt["Type"] == "P":
                model_price = model_price - self.S0 + opt["Strike"] * np.exp(-opt["r"] * opt["T"])
            model_prices.append(model_price)

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
        plt.title("Bates Model vs Market Prices (Lewis)")
        plt.legend()
        plt.grid()
        plt.tight_layout()
        plt.show()



class BatesCalibrator:
    def __init__(self, S0, options_df, method="lewis"):
        self.S0 = S0
        self.options = options_df.copy()
        self.method = method.lower()
        self.i = 0
        self.min_rmse = np.inf
        self.best_params = None

    def _model_call_price(self, strike, T, r, sigma, lam, mu, delta, kappa, theta, v0, rho):
        model = BatesFourier(
            S0=self.S0,
            K=strike,
            T=T,
            r=r,
            sigma=sigma,
            kappa=kappa,
            theta=theta,
            v0=v0,
            rho=rho,
            lam=lam,
            mu=mu,
            delta=delta,
            method=self.method,
            option_type="call"
        )
        return model.price()

    def error_function(self, p):
        sigma, lam, mu, delta, kappa, theta, v0, rho = p

        # Constraints
        if sigma < 0 or lam < 0 or delta < 0 or v0 < 0 or theta < 0 or not -1 <= rho <= 1:
            return 1e3
        if 2 * kappa * theta < sigma**2:
            return 1e3

        errors = []
        for _, opt in self.options.iterrows():
            model_price = self._model_call_price(
                strike=opt["Strike"], T=opt["T"], r=opt["r"],
                sigma=sigma, lam=lam, mu=mu, delta=delta,
                kappa=kappa, theta=theta, v0=v0, rho=rho
            )

            # Adjust put prices via put-call parity
            if opt["Type"] == "P":
                model_price = model_price - self.S0 + opt["Strike"] * np.exp(-opt["r"] * opt["T"])

            errors.append((model_price - opt["Price"])**2)

        rmse = np.sqrt(np.mean(errors))
        if rmse < self.min_rmse:
            self.min_rmse = rmse
            self.best_params = p

        if self.i % 25 == 0:
            print(f"{self.i:4d} | RMSE: {rmse:8.4f} | Best: {self.min_rmse:8.4f} | Params: {np.round(p, 4)}")
        self.i += 1
        return rmse

    def calibrate(self):
        self.i = 0
        self.min_rmse = np.inf

        p0 = brute(
            self.error_function,
            ranges=(
                (0.10, 0.30, 0.05),   # sigma
                (0.1, 0.5, 0.1),      # lambda
                (-0.4, 0.0, 0.1),     # mu
                (0.05, 0.2, 0.05),    # delta
                (1.0, 3.0, 0.5),      # kappa
                (0.01, 0.05, 0.01),   # theta
                (0.01, 0.05, 0.01),   # v0
                (-0.9, 0.1, 0.2),     # rho
            ),
            finish=None
        )

        result = fmin(self.error_function, p0, xtol=1e-5, ftol=1e-5, maxiter=500, maxfun=800)
        return result

    def calibrate_auto(self):
        bounds = [
            (0.01, 1.0),     # sigma
            (0.01, 1.0),     # lambda
            (-1.0, 0.5),     # mu
            (0.01, 1.0),     # delta
            (0.5, 10.0),     # kappa
            (0.005, 0.5),    # theta
            (0.005, 0.5),    # v0
            (-0.999, 0.999)  # rho
        ]
        initial_guess = np.array([0.2, 0.2, -0.2, 0.1, 2.0, 0.02, 0.02, -0.3])

        result = minimize(
            self.error_function,
            initial_guess,
            method='L-BFGS-B',
            bounds=bounds,
            options={'maxiter': 1000, 'disp': True}
        )
        return result.x

    def plot(self, calibrated_params):
        sigma, lam, mu, delta, kappa, theta, v0, rho = calibrated_params
        model_prices = []

        for _, opt in self.options.iterrows():
            model_price = self._model_call_price(
                strike=opt["Strike"], T=opt["T"], r=opt["r"],
                sigma=sigma, lam=lam, mu=mu, delta=delta,
                kappa=kappa, theta=theta, v0=v0, rho=rho
            )
            if opt["Type"] == "P":
                model_price = model_price - self.S0 + opt["Strike"] * np.exp(-opt["r"] * opt["T"])
            model_prices.append(model_price)

        self.options["ModelPrice"] = model_prices
        df = self.options.copy()
        df.set_index("Strike", inplace=True)

        plt.figure(figsize=(10, 6))
        calls = df[df["Type"] == "C"]
        puts = df[df["Type"] == "P"]

        plt.plot(calls.index, calls["Price"], 'bo', label="Market Call Price")
        plt.plot(calls.index, calls["ModelPrice"], 'b--', label="Model Call Price")

        plt.plot(puts.index, puts["Price"], 'ro', label="Market Put Price")
        plt.plot(puts.index, puts["ModelPrice"], 'r--', label="Model Put Price")

        plt.xlabel("Strike")
        plt.ylabel("Option Price")
        plt.title(f"Bates Model vs Market Prices ({self.method.capitalize()})")
        plt.legend()
        plt.grid()
        plt.tight_layout()
        plt.show()