# BU1ST Wash™ Monorepo

BU1ST Wash™ is a premium, Australian-first, on-demand mobile car wash and detailing operating system with three production surfaces:

- **Customer mobile app** (Expo React Native)
- **Washer mobile app** (Expo React Native)
- **Admin dashboard** (Next.js)
- **Backend API + Prisma/PostgreSQL schema**

This repository ships a coherent architecture, realistic data model, and seeded demo data for Sydney launch suburbs.

## Monorepo Layout

```txt
mobile/
  customer/      # Customer app flows
  washer/        # Worker/washer app flows
web/
  admin/         # Admin operating dashboard
backend/
  api/           # Node API, Prisma schema, services
shared/
  types/         # Cross-platform TypeScript domain models
  pricing/       # Configurable pricing engine
  design-tokens/ # BU1ST visual system tokens
  seed/          # Realistic AU launch demo data
```

## Product Surfaces

### 1) Customer app highlights
- Suburb-aware address picker with rollout validation
- 60-second booking flow: vehicles → package → add-ons → schedule → payment
- Multi-car household booking with discount logic
- Recurring plans (weekly, fortnightly, monthly)
- Live job status timeline and ETA tracking
- Washer trust profile (verified badge, rating, completed jobs)
- Before/after proof gallery and dispute entry point

### 2) Washer app highlights
- Onboarding with ABN-ready metadata + compliance docs placeholders
- Availability toggle, break mode, service area management
- Job offer queue with accept/decline and SLA timer
- Guided job execution: arrive → before photos → in-progress → after photos → complete
- Incident flags and customer contact masking policy support
- Earnings, payouts, quality score, lateness/cancellation visibility

### 3) Admin dashboard highlights
- Operational command center with KPI cards and trend context
- Job board with suburb, status, washer, and dispute filters
- Quality assurance queue with before/after proof review
- Pricing rules console (zone, urgency, vehicle tier, promos, subscriptions)
- Worker quality controls (verification, suspension, training state)
- Fleet/B2B management with enquiry funnel and lead pipeline

## Stack
- **TypeScript everywhere**
- **Mobile:** React Native + Expo, TanStack Query, Zustand, React Hook Form + Zod
- **Web admin:** Next.js (App Router), TanStack Query, lightweight component primitives
- **Backend:** Node + Express + Prisma + PostgreSQL
- **Billing:** Stripe-ready architecture (customer cards, refunds, payouts hooks)
- **Realtime/status:** event model + pub/sub-ready service abstractions

## Environment
Copy `.env.example` to `.env` and fill values.

```bash
cp .env.example .env
```

## Database and seed

```bash
cd backend/api
npm install
npx prisma migrate dev --name init
npm run seed
```

## Demo Accounts
- Customer: `olivia.chen@bu1stwash.com.au` / `DemoPass!23`
- Washer: `liam.doyle@bu1stwash.com.au` / `DemoPass!23`
- Admin: `ops.admin@bu1stwash.com.au` / `DemoPass!23`

## Architecture Notes
- Pricing is centrally computed from rule tables (`pricing_rules`) + booking context inputs.
- GST is explicit and receipting supports Australian tax invoices.
- Service zones map to launch suburbs for staged rollout.
- Worker trust score is derived from quality + reliability metrics, not static badges.
- Fleet architecture is first-class, not bolted on.

## Next Steps to Production
- Add Supabase Auth or custom JWT auth service wiring to current route handlers.
- Connect Stripe customer/payment intents and payouts to washer settlement lifecycle.
- Add push channels (Expo Notifications/APNS/FCM) and SMS provider adapter.
- Add map providers (Google Maps/Places) for geocoding, ETA, route confidence.
