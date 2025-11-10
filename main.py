import os

import httpx
from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

security = HTTPBearer()
security_dependency = Depends(security)


def verify_token(credentials: HTTPAuthorizationCredentials):
    """
    Verify the bearer token against the configured API token.
    """
    api_bearer_token = os.environ["API_BEARER_TOKEN"]
    if credentials.credentials != api_bearer_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials


class QueryRequest(BaseModel):
    query: str = Field(
        ...,
        description="SQL query to execute on ClickHouse",
        example="SELECT * FROM system.tables LIMIT 5",
    )

    class Config:
        json_schema_extra = {"example": {"query": "SELECT name, engine FROM system.tables LIMIT 5"}}


API_SERVER_URL = os.environ.get("API_SERVER_URL")

# Initialize FastAPI app with OpenAPI metadata
app = FastAPI(
    title="ClickHouse Bridge API",
    version="1.0.0",
    description="OpenAPI-compliant bridge for querying ClickHouse databases",
    servers=[{"url": API_SERVER_URL, "description": "API Server"}],
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post(
    "/query",
    summary="Execute ClickHouse query",
    description="Execute a SQL query on the ClickHouse database. This is a thin proxy to the ClickHouse HTTP API.",
    tags=["Query"],
)
async def execute_query(
    query_request: QueryRequest, credentials: HTTPAuthorizationCredentials = security_dependency
):
    """
    Execute a SQL query on ClickHouse via HTTP API.

    The query is forwarded directly to ClickHouse's HTTP interface with minimal processing.
    Response format and structure are determined by ClickHouse.

    - **query**: The SQL query to execute
    - **parameters**: Optional query parameters (not commonly used with HTTP API)
    """
    # Verify the bearer token
    verify_token(credentials)

    # Build the ClickHouse URL with query parameters
    url = os.environ.get("CLICKHOUSE_URL", "http://localhost:8123")

    # Get configuration
    query = query_request.query
    clickhouse_database = os.environ.get("CLICKHOUSE_DATABASE", "default")
    clickhouse_username = os.environ.get("CLICKHOUSE_USERNAME", "default")
    clickhouse_password = os.environ.get("CLICKHOUSE_PASSWORD", "")

    # Build query parameters
    params = {"default_format": "JSONCompact"}
    if clickhouse_database:
        params["database"] = clickhouse_database

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                url,
                params=params,
                content=query,
                auth=(clickhouse_username, clickhouse_password),
                headers={"Content-Type": "text/plain"},
                timeout=30.0,
            )

            # If ClickHouse returns an error status code, raise an HTTPException
            # so ChatGPT can see the error message
            if response.status_code >= 400:
                error_message = response.text
                raise HTTPException(
                    status_code=response.status_code, detail=f"ClickHouse error: {error_message}"
                )

            # Return the raw ClickHouse response for successful queries
            return Response(
                content=response.content,
                status_code=response.status_code,
                media_type=response.headers.get("content-type", "application/json"),
            )
        except httpx.RequestError as e:
            # Handle connection errors, timeouts, etc.
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to connect to ClickHouse: {str(e)}",
            ) from e


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
