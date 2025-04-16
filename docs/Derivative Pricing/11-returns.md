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

