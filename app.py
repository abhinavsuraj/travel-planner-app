import streamlit as st
import time
import folium
import pandas as pd
from streamlit_folium import folium_static
import requests
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', force=True)

# Environment variables
API_KEY = os.environ.get("GOOGLE_MAPS_API")  # Replace with your API key or use Streamlit's secrets
WEATHER_API_KEY = os.environ.get("OPENWEATHERMAP_API_KEY")  # Replace with your API key or use Streamlit's secrets

# Function to fetch weather details
def get_weather(location: str) -> str:
    try:
        base_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {"q": location, "appid": WEATHER_API_KEY, "units": "metric"}
        response = requests.get(base_url, params=params).json()
        if response.get("cod") == 200:
            data = response
            return f"{data['name']}: {data['weather'][0]['description']} at {data['main']['temp']}°C"
        return "Weather information unavailable."
    except Exception as e:
        logging.error(f"Error fetching weather: {e}")
        return "Weather information unavailable."

# Function to fetch coordinates of a location
def fetch_coordinates(location: str) -> dict:
    try:
        geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={location}&key={API_KEY}"
        response = requests.get(geocode_url).json()
        if response.get("status") == "OK":
            location = response['results'][0]['geometry']['location']
            return {"latitude": location['lat'], "longitude": location['lng']}
        logging.error(f"Failed to fetch coordinates: {response.get('status')}")
        return {}
    except Exception as e:
        logging.error(f"Error fetching coordinates: {e}")
        return {}

# Function to fetch nearby places
def fetch_nearby_places(lat: float, lng: float, radius: int, category: str) -> list:
    try:
        places_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius={radius * 1000}&type={category}&key={API_KEY}"
        response = requests.get(places_url).json()
        if response.get("status") == "OK":
            return response.get("results", [])
        return []
    except Exception as e:
        logging.error(f"Error fetching nearby places: {e}")
        return []

# Function to display a list of places
def display_places(places, category_name):
    if not places:
        st.write(f"No places found for {category_name}.")
        return

    st.write(f"Top {category_name.title()}s:")
    places_df = pd.DataFrame([
        {"Name": place["name"], "Rating": place.get("rating", "N/A")}
        for place in places
    ])
    st.table(places_df)

# Function to fetch country and currency
def get_country_and_currency(lat: float, lng: float) -> dict:
    try:
        geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}&key={API_KEY}"
        response = requests.get(geocode_url).json()
        if response.get("status") == "OK":
            country_info = {}
            for component in response['results'][0]['address_components']:
                if "country" in component["types"]:
                    country_info["country_name"] = component["long_name"]
                    country_info["country_code"] = component["short_name"]
                    break
            # Map ISO country code to currency (example mapping; replace with API for real-time data)
            country_currency_mapping = {"US": "USD", "IN": "INR", "FR": "EUR", "CN": "CNY"}
            currency = country_currency_mapping.get(country_info.get("country_code"), "USD")
            country_info["currency"] = currency
            return country_info
        else:
            logging.error("Failed to fetch country details.")
            return {"country_name": "Unknown", "currency": "USD"}
    except Exception as e:
        logging.error(f"Error fetching country and currency: {e}")
        return {"country_name": "Unknown", "currency": "USD"}

# Function to display trip results
def display_results(destination, budget, search_radius, categories):
    with st.spinner("Planning your trip..."):
        time.sleep(2)

        # Fetch weather
        weather_info = get_weather(destination)

        # Fetch coordinates
        coordinates = fetch_coordinates(destination)
        if not coordinates or "latitude" not in coordinates or "longitude" not in coordinates:
            st.error("Failed to fetch coordinates for the destination. Please try again.")
            return

        # Fetch country and currency
        country_currency = get_country_and_currency(coordinates["latitude"], coordinates["longitude"])
        currency = country_currency.get("currency", "USD")

        # Display Weather and Budget
        st.write(f"**Weather in {destination}:** {weather_info}")
        st.write(f"**Budget in {currency}:** {budget}")

        # Fetch and display places
        all_places = {}
        map_object = folium.Map(location=[coordinates["latitude"], coordinates["longitude"]], zoom_start=13)
        for category in categories:
            st.write(f"### Top {category.title()}s:")
            places = fetch_nearby_places(
                coordinates["latitude"], coordinates["longitude"], search_radius, category
            )
            if places:
                top_places = places[:5]
                display_places(top_places, category)
                all_places[category] = top_places
                for place in top_places:
                    folium.Marker(
                        location=[place["geometry"]["location"]["lat"], place["geometry"]["location"]["lng"]],
                        popup=place["name"]
                    ).add_to(map_object)
            else:
                st.write(f"No {category}s found within {search_radius} km.")

        # Display the map
        st.write("### Map of Nearby Places:")
        folium_static(map_object)

        # Save itinerary as CSV
        if all_places:
            itinerary_data = [
                {"Category": category, "Name": place["name"], "Rating": place.get("rating", "N/A")}
                for category, places in all_places.items()
                for place in places
            ]
            itinerary_df = pd.DataFrame(itinerary_data)
            csv_data = itinerary_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download Itinerary as CSV",
                data=csv_data,
                file_name="trip_itinerary.csv",
                mime="text/csv"
            )
        else:
            st.write("No places found.")

# Streamlit App Layout
st.title("Travel Planner App")
st.write("Plan your trip with real-time weather, places, and maps!")

destination = st.text_input("Enter your destination:")
budget = st.number_input("Enter your budget (in USD):", min_value=0.0, value=5000.0)
search_radius = st.slider("Search Radius (km):", min_value=1, max_value=20, value=5)
categories = st.multiselect(
    "Select Place Categories:",
    ["restaurant", "cafe", "hotel", "museum", "park", "shopping_mall", "landmark"],
    default=["restaurant"]
)

if st.button("Plan My Trip"):
    if not destination.strip():
        st.error("Please enter a valid destination.")
    elif budget <= 0:
        st.error("Budget must be greater than 0.")
    elif not categories:
        st.error("Please select at least one category.")
    else:
        display_results(destination, budget, search_radius, categories)