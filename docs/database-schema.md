# SocietySaver — Relational Database Schema Specification

## 1. Overview and Design Principles

The SocietySaver database is modeled in PostgreSQL using SQLAlchemy 2.x declarative models and managed via Alembic migrations.

### Key Rules:
1. **Monetary Representation**: Stored as 64-bit BigInteger in integer paise (1 INR = 100 paise).
2. **Timestamps**: All timestamps are stored with timezone (`TIMESTAMP WITH TIME ZONE`) in UTC.
3. **Primary Keys**: UUID v4 across all major entities to prevent enumeration attacks and support multi-system synchronization.
4. **Referential Integrity**: Explicit foreign keys, cascade rules, and check constraints enforce valid state transitions at the database layer.
5. **Soft Deletion**: Applied selectively (`is_active` or `deleted_at`) only to business entities where historical references must be preserved.

---

## 2. Entity-Relationship Overview

```mermaid
erDiagram
    User ||--o{ SocietyMembership : holds
    User ||--o{ Vendor : manages
    User ||--o{ Booking : places
    User ||--o{ Review : writes

    Society ||--o{ SocietyWing : contains
    SocietyWing ||--o{ SocietyUnit : contains
    Society ||--o{ SocietyMembership : enrolls
    Society ||--o{ GroupDeal : hosts

    ServiceCategory ||--o{ ServiceItem : categorizes
    ServiceItem ||--o{ VendorServiceOffering : offers
    Vendor ||--o{ VendorServiceOffering : registers
    Vendor ||--o{ GroupDeal : provides
    Vendor ||--o{ Booking : fulfills

    GroupDeal ||--o{ DealPricingTier : defines
    GroupDeal ||--o{ DealParticipant : joins
    DealParticipant ||--o{ Booking : generates
    
    Booking ||--|| PaymentOrder : bills
    PaymentOrder ||--o{ FinancialLedgerEntry : logs
    Booking ||--o? Review : receives
    Booking ||--o{ SupportTicket : escalates
```

---

## 3. Core Tables Specification

### 3.1. Identity & Multi-Tenancy

#### `users`
- `id`: UUID (PK)
- `email`: VARCHAR(255) (UNIQUE, NOT NULL, INDEXED)
- `phone`: VARCHAR(20) (NULLABLE, INDEXED)
- `password_hash`: VARCHAR(255) (NOT NULL)
- `full_name`: VARCHAR(150) (NOT NULL)
- `role`: VARCHAR(30) (NOT NULL) — `RESIDENT`, `SOCIETY_ADMIN`, `VENDOR`, `PLATFORM_ADMIN`
- `is_active`: BOOLEAN (DEFAULT TRUE)
- `is_verified`: BOOLEAN (DEFAULT FALSE)
- `created_at`: TIMESTAMPTZ (DEFAULT NOW())
- `updated_at`: TIMESTAMPTZ (DEFAULT NOW())

#### `societies`
- `id`: UUID (PK)
- `name`: VARCHAR(200) (NOT NULL)
- `code`: VARCHAR(50) (UNIQUE, NOT NULL) — e.g., `PALM-GROVE-BLR`
- `address_line1`: VARCHAR(255) (NOT NULL)
- `locality`: VARCHAR(150) (NOT NULL)
- `city`: VARCHAR(100) (NOT NULL, INDEXED)
- `state`: VARCHAR(100) (NOT NULL)
- `pincode`: VARCHAR(10) (NOT NULL, INDEXED)
- `timezone`: VARCHAR(50) (DEFAULT 'Asia/Kolkata')
- `created_at`: TIMESTAMPTZ (DEFAULT NOW())

#### `society_wings` & `society_units`
- `society_wings`: `id` (UUID), `society_id` (FK), `name` (e.g. "Tower A")
- `society_units`: `id` (UUID), `wing_id` (FK), `unit_number` (VARCHAR(50), e.g. "402"), UNIQUE(`wing_id`, `unit_number`)

#### `society_memberships`
- `id`: UUID (PK)
- `society_id`: UUID (FK societies.id, NOT NULL, INDEXED)
- `user_id`: UUID (FK users.id, NOT NULL, INDEXED)
- `unit_id`: UUID (FK society_units.id, NULLABLE)
- `role`: VARCHAR(30) (DEFAULT 'RESIDENT') — `RESIDENT`, `SOCIETY_ADMIN`
- `status`: VARCHAR(30) (DEFAULT 'PENDING') — `PENDING`, `APPROVED`, `REJECTED`, `SUSPENDED`
- `verified_at`: TIMESTAMPTZ (NULLABLE)
- UNIQUE (`society_id`, `user_id`)

---

### 3.2. Vendor & Service Catalog

#### `vendors`
- `id`: UUID (PK)
- `user_id`: UUID (FK users.id, NOT NULL) — Primary business owner
- `business_name`: VARCHAR(200) (NOT NULL)
- `contact_email`: VARCHAR(255) (NOT NULL)
- `contact_phone`: VARCHAR(20) (NOT NULL)
- `gstin`: VARCHAR(15) (NULLABLE)
- `verification_status`: VARCHAR(30) (DEFAULT 'PENDING') — `PENDING`, `VERIFIED`, `REJECTED`, `SUSPENDED`
- `commission_rate`: NUMERIC(5,2) (DEFAULT 10.00) — Custom commission override
- `rating_avg`: NUMERIC(3,2) (DEFAULT 5.00)
- `review_count`: INT (DEFAULT 0)
- `created_at`: TIMESTAMPTZ (DEFAULT NOW())

#### `service_categories` & `service_items`
- `service_categories`: `id` (UUID), `name` (VARCHAR), `slug` (VARCHAR UNIQUE), `icon_name` (VARCHAR), `display_order` (INT)
- `service_items`: `id` (UUID), `category_id` (FK), `name` (VARCHAR), `slug` (VARCHAR UNIQUE), `description` (TEXT), `pricing_unit` (VARCHAR — `PER_UNIT`, `PER_SQFT`, `PER_VISIT`, `PER_VEHICLE`), `estimated_duration_mins` (INT), `inclusions` (JSONB), `exclusions` (JSONB)

#### `vendor_service_offerings`
- `id`: UUID (PK)
- `vendor_id`: UUID (FK vendors.id, NOT NULL)
- `service_id`: UUID (FK service_items.id, NOT NULL)
- `base_price_paise`: BIGINT (NOT NULL) — Regular price before group discounts
- `is_active`: BOOLEAN (DEFAULT TRUE)
- UNIQUE(`vendor_id`, `service_id`)

---

### 3.3. Group-Buying Engine

#### `group_deals`
- `id`: UUID (PK)
- `society_id`: UUID (FK societies.id, NOT NULL, INDEXED)
- `service_id`: UUID (FK service_items.id, NOT NULL, INDEXED)
- `vendor_id`: UUID (FK vendors.id, NOT NULL, INDEXED)
- `title`: VARCHAR(255) (NOT NULL)
- `description`: TEXT
- `pricing_mode`: VARCHAR(30) (DEFAULT 'UNIFORM_FINAL_TIER') — `UNIFORM_FINAL_TIER`, `PROSPECTIVE_TIER`
- `status`: VARCHAR(30) (NOT NULL, INDEXED) — `DRAFT`, `PUBLISHED`, `OPEN`, `THRESHOLD_REACHED`, `CONFIRMED`, `COMPLETED`, `CANCELLED`, `EXPIRED`
- `min_participants`: INT (NOT NULL, CHECK > 0)
- `max_participants`: INT (NULLABLE)
- `current_participant_count`: INT (DEFAULT 0, NOT NULL)
- `start_time`: TIMESTAMPTZ (NOT NULL)
- `end_time`: TIMESTAMPTZ (NOT NULL)
- `execution_start_date`: DATE (NOT NULL)
- `execution_end_date`: DATE (NOT NULL)
- `cancellation_deadline`: TIMESTAMPTZ (NOT NULL)
- `created_by_user_id`: UUID (FK users.id)
- `created_at`: TIMESTAMPTZ (DEFAULT NOW())

#### `deal_pricing_tiers`
- `id`: UUID (PK)
- `deal_id`: UUID (FK group_deals.id ON DELETE CASCADE, NOT NULL)
- `tier_level`: INT (NOT NULL) — 1, 2, 3, 4
- `min_units`: INT (NOT NULL) — e.g. 1, 5, 10, 20
- `max_units`: INT (NULLABLE) — e.g. 4, 9, 19, NULL
- `unit_price_paise`: BIGINT (NOT NULL) — e.g. 80000, 70000, 60000, 50000 paise
- UNIQUE(`deal_id`, `tier_level`)

#### `deal_participants`
- `id`: UUID (PK)
- `deal_id`: UUID (FK group_deals.id, NOT NULL, INDEXED)
- `user_id`: UUID (FK users.id, NOT NULL, INDEXED)
- `units_booked`: INT (DEFAULT 1, NOT NULL)
- `initial_tier_price_paise`: BIGINT (NOT NULL) — Quoted price upon joining
- `final_unit_price_paise`: BIGINT (NULLABLE) — Computed upon deal confirmation
- `status`: VARCHAR(30) (DEFAULT 'COMMITTED') — `COMMITTED`, `CONVERTED_TO_BOOKING`, `CANCELLED`
- `joined_at`: TIMESTAMPTZ (DEFAULT NOW())
- UNIQUE(`deal_id`, `user_id`)

---

### 3.4. Bookings & Scheduling

#### `bookings`
- `id`: UUID (PK)
- `booking_reference`: VARCHAR(30) (UNIQUE, NOT NULL, INDEXED) — e.g. `BK-20261016-8492`
- `deal_id`: UUID (FK group_deals.id, NULLABLE)
- `resident_id`: UUID (FK users.id, NOT NULL, INDEXED)
- `society_id`: UUID (FK societies.id, NOT NULL)
- `unit_id`: UUID (FK society_units.id, NULLABLE)
- `service_id`: UUID (FK service_items.id, NOT NULL)
- `vendor_id`: UUID (FK vendors.id, NOT NULL)
- `quantity`: INT (DEFAULT 1, NOT NULL)
- `scheduled_date`: DATE (NOT NULL, INDEXED)
- `scheduled_slot`: VARCHAR(50) (NOT NULL) — e.g. "10:00 - 12:00"
- `status`: VARCHAR(30) (NOT NULL, INDEXED) — `PENDING_PAYMENT`, `CONFIRMED`, `ASSIGNED`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`, `REFUNDED`
- `unit_price_paise`: BIGINT (NOT NULL)
- `subtotal_paise`: BIGINT (NOT NULL)
- `tax_paise`: BIGINT (NOT NULL)
- `platform_fee_paise`: BIGINT (DEFAULT 0)
- `total_amount_paise`: BIGINT (NOT NULL)
- `technician_name`: VARCHAR(100) (NULLABLE)
- `technician_phone`: VARCHAR(20) (NULLABLE)
- `proof_of_service_url`: VARCHAR(500) (NULLABLE)
- `created_at`: TIMESTAMPTZ (DEFAULT NOW())

---

### 3.5. Payments & Financial Ledger

#### `payment_orders`
- `id`: UUID (PK)
- `booking_id`: UUID (FK bookings.id, NOT NULL, INDEXED)
- `provider`: VARCHAR(30) (DEFAULT 'MOCK') — `MOCK`, `RAZORPAY`
- `provider_order_id`: VARCHAR(100) (UNIQUE, NOT NULL, INDEXED)
- `provider_payment_id`: VARCHAR(100) (NULLABLE, INDEXED)
- `amount_paise`: BIGINT (NOT NULL)
- `currency`: VARCHAR(5) (DEFAULT 'INR')
- `status`: VARCHAR(30) (NOT NULL) — `CREATED`, `AUTHORIZED`, `CAPTURED`, `FAILED`, `REFUNDED`
- `webhook_signature_verified`: BOOLEAN (DEFAULT FALSE)
- `idempotency_key`: VARCHAR(100) (UNIQUE, NOT NULL)
- `created_at`: TIMESTAMPTZ (DEFAULT NOW())

#### `financial_ledger_entries` (Immutable Double-Entry Ledger)
- `id`: UUID (PK)
- `booking_id`: UUID (FK bookings.id, NOT NULL, INDEXED)
- `entry_type`: VARCHAR(50) (NOT NULL) — `CUSTOMER_PAYMENT`, `PLATFORM_COMMISSION`, `VENDOR_PAYABLE`, `TAX_COLLECTED`, `CUSTOMER_REFUND`
- `amount_paise`: BIGINT (NOT NULL)
- `debit_account`: VARCHAR(100) (NOT NULL)
- `credit_account`: VARCHAR(100) (NOT NULL)
- `created_at`: TIMESTAMPTZ (DEFAULT NOW())

---

### 3.6. Reviews, Support & Auditing

#### `reviews`
- `id`: UUID (PK)
- `booking_id`: UUID (FK bookings.id, UNIQUE, NOT NULL)
- `vendor_id`: UUID (FK vendors.id, NOT NULL)
- `resident_id`: UUID (FK users.id, NOT NULL)
- `rating`: INT (NOT NULL, CHECK (rating >= 1 AND rating <= 5))
- `comment`: TEXT (NOT NULL)
- `is_verified_booking`: BOOLEAN (DEFAULT TRUE)
- `created_at`: TIMESTAMPTZ (DEFAULT NOW())

#### `audit_logs`
- `id`: UUID (PK)
- `actor_id`: UUID (FK users.id, NULLABLE)
- `action`: VARCHAR(100) (NOT NULL)
- `entity_type`: VARCHAR(50) (NOT NULL)
- `entity_id`: VARCHAR(100) (NOT NULL)
- `ip_address`: VARCHAR(45) (NULLABLE)
- `changes`: JSONB (NOT NULL)
- `created_at`: TIMESTAMPTZ (DEFAULT NOW())
