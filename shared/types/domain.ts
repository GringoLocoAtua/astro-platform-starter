export type UserRole = 'CUSTOMER' | 'WASHER' | 'ADMIN' | 'FLEET_MANAGER';

export type BookingStatus =
  | 'REQUESTED'
  | 'ACCEPTED'
  | 'ON_THE_WAY'
  | 'ARRIVED'
  | 'IN_PROGRESS'
  | 'COMPLETED'
  | 'CANCELLED'
  | 'DISPUTED';

export type VehicleSizeTier = 'SMALL' | 'MEDIUM' | 'LARGE' | 'XL';

export interface Address {
  id: string;
  label: 'HOME' | 'WORK' | 'OTHER';
  line1: string;
  suburb: string;
  state: string;
  postcode: string;
  lat: number;
  lng: number;
  serviceZoneId: string;
}

export interface Vehicle {
  id: string;
  customerId: string;
  make: string;
  model: string;
  bodyType: string;
  sizeTier: VehicleSizeTier;
  condition: 'EXCELLENT' | 'GOOD' | 'WORN' | 'HEAVY_SOIL';
  notes?: string;
}

export interface ServicePackage {
  id: string;
  name: string;
  description: string;
  basePriceCents: number;
  estimatedMinutes: number;
  availableForSubscriptions: boolean;
}

export interface WasherTrustProfile {
  washerId: string;
  verified: boolean;
  trainingStatus: 'NOT_STARTED' | 'IN_PROGRESS' | 'COMPLETED';
  completionScore: number;
  latenessRate: number;
  cancellationRate: number;
}

export interface PricingBreakdown {
  subtotalCents: number;
  discountCents: number;
  gstCents: number;
  totalCents: number;
  appliedRules: string[];
}
