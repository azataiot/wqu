# Asian Options

So far, we dealt with options where the payoff depends only on the final price of the stock:

- Call $max(S_T - K,0)$
- Put $max(K-S_T,0)$

But path-dependent options are different. Their payoff depends on the entire path the stock price takes - not just the final value. 

Its like saying: “I care not just about where you are now, but everywehre you’ve been before you got here”

## Examples of Path-dependent options

1. Asian Option: Payoff depends on the **average price** of the underlying asset during the life of the option. 
   1. Asian Call: $max(\bar S - K,0)$
   2. Asian Put: $max(K-\bar S,0)$
2. Lookback Option: Payoff depends on the **maximum or minimum** stock price during the life of the operation. 
3. Barrier Option: Payoff activates only if a price **hits a barrier** at some point in time. 

## Asian Option with Binary Tree

`wqu` supports building and checking the Asian (european style exercise only) with Python:

```python
from wqu.dp import BinomialTree


bt_asian = BinomialTree(
    S0=100, K=95, T=1, r=0.05,
    u=1.1, d=0.9, N=3,
    option_type='call',
    option_style='asian'
)

bt_asian.build_stock_tree()
bt_asian.build_option_tree()
print("Asian Call Price:", bt_asian.price())
```

