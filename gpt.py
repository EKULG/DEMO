import os
import json

from openai import OpenAI


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def clean_linkedin_data(input_string):
    # Define the JSON schema directly in the request
    schema = {
        "type": "object",
        "properties": {
            "experiences": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": { "type": "string" },
                        "company": { "type": "string" },
                        "employment_type": { "type": "string" },
                        "start_date": { "type": "string" },
                        "end_date": { "type": ["string", "null"] },
                        "duration": { "type": "string" },
                        "location": { "type": "string" },
                        "description": { "type": ["string", "null"] }
                    },
                    "required": ["title", "company", "employment_type", "start_date", "end_date", "duration", "location", "description"],
                    "additionalProperties": False
                }
            }
        },
        "required": ["experiences"],
        "additionalProperties": False
    }
    
    # Define the prompt to instruct the model on what to do
    prompt = f"""
    I have a string of text containing an individual's professional experience. The string may contain duplicate information, spelling errors, nonsensical words, or sentences that have been split halfway. Your task is to clean this string, remove any duplicates, fix errors, and structure it into a JSON format according to the following schema:

    {schema}

    Here is the string you need to clean and structure:

    {input_string}

    Please provide the cleaned and structured JSON output.
    """
    
    messages = [
        {"role": "user", "content": prompt},
    ]
    

    response_format = {
        "type": "json_schema",
        "json_schema": {
        "name": "experiences",
        "strict": True,
        "schema": schema
        }
    }

    # Make the API call
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini-2024-07-18",
        messages=messages,
        temperature=0.0,  # Keep it deterministic
        response_format=response_format
    )
    
    structured_output = completion.choices[0].message.content.strip()

    # Return the structured JSON output
    return json.loads(structured_output)

# Example input string
input_string = """
nce

Stout
1 yr 10 mos

Associate

Full-time

Oct 2023 — Present - 11 mos

San Diego, California, United States

Analyst

Full-time

Nov 2022 - Oct 2023 + 1 yr

San Diego, California, United States

Valuation Analyst

VANTAGE POINT ADVISORS (Acquired by Stout) - Full-time
Jun 2022 — Nov 2022 - 6 mos
San Diego, California, United States

Assurance Staff

EY - Full-time
Jan 2021 - Jun 2022 - 1yr6 mos
San Diego, California, United States

Assurance Intern

Ernst & Young - Internship
Jul 2020 - Aug 2020 - 2 mos
San Diego, California, United States

Intern

Texas Exchange Bank - Internship
Feb 2019 — Mar 2020 - 1yr 2 mos
Fort Worth, Texas, United States

HILO MULAUUIIAL PIUYyialll

Commonwealth Bank of Australia - Internship
Jun 2019 —- Aug 2019 - 3 mos
Sydney, New South Wales, Australia

Financial Advisor Intern

Blankinship & Foster, LLC
Jun 2018 - Aug 2018 - 3 mos
Solana Beach, California

Bag Room Attendant

Lomas Santa Fe Country Club
May 2017 - Aug 2017 - 4 mos
Solana Beach, CA

Chief Financial Officer

Global Vantage
Sep 2012 - Jun 2016 - 3 yrs 10 mos
Pacific Ridge School
"""


if __name__ == "__main__":
    output = clean_linkedin_data(input_string)
    print(output)