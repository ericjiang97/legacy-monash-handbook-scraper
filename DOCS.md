# Monash Handbook Scraper

To initialize you will need to pass in the year, this will run the setup of the scraper

```python
if __name__ == "__main__":
    scraper = Scraper(2007)
```

To run the scraper, you will need to run `scraper.setup()`, this will download all the data into the `self.data` which is using the pandas module (so you can manipulate it however you want)

## Exporting as csv

Simply run `scraper.export_as_csv(fileName)` will export it to the exports directory

```python
scraper.export_as_csv('2008.csv')
```

The above example will export the file to `exports/2008.csv`
