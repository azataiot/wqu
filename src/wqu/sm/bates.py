# src/wqu/sm/bates.py

import numpy as np
from scipy.integrate import quad
from numpy.fft import fft


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