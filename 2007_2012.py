from urllib.request import urlopen
from bs4 import BeautifulSoup
from tqdm import tqdm
from termcolor import colored
import pandas as pd
import re
import json
import os

HTML_PARSER = "html.parser"


class Scraper:
    def __init__(self, year):
        print(colored(f'Initializing scraper with year: {year}', 'yellow'))
        self.root_url = f"http://www.monash.edu.au/pubs/{year}handbooks/units"
        self.units = {}
        print(colored('Initialized!', 'green'))

    def setup(self):
        print(colored('Running setup', 'yellow'))
        self.unit_characters = self.get_unit_characters()
        # self.unit_characters = ['A']
        pbar = tqdm(self.unit_characters)
        unit_links = []
        for character in pbar:
            unit_links += self.get_unit_codes(character.lower())
            pbar.set_description(
                f"Getting units which code start with: {character}")
        print(colored('Successfully got all unit codes!', 'green'))

        print(colored('Getting unit info for all units', 'yellow'))
        self.unit_links = unit_links
        pbar = tqdm(self.unit_links)
        for unit_link in pbar:
            unit_info = self.get_unit_info(unit_link)
            pbar.set_description(f"Processing unit: {unit_link}")
            self.units[unit_info['unit_code']] = unit_info
        print(colored('Successfully got all unit info!', 'green'))
        self.data = pd.DataFrame(self.units).transpose()

    def export_as_csv(self, file_name):
        # check if directory exists
        does_export_dir_exist = os.path.isdir('exports/')
        if not does_export_dir_exist:
            os.mkdir('exports/')
        self.data.to_csv(f'exports/{file_name}')
        print(colored(f'Successfully exported file to {file_name}!', 'green'))

    def get_unit_characters(self):
        page = urlopen(f"{self.root_url}/index-bycode.html")
        soup = BeautifulSoup(page, HTML_PARSER)
        alphabet = soup.find("ul", attrs={"class": "index-code index"})
        # print(alphabet)
        avail_chars = []
        for char in alphabet.find_all("li"):
            avail_chars.append(char.text)
        return avail_chars

    def get_unit_codes(self, character):
        page = urlopen(f"{self.root_url}/index-bycode-{character}.html")
        soup = BeautifulSoup(page, HTML_PARSER)
        units_list = soup.find("ul", attrs={"class": "fixed"})
        unit_codes = []
        for unit in units_list.find_all("li"):
            unit_codes.append(
                unit.find("a")["href"].strip('.html').split('/')[-1])
        return unit_codes

    def get_unit_info(self, unit_code):
        url = f"{self.root_url}/{unit_code}.html"
        page = urlopen(url)
        soup = BeautifulSoup(page, HTML_PARSER)
        unit_info = {}

        synopsis_heading = soup.find('h4', text="Synopsis")
        if (synopsis_heading != None):
            unit_info['synopsis'] = synopsis_heading.find_next_sibling(
                'p').text.strip('\n')
        else:
            unit_info['synopsis'] = None

        offerings_heading = soup.find('h4', text="Offered")
        offerings = (offerings_heading.find_next_sibling(
            'p').text).strip('\n').split('\n')
        unit_info['offerings'] = offerings

        breadcrumbs = soup.find('div', attrs={"id": "breadcrumbs"})
        title = breadcrumbs.find_next_sibling('h1').text.split(' - ')
        unit_info['unit_code'] = title[0]
        unit_info['unit_name'] = title[1]

        quick_info = breadcrumbs.find_next_sibling('h2').text

        sca_band_regex = re.search(r'SCA Band ([0-3])', quick_info)
        if(sca_band_regex == None):
            unit_info['sca_band'] = None
        else:
            unit_info['sca_band'] = int(sca_band_regex.group(1))

        eftsl_regex = re.search(r'([0-9]\.[0-9]{1,3}) EFTSL', quick_info)
        if(eftsl_regex == None):
            unit_info['eftsl'] = None
        else:
            unit_info['eftsl'] = eftsl_regex.group(1)

        credit_points_regex = re.search(r'([0-9]+) points', quick_info)
        if(credit_points_regex == None):
            unit_info['credit_points'] = None
        else:
            unit_info['credit_points'] = int(
                credit_points_regex.group(1))

        assessment_heading = soup.find('h4', text="Assessment")
        if(assessment_heading != None):
            unit_info['assessments'] = (assessment_heading.find_next_sibling(
                'p').get_text(strip=True, separator="\n").replace('\n', ', '))
        else:
            unit_info['assessments'] = None

        contact_hours_heading = soup.find('h4', text="Contact hours")
        if(contact_hours_heading != None):
            unit_info['contact_hours'] = (contact_hours_heading.find_next_sibling(
                'p').get_text(strip=True, separator="\n").replace('\n', ', '))
        else:
            unit_info['contact_hours'] = None
        return unit_info


if __name__ == "__main__":
    year = int(input('Enter handbook year: '))
    if(year < 2012 and year > 2007):
        scraper = Scraper(2008)
        scraper.setup()
        scraper.export_as_csv('2008.csv')
    else:
        print(colored('Year has to be between 2007 and 2012', 'red'))
