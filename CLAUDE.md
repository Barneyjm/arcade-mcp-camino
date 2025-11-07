# Claude Development Guide - Camino MCP Server

This document serves as a guide for Claude (AI assistant) when working on this project. It contains project context, development patterns, and lessons learned.

## Project Overview

This is an MCP (Model Context Protocol) server that wraps the Camino AI API, providing location intelligence tools to AI agents. The server is built using the Arcade MCP Server framework and exposes 6 main tools:

- `search_place` - Place search (free-form or structured)
- `query` - Natural language → Overpass QL queries
- `spatial_relationship` - Distance/direction/travel time calculations
- `place_context` - Location context with nearby places and weather
- `journey_planner` - Multi-waypoint route optimization
- `get_route` - Point-to-point routing with geometry

## Development Workflow

When modifying this project, Claude should:

1. **Read the OpenAPI spec first** - [caminoopenapi.json](https://getcamino.ai/openapi.json) is the source of truth for API endpoints
2. **Match types to the spec** - Return types must match what the API actually returns
3. **Use fully-typed annotations** - Arcade requires `list[dict]` not bare `list`
4. **Test in Claude Desktop** - Runtime behavior differs from development environment
5. **Document performance characteristics** - Note slow endpoints in docstrings

## Code Patterns

### Tool Definition Template

```python
@app.tool(requires_secrets=["CAMINO_API_KEY"])
async def tool_name(
    context: Context,
    param: Annotated[type, "Description"],
    optional_param: Annotated[type | None, "Description"] = None,
) -> dict | list[dict]:
    """Tool description. Note any performance characteristics."""
    api_key = context.get_secret("CAMINO_API_KEY")

    headers = {"X-API-Key": api_key}
    params = {"required_param": param}

    if optional_param is not None:
        params["optional_param"] = optional_param

    url = "https://api.getcamino.ai/endpoint"

    # Use extended timeout for slow endpoints
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
```

### Return Type Guidelines

- Single object response → `dict`
- Array response → `list[dict]`
- Never use bare `list` or `dict` without full typing
- Always check OpenAPI spec for actual response structure

### Timeout Considerations

- Default httpx timeout: 5 seconds
- Complex endpoints (query, journey_planner): 120 seconds
- Simple lookups (search, route): default is fine

## Platform Requirements

**Windows Development**: This project MUST run in WSL (Windows Subsystem for Linux) due to Unix-specific dependencies in the Arcade framework (specifically `fcntl` module). Native Windows execution is not supported.

## Testing Strategy

1. **Add new tools** - Implement based on OpenAPI spec
2. **Verify types** - Ensure return types match actual API responses
3. **Test in Claude Desktop** - Only way to catch runtime serialization issues
4. **Check logs** - MCP logs are in `%APPDATA%\Claude\logs\mcp-server-camino_server.log`

## Common Issues & Solutions

### Type Validation Errors
- **Symptom**: `Input should be a valid dictionary` or `Unsupported parameter type`
- **Cause**: Return type doesn't match actual API response or isn't fully typed
- **Fix**: Use `list[dict]` for arrays, `dict` for objects, check OpenAPI spec

### Timeout Errors
- **Symptom**: `httpx.ReadTimeout`
- **Cause**: Default 5-second timeout too short for complex operations
- **Fix**: Use `httpx.AsyncClient(timeout=120.0)` for slow endpoints

### Windows fcntl Errors
- **Symptom**: `ModuleNotFoundError: No module named 'fcntl'`
- **Cause**: Unix-only module in Arcade dependencies
- **Fix**: Must use WSL, not native Windows

## File Structure

```
arcade-mcp-camino/
├── camino_server/
│   ├── src/camino_server/
│   │   ├── server.py           # Main tool definitions
│   │   └── caminoopenapi.json  # API spec (source of truth)
│   ├── pyproject.toml          # Dependencies
│   └── .env                    # API keys (not in git)
├── README.md                   # User documentation
└── CLAUDE.md                   # This file - development guide
```

## Making Changes

When asked to add or modify tools:

1. Read the OpenAPI spec for the endpoint
2. Implement following the tool definition template
3. Match return types exactly to spec
4. Add appropriate timeout if endpoint is slow
5. Document any performance notes in docstring
6. Update README.md if adding new functionality

## Future Enhancements

Potential areas for improvement:
- Add response caching for repeated queries
- Implement retry logic for failed requests
- Add structured response models with Pydantic
- Support streaming responses for long operations
- Add telemetry/logging for API usage tracking
