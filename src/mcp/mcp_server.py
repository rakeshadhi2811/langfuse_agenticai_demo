from fastmcp import FastMCP
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import requests
import asyncio
import logging
import sys

# Setup logging to debug the server
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Create an instance of the FastMCP class
mcp = FastMCP("MCP Server Class")

@mcp.tool("sum")
def calculator(a: float, b: float)->float:
    '''Perform a basic arithmetic operation on two numbers.'''
    return a + b
    
@mcp.tool("bmi_calculator")
def bmi_calculator(weight: float, height: float):
    '''Calculate BMI given weight and height.'''
    if height == 0:
        return float('inf')
    return weight / (height ** 2)


@mcp.tool("weather_prediction")
def weather_prediction(lat: float, long: float)->str:
    #Predict the weather for a given location based on latitude and longitude.
    
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": long,
        "hourly": "temperature_2m"
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        # Raise exception for bad status codes
        response.raise_for_status()

        # Convert response to JSON
        data = str(response.json())

        # Print JSON response
        print(data)

    except requests.exceptions.RequestException as e:
        print(f"Error calling API: {e}")
    return f"Predicted weather for ({lat}, {long}): data"

@mcp.tool("get_location_coordinates")
def get_location_coordinates(address_string: str)->dict:
    '''Get the coordinates for a given location.'''
    # Placeholder implementation - replace with actual location coordinate logic
    # Initialize Nominatim API with a custom user-agent string
    # (Nominatim requires a unique user-agent identifier to use their free service)
    geolocator = Nominatim(user_agent="my_coordinate_finder_application")
    
    try:
        # Request the location data from the API
        location = geolocator.geocode(address_string)
        
        if location:
            resp = str({
                "address": location.address,
                "latitude": location.latitude,
                "longitude": location.longitude
            })
            return resp
        else:
            return "Location not found."
            
    except GeocoderTimedOut:
        return "The geocoding service timed out. Please try again."
    
if __name__ == "__main__":
    logger.info("Starting MCP Server...")
    try:
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Error running server: {e}", exc_info=True)
        sys.exit(1)