import { create } from 'zustand';

type BookingState = {
  selectedPackage: string;
  setSelectedPackage: (value: string) => void;
};

export const useCustomerBookingStore = create<BookingState>((set) => ({
  selectedPackage: 'Full Inside & Out',
  setSelectedPackage: (value) => set({ selectedPackage: value })
}));
