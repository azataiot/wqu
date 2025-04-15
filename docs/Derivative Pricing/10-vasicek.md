# Vasicek Interest Rate Model

## TL;DR 

The Vasicek model simulates interest rates that bounce around a long-term average.It uses a mean-reverting SDE where randomness and pull-back forces combine.We simulate it using a simple time-stepping method like we did with GBM.



**Vasicek** model is a mathematical model used to describe how interest rates change over time. 

Key idea: Mean Reversion - Interest rates don’t just wander aimlessly, they tend to go back toward some long-term average ( like gravity pulling them in).

 **The SDE (Stochastic Differential Equation):**


$$
dr_t = k(\theta - r_t)dt + \sigma dZ_t
$$


Where:

- $r_t$ interest rate at time t 
- $\theta$ long term average interest rate (mean level)
- $k$: speed of mean reversion (how fast we go back to $\theta$)
- $\sigma$: volatility (how much randomness per unit time)
- $dZ_t$: standard Brownian motion (random noise)



**Intuition Behind the formula** 

- If current rate $r_t < \theta$, the drift $k(\theta - r_t) > 0$ → rate increases
- If $r_t > \theta$, then $k(\theta - r_t) < 0$ → rate drops
- So the rate always tries to **pull back toward** $\theta$ over time



**How do we simulate it ?**

To simulate this using MonteCarlo:

1. Discretize time into steps of $\Delta t$
2. Use this recurrence formula: $r_{t+1} = r_t + k(\theta - r_t)\Delta t + \sigma \sqrt{\Delta t} \cdot \varepsilon$ 
3. where $\varepsilon \sim \mathcal{N}(0, 1)$

This is the **Euler discretization** of the Vasicek process. 

**Long-Run behavior**

- Long term mean = $\theta$ 
- Long term variance = $\frac{\sigma ^2}{2k}$

So we get interest rate paths that **wiggle**, but **hover around the mean** $\theta$. 

## Python

```python
from wqu.dp import Vasicek

# Instantiate model
vas = Vasicek(r0=0.03, k=0.15, theta=0.05, sigma=0.01, seed=42)

# Plot a single path
vas.plot(M=1, color='blue')

# Plot multiple paths
vas.plot(M=10, alpha=0.3)

# Compare how 'theta' affects the mean reversion level
vas.compare_parameters('theta', [0.03, 0.05, 0.07])
```

![img](./assets/1AA9FEA4-A4A3-4708-B6FA-60C61F9F9C63.png)

![vasicek-m10](./assets/vasicek-m10.png)

![vasicek-compare](./assets/vasicek-compare.png)

```python
from wqu.dp.vasicek import Vasicek
import matplotlib.pyplot as plt
import numpy as np

# Parameters
M = 100
N = 100
T = 1.0
r0 = 0.01875
K = 0.20
theta = 0.01
sigma = 0.012

# Time grid
t = np.linspace(0, T, N + 1)

# Create and simulate
vas = Vasicek(r0=r0, k=K, theta=theta, sigma=sigma, T=T, N=N, seed=42)
paths = vas.simulate(M)  # shape (M, N+1)

# Plot each path
plt.figure(figsize=(10, 5))
for j in range(M):
    plt.plot(t, paths[j])

plt.xlabel("Time $t$", fontsize=14)
plt.ylabel("$r(t)$", fontsize=14)
plt.title("Vasicek Paths", fontsize=14)
axes = plt.gca()
axes.set_xlim([0, T])
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
plt.tight_layout()
plt.show()
```

![vasicek-paths](./assets/vasicek-paths.png)