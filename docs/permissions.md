# SocietySaver — Role-Based Access Control (RBAC) & Permissions Matrix

## 1. Principles of Authorization

1. **Server-Side Enforcement**: All permissions are enforced in FastAPI dependencies and database query boundaries. Hiding a button on the client is never considered authorization.
2. **Multi-Tenant Scoping**: Access to society data requires an `APPROVED` membership in that specific society. Knowing a `society_id` provides zero read or write privileges without an active membership.
3. **Negative Access Control Tests**: The test suite explicitly asserts that cross-tenant access attempts fail with `403 Forbidden` or `404 Not Found`.

---

## 2. User Roles

- **`RESIDENT`**: Verified occupant/owner in an approved society.
- **`SOCIETY_ADMIN`**: Designated residential committee member managing a specific society.
- **`VENDOR`**: Commercial service provider offering services, accepting bookings, and managing service execution.
- **`PLATFORM_ADMIN`**: Superuser overseeing platform integrity, onboarding, disputes, and financial operations.

---

## 3. RBAC Permissions Matrix

| Resource / Action | RESIDENT | SOCIETY_ADMIN | VENDOR | PLATFORM_ADMIN | Enforcement Mechanism |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Auth / Profile** | | | | | |
| Register / Login | Allowed | Allowed | Allowed | Allowed | Public endpoint with rate limiting |
| Update own profile & password | Allowed | Allowed | Allowed | Allowed | `get_current_active_user` |
| View / Revoke own active sessions | Allowed | Allowed | Allowed | Allowed | Redis token whitelist check |
| **Society Management** | | | | | |
| Browse public directory of societies | Allowed | Allowed | Allowed | Allowed | Public listing |
| Join society (create membership request) | Allowed | Denied | Denied | Allowed | `require_role(RESIDENT)` |
| View society members | Denied | Own Society | Denied | All | `require_society_admin(society_id)` |
| Approve / reject resident membership | Denied | Own Society | Denied | All | `require_society_admin(society_id)` |
| Create / edit wings & flat units | Denied | Own Society | Denied | All | `require_society_admin(society_id)` |
| **Service Catalog & Vendors** | | | | | |
| View active services & categories | Allowed | Allowed | Allowed | Allowed | Public catalog |
| Register as service vendor | Denied | Denied | Self | Allowed | `require_role(VENDOR)` |
| Manage service offerings & base rates | Denied | Denied | Own Profile | All | `require_vendor_owner(vendor_id)` |
| Verify / approve / reject vendors | Denied | Denied | Denied | Allowed | `require_platform_admin` |
| **Group Deals** | | | | | |
| View published deals in own society | Own Society | Own Society | Assigned Deals | All | `require_approved_society_member` |
| Create / propose group deal | Denied | Own Society | Denied | All | `require_society_admin` or Platform Admin |
| Approve deal pricing rate card | Denied | Own Society | Assigned Vendor| All | Mutually agreed state transition |
| Join group deal (reserve capacity) | Own Society | Own Society | Denied | Denied | `require_approved_society_member` + capacity check |
| Leave group deal (before deadline) | Own Join | Denied | Denied | Allowed | `require_participant_owner` + cancellation policy |
| Cancel deal (under-subscribed/emergency) | Denied | Own Society | Denied | All | State machine transition rule |
| **Bookings & Appointments** | | | | | |
| Create booking from confirmed deal | Own Join | Denied | Denied | Allowed | Deal commitment validation |
| View booking details | Own Booking | Denied | Assigned Only | All | `require_booking_party` |
| Assign technician to booking | Denied | Denied | Assigned Only | All | `require_vendor_owner` |
| Mark status: In-Progress / Completed | Denied | Denied | Assigned Only | All | `require_vendor_owner` + proof upload |
| Cancel booking | Own Booking | Denied | Policy-based | All | Booking state transition rule |
| **Payments & Refunds** | | | | | |
| Initiate payment order | Own Booking | Denied | Denied | Denied | `require_booking_owner` |
| Process payment webhook | Webhook | Webhook | Webhook | Webhook | Razorpay HMAC-SHA256 signature verification |
| View payment receipts & invoices | Own Booking | Denied | Payout statement | All | `require_booking_owner` |
| Issue partial / full refund | Denied | Denied | Denied | Allowed | `require_platform_admin` (with audit log) |
| **Reviews & Complaints** | | | | | |
| Submit review for completed booking | Own Completed | Denied | Denied | Denied | 1 verified review per completed booking |
| Respond to resident review | Denied | Denied | Assigned Vendor| Allowed | `require_vendor_owner` |
| File support ticket / dispute | Own Booking | Own Society | Own Booking | All | Contextual access |
| Resolve dispute / administrative notes | Denied | Denied | Denied | Allowed | `require_platform_admin` |
| **Audit & Platform Admin** | | | | | |
| Configure commission rates & taxes | Denied | Denied | Denied | Allowed | `require_platform_admin` |
| View platform financial ledger | Denied | Denied | Denied | Allowed | `require_platform_admin` |
| View system audit logs | Denied | Denied | Denied | Allowed | `require_platform_admin` |
