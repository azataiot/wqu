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

