# Cyprus Buses Schedule App 🚌

A modern, fast, and fully responsive Progressive Web App (PWA) for viewing up-to-date bus schedules in Cyprus. The app effortlessly aggregates intercity routes, airport expresses, and local municipal routes into a single, beautiful user interface.

## 🌟 Key Features

* **Real-time Parsing:** Python backend dynamically scrapes and extracts timetables from HTML pages and PDF documents (Intercity, Osypa, Kapnos, Limassol Airport Express).
* **Smart UI / UX:** 
  * 🎨 **Premium Glassmorphism Design:** Beautiful dark/light mode adaptable UI, smooth animations, and readable typography (Google Fonts `Inter` / `Outfit`).
  * 🔍 **Live Search:** Instantly filter routes by destination name.
  * ⭐ **Favorites System:** "Star" your most-used routes to pin them to the top of the feed (saved via `localStorage`).
  * ⏱️ **Live Countdown:** The "Nearest" filter not only highlights upcoming buses but shows a live *In X Minutes* countdown badge next to the time.
  * 💶 **Price Extraction:** Automatically parses and displays ticket pricing (e.g. `€4.00`) straight from the provider's website.
* **Progressive Web App (PWA):** Installable on iOS and Android devices directly from the browser for a native app feel and offline capability via service workers.

## 🛠️ Technology Stack

* **Backend:** `Python 3.10+`, `FastAPI`, `aiohttp`, `BeautifulSoup4`, `pdfplumber`
* **Frontend:** Vanilla JavaScript (ES6+), semantic HTML5, modern CSS3 (Flexbox/Grid, Animations)
* **Storage:** In-memory caching with persistent JSON disk-fallback. Client-side `localStorage`.

## 🚀 Installation & Running

### Requirements
* Python 3.10 or higher
* `pip` package manager

### Setup

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd cybuses
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: ensure libraries like `fastapi`, `uvicorn`, `aiohttp`, `beautifulsoup4`, `pdfplumber` are installed).*

3. **Run the server:**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

4. **Open in Browser:**
   Navigate to `http://localhost:8000` or `http://127.0.0.1:8000` in your web browser.

## ⚙️ Architecture

The backend utilizes an asynchronous `ScraperService` that fires parallel requests across different parsers (`intercity.py`, `osypa.py`, `shuttle.py`). Extracted data is normalized into a unified list of dictionaries and placed into memory via `CacheManager`. 

The frontend `app.js` polls the `/api/data` endpoint, maintaining a local state of routes. All UI rendering is handled through modular JS components like `BusCard` and `FilterBar`.

## 🤖 MCP Server (AI Integration)

The project includes a standalone **MCP (Model Context Protocol)** server that exposes intercity bus schedule data to AI assistants (e.g., Telegram bot-secretary, Claude Desktop).

> ⚠️ **MCP is NOT a web page!** Do not open `http://host:8888/mcp` in your browser — you will get a 404.  
> MCP is a machine-to-machine protocol (POST-based) designed for connecting AI clients.

### Running the MCP Server

```bash
# Standalone (for development)
python mcp_server.py

# In Docker — runs automatically alongside the main app
docker run -p 8000:8000 -p 8888:8888 cybuses
```

The server starts on `http://0.0.0.0:8888/mcp` using **Streamable HTTP** transport.

### Available Tools

| Tool | Parameters | Description |
|------|-----------|----------|
| `get_intercity_routes` | — | Lists available routes: Limassol, Nicosia, Larnaca |
| `get_schedule` | `route` | Full schedule (both directions, prices, footnotes) |
| `get_nearest_bus` | `route`, `direction?` | Nearest bus departure with countdown in minutes |

**Route keys (`route`):** `"limassol"`, `"nicosia"`, `"larnaca"`  
**Direction keys (`direction`):** `"from_paphos"`, `"to_paphos"` (optional)

### Connecting from Python (MCP Client)

```python
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

async def get_bus_schedule():
    url = "http://<host>:8888/mcp"  # Replace <host> with your server's address
    
    async with streamablehttp_client(url) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Get available routes
            routes = await session.call_tool("get_intercity_routes", {})
            print(routes.content[0].text)
            
            # Get schedule for Limassol
            schedule = await session.call_tool("get_schedule", {"route": "limassol"})
            print(schedule.content[0].text)
            
            # Get nearest bus from Paphos to Larnaca
            nearest = await session.call_tool("get_nearest_bus", {
                "route": "larnaca",
                "direction": "from_paphos"
            })
            print(nearest.content[0].text)
```

### 🤖 Integrating with your AI Secretary (Telegram Bot / Other Project)

To enable your bot secretary (or any other LLM agent) to call these tools, follow these steps in your bot's codebase:

#### 1. Install dependencies in the bot project
Add the `mcp` library to your bot's `requirements.txt`:
```bash
pip install mcp
```

#### 2. Create the client module `mcp_client.py` in the bot project
Add this helper class to manage connections and invoke MCP tools:

```python
# mcp_client.py
import os
import logging
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

logger = logging.getLogger(__name__)

# CyBuses MCP server URL (e.g., http://localhost:8888/mcp or your container IP)
CYBUSES_MCP_URL = os.getenv("CYBUSES_MCP_URL", "http://localhost:8888/mcp")

class CyBusesClient:
    async def call_tool(self, tool_name: str, arguments: dict = None) -> str:
        """Safely invoke an MCP tool on the CyBuses server"""
        if arguments is None:
            arguments = {}
        try:
            async with streamablehttp_client(CYBUSES_MCP_URL) as (read, write, _):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool(tool_name, arguments)
                    if result and result.content:
                        return result.content[0].text
                    return "Error: Empty response from server."
        except Exception as e:
            logger.error(f"Error calling MCP tool {tool_name}: {e}")
            return f"Failed to retrieve bus data. Error: {str(e)}"

# Create a global client instance
cybuses_client = CyBusesClient()
```

#### 3. Register tools within your AI Secretary system
Integrate helper functions into your LLM agent framework (e.g., LangChain, Custom Agent, or OpenAI Assistants).

**Example integration for a custom Python agent:**

```python
# tools.py in the bot project
from mcp_client import cybuses_client

async def get_intercity_routes_tool() -> str:
    """
    Useful for listing available intercity bus routes in Cyprus (e.g., limassol, nicosia, larnaca).
    """
    return await cybuses_client.call_tool("get_intercity_routes")

async def get_schedule_tool(route: str) -> str:
    """
    Useful for fetching the full schedule of buses for a given route.
    route: str, one of 'limassol', 'nicosia', 'larnaca'
    """
    return await cybuses_client.call_tool("get_schedule", {"route": route})

async def get_nearest_bus_tool(route: str, direction: str = None) -> str:
    """
    Useful for finding the next bus departure relative to the current time.
    route: str ('limassol', 'nicosia', 'larnaca')
    direction: optional str ('from_paphos' or 'to_paphos')
    """
    return await cybuses_client.call_tool("get_nearest_bus", {"route": route, "direction": direction})

# Add these functions to your LLM's toolset.
```

#### 4. Environment Variables
When running the bot container or a local process, add an environment variable pointing to the `cybuses` server:
```bash
CYBUSES_MCP_URL=http://<ip-address-of-cybuses-server>:8888/mcp
```
*(If both the bot and the cybuses server run inside the same Docker network, use the service name: `http://cybuses:8888/mcp`)*


### Example `get_schedule` Output

```
📅 Schedule: Paphos ↔ Limassol
🚌 Paphos ➝ Limassol
   💶 Price: € 5
   05:45, 06:10, 07:30, 08:00, 09:00, 10:00, ... 20:00

🚌 Limassol ➝ Paphos
   💶 Price: € 5
   06:00, 06:25, 07:25, 08:00, ... 21:00
```

### Example `get_nearest_bus` Output

```
🕐 Nearest buses (14:35) — Limassol

🚌 Paphos ➝ Limassol
   ⏰ Next departure: 15:00
   ⏳ In 25 min
   Following: 15:30, 16:00

🚌 Limassol ➝ Paphos
   ⏰ Next departure: 15:00
   ⏳ In 25 min
   Following: 15:30, 16:00
```

### Docker: Port Mapping

```yaml
# docker-compose.yml
services:
  cybuses:
    build: .
    ports:
      - "8000:8000"   # Web UI (FastAPI)
      - "8888:8888"   # MCP Server
```

### Troubleshooting

| Issue | Cause | Solution |
|------|------|---------|
| `GET /mcp → 404` | Opened in browser | MCP doesn't work via browsers. Use an MCP client |
| `Invalid HTTP request` | Browser sends GET request | Use the MCP SDK (`streamablehttp_client`) |
| No data returned | Website intercity-buses.com is down | Check internet access inside the container |

## ⚠️ Error Handling
If a parser fails to locate timetable data (e.g., website redesign or PDF link broken), the backend gracefully generates a visible red "Error Banner" injected natively into the UI to notify the user of the disruption, rather than silently failing.