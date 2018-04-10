# ritter-cykler-tools
**NOTE: Remember to include credentials for the database, etc.**<br/>
Quickly generate testdata and upload it to the database.

## Installation
```{r, engine='bash', count_lines}
pip install -r requirements.txt
```

## Usage

### Testdata
Generates 25 fake products with the firebase style.
```{r, engine='bash', count_lines}
python testdata.py --products=/Users/danielranlehmann/Desktop/test-products.json --count=25 --style="firebase"
```

Generates 25 fake users.
```{r, engine='bash', count_lines}
python testdata.py --users=/Users/danielranlehmann/Desktop/test-users.json --count=25
```

### Database
**Note: You need to have valid auth credentials before you're allowed to write to the database.**<br/>
Upload test users to '/users' location in the database.
```{r, engine='bash', count_lines}
python database.py --set=/users /Users/danielranlehmann/Desktop/test-users.json --email=YOUR_EMAIL_HERE --password=YOUR_PASSWORD_HERE
```
Upload test products to '/products' location in the database.
```{r, engine='bash', count_lines}
python database.py --set=/products /Users/danielranlehmann/Desktop/test-products.json --email=YOUR_EMAIL_HERE --password=YOUR_PASSWORD_HERE
```
Push a new accepted model, to the database.
```{r, engine='bash', count_lines}
python database.py --push=DATABASE_LOCATION PATH_TO_LOCAL_JSON_FILE --email=YOUR_EMAIL_HERE --password=YOUR_PASSWORD_HERE
```
Link imageURLs to a specific object example.
```{r, engine='bash', count_lines}
python database.py --set=products/$product-id/imageURLs PATH_TO_LOCAL_JSON_FILE --email=YOUR_EMAIL_HERE --password=YOUR_PASSWORD_HERE
```

### Storage 
Generate and upload thumbnails from multiple images
```{r, engine='bash', count_lines}
python storage.py --put=/product-images/$product-id/ IMG_PATH_0 IMG_PATH_1 --email=YOUR_EMAIL_HERE --password=YOUR_PASSWORD_HERE --thumbnails=1
```
Upload almost any file to storage.
```{r, engine='bash', count_lines}
python storage.py --put=/legal-contract.pdf /Users/danielranlehmann/Desktop/Desktop\ April/EksamensOpgaveInter2018.pdf  --email=YOUR_EMAIL_HERE --password=YOUR_PASSWORD_HERE --thumbnails=0
```


