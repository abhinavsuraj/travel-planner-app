import streamlit as st
import time
import folium
from streamlit_folium import folium_static
import requests
import pandas as pd
import logging
import json
from folium.plugins import MarkerCluster

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Access API keys from Streamlit Secrets
GOOGLE_MAPS_API = st.secrets["GOOGLE_MAPS_API"]
OPENWEATHERMAP_API_KEY = st.secrets["OPENWEATHERMAP_API_KEY"]

# Functions
def fetch_coordinates(location: str) -> dict:
    """Fetch latitude and longitude for a given location."""
    try:
        geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={location}&key={GOOGLE_MAPS_API}"
        response = requests.get(geocode_url).json()
        if response.get("status") == "OK":
            location_data = response["results"][0]["geometry"]["location"]
            return {"latitude": location_data["lat"], "longitude": location_data["lng"]}
        st.error("Failed to fetch coordinates. Please try again.")
        return {}
    except Exception as e:
        logging.error(f"Error fetching coordinates: {e}")
        return {}

def get_weather(location: str) -> str:
    """Fetch current weather for a given location."""
    try:
        weather_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {"q": location, "appid": OPENWEATHERMAP_API_KEY, "units": "metric"}
        response = requests.get(weather_url, params=params).json()
        if response.get("cod") == 200:
            data = response
            return f"{data['name']}: {data['weather'][0]['description']} at {data['main']['temp']}°C"
        return "Weather information unavailable."
    except Exception as e:
        logging.error(f"Error fetching weather: {e}")
        return "Weather information unavailable."

def fetch_nearby_places(lat: float, lng: float, radius: int, category: str) -> list:
    """Fetch nearby places using Google Places API."""
    try:
        places_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "location": f"{lat},{lng}",
            "radius": radius * 1000,
            "type": category,
            "key": GOOGLE_MAPS_API,
        }
        response = requests.get(places_url, params=params).json()
        if response.get("status") == "OK":
            return response.get("results", [])
        return []
    except Exception as e:
        logging.error(f"Error fetching nearby places: {e}")
        return []

def get_country_and_currency(lat: float, lng: float) -> dict:
    """Fetch country and currency from latitude and longitude."""
    try:
        geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}&key={GOOGLE_MAPS_API}"
        response = requests.get(geocode_url).json()

        if response.get("status") == "OK":
            country_info = {}
            for component in response['results'][0]['address_components']:
                if "country" in component["types"]:
                    country_info["country_name"] = component["long_name"]
                    country_info["country_code"] = component["short_name"]
                    break

            # Currency Mapping
            country_currency_mapping = {
                "US": "USD", "IN": "INR", "FR": "EUR", "CN": "CNY",
                "JP": "JPY", "GB": "GBP", "AU": "AUD", "CA": "CAD",
                "DE": "EUR", "BR": "BRL", "ZA": "ZAR",
            }

            currency = country_currency_mapping.get(country_info.get("country_code"), "USD")
            country_info["currency"] = currency
            return country_info
        else:
            logging.error("Failed to fetch country details.")
            return {"country_name": "Unknown", "currency": "USD"}
    except Exception as e:
        logging.error(f"Error fetching country and currency: {e}")
        return {"country_name": "Unknown", "currency": "USD"}

def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """Convert currency from one type to another."""
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
        response = requests.get(url).json()
        rate = response["rates"].get(to_currency)
        if rate:
            return f"{amount} {from_currency} = {amount * rate:.2f} {to_currency}"
        return "Currency conversion unavailable."
    except Exception as e:
        logging.error(f"Error converting currency: {e}")
        return "Currency conversion unavailable."

def create_map(lat: float, lng: float, places: list) -> folium.Map:
    """Create a map with markers for places."""
    try:
        map_object = folium.Map(location=[lat, lng], zoom_start=13)
        marker_cluster = MarkerCluster().add_to(map_object)

        for place in places:
            folium.Marker(
                location=[place["geometry"]["location"]["lat"], place["geometry"]["location"]["lng"]],
                popup=place["name"],
                tooltip=place["name"],
            ).add_to(marker_cluster)

        return map_object
    except Exception as e:
        logging.error(f"Error creating map: {e}")
        return folium.Map(location=[lat, lng], zoom_start=13)

def display_places(places: list, category_name: str):
    """Display nearby places in a table."""
    if not places:
        st.write(f"No places found for {category_name}.")
        return

    st.write(f"Top {category_name.title()}s:")
    places_df = pd.DataFrame(
        [{"Name": place["name"], "Rating": place.get("rating", "N/A")} for place in places]
    )
    st.table(places_df)

def display_results(destination, budget, search_radius, categories):
    """Main workflow to display trip planning results."""
    with st.spinner("Planning your trip..."):
        time.sleep(2)

        # Fetch Coordinates
        coordinates = fetch_coordinates(destination)
        if not coordinates:
            st.error("Coordinates not found. Please try again.")
            return

        # Fetch Country and Currency
        country_currency = get_country_and_currency(
            coordinates["latitude"], coordinates["longitude"]
        )
        country_name = country_currency.get("country_name", "Unknown")
        currency = country_currency.get("currency", "USD")

        # Convert Budget
        converted_budget = convert_currency(budget, "USD", currency)

        # Fetch Weather
        weather_info = get_weather(destination)
        st.write(f"**Weather in {destination}:** {weather_info}")
        st.write(f"**Converted Budget ({currency}):** {converted_budget}")

        # Fetch and Display Nearby Places
        all_places = {}
        map_object = folium.Map(location=[coordinates["latitude"], coordinates["longitude"]], zoom_start=13)
        for category in categories:
            st.write(f"### Top {category.replace('_', ' ').title()}s:")
            places = fetch_nearby_places(
                coordinates["latitude"], coordinates["longitude"], search_radius, category
            )
            if places:
                # Display top 5 places
                top_places = places[:5]
                display_places(top_places, category)
                all_places[category] = top_places

                # Add places to the map
                for place in top_places:
                    folium.Marker(
                        location=[place["geometry"]["location"]["lat"], place["geometry"]["location"]["lng"]],
                        popup=f"{place['name']} ({category})",
                        tooltip=place["name"]
                    ).add_to(map_object)
            else:
                st.write(f"No {category}s found within {search_radius} km.")

        # Display the Map
        st.write("### Map of Nearby Places:")
        folium_static(map_object)

        # Save Itinerary as CSV
        if all_places:
            itinerary_data = []
            for category, places in all_places.items():
                for place in places:
                    itinerary_data.append({
                        "Category": category,
                        "Name": place["name"],
                        "Rating": place.get("rating", "N/A")
                    })
            itinerary_df = pd.DataFrame(itinerary_data)
            csv_data = itinerary_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download Itinerary as CSV",
                data=csv_data,
                file_name="trip_itinerary.csv",
                mime="text/csv"
            )
        else:
            st.write(f"No places found in any category within {search_radius} km of {destination}.")

# Main UI and Workflow
st.title("Travel Planner App")
st.write("Plan your trip with real-time weather, places, and maps!")

# Input Fields
destination = st.text_input("Enter your destination:")
budget = st.number_input("Enter your budget (in USD):", min_value=0.0, value=5000.0, step=100.0)
search_radius = st.slider("Search Radius (km):", min_value=1, max_value=200, value=5)
categories = st.multiselect(
    "Select Place Categories:",
    options=[
        "restaurant", "cafe", "hotel", "museum", "park", "shopping_mall",
        "night_club", "landmark", "beach", "zoo", "amusement_park",
        "library", "gym", "movie_theater", "temple", "church", "art_gallery",
    ],
    default=["restaurant"]
)

# Validate Inputs and Trigger Planner
if st.button("Plan My Trip"):
    if not destination.strip():
        st.error("Please enter a valid destination.")
    elif budget <= 0:
        st.error("Budget must be greater than 0.")
    elif not categories:
        st.error("Please select at least one place category.")
    else:
        display_results(destination, budget, search_radius, categories)
