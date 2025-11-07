# Camino MCP Server

An MCP (Model Context Protocol) server for the [Camino AI API](https://getcamino.ai), built with the Arcade MCP Server framework. This server provides AI agents with location intelligence, spatial reasoning, and route planning capabilities.

## Features

This MCP server exposes all Camino API endpoints as tools:

- **`search_place`** - Search for places using free-form or structured queries
- **`query`** - Natural language queries converted to Overpass QL for POI discovery
- **`spatial_relationship`** - Calculate distance, direction, and travel time between points
- **`place_context`** - Get context-aware information about locations (nearby places, weather, etc.)
- **`journey_planner`** - Multi-waypoint journey planning with route optimization
- **`get_route`** - Detailed routing between two points with geometry and imagery

## Installation

### Prerequisites

- **Windows users**: Must use WSL (Windows Subsystem for Linux) - see [CLAUDE.md](CLAUDE.md) for details
- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager
- A [Camino API key](https://getcamino.ai)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/arcade-mcp-camino.git
cd arcade-mcp-camino/camino_server
```

2. Install dependencies:
```bash
uv sync
```

3. Create a `.env` file with your Camino API key:
```bash
CAMINO_API_KEY=your-api-key-here
```

## Usage

### With Claude Desktop (Windows via WSL)

Add to your Claude Desktop config (`%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "camino_server": {
      "command": "wsl",
      "args": [
        "bash", "-c",
        "cd /mnt/c/Users/YOUR_USERNAME/path/to/arcade-mcp-camino/camino_server && uv run python -m camino_server.server"
      ],
      "env": {
        "CAMINO_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### With Claude Desktop (macOS/Linux)

```json
{
  "mcpServers": {
    "camino_server": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "-m",
        "camino_server.server"
      ],
      "cwd": "/path/to/arcade-mcp-camino/camino_server",
      "env": {
        "CAMINO_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Standalone

Run the server directly:
```bash
uv run python -m camino_server.server
```

## Example Usage

Once configured in Claude Desktop, you can ask questions like:

- "Find coffee shops near the Eiffel Tower"
- "What's the distance and travel time from Times Square to Central Park?"
- "Plan a journey from my hotel to the museum, then to a restaurant"
- "Get me context about what's around coordinates 40.7589, -73.9851"
- "Find the route from San Francisco to Los Angeles"

## Performance Notes

- The **`query`** endpoint may take 30-60 seconds as it processes complex Overpass API queries and AI ranking
- Other endpoints typically respond in 1-5 seconds
- Use `mode="basic"` for faster, free queries or `mode="advanced"` for enhanced web-enriched results

## Troubleshooting

See [CLAUDE.md](CLAUDE.md) for common issues and solutions, including:
- Windows `fcntl` module errors
- Return type validation errors
- Timeout issues with the query endpoint

## API Documentation

Full API documentation available at: https://getcamino.ai/docs

## License

MIT
