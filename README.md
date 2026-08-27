# JB Claims Processing

Simple claims processing application. Built on fastapi, and a nextjs portal. Uses postgress for persistence. Simple rest api

## Features

- Admin login (JWT)
- List claims with pagination and filtering by claim number / policy ID
- Create a claim against a policy
- Edit a claim's amount, incident date, and description
- Move a claim through its status lifecycle: `SUBMITTED` → `UNDER_REVIEW` →
  `APPROVED` / `REJECTED` → `PAID`. Invalid transitions are rejected by the API.

## Structure

```
.
├── Backend/            FastAPI service
│   ├── app/
│   │   ├── auth/          login, JWT issuing/verification
│   │   ├── claims/        claims CRUD + status transitions
│   │   ├── utils/         db session, logging, shared schemas
│   │   └── models.py      SQLAlchemy models
│   ├── migrations/        Alembic
│   ├── tests/             pytest
│   ├── seed.py            superadmin/demo data seeding
│   ├── entrypoint.sh      migrate + seed, then start uvicorn
│   └── Dockerfile
├── Frontend/           Next.js admin portal
│   ├── src/app/           /login, /claims, /claims/new, /claims/[id]
│   ├── src/lib/           API client, types, auth context
│   └── Dockerfile
├── docker-compose.yml  postgres + portal-api + portal
└── .env.example
```

## Stack choices

| Choice | Reason |
|---|---|
| FastAPI + Next.js as separate services | API and UI deploy and scale independently; API is usable by other clients later |
| FastAPI, async throughout | non-blocking DB I/O, matters under concurrent admin load |
| FastAPI / Pydantic | request/response schemas double as OpenAPI docs (`/docs`), nothing to hand-maintain |
| SQLAlchemy (async) | models, relationships, and indexes as Python instead of raw SQL |
| Postgres | relational integrity between claims/policies/customers, real transactions for status changes |
| Alembic | versioned, reviewable schema migrations instead of ad-hoc SQL |

## Setup

### Docker Compose (recommended)

```bash
cp .env.example .env

Update with your own values, then:

docker compose up --build
```

| Service | URL |
|---|---|
| postgres | localhost:5432 |
| portal-api | http://localhost:8000 (docs at `/docs`) |
| portal | http://localhost:3000 |

On first boot, `portal-api` runs Alembic migrations, seeds a superadmin from
`DEFAULT_SUPERADMIN_*` in `.env`, and — if `SEED_DEMO_DATA=true` — seeds a
sample customer/policy and two claims.

Log in at `http://localhost:3000` with `DEFAULT_SUPERADMIN_EMAIL` /
`DEFAULT_SUPERADMIN_PASSWORD` (defaults: `admin@example.com` / `ChangeMe123!`).

### Without Docker

Backend (needs a reachable Postgres):

```bash
cd Backend
python -m venv venv && source venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env   # edit POSTGRES_* etc.
set -a && source .env && set +a
alembic upgrade head
python seed.py
uvicorn main:app --reload
```

Frontend:

```bash
cd Frontend
npm install
cp .env.example .env.local
npm run dev
```

## Tests

The models expect a Postgres, so point at one at a throwaway
database, e.g.:

```bash
docker run -d --rm --name jb-test-pg \
  -e POSTGRES_DB=jbclaims_test -e POSTGRES_USER=jbclaims -e POSTGRES_PASSWORD=changeme \
  -p 5432:5432 postgres:16-alpine
```

Then, from `Backend/` with dev requirements installed:

```bash
export POSTGRES_HOST=localhost POSTGRES_PORT=5432
export POSTGRES_DB=jbclaims_test POSTGRES_USER=jbclaims POSTGRES_PASSWORD=changeme
export JWT_SECRET=test-secret
pytest
```

Schema is created from the SQLAlchemy models directly (not via Alembic) for
speed and isolation; each test runs in a transaction that's rolled back
afterward. Covers:

- create claim, invalid data → 422
- create claim, valid data → 200
- invalid status transition (`SUBMITTED` → `APPROVED`, skipping `UNDER_REVIEW`) → 400
- valid status transition → 200

## Assumptions and Omissions

- No customer/policy endpoints exist. Creating a claim requires an existing
  `policy_id`, currently only available via the demo seed or a direct insert.
  Out of scope for this exercise, which is scoped to the claims API. Assumed thats managed seperately

- Auth is single-step JWT with no refresh token; it just expires after
  `JWT_EXPIRY_HOURS`. No 2FA/MFA, .
- Tests build schema via `Base.metadata.create_all` rather than running
  Alembic migrations — deliberate, for speed and isolation.
- Assumed admins are managed seperately

## Scaling to 100,000+ Claims

Has the basics for scaling in place:

- Fully async DB access (SQLAlchemy async + asyncpg) — a slow query doesn't
  block the event loop from serving other concurrent requests.
- Indexes on the columns the API actually filters/sorts by: `claim_number`
  (unique), `policy_id`, `status`, `claim_type`, `incident_date`, `created_at`, etc.
- Connection pooling (`pool_size=20`, `max_overflow=40`).

Further improvements that can be done:

- **Pagination** — Use more advanced pagination like keyset, etc for better perfomnce

- **Caching** — read-heavy, rarely-changing lookups  can be put cache in front of Postgres using redis

- **Background workers** — for tasks that can run in async, enabled by rabbitmq or other broker.
- **Read replicas** for list/search traffic, leaving the primary for writes
  and status-transition transactions.
- **Table partitioning** (e.g. by `created_at`) once volume is well past
  100k or reasanable figure, mainly to keep indexes smaller and make archiving easier.
- **Observability** — can add prometheus, etc for monitoring

## Further Improvements

- **2FA/MFA on login** — Add this for extra security
- **External secrets management** (AWS Secrets Manager/Parameter Store,
  Vault) instead of plaintext env vars for `JWT_SECRET`, `POSTGRES_PASSWORD`,
  and the superadmin credentials, with rotation not requiring a redeploy.
- **Customer/policy management API** — none exists; claims can only
  reference policies already in the database. add later mgt for policies and customers
- **Refresh tokens / session revocation** — a leaked JWT is valid until it
  expires; no way to revoke one early.
- **Structured audit trail** — add more writing of stuff to the `AuditLog` 
