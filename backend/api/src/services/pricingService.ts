import { calculatePricing, type PricingInput } from '../../../../shared/pricing/engine';

export function quoteBookingPrice(input: PricingInput) {
  return calculatePricing(input);
}
