import requests
import streamlit as st

# Your API Key
API_KEY = "e39fdab6fb0796adcada066eec8c6c67"
BASE_URL = "https://v1.formula-1.api-sports.io/drivers"

@st.cache_data
def get_driver_image(driver_name):
    """
    Retrieves the image URL for a given driver name from API-Sports.
    """
    headers = {
        'x-apisports-key': API_KEY
    }
    
    # Search for the driver by name
    params = {'search': driver_name}
    
    try:
        response = requests.get(BASE_URL, headers=headers, params=params)
        data = response.json()
        
        # Check if we got a valid response and at least one driver
        if data['response']:
            # Return the 'image' field from the first result
            image_url = data['response'][0].get('image')
            return image_url
        else:
            # Fallback if driver not found
            return "https://www.formula1.com/etc/designs/fom-website/images/f1_logo.svg"
            
    except Exception as e:
        print(f"Error fetching image: {e}")
        return None