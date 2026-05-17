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

> ⚠️ **MCP — это НЕ веб-страница!** Не открывайте `http://host:8888/mcp` в браузере — получите 404.  
> MCP — это машинный протокол (POST-based), предназначенный для подключения AI-клиентов.

### Запуск MCP-сервера

```bash
# Отдельно (для разработки)
python mcp_server.py

# В Docker — запускается автоматически вместе с основным приложением
docker run -p 8000:8000 -p 8888:8888 cybuses
```

Сервер стартует на `http://0.0.0.0:8888/mcp` (Streamable HTTP transport).

### Доступные инструменты (Tools)

| Tool | Параметры | Описание |
|------|-----------|----------|
| `get_intercity_routes` | — | Список маршрутов: Limassol, Nicosia, Larnaca |
| `get_schedule` | `route` | Полное расписание (оба направления, цены, примечания) |
| `get_nearest_bus` | `route`, `direction?` | Ближайший автобус с обратным отсчётом в минутах |

**Значения `route`:** `"limassol"`, `"nicosia"`, `"larnaca"`  
**Значения `direction`:** `"from_paphos"`, `"to_paphos"` (опционально)

### Подключение из Python (MCP-клиент)

```python
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

async def get_bus_schedule():
    url = "http://<host>:8888/mcp"  # Заменить <host> на адрес сервера
    
    async with streamablehttp_client(url) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Получить список маршрутов
            routes = await session.call_tool("get_intercity_routes", {})
            print(routes.content[0].text)
            
            # Получить расписание Limassol
            schedule = await session.call_tool("get_schedule", {"route": "limassol"})
            print(schedule.content[0].text)
            
            # Ближайший автобус из Пафоса в Ларнаку
            nearest = await session.call_tool("get_nearest_bus", {
                "route": "larnaca",
                "direction": "from_paphos"
            })
            print(nearest.content[0].text)
```

### 🤖 Интеграция в AI Секретаря (Telegram-бот из другого проекта)

Чтобы ваш бот-секретарь (или любой другой LLM-агент) мог вызывать эти инструменты, выполните следующие шаги в проекте бота:

#### 1. Установите зависимости в проекте бота
Добавьте библиотеку `mcp` в `requirements.txt` вашего бота:
```bash
pip install mcp
```

#### 2. Создайте клиентский модуль `mcp_client.py` в проекте бота
Добавьте этот вспомогательный класс, который будет управлять соединением и вызовом инструментов:

```python
# mcp_client.py
import os
import logging
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

logger = logging.getLogger(__name__)

# Адрес сервера cybuses (например, http://localhost:8888/mcp или IP контейнера)
CYBUSES_MCP_URL = os.getenv("CYBUSES_MCP_URL", "http://localhost:8888/mcp")

class CyBusesClient:
    async def call_tool(self, tool_name: str, arguments: dict = None) -> str:
        """Безопасный вызов инструмента MCP сервера CyBuses"""
        if arguments is None:
            arguments = {}
        try:
            async with streamablehttp_client(CYBUSES_MCP_URL) as (read, write, _):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool(tool_name, arguments)
                    if result and result.content:
                        return result.content[0].text
                    return "Ошибка: пустой ответ от сервера."
        except Exception as e:
            logger.error(f"Ошибка вызова MCP инструмента {tool_name}: {e}")
            return f"Не удалось получить данные об автобусах. Ошибка: {str(e)}"

# Создаем глобальный клиент
cybuses_client = CyBusesClient()
```

#### 3. Зарегистрируйте инструменты в системе AI секретаря
Интегрируйте функции-обертки в ваш LLM-агент (например, LangChain, Custom Agent или OpenAI Assistants).

**Пример интеграции в кастомного агента на Python:**

```python
# tools.py в проекте бота
from mcp_client import cybuses_client

async def get_intercity_routes_tool() -> str:
    """
    Полезно для получения списка доступных междугородних маршрутов автобусов Кипра (например, limassol, nicosia, larnaca).
    """
    return await cybuses_client.call_tool("get_intercity_routes")

async def get_schedule_tool(route: str) -> str:
    """
    Полезно для получения полного расписания автобусов для указанного маршрута.
    route: строка, один из вариантов: 'limassol', 'nicosia', 'larnaca'
    """
    return await cybuses_client.call_tool("get_schedule", {"route": route})

async def get_nearest_bus_tool(route: str, direction: str = None) -> str:
    """
    Полезно для поиска ближайшего рейса автобуса от текущего времени.
    route: строка ('limassol', 'nicosia', 'larnaca')
    direction: опционально строка ('from_paphos' или 'to_paphos')
    """
    return await cybuses_client.call_tool("get_nearest_bus", {"route": route, "direction": direction})

# Добавьте эти функции в список инструментов, доступных вашей LLM модели.
```

#### 4. Настройка переменных окружения
При запуске Docker-контейнера бота или локального процесса добавьте переменную окружения, указывающую на сервер `cybuses`:
```bash
CYBUSES_MCP_URL=http://<ip-адрес-сервера-cybuses>:8888/mcp
```
*(Если бот и сервер cybuses работают в одной Docker-сети, используйте имя сервиса: `http://cybuses:8888/mcp`)*


### Пример ответа `get_schedule`

```
📅 Расписание: Paphos ↔ Limassol
🚌 Paphos ➝ Limassol
   💶 Цена: € 5
   05:45, 06:10, 07:30, 08:00, 09:00, 10:00, ... 20:00

🚌 Limassol ➝ Paphos
   💶 Цена: € 5
   06:00, 06:25, 07:25, 08:00, ... 21:00
```

### Пример ответа `get_nearest_bus`

```
🕐 Ближайшие автобусы (14:35) — Limassol

🚌 Paphos ➝ Limassol
   ⏰ Ближайший: 15:00
   ⏳ Через 25 мин
   Следующие: 15:30, 16:00

🚌 Limassol ➝ Paphos
   ⏰ Ближайший: 15:00
   ⏳ Через 25 мин
   Следующие: 15:30, 16:00
```

### Docker: маппинг портов

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

| Проблема | Причина | Решение |
|----------|---------|---------|
| `GET /mcp → 404` | Открыли в браузере | MCP не работает через браузер. Используйте MCP-клиент |
| `Invalid HTTP request` | Браузер шлёт GET | Используйте MCP SDK (`streamablehttp_client`) |
| Нет данных | Сайт intercity-buses.com недоступен | Проверьте сетевой доступ из контейнера |

## ⚠️ Error Handling
If a parser fails to locate timetable data (e.g., website redesign or PDF link broken), the backend gracefully generates a visible red "Error Banner" injected natively into the UI to notify the user of the disruption, rather than silently failing.