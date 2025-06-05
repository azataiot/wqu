# Other common issues 

## ModuleNotFoundError: No module named 'pca’

Current Python environment dose not have the `pca` PyPI package, we need to install it ( before other cells)

```python
%%capture pca
!pip install pca
```

