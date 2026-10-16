# SocietySaver — Master Implementation Plan & Phase Tracking

This checklist is the authoritative, persistent tracking document for the development lifecycle of SocietySaver.

---

## 📋 Phase 1: Repository Inspection and Architecture
- [x] Environment inspection (Python 3.12, Node 20, npm 11, Git, Docker verified)
- [x] Git repository initialization
- [x] Root `.gitignore` and `.env.example` creation
- [x] Architecture Specification authored (`docs/architecture.md`)
- [x] Database Schema Specification authored (`docs/database-schema.md`)
- [x] RBAC & Permissions Matrix authored (`docs/permissions.md`)
- [x] Group-Buying Engine Rules & Pricing Semantics authored (`docs/group-buying-rules.md`)
- [x] Master Implementation Plan setup (`docs/implementation-plan.md`)
- [x] Phase 1 Completion Report and formal Phase 2 approval request

---

## 📋 Phase 2: Foundation and Development Environment
- [x] Backend skeleton with FastAPI, Pydantic v2 Settings, and async SQLAlchemy 2.x
- [x] Database session management, Alembic migration framework initialized
- [x] Redis caching & token blacklist helper modules
- [x] Unified application logging, exception handlers, and standard API error schemas
- [x] Frontend setup: Next.js 14 App Router with TypeScript strict mode and Tailwind CSS
- [x] Docker Compose environment (`docker-compose.yml`) for PostgreSQL, Redis, backend, frontend
- [x] Health and readiness endpoints (`/api/v1/health`, `/api/v1/ready`)
- [x] Automated test baseline (pytest runner and sample test passing — 10/10 passed)

---

## 📋 Phase 3: Identity, Authentication, and Tenant Isolation
- [x] User model, Argon2id password hashing, and JWT token service
- [x] Refresh token rotation, session tracking, and Redis token revocation
- [x] Auth endpoints: Register, Login, Refresh, Logout, Profile (`/api/v1/auth/*`)
- [x] Society and SocietyMembership models with wing and flat unit mappings
- [x] Multi-tenant isolation dependencies (`get_current_active_user`, `require_society_member`, `require_society_admin`)
- [x] Society Admin verification and resident membership approval workflows
- [x] Unit & negative access-control integration tests for authentication and multi-tenancy (14/14 tests passing)

---

## 📋 Phase 4: Service Catalog and Vendor Management
- [ ] ServiceCategory and ServiceItem models and endpoints
- [ ] Vendor business profile, verification state, and service offering models
- [ ] Document verification boundary and mock signed URL generation
- [ ] Vendor onboarding and catalog configuration endpoints (`/api/v1/vendors/*`, `/api/v1/services/*`)
- [ ] Platform admin vendor approval/rejection workflows
- [ ] Tests for catalog management and vendor authorization

---

## 📋 Phase 5: Core Group-Buying Engine
- [ ] GroupDeal, DealPricingTier, and DealParticipant models
- [ ] Atomic deal creation, publication, and schedule validation
- [ ] Tiered pricing calculation logic with integer paise arithmetic
- [ ] Atomic deal participation with row-level locking (`SELECT ... FOR UPDATE`)
- [ ] Concurrency safety tests (preventing overselling and race conditions)
- [ ] Deal lifecycle state machine: Draft -> Published -> Open -> Threshold Reached -> Confirmed -> Completed
- [ ] Edge-case handling: Threshold not reached, deal cancellation, and deal expiration
- [ ] Comprehensive unit and integration test suite for the group-buying engine

---

## 📋 Phase 6: Booking, Scheduling, and Payments
- [ ] Booking model, appointment slot management, and capacity validation
- [ ] Deal participant conversion to confirmed bookings
- [ ] Payment gateway abstraction (`PaymentProvider` interface)
- [ ] Mock sandbox payment provider with simulated success/failure modes
- [ ] Razorpay provider implementation with HMAC-SHA256 signature verification
- [ ] Immutable double-entry financial ledger (`financial_ledger_entries`)
- [ ] Cancellation, refund calculation, and commission distribution logic
- [ ] Tests for booking creation, payment webhooks, idempotent replay, and refunds

---

## 📋 Phase 7: Frontend Interfaces & User Journeys
- [ ] Core design system: Curated modern Indian residential marketplace theme, typography, color tokens
- [ ] Public landing page, category exploration, and deal discovery experience
- [ ] Resident Portal: Browse deals, interactive tier progress bar, join deal modal, booking summary, checkout
- [ ] Resident Portal: "My Bookings", slot selector, invoice view, and review submission
- [ ] Society Admin Portal: Member approvals, society deals overview, participation metrics
- [ ] Vendor Portal: Incoming assignments, technician dispatch, status updates, earnings ledger
- [ ] Platform Admin Portal: KPI dashboards, vendor verification queues, dispute management, commission settings
- [ ] Fully responsive UI (mobile, tablet, desktop) with accessibility standards

---

## 📋 Phase 8: Notifications, Reviews, and Support
- [ ] In-app notification center and email notification dispatcher
- [ ] Automated deal reminders (approaching deadline, threshold reached)
- [ ] Verified-booking review and rating system
- [ ] Support ticketing and dispute resolution workflows
- [ ] Background worker tasks for deal expiration and automated notification dispatch

---

## 📋 Phase 9: Quality, Security, and End-to-End Validation
- [ ] Comprehensive Pytest suite covering all domain logic, edge cases, and security boundaries
- [ ] Playwright E2E browser test scenarios (full resident-to-vendor lifecycle)
- [ ] OWASP security audit: CSRF, CORS, SQL injection prevention, IDOR negative tests
- [ ] API performance verification and database index optimization
- [ ] Accessibility (WCAG 2.2 AA) visual and keyboard audit

---

## 📋 Phase 10: DevOps, Deployment Readiness, and Handover
- [ ] Production Dockerfile optimization (multi-stage builds)
- [ ] GitHub Actions CI workflow (linting, tests, build checks)
- [ ] Complete documentation suite (`docs/api-guide.md`, `docs/payments.md`, `docs/deployment.md`, `docs/security.md`, `docs/testing.md`)
- [ ] Seed data scripts for local demonstration (realistic societies, vendors, deals)
- [ ] Final engineering handover report
