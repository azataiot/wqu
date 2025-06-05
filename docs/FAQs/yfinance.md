# Common `yfinance` related issues on the WQU Jupyter Notebooks and prefered solutions 

## NameError: name 'yf' is not defined 

Maybe due to an initial environment setup, the WQU Jupyter notebooks may not have the `yfinance` library pre-installed, so the way to solve this is easy, you just need to install the package with the following (before any other code cells or before importing yfinance): 

```python hl_lines="1"
%%capture yfinance
!pip install yfinance
```

Notice that we added `%%capture yfinance` in the first line. Which is to capture the code cell execution output ( we do not care about the installation details, we just want to have the yfinance)

## KeyError: "['Adj Close'] not in index”

This is due to the feature update on the latest version of `yfinance` , which auto-adjusts the Close prices based on the dividends so there is no need for the 'Adj Close' column, however, the WQU Jupyter notebooks seem to be written in 2022, with earlier versions of the yfinance package, so we have to revert back to the legacy behaviour of the `yfinance` :

change your function call to download OHLCV from:

```python hl_lines="1"
forex_data31 = yf.download("USDINR=X", start="2019-01-02", end="2022-06-30")
forex_data31 = forex_data31.reset_index()
inr_df = forex_data31[["Date", "Adj Close"]]
inr_df.rename(columns={"Adj Close": "inr"}, inplace=True)
```

to:

```python hl_lines="1"
forex_data31 = yf.download("USDINR=X", start="2019-01-02", end="2022-06-30", auto_adjust=False)
forex_data31 = forex_data31.reset_index()
inr_df = forex_data31[["Date", "Adj Close"]]
inr_df.rename(columns={"Adj Close": "inr"}, inplace=True)
```

> Notice the `auto_adjust=False`, which is the key change and it bring us the 'Adj Close' back.

