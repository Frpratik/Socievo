# SocietySaver — Architecture Specification & Technical Blueprint

## 1. Executive Architecture Summary

SocietySaver is designed as a **modular monolith** with clean bounded contexts, explicit domain boundaries, and strong multi-tenant data isolation. The system pairs a high-performance **FastAPI** asynchronous backend (Python 3.12) with a modern **Next.js 14 App Router** frontend (React 18/19, TypeScript in strict mode, Tailwind CSS).

The platform serves four primary personas:
1. **Residents**: Discover deals, join group-buying campaigns, schedule services, execute payments, manage bookings, rate services.
2. **Society Administrators**: Manage society membership, invite residents, initiate/approve society-specific deals, review aggregate service stats.
3. **Service Vendors**: Manage service offerings, set tiered rate cards, review and accept bookings, dispatch technicians, track payouts.
4. **Platform Administrators**: Supervise system entities, verify vendors, configure platform commissions/tax rates, resolve disputes, view financial metrics.

---

## 2. Architecture Decision Records (ADRs)

### ADR 001: Modular Monolith vs Microservices
- **Decision**: Adopt a modular monolith rather than distributed microservices for Phase 1–10.
- **Rationale**: Keeps transactional boundaries simple, avoids distributed 2-phase commits for group deal participation and payments, eliminates network latency between micro-domains, and dramatically eases local development, testing, and deployment while maintaining modular package boundaries for future service extraction if needed.

### ADR 002: Financial Precision & Monetary Representation
- **Decision**: All financial figures (prices, discounts, taxes, fees, commissions, refunds) are strictly represented as **64-bit integers in the smallest currency unit** (e.g., Indian Paise: ₹1.00 = 100 paise).
- **Rationale**: Eliminates floating-point rounding errors and discrepancy issues in financial ledgers, invoice calculations, and payment provider integrations.

### ADR 003: Concurrency Control for Group Deal Participation & Slots
- **Decision**: Use database-level row locking (`SELECT ... FOR UPDATE`) inside atomic database transactions for deal participation counters, capacity checks, and slot reservations.
- **Rationale**: Prevents overselling deal capacity, avoids race conditions when multiple residents join simultaneously at threshold boundaries, and ensures consistent price snapshot generation.

### ADR 004: Multi-Tenancy Isolation
- **Decision**: Shared PostgreSQL database with mandatory foreign keys (`society_id`, `vendor_id`) and tenant context verification enforced at the repository/service layer and scoped in every database query.
- **Rationale**: Provides high developer ergonomics and resource efficiency while enforcing strict authorization barriers.

---

## 3. High-Level System Architecture Diagram

```
+-----------------------------------------------------------------------------------+
|                                 CLIENT CLIENTS                                    |
|   +------------------------------------+    +---------------------------------+   |
|   |   Resident Mobile / Web Browser   |    |    Society Admin & Vendor Portal|   |
|   |         (Next.js App Router)       |    |         (Next.js App Router)    |   |
|   +-----------------+------------------+    +----------------+----------------+   |
+---------------------|----------------------------------------|--------------------+
                      | HTTPS / REST APIs (`/api/v1/*`)        |
                      v                                        v
+-----------------------------------------------------------------------------------+
|                             API INGRESS / REVERSE PROXY                           |
|                         (Nginx / Traefik / Docker Compose)                        |
+-----------------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------------+
|                        FASTAPI APPLICATION (MODULAR MONOLITH)                     |
|                                                                                   |
|  +--------------------+  +--------------------+  +-----------------------------+  |
|  | Auth & Identity    |  | Societies & Units  |  | Service Catalog & Vendors   |  |
|  +--------------------+  +--------------------+  +-----------------------------+  |
|  +--------------------+  +--------------------+  +-----------------------------+  |
|  | Group-Buying Engine|  | Bookings & Slots   |  | Payments & Webhooks         |  |
|  +--------------------+  +--------------------+  +-----------------------------+  |
|  +--------------------+  +--------------------+  +-----------------------------+  |
|  | Reviews & Disputes |  | Notifications      |  | Analytics & Audit Ledger    |  |
|  +--------------------+  +--------------------+  +-----------------------------+  |
|                                                                                   |
|  Core Services Layer:                                                             |
|  - GroupBuyingService  - PricingCalculationEngine - PaymentService                |
|  - BookingService      - NotificationDispatcher    - AuditLogger                  |
+--------------------+-------------------+--------------------+---------------------+
                     |                   |                    |
                     v                   v                    v
+-------------------------+  +------------------------+  +--------------------------+
|  PostgreSQL Database    |  |  Redis Key-Value Cache |  | Celery Task Queue Worker |
|  - ACID Transactions    |  |  - Session / Blacklist |  | - Deal Expiration Task   |
|  - Row-Level Locking    |  |  - Rate Limiting       |  | - Repricing / Refunds    |
|  - Immutable Ledgers    |  |  - PubSub / Celery Q   |  | - Email / Push Reminders |
+-------------------------+  +------------------------+  +--------------------------+
                     |
                     v
+-----------------------------------------------------------------------------------+
|                              EXTERNAL INTEGRATIONS                                |
|  +---------------------+   +---------------------+   +-------------------------+  |
|  | Payment Gateway     |   | Email Provider      |   | Object Storage          |  |
|  | (Razorpay / Mock)   |   | (SMTP / SendGrid)   |   | (Local FS / MinIO / S3) |  |
|  +---------------------+   +---------------------+   +-------------------------+  |
+-----------------------------------------------------------------------------------+
```

---

## 4. Domain Boundaries & Modular Architecture

The FastAPI backend is structured cleanly by domain in `backend/app/`:

| Domain Module | Primary Responsibilities |
| :--- | :--- |
| `auth` | User registration, password hashing (Argon2id), JWT issue/refresh, session revocation, RBAC dependencies. |
| `societies` | Housing society profiles, wings/buildings, flat units, resident membership verification, invite codes. |
| `vendors` | Vendor business registration, document verification status, coverage areas, service catalog offerings. |
| `services` | Master category taxonomy (AC, RO, Cleaning, Plumbing, Electrical), service items, base pricing units. |
| `deals` | **Group-Buying Engine**: Deal creation, tiered pricing rates, participation tracking, threshold triggers, state transitions. |
| `bookings` | Appointment slot reservation, scheduling, vendor assignment, technician dispatch, proof of completion. |
| `payments` | Razorpay order generation, signed webhook verification, mock payment sandbox, immutable financial ledger. |
| `notifications` | In-app notifications, email notifications, deal countdown reminders. |
| `reviews` | Verified booking reviews, vendor ratings, complaints, support tickets, dispute resolution. |
| `admin` | Platform oversight, entity approval/suspension, global commission configuration, audit log exploration. |
| `analytics` | Aggregated KPIs: Gross Booking Value, platform revenue, society conversion, vendor performance. |

---

## 5. Security & Isolation Architecture

1. **Authentication**:
   - Access tokens: Short-lived JWT (30 mins) with user ID, role, and active society context.
   - Refresh tokens: Long-lived (7 days) stored as cryptographically hashed records in the database with Redis revocation checks.
   - Secure HttpOnly cookies with `SameSite=Lax` and configurable `Secure` flags.
2. **Authorization**:
   - Explicit dependency injection guards (`require_role(Role.RESIDENT)`, `require_society_member`, `require_platform_admin`).
   - Every read/write query verifies `society_id` against the authenticated user's approved memberships.
3. **Data Protection**:
   - Zero storage of raw cardholder data (delegated to PCI-DSS compliant Razorpay).
   - Sensitive vendor documents served via short-lived signed URLs.
   - Comprehensive audit logging (`audit_logs` table) for all administrative and financial changes.
