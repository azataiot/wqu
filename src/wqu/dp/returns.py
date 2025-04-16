# src/wqu/dp/returns.py

import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import skew, kurtosis, jarque_bera, norm


class Returns:
    def __init__(self, ticker: str, start: str = "2020-01-01", end: str = None, interval: str = "1d"):
        """
        Initialize StockReturns object to fetch data and compute returns.

        Parameters:
        - ticker: stock symbol (e.g., "AAPL")
        - start: start date (format: "YYYY-MM-DD")
        - end: end date (default: today)
        - interval: data interval (default: "1d", daily)
        """
        self.ticker = ticker.upper()
        self.start = start
        self.end = end
        self.interval = interval
        self.data = self._download_data()
        self.returns = None

    def _download_data(self) -> pd.DataFrame:
        df = yf.download(self.ticker, start=self.start, end=self.end, interval=self.interval)
        df = df[["Close"]].rename(columns={"Close": "Price"})
        df.dropna(inplace=True)
        return df

    def compute_returns(self, method: str = "log"):
        """
        Compute daily returns using specified method: "log" or "simple"
        """
        price = self.data["Price"]
        if method == "log":
            self.returns = np.log(price / price.shift(1)).dropna()
        elif method == "simple":
            self.returns = price.pct_change().dropna()
        else:
            raise ValueError("Method must be 'log' or 'simple'")
        self.returns.name = f"{self.ticker}_{method}_return"
        return self.returns

    def annualized_return(self, method: str = "log") -> float:
        """
        Compute annualized return from daily returns.
        """
        if self.returns is None or not self.returns.name.endswith(method):
            self.compute_returns(method=method)

        if method == "log":
            return 252 * self.returns.mean()
        elif method == "simple":
            return (1 + self.returns.mean()) ** 252 - 1

    def cumulative_return(self, method: str = "log", as_series: bool = True):
        """
        Compute cumulative return.

        Parameters:
        - method: 'log' or 'simple'
        - as_series: if True, return cumulative return time series (default)
                     if False, return total cumulative return as float
        """
        returns = self.compute_returns(method=method)

        if method == "simple":
            cumulative = (1 + returns).cumprod()
        elif method == "log":
            cumulative = np.exp(returns.cumsum())
        else:
            raise ValueError("Method must be 'log' or 'simple'")

        return cumulative if as_series else float((cumulative.iloc[-1] - 1).item())


    def plot_price(self):
        self.data["Price"].plot(figsize=(10, 4), title=f"{self.ticker} Price")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def plot_returns(self, method: str = "log"):
        self.compute_returns(method=method)
        self.returns.plot(figsize=(10, 4), title=f"{self.ticker} {method.capitalize()} Returns")
        plt.xlabel("Date")
        plt.ylabel("Return")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def plot_cumulative_return(self, method: str = "log"):
        """
        Plot cumulative returns over time.

        Parameters:
        - method: 'log' or 'simple'
        """
        returns = self.compute_returns(method=method)

        if method == "simple":
            cumulative = (1 + returns).cumprod()
        elif method == "log":
            cumulative = np.exp(returns.cumsum())
        else:
            raise ValueError("Method must be 'log' or 'simple'")

        cumulative.name = f"Cumulative {method.capitalize()} Return"

        cumulative.plot(figsize=(10, 4), title=f"{self.ticker} Cumulative {method.capitalize()} Return")
        plt.xlabel("Date")
        plt.ylabel("Growth of $1")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def plot_histogram(self, method: str = "log", bins: int = 50):
        """
        Plot histogram of returns with normal distribution overlay.
        """
        returns = self.compute_returns(method)
        mu, sigma = returns.mean(), returns.std()

        plt.figure(figsize=(10, 5))
        plt.hist(returns, bins=bins, density=True, alpha=0.6, label="Empirical")

        x = np.linspace(returns.min(), returns.max(), 100)
        plt.plot(x, norm.pdf(x, mu, sigma), 'r--', label="Normal PDF")

        plt.title(f"{self.ticker} Return Distribution ({method})")
        plt.xlabel("Return")
        plt.ylabel("Density")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def compare_with_normal(self, method: str = "log", bins: int = 50):
        """
        Compare actual returns with a simulated normal distribution.
        """
        returns = self.compute_returns(method)
        mu, sigma = returns.mean(), returns.std()
        normal_sim = np.random.normal(mu, sigma, size=len(returns))

        plt.figure(figsize=(10, 5))
        plt.hist(returns, bins=bins, alpha=0.5, label="Actual Returns", density=True)
        plt.hist(normal_sim, bins=bins, alpha=0.5, label="Simulated Normal", density=True)
        plt.title(f"{self.ticker} Actual vs Normal Returns ({method})")
        plt.xlabel("Return")
        plt.ylabel("Density")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def summary(self, method: str = "log") -> dict:
        """
        Return a summary dictionary with performance + statistical properties.
        """
        price = self.data["Price"]
        returns = self.compute_returns(method)

        jb_stat, jb_p = jarque_bera(returns)

        return {
            "ticker": self.ticker,
            "start_date": price.index[0].strftime("%Y-%m-%d"),
            "end_date": price.index[-1].strftime("%Y-%m-%d"),
            "final_price": price.iloc[-1].item(),
            "total_return": self.cumulative_return(method=method, as_series=False),
            "annualized_return": self.annualized_return(method=method).item(),
            "average_daily_return": returns.mean().item(),
            "volatility_daily": returns.std().item(),
            "volatility_annual": (returns.std() * np.sqrt(252)).item(),
            "skewness": skew(returns).item(),
            "kurtosis": kurtosis(returns).item(),  # excess kurtosis
            "jarque_bera_stat": jb_stat.item(),
            "jarque_bera_p": jb_p.item(),
        }