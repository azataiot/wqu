# Other common issues 

## ModuleNotFoundError: No module named 'pca’

Current Python environment dose not have the `pca` PyPI package, we need to install it ( before other cells)

```python
%%capture pca
!pip install pca
```

## ModuleNotFoundError: No module named 'pandas_datareader’

same as above, you need to install this package with:

```python
%%capture pdr
!pip install pandas_datareader
```

## ModuleNotFoundError: No module named 'openpyxl’

```python
%%capture openpyxl
!pip install openpyxl
```

