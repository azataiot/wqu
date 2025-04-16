import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import skew, kurtosis, jarque_bera, norm
import seaborn as sns

class Returns:
    def __init__(self, ticker: str = None, tickers: list = None, start: str = "2020-01-01", end: str = None, interval: str = "1d"):
        """
        Initialize Returns object to fetch data and compute returns for one or more tickers.

        Parameters:
        - ticker: single ticker (str)
        - tickers: list of tickers (list[str])
        - start, end, interval: yfinance parameters
        """
        if ticker and tickers:
            raise ValueError("Pass either 'ticker' or 'tickers', not both.")
        elif ticker:
            self.tickers = [ticker.upper()]
        elif tickers:
            self.tickers = [t.upper() for t in tickers]
        else:
            raise ValueError("You must provide either 'ticker' or 'tickers'.")

        self.start = start
        self.end = end
        self.interval = interval
        self.data = self._download_data()
        self.returns = None

    @property
    def is_multi(self):
        return len(self.tickers) > 1

    def _download_data(self):
        df = yf.download(self.tickers, start=self.start, end=self.end, interval=self.interval, group_by="ticker", auto_adjust=True)

        if not self.is_multi:
            df = df[["Close"]].rename(columns={"Close": "Price"})
        else:
            df = df.stack(level=0, future_stack=True)[["Close"]].rename(columns={"Close": "Price"}).unstack()
        df.dropna(inplace=True)
        return df

    def compute_returns(self, method="log"):
        price = self.data["Price"] if not self.is_multi else self.data["Price"]
        if method == "log":
            returns = np.log(price / price.shift(1)).dropna()
        elif method == "simple":
            returns = price.pct_change().dropna()
        else:
            raise ValueError("Method must be 'log' or 'simple'")
        self.returns = returns
        return returns

    def plot_price(self):
        prices = self.data["Price"]
        title = f"{', '.join(self.tickers)} Price"
        prices.plot(figsize=(10, 4), title=title)
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def plot_returns(self, method="log"):
        returns = self.compute_returns(method)
        returns.plot(figsize=(10, 4), title=f"{', '.join(self.tickers)} {method.capitalize()} Returns")
        plt.xlabel("Date")
        plt.ylabel("Return")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def plot_cumulative_return(self, method="log"):
        returns = self.compute_returns(method)
        if method == "simple":
            cumulative = (1 + returns).cumprod()
        elif method == "log":
            cumulative = np.exp(returns.cumsum())
        cumulative.plot(figsize=(10, 4), title=f"{', '.join(self.tickers)} Cumulative {method.capitalize()} Return")
        plt.xlabel("Date")
        plt.ylabel("Growth of $1")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def plot_histogram(self, method="log", bins=50):
        returns = self.compute_returns(method)
        if not self.is_multi:
            returns = returns.to_frame()

        plt.figure(figsize=(10, 5))
        for col in returns.columns:
            mu, sigma = returns[col].mean(), returns[col].std()
            x = np.linspace(returns[col].min(), returns[col].max(), 100)
            plt.hist(returns[col], bins=bins, alpha=0.5, density=True, label=f"{col} Empirical")
            plt.plot(x, norm.pdf(x, mu, sigma), '--', label=f"{col} Normal PDF")

        plt.title("Return Distributions")
        plt.xlabel("Return")
        plt.ylabel("Density")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()


    def plot_correlation_heatmap(self, method: str = "log"):
        """
        Plot a heatmap of pairwise correlations between tickers.
        """
        if not self.is_multi:
            raise ValueError("Correlation heatmap requires multiple tickers.")

        returns = self.compute_returns(method=method)
        corr = returns.corr()

        plt.figure(figsize=(8, 6))
        sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", vmin=-1, vmax=1)
        plt.title(f"{method.capitalize()} Return Correlation Heatmap")
        plt.tight_layout()
        plt.show()

    def compare_with_normal(self, method="log", bins=50):
        returns = self.compute_returns(method)
        if not self.is_multi:
            returns = returns.to_frame()

        plt.figure(figsize=(10, 5))
        for col in returns.columns:
            mu, sigma = returns[col].mean(), returns[col].std()
            normal_sim = np.random.normal(mu, sigma, size=len(returns))
            plt.hist(returns[col], bins=bins, alpha=0.5, label=f"{col} Actual", density=True)
            plt.hist(normal_sim, bins=bins, alpha=0.3, label=f"{col} Simulated", density=True)

        plt.title("Actual vs Simulated Normal Returns")
        plt.xlabel("Return")
        plt.ylabel("Density")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def simulate_correlated_returns(self, method: str = "log", n_days: int = 252, seed: int = 42) -> pd.DataFrame:
        """
        Simulate returns for all tickers using Cholesky decomposition.

        Returns:
            Simulated returns (DataFrame)
        """
        if not self.is_multi:
            raise ValueError("Correlation simulation requires multiple tickers.")

        np.random.seed(seed)
        historical = self.compute_returns(method)
        mu = historical.mean().values
        sigma = historical.std().values
        corr = historical.corr().values

        cov = np.outer(sigma, sigma) * corr
        chol = np.linalg.cholesky(cov)

        z = np.random.randn(n_days, len(self.tickers))
        correlated = z @ chol.T + mu

        dates = pd.date_range(start=self.data.index[-1], periods=n_days + 1, freq="B")[1:]
        return pd.DataFrame(correlated, columns=self.tickers, index=dates)

    def summary(self, method="log"):
        price = self.data["Price"]
        returns = self.compute_returns(method)
        summaries = {}

        if not self.is_multi:
            returns = returns.to_frame()
            price = price.to_frame()

        for col in returns.columns:
            jb_stat, jb_p = jarque_bera(returns[col])
            summaries[col] = {
                "start_date": price[col].dropna().index[0].strftime("%Y-%m-%d"),
                "end_date": price[col].dropna().index[-1].strftime("%Y-%m-%d"),
                "final_price": price[col].iloc[-1].item(),
                "total_return": float((np.exp(returns[col].cumsum()).iloc[-1] - 1).item()) if method == "log" else float(((1 + returns[col]).cumprod().iloc[-1] - 1).item()),
                "annualized_return": (252 * returns[col].mean()).item() if method == "log" else ((1 + returns[col].mean()) ** 252 - 1).item(),
                "average_daily_return": returns[col].mean().item(),
                "volatility_daily": returns[col].std().item(),
                "volatility_annual": (returns[col].std() * np.sqrt(252)).item(),
                "skewness": skew(returns[col]).item(),
                "kurtosis": kurtosis(returns[col]).item(),
                "jarque_bera_stat": jb_stat.item(),
                "jarque_bera_p": jb_p.item(),
            }

        return summaries if self.is_multi else summaries[self.tickers[0]]