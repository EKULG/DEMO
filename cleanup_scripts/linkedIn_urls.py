import os 
import requests
import dotenv
from bs4 import BeautifulSoup

from mongo_db import return_pitchbook_data

dotenv.load_dotenv()


pe_no_url_query = {
    '$and': [
        {"financingStatus": "Private Equity-Backed"}, # Placeholder for the actual column name
        {"LinkedinURL": ""} # Placeholder for the actual LinkedIn column name
        
    ]
}

data = return_pitchbook_data(query=pe_no_url_query)


breakpoint()


api_key = os.environ.get('SCRAPER_API_KEY')
target_url = "" # TODO fill with a google search for the company linkedIn
scraperapi_url = f"" # TODO fill with scraperapi url

response = requests.get(scraperapi_url)

soup = BeautifulSoup(response.text, "html.parser")

# NOTE - if we just want the first results from google - do this
# first_linkedin_href = soup.find("a", href=lambda href: href and "www.linedin.com" in href)
all_linkedin_hrefs = soup.find_all("a", href=lambda href: href and "www.linedin.com" in href)
linkedin_url = all_linkedin_hrefs[0]['href']


# NOTE - can perhaps use this data as a way to validate if correct company
first_result_text = soup.find("div", class_="MjjYud")


breakpoint()