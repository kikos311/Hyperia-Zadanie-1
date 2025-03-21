# Author: Kristian Siska
# Last change: 21.3.2025
# Contact: kristiansiska@gmail.com
# Description: This script scrapes leaflet data from the Prospektmaschine website and saves it to a JSON file.


# For html requests 
import requests

# For parsing html content
from bs4 import BeautifulSoup

# For date formatting 
from datetime import datetime

# For regular expressions in the date parsing in case of some weird date formats
import re

# For saving the data to a JSON file 
import json


# The scraper class because the script should probably be object-oriented
class ProspektmaschineScraper:
    # The url of the target website 
    # The target url is the one that is scraped
    BASE_URL = "https://www.prospektmaschine.de"
    TARGET_URL = f"{BASE_URL}/hypermarkte/"


    # The constructor of the class
    # Just starts a requests session
    def __init__(self):
        self.session = requests.Session()
    


    # Fetches the page content
    # Returns the html content of the page
    def fetch_page(self, url):

        response = self.session.get(url)
        response.raise_for_status()
        response_text = response.text

        return response_text
    

    # Parses the page content
    # Returns a list of dictionaries with the leaflet data
    def parse_page(self, html):
        
        # Usage of the BeautifulSoup library to parse the html content
        # We create a soup object from the html content
        soup = BeautifulSoup(html, "html.parser")
        # List for the leaflets
        leaflets = []
        # Current time in the format of "YYYY-MM-DD HH:MM:SS for later use
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        

        # I had to search for the classes in the html content. Leaflets are either in the brochure-thumb or letaky-grid classes
        # It is going through the leaflets and extracting the data by the classes and tags of the html content
        # For every data that it can't find it sets it to "Unknown"
        for item in soup.select(".brochure-thumb"):

            # The title of the leaflet
            title_tag = item.select_one(".grid-item-content strong")
            title = title_tag.get_text(strip=True) if title_tag else "Unknown"

            # The thumbnail of the leaflet
            img_tag = item.select_one(".img-container img")
            thumbnail = img_tag.get("src") or img_tag.get("data-src", "") if img_tag else ""

            # The shop name of the leaflet
            shop_tag = item.select_one(".grid-logo img")
            shop_name = shop_tag["alt"].replace("Logo ", "") if shop_tag else "Unknown"
            
           
            # The date of the leaflet
            # I use my functions to format the date
            # Some leaflets have a range of dates, some have only one date so I had to use regular expressions to extract the dates
            date_tag = item.select_one(".grid-item-content small.hidden-sm") or item.select_one(".grid-item-content small.visible-sm")
            date_text  = date_tag.get_text(strip=True) if date_tag else ""
          


            match_range = re.search(r"(\d{2}\.\d{2}\.\d{4}) - (\d{2}\.\d{2}\.\d{4})", date_text)
            match_single = re.search(r"(?:von \w+ )?(\d{2}\.\d{2}\.\d{4})", date_text)
            
            # If the date is in a range it will extract the dates
            # If the date is a single date it will extract the date and set the valid_to to "Unknown"   
            if match_range:
                valid_from, valid_to = match_range.groups()
            elif match_single:
                valid_from = match_single.group(1)
                valid_to = "Unknown"
            else:
                valid_from, valid_to = "Unknown", "Unknown"

            
            
            # Our list of dictionaries with the leaflet data
            leaflets.append({
                "title": title,
                "thumbnail": thumbnail,
                "shop_name": shop_name,
                "valid_from": valid_from,
                "valid_to": valid_to,
                "parsed_time": now
            })
        
        return leaflets
    
    # Function to parse the dates
    # Returns the valid from and valid to dates
    def parse_dates(self, date_text):
        
        date_parts = date_text.split(" - ")
        if len(date_parts) == 2:
            valid_from = self.format_date(date_parts[0])
            valid_to = self.format_date(date_parts[1])
        else:
            valid_from = valid_to = "Unknown"
        return valid_from, valid_to
    
    # Function to format the date
    # Returns the date in the format of "YYYY-MM-DD"
    def format_date(self, date_str):
       
        try:
            return datetime.strptime(date_str, "%d.%m.%Y").strftime("%Y-%m-%d")
        except ValueError:
            return "Unknown"
    
    # Just saving the data to a JSON file
    # The data is the data that is saved to the file
    def save_to_json(self, data, filename="leaflets.json"):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    

    # The main function of the script
    # It runs the scraper and saves the data to a JSON file
    def run(self):
        html = self.fetch_page(self.TARGET_URL)
        leaflets = self.parse_page(html)
        self.save_to_json(leaflets)
        print(f"Scraped {len(leaflets)} leaflets and saved to leaflets.json")



# Starting the script
if __name__ == "__main__":
    scraper = ProspektmaschineScraper()
    scraper.run()


