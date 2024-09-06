from mongo_db import return_collection
from gpt import clean_linkedin_data


raw_linkedin_collection = return_collection(collection_name='linkedinRaw')
clean_linkedin_collection = return_collection(collection_name='linkedinClean')
query={}
results = raw_linkedin_collection.find(query)
results = list(results)


for linkedin_raw in results:
    for company, linkedin_people in linkedin_raw['companies'].items():
        for person in linkedin_people:
            if person in ['Out of Network', 'No profile results']:
                continue
            else:
                if 'expirence' in person:
                    cleaned_experiences = clean_linkedin_data(person['expirence'])
                    person.pop('expirence')
                    cleaned_li = {**person, **cleaned_experiences}
                    cleaned_li['search_query_id'] = linkedin_raw['search_query_id']
                    cleaned_li['PitchBook Company Name'] = company
                    clean_linkedin_collection.insert_one(cleaned_li)