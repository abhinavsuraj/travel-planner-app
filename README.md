# Travel Planner App

## Overview
The **Travel Planner App** is a user-friendly web application that assists in planning trips by providing weather updates, nearby points of interest, currency conversion, and downloadable itineraries. Built using **Streamlit** and **LangChain**, it demonstrates expertise in API integration, geospatial data processing, and interactive data visualization.

---

## Features
- **Weather Updates**: Get real-time weather information for your destination.
- **Currency Conversion**: Convert your budget from USD to the destination's local currency.
- **Nearby Places**: Discover top nearby attractions based on your selected categories.
- **Interactive Map**: View places of interest plotted on a dynamic map.
- **Downloadable Itinerary**: Save trip details as a CSV or JSON file.

---

## Technology Stack
- **Frontend**: Streamlit for building the interactive interface.
- **Backend**:
  - LangChain for workflow orchestration and automation.
  - Python for data processing and API integration.
- **APIs**:
  - Google Maps API for geocoding and nearby places.
  - OpenWeather API for weather updates.
  - Exchange Rate API for currency conversion.
- **Visualization**:
  - Folium for map rendering.
  - Pandas for data manipulation and export.

---

## How to Run the App
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/travel-planner-app.git
   cd travel-planner-app
   ```

2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up the `.env` file with your API keys:
   ```plaintext
   GOOGLE_MAPS_API=your_google_maps_api_key
   OPENWEATHERMAP_API_KEY=your_openweathermap_api_key
   ```

4. Run the application:
   ```bash
   streamlit run app.py
   ```

---

## Usage
1. Enter a destination, budget, radius, and select categories of interest.
2. View real-time weather, currency conversion, and nearby places on the dashboard.
3. Explore places on an interactive map.
4. Download your trip itinerary for offline use.

---

## Jupyter Notebook
The project includes a Jupyter Notebook (`travel_planner_agent_demo.ipynb`) showcasing:
- Agent-based workflow using **LangChain**.
- Automated travel planning steps such as fetching weather, geolocation, and creating itineraries.
- Instructional guidance for customization and usage.

---

## Example Outputs
- **Coordinates**: Fetch latitude and longitude for a location.
- **Weather**: Real-time weather conditions.
- **Nearby Places**: A list of attractions with ratings.
- **Map**: HTML map file with plotted locations.
- **Itinerary**: JSON or CSV file with trip details.

---

## Contribution
Contributions are welcome! Fork the repository, make changes, and create a pull request to suggest improvements or new features.

---

## License
This project is licensed under the MIT License. See `LICENSE` for more details.

---

Feel free to adjust the links or add your GitHub username to personalize it further!