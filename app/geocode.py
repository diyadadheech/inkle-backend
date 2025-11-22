# app/geocode.py
import httpx
from .config import NOMINATIM_URL, APP_USER_AGENT

async def geocode_place(place_name: str, limit: int = 1):
    """
    Returns list of candidate places from Nominatim (each: dict with lat, lon, display_name).
    """
    params = {
        "q": place_name,
        "format": "json",
        "addressdetails": 1,
        "limit": limit
    }
    headers = {"User-Agent": APP_USER_AGENT}
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.get(NOMINATIM_URL, params=params, headers=headers)
        r.raise_for_status()
        data = r.json()
        # data is list of results
        return data
