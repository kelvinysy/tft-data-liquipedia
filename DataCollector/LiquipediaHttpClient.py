import requests
import time
import json
import os
import datetime

def _fetch_match_data(response_fn, starting_pageid: int, max_pageid: int, output_dir: str = ".", filename_prefix: str = "match-pageid"):
    """Shared fetch loop. response_fn(params) should return a requests.Response."""
    max_backoff: int = 2 * 60 * 60  # 2 hours in seconds

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    updated_pages = []
    seen_not_written_pages = []
    pages_iterated = 0

    pageid = starting_pageid
    while pageid <= max_pageid:
        params = {
            "limit": 1000,
            "wiki": "tft",
            "conditions": f"[[pageid::{pageid}]]"
        }

        backoff = 60  # Backoff starts at 60 seconds for 429 errors
        success = False

        while not success:
            print(f"Fetching pageid {pageid}...")
            try:
                response = response_fn(params)

                if response.status_code == 200:
                    backoff = 60
                    data = response.json()

                    # Check if the result is not empty. Liquipedia typically returns {"result": [...]}
                    results = data.get("result", [])

                    if data and (isinstance(data, list) and len(data) > 0 or isinstance(data, dict) and results):
                        filename = os.path.join(output_dir, f"{filename_prefix}-{pageid}.json")
                        
                        save_new = True
                        if os.path.exists(filename):
                            try:
                                with open(filename, 'r', encoding='utf-8') as f:
                                    existing_data = json.load(f)
                                if existing_data == data:
                                    print(f"Data for {filename} is unchanged. Skipping.")
                                    save_new = False
                                else:
                                    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                                    old_filename = os.path.join(output_dir, f"{filename_prefix}-{pageid}-old-{timestamp}.json")
                                    os.rename(filename, old_filename)
                                    print(f"Data changed. Renamed existing to {old_filename}")
                            except Exception as e:
                                print(f"Error reading/parsing existing file {filename}: {e}. Overwriting.")
                        
                        if save_new:
                            with open(filename, 'w', encoding='utf-8') as f:
                                json.dump(data, f, ensure_ascii=False, indent=4)
                            print(f"Saved {filename}")
                            updated_pages.append(pageid)
                        else:
                            seen_not_written_pages.append(pageid)
                    else:
                        print(f"Result empty for pageid {pageid}. Not saving.")

                    success = True
                    pageid += 1
                    pages_iterated += 1

                    if pages_iterated % 20 == 0:
                        print(f"--- Checkpoint: Iterated {pages_iterated} pages ---")
                        print(f"Updated pages in this run: {updated_pages}")
                        print(f"Seen but not written pages in this run: {seen_not_written_pages}")

                    # API requests should be max 1 per minute according to req
                    print("Waiting 60 seconds to respect rate limit...")
                    time.sleep(60)

                elif response.status_code == 429:
                    print(f"Rate limited (429). Backing off for {backoff} seconds...")
                    time.sleep(backoff)
                    backoff = min(backoff * 2, max_backoff)  # type: ignore
                else:
                    print(f"Error {response.status_code}: {response.text} \n-----\n {response.reason} \n-----\n {response.headers} \n-----\n")
                    print("Waiting 60 seconds before retrying...")
                    time.sleep(60)
            except Exception as e:
                print(f"Request failed with exception: {e}")
                print("Waiting 60 seconds before retrying...")
                time.sleep(60)


def fetch_match_data_get(base_url: str, api_key: str, starting_pageid: int, max_pageid: int, output_dir: str = ".", filename_prefix: str = "match-pageid"):
    """Fetch match data using a GET request. API key is sent as an Authorization header."""
    headers = {
        "User-Agent": "PythonClient (kelvin.yeung@rocketmail.com)",
        "Authorization": f"Apikey {api_key}"
    }
    _fetch_match_data(
        lambda params: requests.get(base_url, headers=headers, params=params),
        starting_pageid, max_pageid, output_dir, filename_prefix
    )


def fetch_match_data_post(base_url: str, api_key: str, starting_pageid: int, max_pageid: int, output_dir: str = ".", filename_prefix: str = "match-pageid"):
    """Fetch match data using a POST request. API key is sent as a parameter in the request body."""
    headers = {
        "User-Agent": "PythonClient (kelvin.yeung@rocketmail.com)",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    def post_fn(params):
        return requests.post(base_url, headers=headers, data={**params, "apikey": api_key})

    _fetch_match_data(post_fn, starting_pageid, max_pageid, output_dir, filename_prefix)

if __name__ == "__main__":
    # Placeholder for the API key, since it will be provided later
    api_key = os.environ.get("LIQUIPEDIA_API_KEY", "YOUR_API_KEY_HERE")
    
    # Change to the pageid you want to stop at
    limit_pageid = 12000
    starting_pageid = 734
    base_url = "https://api.liquipedia.net/api/v3/match"
    filename_prefix = "v3-match-pageid"

    # replace with get or post depending on endpoint
    fetch_match_data_get(base_url, api_key, starting_pageid, limit_pageid, "./data", filename_prefix)
