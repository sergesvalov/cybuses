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

### Running the MCP Server

```bash
python mcp_server.py
```

The server starts on `http://0.0.0.0:8888/mcp` using **Streamable HTTP** transport.

### Available Tools

| Tool | Description |
|------|-------------|
| `get_intercity_routes` | Lists all available intercity routes (Limassol, Nicosia, Larnaca) |
| `get_schedule(route)` | Full timetable for a route (both directions, prices, notes) |
| `get_nearest_bus(route, direction?)` | Nearest departure from current time with countdown |

### Connecting from an MCP Client (Python)

```python
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

async with streamablehttp_client("http://<host>:8888/mcp") as (read, write, _):
    async with ClientSession(read, write) as session:
        await session.initialize()
        result = await session.call_tool("get_schedule", {"route": "limassol"})
```

## ⚠️ Error Handling
If a parser fails to locate timetable data (e.g., website redesign or PDF link broken), the backend gracefully generates a visible red "Error Banner" injected natively into the UI to notify the user of the disruption, rather than silently failing.