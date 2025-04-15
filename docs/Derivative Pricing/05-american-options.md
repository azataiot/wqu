# American Options

American options are different from the European options. American options allow the buyer to exercise the option at any point in time. This important characteristic has further derived implications in real markets: 

- Flexibility to the buyer 
- Risk to the seller 
- Hedging (delta) exposure 
- OTC vs.Exchange-traded 
- Popularity 
- High premiums ( options prices )

## Binomial Mode for American Options 

In the binomial tree, we move backward in time just like for European options - but now, at each node we check:


$$
\text{Option Value }=max(\text{ Hold Value},\text{ Exercise Value})
$$



That is :

- Hold value: discounted expected value from the two next steps
  - $\text{Hold} = e^{-r \Delta t} \cdot \left[ p \cdot V_{t+1,i+1} + (1 - p) \cdot V_{t+1,i} \right]$
- Exercise value: immediate payoff from exercising the option 
  - Call: $max(S_{t,i} - K,0)$
  - Put: $max(K - S_{t,i},0)$

Where American Option Value at node (t,i):


$$
V_{t,i} = \max \left( \text{Immediate Payoff},\ \text{Discounted Expected Future Value} \right)
$$


When is early exercise not optimal ? 

> For American call options on non-dividend-paying stocks:
>
> Never exercise early. Its better to hold. 
>
> For American put options, early exercise sometimes are optimal. 

## Code

In `wqu` the American options is handled by the same class `BinomialTree` and can be used as:

```python
from wqu.dp import BinomialTree


bt_put_am = BinomialTree(S0=50, K=52, T=2, r=0.05, u=1.2, d=0.8, N=2, option_type='put', option_style='american')
bt_put_am.build_stock_tree()
bt_put_am.build_option_tree()
bt_put_am.summary()

bt_put_am.price()
```

Or 

```python
bt_call_am = BinomialTree(S0=50, K=52, T=2, r=0.05, u=1.2, d=0.8, N=2, option_type='call', option_style='american')
bt_call_am.summary()

bt_call_am.price()
```

Put-call parity for the American style call options also possible with:

```python
bt_call_am.check_put_call_parity(verbose=True)
```

## Delta hedging for American style

In Europian options, delta hedge is planned based on the final option payoff only and no early exercise means its easier to implement. However, in the American options, due to the fact that the option might be exercised early, the value ofthe option may not follow a smooth path like the European case. This makes hedging harder, more dynamic and potentially more expensive. 

Dynamic hedging means:

- Adjust the delta hedge **step-by-step**
- At every node in the binomial tree, recalculate $\Delta$
- Buy/Sell stock to match the new delta.

Delta is still: 


$$
\Delta = \frac{V_{\text{up}} - V_{\text{down}}}{S_{\text{up}} - S_{\text{down}}}
$$


for both American and European options, but: 

- With American options, payoff can change earlier 
- Hence the option value tree is different 
- So delta tree is different 
- So hedging strategy is different 



This can be done with the following code if using `wqu`:

```python
from wqu.dp import BinomialTree


bt_put_am = BinomialTree(S0=50, K=52, T=2, r=0.05, u=1.2, d=0.8, N=2, option_type='put', option_style='american')
bt_put_am.build_stock_tree()
bt_put_am.build_option_tree()
bt_put_am.summary()

bt_put_am.price()
```

We can also simulate a specic hedge path. 

```python
bt_am_put = BinomialTree(S0=50, K=52, T=2, r=0.05, u=1.2, d=0.8, N=2, option_type='put', option_style='american')
bt_am_put.build_stock_tree()
bt_am_put.build_option_tree()
bt_am_put.build_delta_tree()

# Simulate dynamic hedge for path: up then down
bt_am_put.simulate_delta_hedge(path='ud')
```

which returns response similar to:

```
Initial Hedge:
Stock: 50.00, Delta: -0.53, Shares: -0.53, Cash: 26.46, Total: 0.00

Step | Stock  | Delta  | Shares Δ | Stock Value | Cash | Total
 1    | 60.00   | -0.17  | 0.36     | -10.00      | 8.33   | -1.67
 2    | 48.00   | 0.00   | 0.17     | 0.00        | -1.67  | -1.67

Final Results:
  Hedged Portfolio Value : -1.6667
  Option Payoff          : 4.0000
  Hedging Error          : -5.6667
(np.float64(-1.6666666666666679),
 np.float64(4.0),
 np.float64(-5.666666666666668))
```



**Why is the Hedging Error there ?** 

This is expected. 

Dynamic delta hedging in discrete time is an approximation. We are only hedging once per time step, delta changes between time steps, but we can’t react instantly. For American options, early exercise adds more complexity - hedge based on the value to hold, but the option may be exercised earlier. 













