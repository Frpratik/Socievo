# SocietySaver — Group-Buying Marketplace for Residential Housing Societies

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2014-black.svg?logo=next.js)](https://nextjs.org)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791.svg?logo=postgresql)](https://www.postgresql.org)
[![Redis](https://img.shields.io/badge/Cache-Redis-DC382D.svg?logo=redis)](https://redis.io)

**SocietySaver** is an enterprise-grade, full-stack marketplace connecting residential housing societies across India with pre-vetted service vendors for volume-discounted home services (AC maintenance, deep cleaning, RO repair, pest control, car washing, etc.).

By aggregating demand from residents within the same gated community or apartment society, the platform unlocks tiered volume pricing, lowers vendor acquisition and logistics costs, and delivers transparent, auditable booking, payment, and scheduling workflows.

---

## 🏛️ System Architecture Overview

```
                                  +-----------------------------+
                                  |     Next.js 14 Frontend     |
                                  | (App Router, Tailwind, TS)  |
                                  +--------------+--------------+
                                                 | HTTPS / REST
                                                 v
                                  +-----------------------------+
                                  |     FastAPI Backend API     |
                                  |  (Modular Monolith, v1)     |
                                  +---+----------+----------+---+
                                      |          |          |
                   +------------------+          |          +------------------+
                   v                             v                             v
+-------------------------------+ +-------------------------------+ +-------------------------------+
|     PostgreSQL (Source)       | |     Redis (Cache & Queue)     | |   Celery Background Worker    |
| (Multi-tenant schema, UTC)    | | (Token revocation, rate limit)| | (Deal expiry, notifications)  |
+-------------------------------+ +-------------------------------+ +-------------------------------+
```

---

## 📁 Repository Structure

```
├── backend/                  # FastAPI Python backend
│   ├── app/
│   │   ├── api/v1/           # Modular domain routers (auth, societies, deals, bookings, etc.)
│   │   ├── core/             # Security, JWT, hashing, config, logging, middleware
│   │   ├── db/               # SQLAlchemy 2.x async session, base models, migrations
│   │   ├── models/           # Domain entity models (PostgreSQL)
│   │   ├── schemas/          # Pydantic v2 validation & response schemas
│   │   ├── services/         # Business logic layer (GroupBuyingEngine, Payments, etc.)
│   │   └── workers/          # Celery / background worker tasks
│   ├── tests/                # Pytest unit & integration test suites
│   ├── alembic/              # Database migration versions
│   └── requirements.txt      # Pinned Python dependencies
├── frontend/                 # Next.js 14 App Router TypeScript frontend
│   ├── src/
│   │   ├── app/              # App router pages (public, resident, admin, vendor)
│   │   ├── components/       # Reusable UI & design system components
│   │   ├── hooks/            # TanStack Query & custom React hooks
│   │   ├── lib/              # API client, auth session, utilities
│   │   └── types/            # Typed TypeScript contracts matching OpenAPI
│   └── package.json
├── infra/                    # Docker Compose & local infrastructure setup
├── docs/                     # Architecture, specifications, and runbooks
│   ├── architecture.md       # Full architectural blueprint & domain boundaries
│   ├── database-schema.md    # Detailed entity relationships, constraints, indexes
│   ├── permissions.md        # Comprehensive RBAC matrix
│   ├── group-buying-rules.md # Tier pricing engine, repricing semantics & state machine
│   ├── implementation-plan.md# Master checklist across development phases
│   ├── api-guide.md          # REST API standards & documentation
│   ├── payments.md           # Payment flow, reconciliation & webhook security
│   └── deployment.md         # Production rollout & operational guides
├── .env.example              # Environment variables template
└── README.md
```

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.12+
- Node.js 20+ & npm 11+
- PostgreSQL & Redis (or Docker)

### Phase-by-Phase Roadmap
Refer to [`docs/implementation-plan.md`](./docs/implementation-plan.md) for the active phase checklist and verification steps.
