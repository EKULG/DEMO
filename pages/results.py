import json

import pandas as pd
import streamlit as st
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

from mongo_db import return_collection
from authentication import display_login_page


if 'username' not in st.session_state:
    st.session_state['username'] = None
    
# LOGIN PAGE
if st.session_state['username'] is None:
    display_login_page()
    st.stop()


def find_closest_company(row):
    company_names = [exp['company'] for exp in row['experiences']]
    closest_match, score = process.extractOne(row['PitchBook Company Name'], company_names, scorer=fuzz.partial_ratio)
    # Find the dictionary with the matching company name
    closest_dict = next((exp for exp in row['experiences'] if exp['company'] == closest_match), None)
    return closest_dict


def return_pitchbook_desc(pitchbook_company):
    query = {'LinkedinURL': {'$regex': pitchbook_company, '$options': 'i'}}  # 'i' makes it case-insensitive
    projection = {'_id': 0, 'description': 1} 
    pitchbook_results = pitchbook_collection.find(query, projection)
    pitchbook_results = list(pitchbook_results)
    return pitchbook_results[0]['description']


if 'search_query_id' in st.session_state:
    st.title('SEARCH RESULTS')

    pitchbook_collection = return_collection(collection_name='URLS')
    clean_linkedin_collection = return_collection(collection_name='linkedinClean')
    query = {'search_query_id': "4c76bec9-3769-4731-b9f3-a40f1efc426b"}
    results = clean_linkedin_collection.find(query)
    results = list(results)
    search_results = pd.DataFrame(results)

    search_results['Name'] = search_results['nameAndBio'].apply(lambda x: json.loads(x)['name'])
    search_results['bioDescription'] = search_results['nameAndBio'].apply(lambda x: json.loads(x)['bioDescription'])

    search_results['Relevant Pitchbook Experience'] = search_results.apply(find_closest_company, axis=1)

    search_results['Most Relevant Company'] = search_results['Relevant Pitchbook Experience'].apply(lambda x: x['company'])

    search_results['Most Relevant Role'] = search_results['Relevant Pitchbook Experience'].apply(lambda x: x['title'])

    search_results['Tenure'] = search_results['Relevant Pitchbook Experience'].apply(lambda x: x['duration'] if x['end_date'] != 'Present' else x['end_date'])

    search_results['Experience Summary'] = search_results['Relevant Pitchbook Experience'].apply(lambda x: x['description'])

    # NOTE - ineffective way of doing this. Your calling for the same company
    search_results['PitchBook Company Description'] = search_results['PitchBook Company Name'].apply(return_pitchbook_desc)

    search_results['Current Company'] = search_results['experiences'].apply(lambda x: x[0]['company'])
    search_results['Current Role'] = search_results['experiences'].apply(lambda x: x[0]['title'])

    search_results['linkedInURL'] = search_results['linkedInURL'].apply(lambda x: x[0])

    cols = ['Name', 'bioDescription', 'Most Relevant Role', 'Most Relevant Company', 'Tenure', 'Experience Summary',
            'PitchBook Company Description', 'Current Company', 'Current Role', 'linkedInURL']

    display_results = search_results[cols]
    
    display_results

else:
    st.markdown("### No search has been submitted")