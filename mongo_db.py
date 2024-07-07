from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pandas as pd
import urllib.parse


def standardize_key(key):
    if "private or public company?" in key:
        return 'private or public company?'
    elif "current revenue?" in key:
        return 'current revenue?'
    elif "industry is" in key:
        return 'industry'
    elif "When was" in key and "founded" in key:
        return 'founded'
    elif "When was" in key and "acquired" in key:
        return 'acquired'
    elif "Where is" in key and "headquartered" in key:
        return 'headquarters'
    elif "acquired by" in key or "Who acquired" in key:
        return 'acquired by'
    elif "competitors" in key:
        return 'competitors'
    elif "investors" in key:
        return 'investors'
    elif "valuation" in key:
        return 'valuation'
    elif "CEO" in key:
        return 'CEO'
    elif "founder" in key:
        return 'founder'
    elif "funding" in key:
        return 'funding'
    elif "parentCompany" in key:
        return 'parentCompany'
    elif "formerlyKnownAs" in key:
        return 'formerlyKnownAs'
    elif "Latest Deal Amount" in key:
        return 'Latest Deal Amount'
    elif "What is the size of" in key:
        return 'company size'
    elif "Investments" in key:
        return 'Investments'
    elif "Employees" in key:
        return 'Employees'
    elif "otherIndustries" in key:
        return 'otherIndustries'
    else:
        return key


def standardize_keys(document):
    standardized_document = {}
    for key, value in document.items():
        standardized_key = standardize_key(key)
        if standardized_key in standardized_document:
            if isinstance(standardized_document[standardized_key], list):
                standardized_document[standardized_key].append(value)
            else:
                standardized_document[standardized_key] = [standardized_document[standardized_key], value]
        else:
            standardized_document[standardized_key] = value
    return standardized_document


uri_template = "mongodb+srv://{username}:{password}@serverlessinstance0.fs8o4zf.mongodb.net/?retryWrites=true&w=majority&appName=ServerlessInstance0"

username = "lukeg"
password = "v3iJ2OSNoHKooUYA"

username = urllib.parse.quote_plus(username)
password = urllib.parse.quote_plus(password)

uri = uri_template.format(username=username, password=password)

client = MongoClient(uri, server_api=ServerApi('1'))

db_name = 'HotelData'
collection_name = 'URLS'

db = client[db_name]
collection = db[collection_name]

query = {}
results = collection.find(query).limit(300)
results = list(results) # needed as the cursor object is weird when you interact with it directly so save variable as list then interact with

standardized_results = [standardize_keys(doc) for doc in results]

data = pd.DataFrame(standardized_results)

breakpoint()

# Filter out all the data that doesn't fall into one of the predefined columns
# See if I can get a percentage of the dirt data and see how small this is
