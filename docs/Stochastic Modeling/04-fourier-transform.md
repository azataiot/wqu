# Fourier-Based option pricing (BS)

We want to compute this integral from Carr-Madan’s formula:


$$
C_0 = \frac{e^{-\alpha k}}{\pi} \int_0^{\infty} e^{-i\nu k} \Psi(\nu)\, d\nu 
$$


This is the option price in the Fourier domain — but how do you compute an **integral from 0 to ∞** on a computer? 

## **Discrete Fourier Transform (DFT)**

**Trapezoidal Rule**

We **truncate the upper bound** (say at B) and discretize it into **N steps** using spacing $\eta = B/N$.  We approximate the integral as a **finite sum**: 


$$
\int_0^B e^{-i \nu k} \Psi(\nu) d\nu \approx \sum_{j=1}^{N} e^{-i \nu_j k} \Psi(\nu_j) \eta
$$


This is the **Discrete Fourier Transform (DFT)**:


$$
C_T(k) \approx \frac{e^{-\alpha k}}{\pi} \sum_{j=1}^{N} e^{-i \nu_j k} \Psi(\nu_j) \eta
$$


Where: $\nu_j = \eta(j - 1)$

## Fast Fourier Transform (FFT)

Now here’s the cool part: We can compute all these integrals **for a range of strikes** using a single **FFT** — super efficiently. 

This is possible because DFT is mathematically the same structure as FFT. 

We define:

- A grid of frequencies $\nu_j = \eta(j - 1)$
- A grid of strikes $k_u = -b + \lambda(u - 1)$ 

Then we can write the FFT-friendly version: 


$$
C_T(k_u) \approx \frac{e^{-\alpha k_u}}{\pi} \sum_{j=1}^{N} e^{-i \eta \lambda (j-1)(u-1)} \cdot x_j
$$


Where:

- $x_j = e^{ib\nu_j} \Psi(\nu_j) \eta$
- $\eta \lambda = \frac{2\pi}{N}$ ensures orthogonality for FFT

Now this sum is exactly what FFT is designed to compute!

## Simpson’s Rule (for better accuracy)

You can replace the trapezoidal weights with **Simpson’s Rule** for improved accuracy: 


$$
\int f(x) dx \approx \frac{\eta}{3} \left[f_0 + 4f_1 + 2f_2 + 4f_3 + \dots + f_N\right]
$$


This becomes:


$$
C_T(k_u) \approx \frac{e^{-\alpha k_u}}{\pi} \sum_{j=1}^N e^{-i \eta \lambda (j-1)(u-1)} x_j \cdot \left(\frac{\eta}{3}(3 + (-1)^j - \delta_{j-1})\right)
$$


> Instead of computing the Carr-Madan integral directly, we **discretize** it using the **trapezoidal or Simpson’s rule**, then convert it into a **DFT** — and accelerate the computation using the **FFT** algorithm. This gives us option prices **across a whole range of strikes** in one fast operation

- This version **works best for ITM/ATM** options (i.e. near-the-money)
- For OTM cases, tweaks are needed to stabilize integrability — this will come in future lessons.



## Fourier-based Option Pricing

## Carr-Madan FFT Pricing 

The Carr-Madan method gives us a way to price European call options using the FFT by converting the payoff into the Fourier domain.

We compute:


$$
\psi(u) = \frac{e^{-rT} \phi(u - (α + 1)i)}{α^2 + α - u^2 + i(2α + 1)u}
$$


Where:

- $\phi(u)$ is the **characteristic function** of $\log(S_T)$,
- α is a **damping factor** to make the call price integrable,
- $\psi(u)$ is then inverse Fourier transformed using FFT to get prices.

Then we recover the original prices:


$$
C(K) = \frac{e^{-αk}}{\pi} \text{Re}(\text{FFT})
$$

$$
C(K) = \frac{e^{-αk}}{π} \text{Re}(FFT of ψ)
$$
Note that By default, numpy.fft.fft() **returns an unscaled sum**, while the true integral approximates: 


$$
\int f(u)\, du \approx \eta \sum f(u_j)
$$


## Lewis vs. Carr-Madan

The **Lewis (2001)** and **Carr-Madan (1999)** methods are both **Fourier-based approaches for option pricing**, and while they aim for similar goals — computing option prices using the **characteristic function** — they differ in **how they handle the Fourier transform** and **what functions they transform**. 

Both methods:



- Use the **characteristic function** $\phi(u) = \mathbb{E}[e^{iu \log S_T}]$
- Price **European options** (typically calls) by moving into the **frequency domain**
- Use **Fourier transforms** to handle integrations more efficiently and stably
- Work especially well for **non-Black-Scholes models**, like Heston or Variance Gamma

###  **Core Difference: What Gets Transformed?**

|                   | **Carr-Madan (1999)**                      | **Lewis (2001)**                                             |
| ----------------- | ------------------------------------------ | ------------------------------------------------------------ |
| **Transforms**    | **Damped call price** e^{\alpha k} C(k)    | **Payoff function** (e^{k} - K)^+                            |
| **Key Parameter** | Introduces damping factor \alpha > 0       | No damping required if CF is integrable                      |
| **Approach**      | Fourier **transform of the price**         | Fourier **inversion formula** directly                       |
| **Use of FFT?**   | Yes, FFT is used in pricing                | Also compatible with FFT (though less common)                |
| **Works with**    | A wide class of Lévy models                | Same, but cleaner when CF is integrable                      |
| **Main paper**    | *Carr & Madan: Option valuation using FFT* | *Lewis: A Simple Option Formula for General Jump-Diffusions* |

### **Carr-Madan** 

- Defines a **modified call price**: $\tilde{C}(k) = e^{\alpha k} C(k)$ 

- Then takes its **Fourier transform**: $ \mathcal{F}[\tilde{C}(k)] = \int_{-\infty}^{\infty} e^{iuk} \tilde{C}(k) dk $
- Inversion (via FFT) is used to get back $C(k)$

Why damping? Because the raw call price function C(k) isn’t square-integrable (blows up at infinity), so Carr-Madan **multiplies by an exponential decay factor** to make the Fourier transform valid. 

### **Lewis**

- Works with a representation of the option price using the **inverse Fourier transform**: $C(K) = e^{-rT} \cdot \frac{1}{2\pi} \int_{\mathbb{R}} \frac{\phi(u - i)}{iu} e^{-iuk} du$ 
- **No damping required**, but assumes the characteristic function is integrable
- Mathematically neater, often more elegant (but sometimes numerically more delicate)


$$
C(K) = \frac{S_0 - \sqrt{S_0 K} e^{-rT}}{\pi} \int_0^\infty \text{Re} \left( \frac{e^{i u \ln(S_0/K)} \phi(u - 0.5i)}{u^2 + 0.25} \right) \, du
$$




## Coding

```python
# Black-Scholes Analytical 

from wqu.dp import BlackScholes

# Example: A call option

# S0 = 100
# K = 100
# T = 1
# r = 0.05
# sigma = 0.2

bs = BlackScholes(S0=100, K=100, T=1, r=0.05, sigma=0.2, option_type="call")

print("Option Price:", bs.price())
print("Delta:", bs.delta())
print("Gamma:", bs.gamma())
print("Vega:", bs.vega())
print("Theta:", bs.theta())
print("Rho:", bs.rho())
```

```
Option Price: 10.450583572185565
Delta: 0.6368306511756191
Gamma: 0.018762017345846895
Vega: 37.52403469169379
Theta: -6.414027546438197
Rho: 53.232481545376345
```



```python
from wqu.sm import BlackScholesFourier

S0 = 100
K = 100
T = 1
r = 0.05
sigma = 0.2

bs_fft = BlackScholesFourier(S0, K, T, r, sigma, method="carr-madan", option_type="call")
print("Carr-Madan FFT Call Price:", bs_fft.price())

bs_lewis = BlackScholesFourier(S0, K, T, r, sigma, method="lewis", option_type="call")
print("Lewis Method Call Price:", bs_lewis.price())
```

```
Carr-Madan FFT Call Price: 10.450583529672013
Lewis Method Call Price: 10.450583572184783
```