from .keys import PEXELS_API_KEY, OPEN_WEATHER_API_KEY
import requests
import json


def get_photo(city, state):
    # Create a dictionary for the headers to use in the request
    headers = {"Authorization": PEXELS_API_KEY}
    params = {
        "per_page": 1,
        "query": city + " " + state,
    }
    # Create the URL for the request with the city and state
    url = "https://api.pexels.com/v1/search"
    # Make the request
    response = requests.get(url, params=params, headers=headers)
    # Parse the JSON response
    content = json.loads(response.content)
    # Return a dictionary that contains a `picture_url` key and
    #   one of the URLs for one of the pictures in the response
    try:
        return {"picture_url": content["photos"][0]["src"]["original"]}
    except:
        return {"picture_url": None}


def get_weather_data(city, state):
    # headers = {"Authorization": OPEN_WEATHER_API_KEY}
    params = {
        "q": f"{city}, {state}, USA",
        "appid": OPEN_WEATHER_API_KEY,
        "limit": 1,
    }
    # Create the URL for the geocoding API with the city and state
    url = "http://api.openweathermap.org/geo/1.0/direct"
    # Make the request
    response = requests.get(url, params=params)
    # Parse the JSON response
    content = json.loads(response.content)
    # Get the latitude and longitude from the response
    try:
        lat = content[0]["lat"]
        lon = content[0]["lon"]
    except:
        lat = None
        lon = None

    # Create the URL for the current weather API with the latitude
    #   and longitude
    # Make the request
    # Parse the JSON response
    # Get the main temperature and the weather's description and put
    #   them in a dictionary
    # Return the dictionary

    params2 = {"lat": lat, "lon": lon, "appid": OPEN_WEATHER_API_KEY}
    url2 = "https://api.openweathermap.org/data/2.5/weather"
    response2 = requests.get(url2, params=params2)
    content2 = json.loads(response2.content)
    try:
        return {
            "temp": content2["main"]["temp"],
            "description": content2["weather"][0]["description"],
        }
    except:
        return {"temp": None, "description": None}
