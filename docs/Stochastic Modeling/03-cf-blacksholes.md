# Black-Scholes Characteristic Function(CF)

CF is defined as:


$$
\phi_X(u) = \mathbb{E}\left[e^{iuX}\right]
$$


It’s the **expected value of a complex exponential**, and it uniquely determines the distribution of the random variable X — like a frequency signature of the distribution. 

## Deriving the Black-Scholes Characteristic Function 

We assume that: 


$$
s_T = \log S_T \sim \mathcal{N}\left(s_0 + \left(\mu - \frac{1}{2} \sigma^2\right)T, \sigma^2 T \right)
$$


That’s just the **log of the stock price under GBM**, which is **normally distributed**. 

Then using the Definition of the CF, substitute in the normal PDF and solve:


$$
\phi_{s_T}(u) = \int_{-\infty}^\infty e^{ius_T} f(s_T)\, ds_T
$$


Then combine the exponentials, we get:


$$
\phi_{s_T}(u) = \int_{-\infty}^\infty e^{ius_T - \frac{(s_T - \hat{\mu})^2}{2 \hat{\sigma}^2}} \, ds_T
$$


Where:

- $\hat{\mu} = s_0 + \left(\mu - \frac{1}{2}\sigma^2\right)T$
- $\hat{\sigma} = \sigma \sqrt{T}$

This is just a normal PDF wrapped in a complex exponential. 

To solve the integral, we rewrite the exponent using a **completing-the-square trick**:


$$
ius_T - \frac{(s_T - \hat{\mu})^2}{2 \hat{\sigma}^2}
= -\frac{(s_T - y)^2}{2\hat{\sigma}^2} + \text{constants}
$$


We end up with:


$$
\phi_{s_T}(u) = \exp \left( iu \hat{\mu} - \frac{1}{2} u^2 \hat{\sigma}^2 \right)
$$


Substituiting back:


$$
\phi_{s_T}(u) = \exp \left( iu \left(s_0 + \left(\mu - \frac{1}{2} \sigma^2\right)T \right) - \frac{1}{2} u^2 \sigma^2 T \right)
$$


This is the **closed-form CF** of $\log S_T$ in the **Black-Scholes model**.

This is actually the same as the CF of a normal distribution: 


$$
\phi_X(u) = \exp \left(iu \mu - \frac{1}{2} u^2 \sigma^2 \right)
$$


So this confirms that:



- $\log S_T$ is normal 
- The CF matches the theory

We derived the characteristic function of $\log S_T$ under Black-Scholes by plugging the normal distribution into the definition of CF and simplifying the integral using a **completing-the-square trick**. This gives us a clean formula that’s perfect for plugging into **Fourier pricing methods**.

