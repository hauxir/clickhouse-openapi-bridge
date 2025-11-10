# ClickHouse OpenAPI Bridge

An OpenAPI-compliant HTTP bridge for querying ClickHouse databases. This lightweight FastAPI service provides a secure, authenticated REST API interface to execute SQL queries against ClickHouse.

## Features

- **OpenAPI/Swagger Documentation**: Auto-generated API documentation at `/docs`
- **Bearer Token Authentication**: Secure API access with token-based authentication
- **ClickHouse Proxy**: Thin proxy layer to ClickHouse's HTTP interface
- **CORS Support**: Cross-origin resource sharing enabled for web applications
- **Docker Support**: Containerized deployment with Docker
- **Modern Python Stack**: Built with FastAPI, Pydantic, and httpx

## Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended) or pip
- ClickHouse database instance
- Docker (optional, for containerized deployment)

## Installation

### Using uv

```bash
# Clone the repository
git clone <repository-url>
cd clickhouse-openapi-bridge

# Install dependencies
uv sync
```

## Configuration

Create a `.env` file in the project root (use `.env.example` as a template):

```bash
# API Authentication
API_BEARER_TOKEN=your-secret-token-here

# ClickHouse Configuration
CLICKHOUSE_URL=http://localhost:8123
CLICKHOUSE_USERNAME=default
CLICKHOUSE_PASSWORD=
CLICKHOUSE_DATABASE=default

# Server Configuration
API_SERVER_URL=http://localhost:8000
```

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `API_BEARER_TOKEN` | Bearer token for API authentication | - | Yes |
| `API_SERVER_URL` | Public URL of the API server | - | Yes |
| `CLICKHOUSE_URL` | ClickHouse HTTP interface URL | `http://localhost:8123` | Yes |
| `CLICKHOUSE_USERNAME` | ClickHouse username | `default` | Yes |
| `CLICKHOUSE_PASSWORD` | ClickHouse password | `` | Yes |
| `CLICKHOUSE_DATABASE` | Default database to query | `default` | Yes |

## Usage

### Running Locally

```bash
# Using uv
uv run uvicorn main:app --host 0.0.0.0 --port 8000

# Or with hot reload for development
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Using the provided run script
chmod +x run.sh
./run.sh
```

### Running with Docker

```bash
# Build the Docker image
docker build -t clickhouse-openapi-bridge .

# Run the container
docker run -p 8000:8000 \
  -e API_BEARER_TOKEN=your-secret-token \
  -e CLICKHOUSE_URL=http://clickhouse:8123 \
  -e CLICKHOUSE_USERNAME=default \
  -e CLICKHOUSE_PASSWORD=your-password \
  -e CLICKHOUSE_DATABASE=default \
  clickhouse-openapi-bridge
```

## API Documentation

Once the service is running, visit:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

### API Endpoints
- Returns data in ClickHouse's JSONCompact format by default
- Status codes:
  - `200`: Query executed successfully
  - `401`: Invalid or missing authentication token
  - `400-499`: ClickHouse query error
  - `503`: Failed to connect to ClickHouse

## Development

```bash
# Run linter
uv run ruff check .

# Format code
uv run ruff format .

# Fix auto-fixable issues
uv run ruff check --fix .
```
