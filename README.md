# LLM Inference Gateway

A lightweight API gateway for Large Language Model (LLM) inference, built
with FastAPI and Groq. The gateway provides a centralized interface for
LLM requests, Redis-based response caching, API-key authentication,
concurrency control, and basic request metrics.

The project explores backend engineering concepts relevant to serving
LLM applications, including asynchronous I/O, request validation,
caching, resource management, and latency measurement.

## Features

- **LLM inference:** Send prompts to a Groq-hosted language model through
  a centralized API.
- **Asynchronous API:** Use FastAPI and HTTPX for asynchronous request
  handling and upstream HTTP calls.
- **Redis response caching:** Cache eligible responses using a
  deterministic SHA-256 cache key and configurable expiration time.
- **API-key authentication:** Protect chat and monitoring endpoints using
  an `X-API-Key` HTTP header.
- **Concurrency control:** Limit simultaneous upstream inference calls
  using an `asyncio.Semaphore`.
- **Request metrics:** Track request counts, cache hits, cache misses,
  completed requests, provider errors, and average recorded latency.
- **Request validation:** Validate incoming chat requests using Pydantic.
- **Error handling:** Translate upstream provider failures into
  appropriate HTTP responses.
- **Interactive API documentation:** Explore and test endpoints through
  FastAPI's Swagger UI.

## Architecture

```text
                    Client Application
                           |
                           v
                    FastAPI Gateway
                           |
                  API-Key Authentication
                           |
                           v
                 Request Validation
                           |
                           v
                  Redis Cache Lookup
                           |
                 +---------+---------+
                 |                   |
              Cache Hit           Cache Miss
                 |                   |
                 |                   v
                 |           Concurrency Control
                 |                   |
                 |                   v
                 |              Groq API
                 |                   |
                 |                   v
                 |             LLM Response
                 |                   |
                 |                   v
                 |            Redis Cache Write
                 |                   |
                 +---------+---------+
                           |
                           v
                    JSON Response
                           |
                           v
                         Client
```

Monitoring is exposed through a separate authenticated endpoint.

## Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| API framework | FastAPI | HTTP endpoints and request handling |
| Language | Python | Application logic |
| LLM provider | Groq API | Hosted LLM inference |
| HTTP client | HTTPX | Asynchronous upstream requests |
| Cache | Redis | Temporary response storage |
| Configuration | Pydantic Settings | Environment-based configuration |
| Validation | Pydantic | Request and response schemas |
| Concurrency | asyncio | Asynchronous execution and concurrency limiting |
| API documentation | Swagger UI | Interactive API exploration |

## Project Structure

```text
llm-inference-gateway/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── health.py
│   │       ├── chat.py
│   │       └── metrics.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── redis_client.py
│   │   ├── limits.py
│   │   └── metrics.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── chat.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── cache.py
│   │   └── llm_provider.py
│   └── main.py
├── tests/
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

The structure separates HTTP routes, application configuration,
request schemas, security, metrics, caching, and LLM provider logic.

## Prerequisites

- Python 3.11 or newer recommended.
- Redis running locally or at a configured Redis URL.
- A Groq API key.
- Git.

The implementation should also be compatible with your installed Python
version, provided all dependencies support it.

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Adi485455/llm-inference-gateway.git
cd llm-inference-gateway
```

### 2. Create a virtual environment

macOS and Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file using `.env.example` as a reference.

Example configuration:

```dotenv
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b

REDIS_URL=redis://localhost:6379/0
CACHE_TTL_SECONDS=300

GATEWAY_API_KEY=replace_with_a_strong_random_secret
MAX_CONCURRENT_REQUESTS=5
```

Replace the placeholder values with your own configuration.

Never commit `.env` or expose API keys in source code, logs, screenshots,
or public repositories.

The gateway API key is used by clients to authenticate with this
application. The Groq API key is used by the gateway to authenticate
with the upstream provider.

### 5. Start Redis

If Redis is installed through Homebrew on macOS:

```bash
brew services start redis
```

Verify that Redis is running:

```bash
redis-cli ping
```

Expected output:

```text
PONG
```

If Redis is already running, there is no need to start it again.

### 6. Start the gateway

From the project root:

```bash
uvicorn app.main:app --reload
```

The application will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

| Method | Endpoint | Authentication | Description |
|---|---|---|---|
| GET | `/health` | Not required | Health-check endpoint |
| POST | `/v1/chat/completions` | `X-API-Key` | Generate an LLM response |
| GET | `/admin/metrics` | `X-API-Key` | Retrieve application metrics |

### 1. Health Check

Request:

```bash
curl http://127.0.0.1:8000/health
```

The endpoint returns the application's health response.

Note that an application health check does not necessarily confirm
that Redis and the upstream LLM provider are available.

### 2. Chat Completion

Endpoint:

```text
POST /v1/chat/completions
```

Required header:

```text
X-API-Key: your_gateway_api_key
```

Example request:

```bash
curl -X POST http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_gateway_api_key" \
  -d '{
    "message": "Explain binary search in simple terms."
  }'
```

Example response:

```json
{
  "model": "openai/gpt-oss-20b",
  "response": "Binary search is an efficient algorithm for finding an item in a sorted collection..."
}
```

The actual response depends on the configured model and prompt.

### 3. Monitoring Metrics

Endpoint:

```text
GET /admin/metrics
```

Required header:

```text
X-API-Key: your_gateway_api_key
```

Example request:

```bash
curl http://127.0.0.1:8000/admin/metrics \
  -H "X-API-Key: your_gateway_api_key"
```

The endpoint returns counters and latency information maintained by
the application.

The exact values depend on requests processed since the application
started.

## How Response Caching Works

The gateway checks Redis before making an upstream inference request.

1. Receive and validate the incoming request.
2. Construct a cache key from the model and prompt.
3. Hash the serialized request data using SHA-256.
4. Look up the key in Redis.
5. Return the cached response if an entry exists.
6. Otherwise, call the LLM provider.
7. Store the generated response with a configurable TTL.
8. Return the response to the client.

The default cache expiration is 300 seconds.

Conceptually:

```text
Request
   |
   v
Generate Cache Key
   |
   v
Redis Lookup
   |
   +---- Hit ----> Return Cached Response
   |
   +---- Miss ---> Call LLM Provider
                       |
                       v
                  Cache Result
                       |
                       v
                  Return Response
```

### Benefits

- Avoids repeated upstream inference for identical eligible requests.
- Can reduce response latency for cache hits.
- Can reduce upstream API usage.
- Separates caching logic from the provider implementation.

### Limitations

The current cache uses exact prompt matching. Semantically similar prompts
are not considered equivalent.

The cache key must be extended if the request schema later includes
parameters such as temperature, output token limits, system instructions,
or other generation settings.

Sensitive prompts and generated responses require appropriate access
controls and retention policies. Hashing the cache key does not encrypt
the cached content.

## Concurrency Control

The gateway uses an `asyncio.Semaphore` to limit the number of simultaneous
upstream inference calls within one application process.

The configured default is five concurrent calls.

This helps control the number of requests actively consuming upstream
inference capacity.

The semaphore does not provide a bounded waiting queue. Additional requests
may wait for an available slot, and the limit is not shared across multiple
application processes or machines.

A production implementation would need explicit queue limits, request
deadlines, overload responses, and potentially distributed rate limiting.

## Authentication

The gateway protects its chat and monitoring endpoints using the
`X-API-Key` request header.

Requests without a valid key are rejected with HTTP 401.

The key is compared using `secrets.compare_digest()`.

For production use, authentication should be complemented by secure secret
storage, key rotation, HTTPS, access logging, and appropriate rate limits.

## Error Handling

The gateway handles common upstream failures and maps provider errors
to HTTP 502 responses.

Unexpected gateway errors are handled separately.

Redis failure handling and more comprehensive timeout, retry, and overload
policies remain areas for improvement.

The gateway does not currently implement a complete production-grade
retry or circuit-breaker system.

## Performance Evaluation

The project includes basic request metrics and supports manual comparisons
between cache hits and cache misses.

For meaningful benchmarks, measure:

- Median latency (P50).
- Tail latency (P95).
- Throughput in requests per second.
- Cache hit ratio.
- Upstream provider errors.
- Behavior under concurrent load.

Record the test environment, request workload, number of iterations,
and whether measurements include network and provider latency.

Do not interpret a small local benchmark as a guarantee of production
performance.

Benchmark results should be added here after running reproducible tests.

## Current Limitations

- Uses a single configured LLM provider.
- Caching uses exact request matching rather than semantic similarity.
- Metrics are stored in process memory and reset on application restart.
- Metrics are not shared across multiple application workers.
- Concurrency control applies within a single process.
- Waiting requests are not managed by a bounded queue.
- Redis outages and overload scenarios need more robust handling.
- Production deployment, TLS termination, and distributed rate limiting
  are not yet implemented.

## Roadmap

- [x] FastAPI application and health endpoint
- [x] Groq provider integration
- [x] Redis response caching
- [x] Gateway API-key authentication
- [x] Basic concurrency control
- [x] Basic request metrics
- [ ] Graceful degradation when Redis is unavailable
- [ ] Improved request deadlines and overload handling
- [ ] Reproducible load testing and benchmark reports
- [ ] Containerized deployment
- [ ] Multi-provider routing

## Learning Outcomes

This project explores practical backend and LLM-serving concepts:

- Designing API boundaries around LLM inference.
- Separating routes, schemas, configuration, and provider logic.
- Using asynchronous HTTP clients.
- Implementing TTL-based response caching.
- Managing concurrent upstream requests.
- Protecting endpoints with API-key authentication.
- Collecting basic latency and request metrics.
- Evaluating the trade-offs between latency, caching, and resource usage.

## License

No license has been specified yet.