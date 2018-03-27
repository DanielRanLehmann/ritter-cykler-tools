# ritter-cykler-tools
Generate testdata and quickly upload data to database

## Installation
```{r, engine='bash', count_lines}
pip install -r requirements.txt
```

## Example usage
Generates 25 fake products with the firebase style.

```{r, engine='bash', count_lines}
python testdata.py --products="/Users/danielranlehmann/Desktop/test-products.json" --count=25 --style="firebase"
```

Generates 25 fake users.

```{r, engine='bash', count_lines}
python testdata.py --users="/Users/danielranlehmann/Desktop/test-users.json" --count=25"
```

