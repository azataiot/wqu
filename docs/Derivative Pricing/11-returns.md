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