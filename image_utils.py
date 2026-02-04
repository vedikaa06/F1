import requests
import pandas as pd
import time

# Your API Credentials
API_KEY = "e39fdab6fb0796adcada066eec8c6c67"
BASE_URL = "https://v1.formula-1.api-sports.io"
HEADERS = {'x-apisports-key': API_KEY}

def fetch_f1_image(endpoint, search_query):
    """
    Generic function to fetch images for drivers or teams.
    endpoint: 'drivers' or 'teams'
    search_query: The name of the driver or team
    """
    url = f"{BASE_URL}/{endpoint}"
    params = {'search': search_query}
    
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        data = response.json()
        
        if data['response'] and len(data['response']) > 0:
            # Return the image link from the first search result
            return data['response'][0]['image']
    except Exception as e:
        print(f"Error fetching {search_query}: {e}")
    
    return None # Returns None if not found

def sync_all_images():
    print("🔄 Syncing Driver and Team images...")
    
    # 1. Sync Driver Images (using names from your driver_lookup.csv)
    drivers_df = pd.read_csv('driver_lookup.csv')
    # We only fetch images for drivers if we haven't already to save API quota
    drivers_df['image_url'] = drivers_df['driver_name'].apply(lambda x: fetch_f1_image('drivers', x))
    drivers_df.to_csv('driver_image_lookup.csv', index=False)
    
    # 2. Sync Team Images (using names from your team_lookup.csv)
    teams_df = pd.read_csv('team_lookup.csv')
    teams_df['logo_url'] = teams_df['name'].apply(lambda x: fetch_f1_image('teams', x))
    teams_df.to_csv('team_image_lookup.csv', index=False)

    print("✅ All images synced to local CSV lookups!")

if __name__ == "__main__":
    sync_all_images()