# BU1ST Wash™ Architecture

## System topology
- `mobile/customer`: customer booking and tracking UX.
- `mobile/washer`: worker operations UX with proof-of-work pipeline.
- `web/admin`: operational control plane.
- `backend/api`: pricing, booking state machine, trust/quality services.
- `shared`: domain contracts, pricing engine, design tokens.

## Domain priorities
1. Fast booking conversion with minimal typing.
2. Trust + quality instrumentation on every booking.
3. Suburb-launch controls and service-zone economics.
4. AU-ready tax/payment model with GST line-item support.
5. Fleet architecture as first-class booking mode.

## Booking state machine
`REQUESTED -> ACCEPTED -> ON_THE_WAY -> ARRIVED -> IN_PROGRESS -> COMPLETED`

Exception states:
- `CANCELLED`
- `DISPUTED`

Each transition writes to `BookingStatusEvent`, enabling customer timeline UX, admin audit, and SLA analytics.

## Pricing architecture
Price = (package base × vehicle multiplier + add-ons) × urgency + zone fee − discounts

Discount stack inputs:
- subscription discount
- promo discount
- multi-car discount
- fleet contract discount

Discount stack is capped at 40% to protect margin floors.

## Trust architecture
- Washer verification + training status
- Completion, lateness, cancellation metrics
- Before/after proof media
- Incident flags + dispute tickets
- Admin QA review queue
- Worker suspension state

## Fleet/B2B architecture
- Fleet account and vehicle roster entities
- Monthly invoice billing mode
- Site/service instructions and account manager notes
- Proof-of-service history and report export pathways
