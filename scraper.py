from urllib.request import urlopen
from bs4 import BeautifulSoup
from tqdm import tqdm
import re
import json

HTML_PARSER = "html.parser"


class Scraper:
    def __init__(self, year):
        self.root_url = f"http://www.monash.edu.au/pubs/{year}handbooks/units"
        self.units = {}
        self.setup()
        pass

    def setup(self):
        self.unit_characters = self.get_unit_characters()
        unit_links = []
        for character in self.unit_characters:
            unit_links += self.get_unit_codes(character.lower())
        self.unit_links = unit_links
        pbar = tqdm(self.unit_links)
        for unit_link in pbar:
            unit_info = self.get_unit_info(unit_link)
            pbar.set_description("Processing %s" % unit_link)
            self.units[unit_info['unit_code']] = unit_info

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
        offerings_dict = {}
        offerings = (offerings_heading.find_next_sibling(
            'p').text).strip('\n').split('\n')
        if(len(offerings) > 1):
            for offering in offerings:
                current_offer = offering.split(' ')
                offer_location = current_offer[0]
                offer_teaching_period = ' '.join(current_offer[1:])

                if(offer_location not in offerings_dict):
                    offerings_dict[offer_location] = [offer_teaching_period]
                else:
                    offerings_dict[offer_location].append(
                        offer_teaching_period)

            unit_info['offerings'] = offerings_dict
        else:
            unit_info['offerings'] = None

        breadcrumbs = soup.find('div', attrs={"id": "breadcrumbs"})
        title = breadcrumbs.find_next_sibling('h1').text.split(' - ')
        unit_info['unit_code'] = title[0]
        unit_info['unit_name'] = title[1]

        quick_info = breadcrumbs.find_next_sibling('h2').text
        quick_info_dict = {}

        sca_band_regex = re.search(r'SCA Band ([0-3])', quick_info)
        if(sca_band_regex == None):
            quick_info_dict['sca_band'] = None
        else:
            quick_info_dict['sca_band'] = int(sca_band_regex.group(1))

        eftsl_regex = re.search(r'([0-9]\.[0-9]{1,3}) EFTSL', quick_info)
        if(eftsl_regex == None):
            quick_info_dict['eftsl'] = None
        else:
            quick_info_dict['eftsl'] = eftsl_regex.group(1)

        credit_points_regex = re.search(r'([0-9]+) points', quick_info)
        if(credit_points_regex == None):
            quick_info_dict['credit_points'] = None
        else:
            quick_info_dict['credit_points'] = int(
                credit_points_regex.group(1))

        unit_info['quick_info'] = quick_info_dict

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
    scraper = Scraper(2008)
    # print(scraper.get_unit_info('AMB1003'))
    print(json.dumps(scraper.units, sort_keys=True,
                     indent=2, separators=(',', ': ')))
