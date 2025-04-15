# Derivative Pricing

## TL;DR

Derivative pricing refers to the process of determining the fair value of a derivative financial instrument, such as an option, future, or swap. It involves using mathematical models and market data to calculate the theoritical price of the derivative based on factors like the underlying asset's price, volatility, time to expiration, and interest rates. 

## Participants 

### Buy side

Derivatives on the buy-side refer to financial institutions, such as investment funds or asset managers, that purchase derivative contracts like options, futures, or swaps to manage risk or gain exposure to certain assets or markets. 

### Sell side 

Derivatives on the sell-side refer to financial institutions, such as investment banks, that create, market, and trade derivative products like futures, options, and swaps. The sell-side provides these derivative instruments to clients, such as hedge funds and institutional investors, to help them manage financial risks or speculate on market movements. 

## Equity Options

### Features

- Call vs. Put 
- Moneyness & Liquidity -> OTM/ATM/ITM ?
- European vs. American vs. Asian -> Early exercise? 
- Non-linear payoffs 
- Leverage -> e.g., 100 shares of underlying stock 
- OTC vs. Exchange traded -> credit risk ? 
- Exposure to volatility -> e.g., Butterfly / Stradles 

### Payoff

Call Option: $(S_t - K)^+ = max(S_t - K;0)$

Put Option: $(K-S_t)^+ = max(K-S_t;0)$

## Price Process

The essential characteristics of a derivative is that it's payoff depends on the evolution of an underlying asset (e.g., a stock for equity options)

> Thus a key aspect for pricing (and our first step) is to model the future evolution of the underlying asset.

Techniques for modeling underlying stock price evolution: 

- Binomial Model 

  Binomial model assumes that stock price can make, at any point in time, upward (u) or downward (d) movements. 

## Risk-neutral valuation 

Prices are computed under a risk-neutral measure, where expected returns are discounted at the risk-free rate rather than the actual expected return. 

The risk-neutral probability is derived as:

$$
p = \frac{e^{rT}-d}{u-d}
$$

Where:
- $r$: the risk free interest rate 
- $u,d$: up and down factors 
- $T$: Time to maturity 

Then the price of a European call option becomes :

$$
C_0 = e^{-rT}[pc_u + (1-p)c_d]
$$

where $c_u,c_d$ are the call payoffs in up and down states. 

