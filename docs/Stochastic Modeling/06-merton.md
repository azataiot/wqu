# Merton Model

The **Merton Model** adds a simple twist to the classic Black-Scholes setup: → **It allows for jumps in the price** of an asset. Imagine a stock doesn’t always move smoothly — sometimes it jumps up or down due to surprise news or shocks. Merton modeled this using a **Poisson jump process** on top of the regular Brownian motion.

The asset price follows:


$$
dS_t = (r - r_J) S_t \, dt + \sigma S_t \, dZ_t + J_t S_t \, dN_t
$$


Where:



- $r$ is the risk-free rate.

- $\sigma$ is volatility.

- $Z_t$ is a Brownian motion.

- $N_t \sim \text{Poisson}(\lambda)$ — random jump times.

- $J_t$ is the jump size:

  $\log(1 + J_t) \sim \mathcal{N}(\log(1 + \mu_J) - \frac{\delta^2}{2}, \delta^2)$

- $r_J = \lambda \left(e^{\mu_J + \delta^2/2} - 1\right)$ is a correction to make the model risk-neutral.

##  Characteristic Function

We can price European options via **Lewis (2001)** using the characteristic function: 


$$
\phi(u, T) = \exp\left( \left(i u \omega - \frac{1}{2} u^2 \sigma^2 + \lambda (e^{i u \mu_J - \frac{1}{2} u^2 \delta^2} - 1) \right) T \right)
$$


Where: $\omega = r - \frac{1}{2} \sigma^2 - \lambda (e^{\mu_J + \delta^2/2} - 1)$

## Lewis Pricing Formula

Given $\phi(u, T)$, the price of a call option is: 


$$
C_0 = S_0 - \sqrt{S_0 K} e^{-rT} \cdot \frac{1}{\pi} \int_0^\infty \text{Re} \left[ e^{i u \log(S_0/K)} \cdot \phi(u - i/2, T) \right] \cdot \frac{1}{u^2 + \frac{1}{4}} du
$$
This is the **semi-analytical expression**.

## Code

```python

from wqu.sm import MertonFourier

S0 = 100
K = 100
T = 1
r = 0.05
sigma = 0.4
lam = 1
mu = -0.2
delta = 0.1

merton = MertonFourier(S0, K, T, r, sigma, lam, mu, delta)
print(f"Merton Call Option Price (Lewis method): {merton.price():.6f}")
```

```
Merton Call Option Price (Lewis method): 19.947854
```

```python
merton = MertonFourier(
    S0=100, K=100, T=1, r=0.05,
    sigma=0.4, lam=1, mu=-0.2, delta=0.1,
    option_type="call"
)

merton.plot(K_range=(60, 140))
```

![img](./assets/858326C2-7366-4C65-A476-CDC0EE4E19A3.png)

```python
import pandas as pd
from wqu.sm import MertonCalibrator

# Load the dataset
df = pd.read_csv("option_data_M2.csv")
df["Date"] = pd.to_datetime(df["Date"])
df["Maturity"] = pd.to_datetime(df["Maturity"])
df["T"] = (df["Maturity"] - df["Date"]).dt.days / 365
df["r"] = 0.005

# Set tolerance and filter ATM options
S0 = 3225.93
tol = 0.02
options = df[(abs(df["Strike"] - S0) / S0) < tol].copy()

# Run calibration
calibrator = MertonCalibrator(S0, options)
opt_params = calibrator.calibrate()
print("Optimal Parameters:", opt_params)
```

```
   0 | [ 0.075  0.1   -0.5    0.1  ] |  31.540 |  31.540
  50 | [ 0.075  0.3   -0.1    0.3  ] |  22.852 |  11.298
 100 | [ 0.1  0.2 -0.2  0.2] |  19.922 |   8.654
 150 | [ 0.125  0.1   -0.3    0.1  ] |  10.704 |   5.571
 200 | [ 0.125  0.4   -0.5    0.3  ] |  55.500 |   4.662
 250 | [0.15 0.2  0.   0.2 ] |   6.619 |   3.586
 300 | [ 0.175  0.1   -0.1    0.1  ] |  14.171 |   3.586
 350 | [ 0.175  0.4   -0.3    0.3  ] |  54.376 |   3.586
 400 | [ 0.2  0.3 -0.4  0.2] |  63.380 |   3.586
 450 | [ 0.14702168  0.19533978 -0.10189428  0.10218084] |   3.495 |   3.428
 500 | [ 0.14987758  0.11503181 -0.14398098  0.09850597] |   3.401 |   3.401
 550 | [ 0.15597729  0.01124105 -0.20255149  0.07785796] |   3.359 |   3.359
 600 | [ 0.15617567  0.00947711 -0.20364524  0.07721602] |   3.358 |   3.358
Optimization terminated successfully.
         Current function value: 3.358419
         Iterations: 107
         Function evaluations: 183
Optimal Parameters: [ 0.15619381  0.009201   -0.20380034  0.07715499]
```

```python
# Plot fit
calibrator.plot(opt_params)
```

![merton-fit-plot](./assets/merton-fit-plot.png)





















