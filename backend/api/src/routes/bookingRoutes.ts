import type { Request, Response } from 'express';
import { quoteBookingPrice } from '../services/pricingService';

export function getBookingQuote(req: Request, res: Response) {
  const quote = quoteBookingPrice({
    vehicleSize: (req.body.vehicleSize ?? 'MEDIUM'),
    basePackageCents: req.body.basePackageCents ?? 7900,
    addOnCents: req.body.addOnCents ?? 0,
    urgencyMultiplier: req.body.urgencyMultiplier ?? 1,
    zoneFeeCents: req.body.zoneFeeCents ?? 0,
    subscriptionDiscountPct: req.body.subscriptionDiscountPct ?? 0,
    promoDiscountPct: req.body.promoDiscountPct ?? 0,
    multiCarDiscountPct: req.body.multiCarDiscountPct ?? 0,
    isFleet: req.body.isFleet ?? false,
    fleetDiscountPct: req.body.fleetDiscountPct ?? 0
  });

  res.json({ quote });
}
