# WQU

Custom Python scripts for the WQU related stuff.

## Installation

```bash
pip install wqu
``` 
if using UV (recommended) use the following command:
```bash
uv add wqu
```

## Usage

NOTE: currently package is not stable and interfaces are object to frequent changes. Not recommended for production use.

Current available modules:


- pricing: A package for pricing options and other financial instruments.
- volatility: A package for calculating volatility.
- data: A package for data manipulation and analysis.
- utils: A package for utility functions.
- graph: A package for graphing functions.
- stream: A package for streaming real-time financial data. 

For the pricing:
```
pricing
├── binomial.py
├── greeks.py
├── hedging.py
├── options.py
└── trinomial.py
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
All tests must pass before merging the code.

## License

[MIT](https://choosealicense.com/licenses/mit/)


## Note: 

This package is built with my personal interest, and it is not an official package of WQU, using this package is at your own risk.



