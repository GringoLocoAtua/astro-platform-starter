import type { PricingBreakdown, VehicleSizeTier } from '../types/domain';

export interface PricingInput {
  vehicleSize: VehicleSizeTier;
  basePackageCents: number;
  addOnCents: number;
  urgencyMultiplier: number;
  zoneFeeCents: number;
  subscriptionDiscountPct: number;
  promoDiscountPct: number;
  multiCarDiscountPct: number;
  isFleet: boolean;
  fleetDiscountPct: number;
}

const vehicleTierMultipliers: Record<VehicleSizeTier, number> = {
  SMALL: 1,
  MEDIUM: 1.1,
  LARGE: 1.22,
  XL: 1.35
};

export function calculatePricing(input: PricingInput): PricingBreakdown {
  const appliedRules: string[] = [];
  const tierAdjusted = Math.round(input.basePackageCents * vehicleTierMultipliers[input.vehicleSize]);
  appliedRules.push(`vehicle_tier_${input.vehicleSize.toLowerCase()}`);

  const urgencyAdjusted = Math.round((tierAdjusted + input.addOnCents) * input.urgencyMultiplier);
  if (input.urgencyMultiplier > 1) appliedRules.push('urgency_surcharge');

  const preDiscount = urgencyAdjusted + input.zoneFeeCents;
  if (input.zoneFeeCents > 0) appliedRules.push('zone_travel_fee');

  const percentageDiscount =
    input.subscriptionDiscountPct + input.promoDiscountPct + input.multiCarDiscountPct + (input.isFleet ? input.fleetDiscountPct : 0);

  const cappedDiscountPct = Math.min(percentageDiscount, 40);
  const discountCents = Math.round(preDiscount * (cappedDiscountPct / 100));
  if (discountCents > 0) appliedRules.push('discount_stack');

  const subtotalCents = preDiscount - discountCents;
  const gstCents = Math.round(subtotalCents / 11); // AU GST inclusive display support
  const totalCents = subtotalCents;

  return {
    subtotalCents,
    discountCents,
    gstCents,
    totalCents,
    appliedRules
  };
}
