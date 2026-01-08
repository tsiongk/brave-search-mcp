# Brave Search MCP Server

A Dedalus MCP server that provides web and local search capabilities using the [Brave Search API](https://brave.com/search/api/).

## Features

- **Web Search**: General web search for articles, news, and online content
- **Local Search**: Find local businesses, restaurants, and places with ratings, hours, and contact info

## Setup

### 1. Get a Brave API Key

1. Go to [Brave Search API](https://brave.com/search/api/)
2. Sign up for an API key
3. Copy your subscription token

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```
BRAVE_API_KEY=your_api_key_here
```

### 3. Install Dependencies

```bash
uv sync
```

### 4. Run the Server

```bash
uv run python src/main.py
```

The server will start on `http://localhost:8080`.

## Tools

### `brave_web_search`

Performs a web search using the Brave Search API.

**Parameters:**
- `query` (str, required): Search query (max 400 chars, 50 words)
- `count` (int, optional): Number of results (1-20, default 10)
- `offset` (int, optional): Pagination offset (max 9, default 0)

**Example:**
```python
await client.call_tool("brave_web_search", {
    "query": "python async programming",
    "count": 5
})
```

### `brave_local_search`

Searches for local businesses and places.

**Parameters:**
- `query` (str, required): Local search query (e.g., "pizza near Central Park")
- `count` (int, optional): Number of results (1-20, default 5)

**Example:**
```python
await client.call_tool("brave_local_search", {
    "query": "coffee shops in San Francisco",
    "count": 3
})
```

## Testing

Run the test client:

```bash
uv run python src/client.py
```

## License

MIT
