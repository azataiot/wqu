# Stock returns

## Simple Returns 

If a stock goes from \$100 to \$110: 


$$
R_t = \frac{P_t - P_{t-1}}{P_{t-1}} = \frac{110 - 100}{100} = 0.10 = 10\%
$$


Easy to interpret, additive over time frames.

## Continuously Compounded Returns (Log Returns)


$$
r_t = \ln \left( \frac{P_t}{P_{t-1}} \right)
$$


Why log returns?



- More mathematically elegant
- Additive across time
- Preferred in models like GBM and Black-Scholes

## Annualized Returns

We often want to **scale** returns to a yearly basis.  (Assuming 252 trading days in a year)

- For simple daily returns: $R_{\text{annual}} = (1 + \bar{R}_{\text{daily}})^{252} - 1$  (**Compounds** returns over time. Uses geometric growth.)
- For log returns: $r_{\text{annual}} = 252 \cdot \bar{r}_{\text{daily}}$  (**Adds** returns over time. Uses arithmetic approximation.)



When returns are small and volatility is low, **log ≈ simple**.

But as returns and volatility grow:



- Log returns **underestimate** performance
- Simple returns **capture compounding effects**

## Working with APIs

To get real stock data (like prices of AAPL or SPY), we use financial data APIs, e.g.:
	•	Yahoo Finance (via yfinance)
	•	Alpha Vantage
	•	Polygon.io
	•	Quandl 

## Characteristics of the Returns 

Do real-world stock returns behave like the normal distribution (bell curve) ? Mostly models (like Black-Scholes, GBM, etc.) assume: $r_t \sim \mathcal{N}(\mu, \sigma^2)$ but is that assumption actually valid ?

These are **empirical truths** observed from real market data — patterns that keep showing up: 

- Returns are not normally distributed. 
  - They have fat tails (more extreme events than a normal distribution would predict)
  - They are leptokurtic (higher peaks and fatter tails)
- Negative Skew
  - Big drops happen more than big gains 
  - The distribution is often tilted left 
- Volatility Clustering
  - High volatility periods tend to follow each other 
  - This violates the i.i.d. assumption of many models 

## Test for normality 

 **Jarque-Bera Test**

A test that checks whether skewness and kurtosis deviate from those of a normal distribution. 


$$
\text{JB} = \frac{n}{6} \left( S^2 + \frac{(K - 3)^2}{4} \right)
$$


Where:



- n = number of observations
- S = skewness
- K = kurtosis 

 If JB is **large** and p-value is **small**, we **reject** the normality assumption. 

If stock returns aren’t normal:

- Models like Black-Scholes may **underestimate** extreme events (like crashes)
- We may need **more advanced models** (e.g., jump-diffusion, GARCH, heavy-tailed distributions)

## Correlated Returns

In many real-world scenarios, we deal with multiple stocks, not just one. For example:

- Basket options depends on several assets 
- Portfolio risk (VaR) requires simulating a group of stocks 
- Stocks in the same industry or index are not independent 

So we want to simulate their prices, but also respect their correlations. 

### GBM for one single stock 

We simulate prices using: $dS_t = \mu S_t dt + \sigma S_t dW_t$ , Or in discrete form: $S_{t+1} = S_t \cdot \exp\left((\mu - \frac{1}{2}\sigma^2)\Delta t + \sigma \sqrt{\Delta t} \cdot \varepsilon_t \right)$ where $\varepsilon_t \sim N(0,1)$. If we simulate two stocks this way using independent $\varepsilon$, they’ll be **uncorrelated**. But real stock returns **are correlated** (e.g., Apple and Microsoft move similarly).

### Cholesky Decomposition

To simulate correlated random shocks $\varepsilon_1, \varepsilon_2$, we can use:  **Cholesky Decomposition**

1. Let $\Sigma$ be your **correlation matrix** (e.g., from historical returns)

2. Compute the **Cholesky factor**: $L \text{ such that } \Sigma = L L^\top$ 
3. Generate independent $z \sim \mathcal{N}(0, I)$ 
4. Create correlated values: $\varepsilon = L z$ 

This guarantees that the resulting $\varepsilon$ values have the **desired correlation**.

We use Cholesky decomposition to simulate multiple stocks whose random price changes are correlated.
Instead of sampling independent normal variables, we sample correlated ones using: $\varepsilon = Lz, \quad \text{where } LL^\top = \Sigma$ 



## Coding

```python
from wqu.dp import Returns

# Create a stock return analyzer
apple = Returns("AAPL", start="2022-01-01")

# Plot price history
apple.plot_price()

# Plot log returns
apple.plot_returns(method="log")

# Annualized return
print("Annualized Log Return:", apple.annualized_return(method="log"))
print("Annualized Simple Return:", apple.annualized_return(method="simple"))
```

![img](./assets/E910EDD7-F65E-479B-9661-B8EF63D80DBA.png)

![img](./assets/0832608A-CF5C-4399-903E-56F77791E9E0.png)

```python
Annualized Log Return: Ticker
AAPL    0.037431
dtype: float64
Annualized Simple Return: Ticker
AAPL    0.083985
dtype: float64
```

```python
apple = Returns("AAPL", start="2022-01-01")

# Cumulative log return plot
apple.plot_cumulative_return(method="log")

# Cumulative simple return plot
apple.plot_cumulative_return(method="simple")
```



![img](./assets/AA3C122B-208E-4240-845D-FDA4C0E15D08.png)

```python
total_return = apple.cumulative_return(method="log", as_series=False)
print(f"Total return over the period: {total_return:.2%}")
```

```
Total return over the period: 13.00%
```

```python
# Full summary
from pprint import pprint
pprint(apple.summary(method="log"))
```

```python
{'annualized_return': 0.03743128332933439,
 'average_daily_return': 0.0001485368386084698,
 'end_date': '2025-04-15',
 'final_price': 202.13999938964844,
 'start_date': '2022-01-03',
 'ticker': 'AAPL',
 'total_return': 0.13003185000794049,
 'volatility_annual': 0.29385309739549303,
 'volatility_daily': 0.018511005183202773}
```

```python
from pprint import pprint

apple = Returns("AAPL", start="2022-01-01")

# Full stats
pprint(apple.summary(method="log"))

# Histogram
apple.plot_histogram()

# Real vs Normal
apple.compare_with_normal()
```

```
{'annualized_return': 0.037431283329334854,
 'average_daily_return': 0.00014853683860847165,
 'end_date': '2025-04-15',
 'final_price': 202.13999938964844,
 'jarque_bera_p': 1.5079435967188569e-307,
 'jarque_bera_stat': 1412.9657533659843,
 'kurtosis': 6.388733674088982,
 'skewness': 0.3116206222444215,
 'start_date': '2022-01-03',
 'ticker': 'AAPL',
 'total_return': 0.13003185000794226,
 'volatility_annual': 0.2938530771694982,
 'volatility_daily': 0.01851100390908486}
```

![img](./assets/AA87CA9F-D9DF-43B2-A3D2-28BDE4C826AF.png)

![img](./assets/D2FC779B-8EC7-4870-8767-8295CBD03F82.png)

```python
multi = Returns(tickers=["AAPL", "MSFT", "GOOG"], start="2022-01-01")
multi.plot_returns()
pprint(multi.summary())
```

![multi-returns](./assets/multi-returns.png)

```json
{'AAPL': {'annualized_return': 0.03743128332933385,
          'average_daily_return': 0.00014853683860846764,
          'end_date': '2025-04-15',
          'final_price': 202.13999938964844,
          'jarque_bera_p': 1.5058893297318933e-307,
          'jarque_bera_stat': 1412.9684798174567,
          'kurtosis': 6.388739786712888,
          'skewness': 0.3116211853517522,
          'start_date': '2022-01-03',
          'total_return': 0.1300318500079385,
          'volatility_annual': 0.2938530289858372,
          'volatility_daily': 0.018511000873799522},
 'GOOG': {'annualized_return': 0.028895018225221582,
          'average_daily_return': 0.00011466277073500627,
          'end_date': '2025-04-15',
          'final_price': 158.67999267578125,
          'jarque_bera_p': 6.480725439193935e-62,
          'jarque_bera_stat': 281.7828866220795,
          'kurtosis': 2.857321584240662,
          'skewness': -0.11505899180745548,
          'start_date': '2022-01-03',
          'total_return': 0.0989634972040998,
          'volatility_annual': 0.33268847483008585,
          'volatility_daily': 0.020957404010899492},
 'MSFT': {'annualized_return': 0.05185782809416014,
          'average_daily_return': 0.0002057850321196831,
          'end_date': '2025-04-15',
          'final_price': 385.7300109863281,
          'jarque_bera_p': 1.0016216603866884e-53,
          'jarque_bera_stat': 244.07077916353825,
          'kurtosis': 2.663900517276484,
          'skewness': 0.07267980584196587,
          'start_date': '2022-01-03',
          'total_return': 0.18454777992431826,
          'volatility_annual': 0.27965063119298217,
          'volatility_daily': 0.01761633390759221}}
```

```python
# For multiple tickers
multi = Returns(tickers=["AAPL", "MSFT", "GOOG"], start="2022-01-01")

# Heatmap
multi.plot_correlation_heatmap()

# Simulate correlated returns (like a Monte Carlo engine)
simulated = multi.simulate_correlated_returns(n_days=252)
print(simulated.head())

# plot one simulated ticker
simulated["AAPL"].cumsum().plot(title="Simulated AAPL Path", figsize=(10, 4))
```

![img](./assets/104E1546-7BE3-4A88-8BA8-3D262217536D.png)

```
                AAPL      MSFT      GOOG
2025-04-16  0.010525  0.003827  0.012896
2025-04-17  0.032033  0.014188  0.014764
2025-04-18  0.033211  0.029396  0.018340
2025-04-21  0.011485 -0.000376 -0.001103
2025-04-22  0.005186 -0.024903 -0.027260
```

![img](./assets/68A1B7F4-117C-43E1-9F5B-8102E557C732.png)

