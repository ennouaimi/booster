# Booster

Booster is a **configurable Spring Boot project starter**. The goal is to avoid rebuilding the same infrastructure every time a new Java/Spring service is created.

It provides a reusable technical foundation while deliberately leaving application-specific business code out of the generated project.

## What Booster can generate

A new project can include, depending on configuration:

- Java 21 + Spring Boot 3.5
- REST API + Bean Validation
- Spring Data JPA
- PostgreSQL or H2
- Flyway migrations
- JWT authentication with register/login
- BCrypt password hashing
- role-ready Spring Security
- configurable public endpoints
- configurable CORS origins
- Swagger / OpenAPI
- Spring Boot Actuator health + metrics
- Bucket4j HTTP rate limiting
- Dockerfile + PostgreSQL Docker Compose
- JUnit / Spring Boot test dependencies
- optional Testcontainers dependencies
- standardized API error responses
- `/api/ping` starter endpoint
- environment-variable based configuration

The generated code contains infrastructure only. It does **not** include application-specific domain code.

## Quick start

Generate a project with the defaults:

```bash
python generate.py invoice-api
```

Choose the main options directly from the command line:

```bash
python generate.py invoice-api \
  --package com.mycompany.invoice \
  --security jwt \
  --database postgres
```

Minimal API without authentication:

```bash
python generate.py public-catalog \
  --package com.mycompany.catalog \
  --security none \
  --database postgres \
  --no-rate-limit
```

You can also configure everything in one file:

```bash
cp booster.example.json booster.json
python generate.py --config booster.json
```

By default the project is generated into a directory named after the service. Use `--output` to choose another directory.

## Configuration

Example:

```json
{
  "name": "billing-service",
  "group": "com.acme",
  "package": "com.acme.billing",
  "description": "Billing API",
  "java": 21,
  "port": 8080,
  "database": "postgres",
  "flyway": true,
  "security": "jwt",
  "cors_origins": [
    "http://localhost:3000",
    "https://app.acme.com"
  ],
  "public_paths": [
    "/api/auth/**",
    "/actuator/health",
    "/swagger-ui/**",
    "/v3/api-docs/**"
  ],
  "swagger": true,
  "actuator": true,
  "rate_limit": true,
  "rate_limit_requests_per_minute": 120,
  "docker": true,
  "testcontainers": true
}
```

### Security

`security` currently supports:

- `jwt`: stateless JWT authentication, user persistence, register/login endpoints, BCrypt and Spring Security.
- `none`: no authentication layer generated.

Security-specific values such as the JWT secret are **not committed into the generated application**. They are read from environment variables.

### Database

`database` supports:

- `postgres`: production-oriented PostgreSQL configuration and optional Docker Compose.
- `h2`: lightweight in-memory database, useful for prototypes.

With Flyway enabled, Booster creates the initial migration folder automatically.

## Environment variables

The generated project contains `.env.example`. Typical variables are:

```text
PORT=8080
PGHOST=localhost
PGPORT=5432
PGDATABASE=app
PGUSER=app
PGPASSWORD=app
JWT_SECRET=replace-with-a-long-random-secret-at-least-32-bytes
SWAGGER_ENABLED=true
RATE_LIMIT_RPM=120
```

Never commit the real `.env` file or production secrets.

## Why these defaults?

These defaults cover common needs for modern Spring Boot services: externalized PostgreSQL configuration, Flyway migrations, stateless JWT security, explicit CORS, Swagger toggles, Actuator health probes, metrics, rate limiting, Docker support and reusable error handling.

Business-specific code is intentionally excluded so Booster stays useful for unrelated Spring projects.

## Intended workflow

```text
Booster config
     ↓
python generate.py
     ↓
ready Spring Boot skeleton
     ↓
add the new project's domain code
```

The important idea is that **the generated application is disposable; Booster is the source of truth for the technical starter**. Improvements that are useful to every future Spring project should be added here rather than copied manually from one application to another.
