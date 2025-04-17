# Reinforcement Learning

## Reinforcement Learning Into

### What is Reinforcement Learning?

Imagine teaching a dog tricks. 

- You say “sit” 🐶,
- If the dog sits, you give it a treat 🍖, 
- If not, no treat. 

Over time, the dog learns that **sitting when you say “sit” gets a reward**, and it dose it more often. 

Reinforcement Learning (RL) is just like that - but for **computers** and **algorithms**. 

> It’s a way for machines to learn how to make decisions by trying things out and getting rewards or penalties. 

### Key Concepts in RL

let’s break down RL into its key components using intuitive examples:

| **RL Concept**  | **Dog Analogy**                 | **Financial Analogy (Trading Bot)**                          |
| --------------- | ------------------------------- | ------------------------------------------------------------ |
| **Agent**       | The dog                         | The trading algorithm                                        |
| **Environment** | Your living room                | The financial market                                         |
| **Action**      | Sit, bark, roll                 | Buy, sell, hold                                              |
| **State**       | Is the dog standing or sitting? | Stock prices, indicators, portfolio state                    |
| **Reward**      | Getting a treat                 | Profit from a trade or return on investment                  |
| **Policy**      | Rule for behavior               | Strategy for choosing actions (buy/sell) based on market state |

### How dose learning happen ?

**Trial-and-error:**

- The agent starts by exploring randomly (e.g., random trades). 
- It gets  feedback from the environment: **profit or loss**
- It learns over time to **favor actions that lead to better outcomes**

### Formal Math View

In RL, we model problems using a **Markov Decision Process (MDP)**. 

An MDP is a tuple:


$$
MDP = (S,A,P,R,\gamma)
$$


Where: 

- $S$: Set of states (e.g., stock prices, portfolio) 
- $A$: Set of actions (e.g., buy/sell/hold)
- $P(s'|s,a)$: Transition probability from state $s$ to $s'$ when taking action $a$
- $R(s,a)$: Reward function 
- $\gamma \in [0,1]$: Discount factor (how much future rewards are worth today)

The goal: learn a policy $\pi(a|s)$ that maximizes the expected reward over time. 

### The Core Equation (Bellman Equation)

The Bellman Equation tells how to think about value in TL. 


$$
V^{\pi}(s) = \mathbb{E}_{\pi} \left[ R(s,a) + \gamma V^{\pi}(s{\prime}) \right]
$$


Tis says:

> The value of a state is the reward you get now plus the value of the next state, discounted. 

In finance: 

- $V^\pi(S)$: Expected return from current portfolio state 
- $R(s,a)$: Profit/loss from an action 
- $\gamma$: Time-value of money 





