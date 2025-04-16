# src/wqu/sm/black_scholes.py

import numpy as np
from numpy.fft import fft
from scipy.integrate import quad
from scipy.stats import norm

# ------------------------------------------
# Black-Scholes Model with Fourier Transform
# This class implements the Carr-Madan and Lewis methods for option pricing.
# ------------------------------------------
class BlackScholesFourier:
    def __init__(self, S0, K, T, r, sigma, method="carr-madan", option_type="call", alpha=1.5):
        self.S0 = S0
        self.K = K
        self.T = T
        self.r = r
        self.sigma = sigma
        self.method = method.lower()
        self.option_type = option_type.lower()
        self.alpha = alpha
        self.integration_limit = 100

        if self.option_type not in ["call", "put"]:
            raise ValueError("Only call and put options are supported.")
        if self.method not in ["carr-madan", "lewis"]:
            raise ValueError("Method must be 'carr-madan' or 'lewis'.")

    def characteristic_function(self, v):
        return np.exp(
            (1j * v * (self.r - 0.5 * self.sigma ** 2) * self.T - 0.5 * self.sigma ** 2 * v ** 2 * self.T)
        )

    def _price_lewis(self):
        def integrand(u):
            v = u - 0.5j
            phi = self.characteristic_function(v)
            numerator = np.exp(1j * u * np.log(self.S0 / self.K)) * phi
            denominator = u**2 + 0.25
            return np.real(numerator / denominator)

        integral, _ = quad(integrand, 0, self.integration_limit)

        call_price = max(0, self.S0 - np.exp(-self.r * self.T) * (np.sqrt(self.S0 * self.K)) / np.pi * integral)

        return call_price if self.option_type == "call" else self._put_from_call(call_price)

    def _price_carr_madan(self):
        k = np.log(self.K / self.S0)
        x0 = np.log(self.S0 / self.S0)
        g = 1
        N = g * 4096
        eps = (g * 150)**-1
        eta = 2 * np.pi / (N * eps)
        b = 0.5 * N * eps - k
        u = np.arange(1, N + 1)
        vo = eta * (u - 1)

        if self.S0 >= 0.95 * self.K:
            alpha = self.alpha
            v = vo - (alpha + 1) * 1j
            damped_cf = np.exp(-self.r * self.T) * (
                    self.characteristic_function(v)
                    / (alpha**2 + alpha - vo**2 + 1j * (2 * alpha + 1) * vo)
            )
        else:
            alpha = 1.1  # Fixed for OTM options
            v_neg = vo - 1j * (alpha + 1)
            v_pos = vo + 1j * (alpha - 1)

            common_term_neg = 1j * (vo - 1j * alpha)
            common_term_pos = 1j * (vo + 1j * alpha)

            damped_cf_neg = np.exp(-self.r * self.T) * (
                    1 / (1 + common_term_neg)
                    - np.exp(self.r * self.T) / common_term_neg
                    - self.characteristic_function(v_neg) / (common_term_neg**2 - 1j * common_term_neg)
            )

            damped_cf_pos = np.exp(-self.r * self.T) * (
                    1 / (1 + common_term_pos)
                    - np.exp(self.r * self.T) / common_term_pos
                    - self.characteristic_function(v_pos) / (common_term_pos**2 - 1j * common_term_pos)
            )

        delt = np.zeros(N)
        delt[0] = 1
        j = np.arange(1, N + 1)
        SimpsonW = (3 + (-1) ** j - delt) / 3

        if self.S0 >= 0.95 * self.K:
            FFTFunc = np.exp(1j * b * vo) * damped_cf * eta * SimpsonW
            payoff = fft(FFTFunc).real
            CallValueM = np.exp(-alpha * k) / np.pi * payoff
        else:
            FFTFunc = (
                    np.exp(1j * b * vo) * (damped_cf_neg - damped_cf_pos) * 0.5 * eta * SimpsonW
            )
            payoff = fft(FFTFunc).real
            CallValueM = payoff / (np.sinh(alpha * k) * np.pi)

        pos = int((k + b) / eps)
        call_value = CallValueM[pos] * self.S0

        return call_value if self.option_type == "call" else self._put_from_call(call_value)

    def _put_from_call(self, call_price):
        """Use put-call parity to compute put price from call price"""
        return call_price - self.S0 + self.K * np.exp(-self.r * self.T)

    def price(self):
        if self.method == "lewis":
            return self._price_lewis()
        else:
            return self._price_carr_madan()