# app/agents.py
import asyncio
import httpx
from typing import List, Dict, Optional
from .geocode import geocode_place
from .config import OPEN_METEO_URL, OVERPASS_URL, APP_USER_AGENT


class WeatherAgent:
    async def get_weather(self, lat: float, lon: float) -> Dict:
        params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": "true",
            "hourly": "precipitation_probability",
            "timezone": "UTC"
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(OPEN_METEO_URL, params=params)
            r.raise_for_status()
            data = r.json()

            current = data.get("current_weather", {})
            hourly = data.get("hourly", {})

            prob = None
            if "precipitation_probability" in hourly:
                plist = hourly["precipitation_probability"]
                if plist:
                    prob = plist[0]

            return {
                "temperature_c": current.get("temperature"),
                "wind_speed": current.get("windspeed"),
                "weather_code": current.get("weathercode"),
                "precipitation_probability_percent": prob
            }


class PlacesAgent:
    async def get_places(self, lat: float, lon: float, radius: int = 5000, limit: int = 5) -> List[str]:

        q = f"""
        [out:json][timeout:25];
        (
          node(around:{radius},{lat},{lon})[tourism];
          node(around:{radius},{lat},{lon})[historic];
          node(around:{radius},{lat},{lon})[amenity=park];
          node(around:{radius},{lat},{lon})[leisure=park];
          node(around:{radius},{lat},{lon})[tourism=attraction];
        );
        out center {limit};
        """

        headers = {"User-Agent": APP_USER_AGENT}

        async with httpx.AsyncClient(timeout=25.0) as client:
            r = await client.post(OVERPASS_URL, data=q, headers=headers)
            r.raise_for_status()
            data = r.json()

            elements = data.get("elements", [])
            names = []

            for el in elements:
                tags = el.get("tags", {})
                name = tags.get("name") or tags.get("amenity") or tags.get("historic") or tags.get("tourism")
                if name:
                    names.append(name)
                if len(names) >= limit:
                    break

            # Deduplicate
            unique = []
            for n in names:
                if n not in unique:
                    unique.append(n)
                if len(unique) >= limit:
                    break

            return unique


class ParentAgent:
    def __init__(self):
        self.weather_agent = WeatherAgent()
        self.places_agent = PlacesAgent()

    async def handle(self, user_input: str) -> Dict:

        # --- Extract place ---
        place = self.extract_place(user_input)
        if not place:
            place = user_input.strip()

        # --- FIX: Default to India for single-city inputs ---
        if "," not in place:
            place = place + ", India"

        # --- Geocode ---
        geocode_results = await geocode_place(place, limit=1)
        if not geocode_results:
            return {"error": True, "message": f"Sorry, I don't know of a place called '{place}'."}

        loc = geocode_results[0]
        lat = float(loc["lat"])
        lon = float(loc["lon"])
        display_name = loc.get("display_name", place)

        # Decide what user asked
        user_l = user_input.lower()
        want_weather = any(t in user_l for t in ["weather", "rain", "forecast", "temperature"])
        want_places = any(t in user_l for t in ["place", "visit", "go to", "attraction", "things to do", "places to"])

        if not (want_weather or want_places):
            want_weather = True
            want_places = True

        # Run both in parallel
        tasks = []
        if want_weather: tasks.append(self.weather_agent.get_weather(lat, lon))
        if want_places: tasks.append(self.places_agent.get_places(lat, lon))

        results = await asyncio.gather(*tasks)

        res_weather = results[0] if want_weather else None
        res_places = results[-1] if want_places else None

        # Build final response
        response = {
            "place_queried": display_name,
            "latitude": lat,
            "longitude": lon
        }

        if res_weather: response["weather"] = res_weather
        if res_places is not None: response["places"] = res_places

        response["message"] = self.build_message(display_name, res_weather, res_places)
        return response

    def extract_place(self, text: str) -> Optional[str]:
        lower = text.lower()
        markers = ["going to", "gonna go to", "i'm going to", "i am going to", "places to", "visit", "to", "in"]
        markers = sorted(markers, key=lambda x: -len(x))

        for m in markers:
            if m in lower:
                i = lower.rfind(m)
                cand = text[i + len(m):].strip(" .?!")
                if "," in cand:
                    cand = cand.split(",")[0].strip()
                if cand:
                    return cand

        words = text.strip().split()
        if words:
            return words[-1].strip(".,?!")

        return None

    def build_message(self, place_display: str, weather: Optional[Dict], places: Optional[List[str]]) -> str:
        parts = []

        if weather:
            temp = weather.get("temperature_c")
            prob = weather.get("precipitation_probability_percent")

            s = f"In {place_display.split(',')[0]} it's currently {temp}°C"
            if prob is not None:
                s += f" with a chance of {prob}% to rain."
            else:
                s += "."

            parts.append(s)

        if places:
            if places:
                bullets = "\n- " + "\n- ".join(places)
                parts.append(f"And these are the places you can go:{bullets}")
            else:
                parts.append("I couldn't find tourist places nearby.")

        return " ".join(parts)
