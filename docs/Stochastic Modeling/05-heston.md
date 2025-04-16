# Fourier Methods for Heston Model

We are extending our Fourier-based pricing methods — like we did in Black-Scholes — to a more realistic model of financial markets called the **Heston Model**, which allows **volatility to be stochastic (i.e., random)**. 

## The Pricing Equation (Lewis 2001)

Under the Heston model, the **European call option price** is given by this integral (Lewis-style): 


$$
C_0 = S_0 - \frac{\sqrt{S_0 K} \, e^{-rT}}{\pi} \int_0^{\infty} \text{Re} \left[ \frac{e^{i u \log(S_0/K)} \, \phi(u - i/2)}{u^2 + 1/4} \right] du
$$


This formula has three key parts:



- $\phi(u)$: **Characteristic function** of the log-price under the Heston model.
- $\text{Re}[\cdot]$: Take only the real part.
- $\int_0^\infty \cdots du$: Numerically integrated.



The Heston model assumes:



- The **asset price** $S_t$ and its **volatility** $\nu_t$ both follow stochastic (random) processes.
- The **volatility itself is mean-reverting** — it wants to go back to some long-term average.



It adds realism, especially for modeling:

- Volatility smiles/skews
- Market shocks
- Fat tails in return distribution

## Characteristic Function in Heston (φH(u, T))

This is the most technical part: deriving the **characteristic function** under Heston dynamics. It’s a complex exponential with parts: 


$$
\phi_H(u, T) = \exp \left( H_1(u, T) + H_2(u, T) \cdot \nu_0 \right)
$$


Where:



- $H_1(u, T)$ and $H_2(u, T)$ are expressions derived from solving the SDEs.

- They depend on:

  

  - $\kappa_\nu$: speed of mean reversion
  - $\theta_\nu$: long-term mean of variance
  - $\sigma_\nu$: volatility of variance (vol of vol)
  - $\rho$: correlation between asset returns and variance
  - $\nu_0$: initial variance level

> “How does the distribution of log-prices change when both the price and its volatility are random?”

## How to Price an Option with It?

Same idea as Black-Scholes Lewis-style pricing:



1. Plug $φH(u − i/2)$ into the integral formula.
2. Use a **quadrature method** (like Simpson’s Rule or scipy.integrate.quad) to numerically integrate it.
3. Done — you get a call price.



## Calibration of Heston Model

Since the model has **5 unknown parameters**:  $\kappa_\nu, \theta_\nu, \sigma_\nu, \rho, \nu_0$

We calibrate it like this:

1. Define a **loss function** = squared difference between market prices and model prices.

2. Use optimization (scipy.optimize) to minimize that loss.

3. Often we **do it in 2 stages**:

   

   - Coarse grid search (brute force)
   - Fine optimization (e.g., L-BFGS-B)

   

## Coding

```python
import pandas as pd
from datetime import datetime
from wqu.sm import HestonCalibrator

# Load from CSV
data_path = "option_data.csv"
data = pd.read_csv(data_path)

# Set index level and tolerance
S0 = 3225.93
tol = 0.02

# Filter near-the-money European call options
options = data[(abs(data["Strike"] - S0) / S0) < tol].copy()
options["Date"] = pd.to_datetime(options["Date"])
options["Maturity"] = pd.to_datetime(options["Maturity"])
options["T"] = (options["Maturity"] - options["Date"]).dt.days / 365
options["r"] = 0.02  # constant short rate

# Initialize and run calibration
calibrator = HestonCalibrator(S0=S0, options_df=options)
optimal_params = calibrator.calibrate()

# Display results
print("Optimal Parameters:", optimal_params)
```

```
>>> Starting brute-force search...
   0 | [ 2.5   0.01  0.05 -0.75  0.01] | MSE: 820.892168 | Min MSE: 820.892168
  25 | [ 2.5   0.02  0.05 -0.75  0.02] | MSE: 23.863624 | Min MSE: 21.567743
  50 | [ 2.5   0.02  0.25 -0.75  0.03] | MSE: 89.654952 | Min MSE: 21.567743
  75 | [ 2.5   0.03  0.15 -0.5   0.01] | MSE: 193.282610 | Min MSE: 21.567743
 100 | [ 2.5   0.04  0.05 -0.5   0.02] | MSE: 176.339739 | Min MSE: 21.567743
 125 | [ 2.5   0.04  0.25 -0.5   0.03] | MSE: 486.964581 | Min MSE: 21.567743
 150 | [ 7.5   0.01  0.15 -0.25  0.01] | MSE: 840.337090 | Min MSE: 21.567743
 175 | [ 7.5   0.02  0.05 -0.25  0.02] | MSE: 24.810371 | Min MSE: 21.567743
 200 | [ 7.5   0.02  0.25 -0.25  0.03] | MSE: 24.834228 | Min MSE: 21.567743
 225 | [7.5  0.03 0.15 0.   0.01] | MSE: 110.936421 | Min MSE: 21.567743
 250 | [7.5  0.04 0.05 0.   0.02] | MSE: 540.182792 | Min MSE: 21.567743
 275 | [7.5  0.04 0.25 0.   0.03] | MSE: 783.221740 | Min MSE: 21.567743
>>> Refining with local search...
 300 | [ 2.61379559  0.00992657  0.15610448 -0.76361614  0.02778356] | MSE: 8.045766 | Min MSE: 7.795453
 325 | [ 1.9152359   0.01257942  0.16036675 -0.91693167  0.0248233 ] | MSE: 6.300806 | Min MSE: 6.146318
 350 | [ 2.04831069  0.01215428  0.15832201 -0.89057611  0.02532865] | MSE: 6.150503 | Min MSE: 6.144623
 375 | [ 2.0376908   0.01207312  0.16816435 -0.86785979  0.02553311] | MSE: 6.097042 | Min MSE: 6.075189
 400 | [ 1.97316132  0.01247835  0.2032535  -0.83478704  0.0254568 ] | MSE: 6.001525 | Min MSE: 5.996115
 425 | [ 2.07617861  0.01268556  0.21375606 -0.83213139  0.02575716] | MSE: 5.947748 | Min MSE: 5.947748
 450 | [ 2.66904762  0.0147503   0.22891593 -0.87575667  0.02607257] | MSE: 5.683904 | Min MSE: 5.683904
 475 | [ 3.14901508  0.01554998  0.22701309 -0.86349685  0.02615741] | MSE: 5.357630 | Min MSE: 5.357630
 500 | [ 3.75301757  0.0179153   0.33579328 -0.72953664  0.02611118] | MSE: 4.602526 | Min MSE: 4.498631
 525 | [ 5.15416061  0.01857864  0.40457683 -0.45664742  0.0270172 ] | MSE: 3.894461 | Min MSE: 3.824773
 550 | [ 5.14078039  0.01861684  0.42859861 -0.43432012  0.02728158] | MSE: 3.769001 | Min MSE: 3.749195
 575 | [ 5.0507416   0.01868091  0.43385652 -0.44775932  0.02732562] | MSE: 3.718624 | Min MSE: 3.716546
 600 | [ 5.05235394  0.01871275  0.43473462 -0.44693948  0.02730235] | MSE: 3.716004 | Min MSE: 3.715792
 625 | [ 5.05371685  0.01872767  0.43504931 -0.44691718  0.0272971 ] | MSE: 3.715524 | Min MSE: 3.715392
 650 | [ 5.04446488  0.01872907  0.43469053 -0.44848558  0.02728228] | MSE: 3.715380 | Min MSE: 3.715376
 675 | [ 5.04382644  0.0187266   0.43463479 -0.44869357  0.02728557] | MSE: 3.715374 | Min MSE: 3.715374
 700 | [ 5.04426287  0.01872709  0.4346593  -0.44857764  0.02728496] | MSE: 3.715373 | Min MSE: 3.715373
 725 | [ 5.04476043  0.01872427  0.43464808 -0.44841756  0.02728689] | MSE: 3.715371 | Min MSE: 3.715371
 750 | [ 5.04505376  0.01872602  0.43468094 -0.44837446  0.02728584] | MSE: 3.715370 | Min MSE: 3.715370
 775 | [ 5.04707738  0.01872566  0.434764   -0.44801571  0.02728898] | MSE: 3.715367 | Min MSE: 3.715367
 800 | [ 5.04731712  0.01872561  0.43477373 -0.44796137  0.02728913] | MSE: 3.715367 | Min MSE: 3.715367
 825 | [ 5.04735223  0.01872569  0.43477611 -0.44795766  0.02728916] | MSE: 3.715367 | Min MSE: 3.715367
 850 | [ 5.04735429  0.0187257   0.43477637 -0.44795746  0.02728915] | MSE: 3.715367 | Min MSE: 3.715367
 875 | [ 5.04735384  0.01872571  0.43477645 -0.44795738  0.02728914] | MSE: 3.715367 | Min MSE: 3.715367
 900 | [ 5.04736306  0.01872573  0.43477709 -0.44795509  0.02728912] | MSE: 3.715367 | Min MSE: 3.715367
 925 | [ 5.04735787  0.01872573  0.43477684 -0.44795621  0.02728912] | MSE: 3.715367 | Min MSE: 3.715367
Optimization terminated successfully.
         Current function value: 3.715367
         Iterations: 479
         Function evaluations: 798
Optimal Parameters: [ 5.04735844  0.01872573  0.43477689 -0.44795617  0.02728912]
```

