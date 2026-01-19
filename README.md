# leads

FastAPI Clean Architecture API applying SOLID principles and GoF/GRASP design patterns.

## 🚀 Tech Stack

- **Python**: 3.12+
- **FastAPI**: 0.115+ (async web framework)
- **SQLAlchemy**: 2.0+ (async ORM)
- **PostgreSQL**: 16 (database)
- **Redis**: 7 (cache)
- **Alembic**: 1.14+ (migrations)
- **Pydantic**: 2.10+ (data validation)
- **Ruff**: 0.8+ (linter and formatter)

## 📁 Project Structure

```
leads/
├── app/
│   ├── api/              # HTTP Endpoints (presentation layer)
│   ├── core/             # Configuration, security, events
│   ├── db/               # SQLAlchemy session and base
│   ├── models/           # SQLAlchemy models (tables)
│   ├── schemas/          # Pydantic schemas (validation)
│   ├── repositories/     # Repository pattern (data access)
│   ├── services/         # Service layer (business logic)
│   ├── factories/        # Factory pattern (service creation)
│   └── utils/            # General utilities
├── tests/                # Unit and integration tests
├── alembic/              # Database migrations
└── docker-compose.yml    # Service orchestration
```

## 🎨 Applied Design Patterns

### SOLID
- **S**ingle Responsibility: Each module has a single responsibility
- **O**pen/Closed: Extendable without modifying existing code
- **L**iskov Substitution: Subclasses interchangeable with base classes
- **I**nterface Segregation: Specific and small interfaces
- **D**ependency Inversion: Dependencies on abstractions, not concretions

### GoF (Gang of Four)
- **Singleton**: Config, CacheService
- **Factory**: ServiceFactory for service creation
- **Strategy**: PasswordHasher (Bcrypt/Argon2 interchangeable)
- **Observer**: EventDispatcher for system events
- **Repository**: Data access abstraction

### GRASP
- **Creator**: Factories responsible for creating objects
- **Information Expert**: Each class knows its own data
- **Controller**: Endpoints as HTTP controllers
- **Low Coupling**: Independent modules
- **High Cohesion**: Related responsibilities together

## 🛠️ Installation and Usage

### Option 1: With Docker (Recommended)

```bash
# 1. Clone and enter directory
cd leads

# 2. Copy environment variables
cp .env.example .env

# 3. Edit .env with your settings
nano .env

# 4. Start services
docker-compose up -d

# 5. Run migrations
docker-compose exec api alembic upgrade head
```

### Option 2: Local Development

```bash
# 1. Create virtual environment with uv (recommended)
uv venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# 2. Install dependencies
uv sync
# or
pip install -r requirements.txt

# Note: If you see a warning about VIRTUAL_ENV not matching,
# it's safe to ignore. UV will create the correct virtual environment.

# 3. Copy and configure .env
cp .env.example .env

# 4. Start PostgreSQL and Redis (with Docker)
docker-compose up -d db redis

# 5. Run migrations
alembic upgrade head

# 6. Start development server
uvicorn app.main:app --reload
```

## 📚 API Endpoints

Once the server is started, the API is available at:

- **API Base**: http://localhost:8000
- **Interactive Documentation (Swagger)**: http://localhost:8000/docs
- **Alternative Documentation (ReDoc)**: http://localhost:8000/redoc

### Available Endpoints

#### Users
- `GET /api/v1/users` - List users
- `GET /api/v1/users/{id}` - Get user
- `POST /api/v1/users` - Create user
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user

#### Products
- `GET /api/v1/products` - List products

#### Orders
- `GET /api/v1/orders` - List orders

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific tests
pytest tests/unit/
pytest tests/integration/
```

## 🔧 Herramientas de Desarrollo

### Linting y Formateo

```bash
# Lint con ruff
ruff check .

# Formato con ruff
ruff format .

# Pre-commit hooks (automático antes de cada commit)
pre-commit install
pre-commit run --all-files
```

### Database Migrations

```bash
# Create new migration (autogenerate)
alembic revision --autogenerate -m "change description"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# View history
alembic history
```

## 🐛 Debugging

### Logs

```bash
# View API logs (docker-compose)
docker-compose logs -f api

# View API logs (docker)
docker logs mi-api

# View PostgreSQL logs
docker-compose logs -f db

# View Redis logs
docker-compose logs -f redis
```

### Database Access

```bash
# Connect to PostgreSQL (docker-compose)
docker-compose exec db psql -U postgres -d mi_api

# Connect to PostgreSQL (docker)
docker exec -it mi-api-db psql -U postgres -d mi_api

# Connect to Redis
docker-compose exec redis redis-cli
```

### Docker Management

```bash
# Run migrations
docker exec mi-api alembic upgrade head

# Create new migration
docker exec mi-api alembic revision --autogenerate -m "description"

# Restart services
docker-compose restart

# View service status
docker ps

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## 📖 Additional Documentation

### Adding a New Endpoint

1. Create model in `app/models/`
2. Create schema in `app/schemas/`
3. Create repository in `app/repositories/`
4. Create service in `app/services/`
5. Add factory method in `app/factories/service_factory.py`
6. Create endpoint in `app/api/v1/endpoints/`
7. Register router in `app/api/v1/router.py`
8. Create migration: `alembic revision --autogenerate -m "add new_model"`
9. Apply: `alembic upgrade head`

### Important Environment Variables

- `DATABASE_URL`: PostgreSQL connection URL
- `REDIS_URL`: Redis connection URL
- `SECRET_KEY`: Secret key for JWT (change in production)
- `CORS_ORIGINS`: Allowed origins for CORS

## 🤝 Contributing

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project uses a base architecture generated with professional design principles.

## 🙏 Acknowledgments

- FastAPI for the excellent framework
- SQLAlchemy for the powerful ORM
- Alembic for migrations
- Ruff for ultra-fast linting
