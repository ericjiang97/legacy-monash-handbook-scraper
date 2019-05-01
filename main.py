from modules import zerosevenscraper
from modules import twelvescraper
from termcolor import colored


if __name__ == "__main__":
    year = int(input('Enter handbook year: '))
    if(year < 2012 and year > 2007):
        scraper = oldscraper.Scraper(year)
        scraper.setup()
        scraper.export_as_csv(f'{year}.csv')
    elif(year >= 2012 and year < 2016):
        scraper = twelvescraper.Scraper(year)
        scraper.setup()
        scraper.export_as_csv(f'{year}.csv')
    else:
        print(colored('Year has to be between 2008 and 2012', 'red'))
