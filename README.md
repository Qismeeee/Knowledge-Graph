# Code Knowledge Graph

Deterministic code indexing and cross-service dependency analysis for monorepo/multi-repo environments. Specialized for banking domain (C#/ASP.NET, Python, TypeScript, Go).

## Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Git

### Setup

```bash
# Install dependencies
pip install -e ".[dev]"

# Copy env file
cp .env.example .env

# Start Neo4j + API
docker-compose up -d

# Run tests
pytest -v

# Start API (local)
python app/main.py
```

API available at `http://localhost:8000`  
Neo4j Browser: `http://localhost:7474`  
Swagger Docs: `http://localhost:8000/docs`

## Architecture

```
ckg/
├── config/           # Settings, logging
├── app/
│   ├── main.py       # FastAPI entry
│   ├── models/       # Pydantic schemas
│   ├── api/          # Route handlers
│   ├── domain/       # Business logic
│   ├── infrastructure/ # DB, external services
│   └── extractors/   # Language-specific parsers
├── tests/            # Tests
└── docs/             # Documentation
```

## Features

- **Multi-language indexing**: Python, TypeScript, C#, Go
- **Banking patterns**: DbContext, DDD aggregates, event handlers, gRPC services
- **Deterministic extraction**: Tree-sitter AST + regex patterns
- **Cross-service dependency**: HTTP, gRPC, event, shared DB detection
- **Knowledge graph**: Neo4j storage + Cypher queries
- **Q&A pipeline**: Intent classification → Entity resolution → Retrieval → Synthesis

## Development

```bash
# Format code
black app tests

# Lint
ruff check app tests

# Type check
mypy app

# Run tests with coverage
pytest --cov=app --cov-report=html
```

## Dependencies

- **FastAPI**: Web framework
- **Neo4j**: Graph database
- **tree-sitter**: Code parsing
- **litellm**: LLM integration
- **APScheduler**: Job scheduling

See `requirements.txt` for full list.

## Project Status

**Phase 1**: ✅ Project setup (pyproject, Docker, basic API)  
**Phase 2**: In progress - Neo4j schema + code extractors  
**Phase 3**: Planned - Cross-service resolution  
**Phase 4**: Planned - Q&A engine  
**Phase 5**: Planned - Evaluation + dashboard
