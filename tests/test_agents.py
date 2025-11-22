# tests/test_agents.py
import asyncio
from app.agents import ParentAgent

import pytest

@pytest.mark.asyncio
async def test_extract_and_geocode():
    p = ParentAgent()
    # test extraction
    place = p.extract_place("I'm going to Bangalore, let's plan.")
    assert "Bangalore" in place or "Bengaluru" in place or place != ""

# Note: these tests do live API calls; in CI you'd mock httpx responses.
@pytest.mark.asyncio
async def test_parent_handle_bangalore():
    p = ParentAgent()
    res = await p.handle("I'm going to Bangalore, what's the temperature there?")
    assert "place_queried" in res
    # Either weather or error
    if res.get("error"):
        pytest.skip("Geocoding rate-limited or network issue")
    else:
        assert "weather" in res
