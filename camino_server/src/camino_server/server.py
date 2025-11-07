#!/usr/bin/env python3
"""camino_server MCP server"""

import sys
from typing import Annotated

import httpx
from arcade_mcp_server import Context, MCPApp
from arcade_mcp_server.auth import Reddit

app = MCPApp(name="camino_server", version="1.0.0", log_level="DEBUG")


@app.tool(requires_secrets=["CAMINO_API_KEY"])
async def search_place(
    context: Context,
    query: Annotated[str | None, "Free-form search query (e.g., 'Eiffel Tower')"] = None,
    amenity: Annotated[str | None, "Name and/or type of POI (e.g., 'restaurant', 'Starbucks')"] = None,
    street: Annotated[str | None, "Street name with optional housenumber (e.g., '123 Main Street')"] = None,
    city: Annotated[str | None, "City name (e.g., 'Paris', 'New York')"] = None,
    county: Annotated[str | None, "County name"] = None,
    state: Annotated[str | None, "State or province name (e.g., 'California', 'Ontario')"] = None,
    country: Annotated[str | None, "Country name (e.g., 'France', 'United States')"] = None,
    postalcode: Annotated[str | None, "Postal/ZIP code (e.g., '10001', '75001')"] = None,
    limit: Annotated[int, "Maximum number of results to return"] = 10,
    include_photos: Annotated[bool, "Include street-level imagery data from OpenStreetCam"] = False,
    photo_radius: Annotated[int, "Search radius for street photos in meters"] = 100,
    mode: Annotated[str, "Search mode: 'basic' (free, OSM only) or 'advanced' (web enrichment, AWS fallback)"] = "basic",
) -> list[dict]:
    """Search for places using free-form or structured queries"""
    # Get API key from context
    api_key = context.get_secret("CAMINO_API_KEY")

    # Prepare the request
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json",
    }

    params = {
        "limit": limit,
        "include_photos": include_photos,
        "photo_radius": photo_radius,
        "mode": mode,
    }

    # Add optional parameters
    if query is not None:
        params["query"] = query
    if amenity is not None:
        params["amenity"] = amenity
    if street is not None:
        params["street"] = street
    if city is not None:
        params["city"] = city
    if county is not None:
        params["county"] = county
    if state is not None:
        params["state"] = state
    if country is not None:
        params["country"] = country
    if postalcode is not None:
        params["postalcode"] = postalcode

    url = "https://api.getcamino.ai/search"

    # Make the request
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, params=params)
        response.raise_for_status()

        # Return the response
        return response.json()


@app.tool(requires_secrets=["CAMINO_API_KEY"])
async def query(
    context: Context,
    query: Annotated[str | None, "Natural language query, e.g., 'coffee near me'"] = None,
    lat: Annotated[float | None, "Latitude for the center of your search"] = None,
    lon: Annotated[float | None, "Longitude for the center of your search"] = None,
    radius: Annotated[int, "Search radius in meters"] = 1000,
    rank: Annotated[bool, "Use AI to rank results by relevance"] = True,
    limit: Annotated[int, "Maximum number of results to return (1-100)"] = 20,
    offset: Annotated[int, "Number of results to skip for pagination"] = 0,
    answer: Annotated[bool, "Generate a human-readable answer summary"] = False,
    time: Annotated[str | None, "Time parameter: '2020-01-01' (point), '2020..' (since), '2020..2024' (range)"] = None,
    osm_ids: Annotated[str | None, "Comma-separated OSM IDs (e.g., 'node/123,way/456')"] = None,
    mode: Annotated[str, "Query mode: 'basic' (free, OSM only) or 'advanced' (web enrichment)"] = "basic",
) -> dict:
    """Query places using natural language and location, converts to Overpass query. Note: This endpoint may take 30-60 seconds due to Overpass API processing and AI ranking."""
    api_key = context.get_secret("CAMINO_API_KEY")

    headers = {"X-API-Key": api_key}
    params = {
        "radius": radius,
        "rank": rank,
        "limit": limit,
        "offset": offset,
        "answer": answer,
        "mode": mode,
    }

    if query is not None:
        params["query"] = query
    if lat is not None:
        params["lat"] = lat
    if lon is not None:
        params["lon"] = lon
    if time is not None:
        params["time"] = time
    if osm_ids is not None:
        params["osm_ids"] = osm_ids

    url = "https://api.getcamino.ai/query"

    # Extended timeout for query endpoint (Overpass API can be slow)
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()


@app.tool(requires_secrets=["CAMINO_API_KEY"])
async def spatial_relationship(
    context: Context,
    start_lat: Annotated[float, "Starting point latitude"],
    start_lon: Annotated[float, "Starting point longitude"],
    end_lat: Annotated[float, "Ending point latitude"],
    end_lon: Annotated[float, "Ending point longitude"],
    include_distance: Annotated[bool, "Include distance calculation"] = True,
    include_direction: Annotated[bool, "Include direction calculation"] = True,
    include_travel_time: Annotated[bool, "Include travel time estimates"] = True,
    include_description: Annotated[bool, "Include human-readable description"] = True,
) -> dict:
    """Calculate spatial relationships between two points including distance, direction, and travel time"""
    api_key = context.get_secret("CAMINO_API_KEY")

    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json",
    }

    include_fields = []
    if include_distance:
        include_fields.append("distance")
    if include_direction:
        include_fields.append("direction")
    if include_travel_time:
        include_fields.append("travel_time")
    if include_description:
        include_fields.append("description")

    body = {
        "start": {"lat": start_lat, "lon": start_lon},
        "end": {"lat": end_lat, "lon": end_lon},
        "include": include_fields,
    }

    url = "https://api.getcamino.ai/relationship"

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=body)
        response.raise_for_status()
        return response.json()


@app.tool(requires_secrets=["CAMINO_API_KEY"])
async def place_context(
    context: Context,
    lat: Annotated[float, "Latitude of the location"],
    lon: Annotated[float, "Longitude of the location"],
    radius: Annotated[int, "Search radius in meters"] = 500,
    context_query: Annotated[str | None, "Additional context about what you're looking for"] = None,
    time: Annotated[str | None, "Time parameter: '2020-01-01' (point), '2020..' (since), '2020..2024' (range)"] = None,
    include_weather: Annotated[bool, "Include current weather and forecast"] = False,
    weather_forecast: Annotated[str, "Weather forecast type: 'daily' or 'hourly'"] = "daily",
) -> dict:
    """Get context-aware information about a location including nearby places and area description"""
    api_key = context.get_secret("CAMINO_API_KEY")

    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json",
    }

    body = {
        "location": {"lat": lat, "lon": lon},
        "radius": radius,
        "include_weather": include_weather,
        "weather_forecast": weather_forecast,
    }

    if context_query is not None:
        body["context"] = context_query
    if time is not None:
        body["time"] = time

    url = "https://api.getcamino.ai/context"

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=body)
        response.raise_for_status()
        return response.json()


@app.tool(requires_secrets=["CAMINO_API_KEY"])
async def journey_planner(
    context: Context,
    waypoints: Annotated[list[dict], "List of waypoints with lat, lon, and purpose fields"],
    transport_mode: Annotated[str, "Mode of transport: walking, driving, cycling"] = "walking",
    time_budget: Annotated[str | None, "Time budget for the journey (e.g., '2 hours')"] = None,
) -> dict:
    """Multi-waypoint journey planning with route optimization and feasibility analysis"""
    api_key = context.get_secret("CAMINO_API_KEY")

    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json",
    }

    body = {
        "waypoints": waypoints,
        "constraints": {
            "transport": transport_mode,
        }
    }

    if time_budget is not None:
        body["constraints"]["time_budget"] = time_budget

    url = "https://api.getcamino.ai/journey"

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=body)
        response.raise_for_status()
        return response.json()


@app.tool(requires_secrets=["CAMINO_API_KEY"])
async def get_route(
    context: Context,
    start_lat: Annotated[float, "Start latitude"],
    start_lon: Annotated[float, "Start longitude"],
    end_lat: Annotated[float, "End latitude"],
    end_lon: Annotated[float, "End longitude"],
    mode: Annotated[str, "Mode of transport: car, bike, or foot"] = "car",
    include_geometry: Annotated[bool, "Include detailed route geometry and waypoints for mapping. Only include if you will be showing the user a map"] = False,
    include_imagery: Annotated[bool, "Include street-level imagery at key waypoints"] = False,
) -> dict:
    """Get routing information from a start to an end point"""
    api_key = context.get_secret("CAMINO_API_KEY")

    headers = {"X-API-Key": api_key}
    params = {
        "start_lat": start_lat,
        "start_lon": start_lon,
        "end_lat": end_lat,
        "end_lon": end_lon,
        "mode": mode,
        "include_geometry": include_geometry,
        "include_imagery": include_imagery,
    }

    url = "https://api.getcamino.ai/route"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()


# Run with specific transport
if __name__ == "__main__":
    # Get transport from command line argument, default to "stdio"
    # - "stdio" (default): Standard I/O for Claude Desktop, CLI tools, etc.
    #   Supports tools that require_auth or require_secrets out-of-the-box
    # - "http": HTTPS streaming for Cursor, VS Code, etc.
    #   Does not support tools that require_auth or require_secrets unless the server is deployed
    #   using 'arcade deploy' or added in the Arcade Developer Dashboard with 'Arcade' server type
    transport = sys.argv[1] if len(sys.argv) > 1 else "stdio"

    # Run the server
    app.run(transport=transport, host="127.0.0.1", port=8000)