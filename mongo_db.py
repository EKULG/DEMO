import os
import uuid
import urllib.parse

import dotenv
import pandas as pd
import streamlit as st
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


dotenv.load_dotenv()


@st.cache_resource
def mongodb_client():
    uri_template = "mongodb+srv://{username}:{password}@serverlessinstance0.fs8o4zf.mongodb.net/?retryWrites=true&w=majority&appName=ServerlessInstance0"

    username = urllib.parse.quote_plus(os.environ.get('MONGO_USERNAME'))
    password = urllib.parse.quote_plus(os.environ.get('MONGO_PASSWORD'))

    uri = uri_template.format(username=username, password=password)

    client = MongoClient(uri, server_api=ServerApi('1'))

    return client


def return_collection(collection_name):  
    db_name = 'HotelData'
    client = mongodb_client()
    
    db = client[db_name]
    collection = db[collection_name]
    
    return collection


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


def create_search_query(role, region, industry, pe_backed=True):
    search_query_collection = return_collection(collection_name="search_query")
    
    unique_id = str(uuid.uuid4())
    linkedin_company_names = li_url_from_pitchbook(region, industry)
    
    search_query = {
        "search_query_id": unique_id,
        "role": role,
        "region": region,
        "industry": industry,
        "pe_backed": pe_backed,
        "linkedin_company_name": linkedin_company_names,
        "linkedin_scrape_status": "todo"
    }
    
    search_query_collection.insert_one(search_query)
    
    return unique_id


def return_pitchbook_data(query={}, standardize=True, limit=3000):
    collection = return_collection(collection_name='URLS')
    results = collection.find(query).limit(limit)
    results = list(results) # needed as the cursor object is weird when you interact with it directly so save variable as list then interact with

    if standardize:
        standardized_results = [standardize_keys(doc) for doc in results]
        data = pd.DataFrame(standardized_results)
    else:
        data = pd.DataFrame(results)
    
    return data


@st.cache_data(show_spinner=False)
def pe_backed_with_url():
    collection = return_collection(collection_name='URLS')
    pe_with_url_query = {
        '$and': [
            {"financingStatus": "Private Equity-Backed"},  # Ensure financing status is "Private Equity-Backed"
            {"LinkedinURL": {"$ne": ""}},  # Ensure LinkedinURL is not an empty string
            {"corporateOffice": {"$nin": [None, False, "", [], {}]}},
        ]
    }
    documents = collection.find(pe_with_url_query, {"primaryIndustry": 1, "corporateOffice": 1, "_id": 0})
    results = list(documents)
    
    pe_backed_data = pd.DataFrame(results)
    
    pe_backed_data['Region'] = pe_backed_data['corporateOffice'].apply(lambda region: region.split(",")[-1].strip())
    
    return pe_backed_data[['Region', 'primaryIndustry']]


def li_url_from_pitchbook(region, industry):
    collection = return_collection(collection_name='URLS')
    # MongoDB query
    query = {
        "primaryIndustry": industry,
        "financingStatus": "Private Equity-Backed",
        "LinkedinURL": {"$ne": ""},  # Ensure LinkedinURL is not an empty string
        "corporateOffice": {"$regex": region, "$options": "i"}  # Search for the region within the corporateOffice string
    }

    # Execute the query
    documents = collection.find(query)
    results = list(documents)
    
    # Extract company name from Lini
    linkedin_company_names = [res['LinkedinURL'].split('/')[-1] for res in results]
    
    return linkedin_company_names


if __name__ == "__main__":
    # pe_backed_with_url()
    # results = li_url_from_pitchbook(region="San Antonio", industry="Regional Banks")
    create_search_query("CFO", region="San Antonio", industry="Regional Banks")
    
    breakpoint()











# NOTE - for issue with column names
# Filter out all the data that doesn't fall into one of the predefined columns
# See if I can get a percentage of the dirt data and see how small this is