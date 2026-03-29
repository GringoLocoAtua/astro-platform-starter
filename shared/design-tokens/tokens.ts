export const colors = {
  bg: '#F6F8FB',
  surface: '#FFFFFF',
  textPrimary: '#0E1726',
  textSecondary: '#4A5A73',
  accent: '#0A84FF',
  accentDark: '#0063CC',
  success: '#16A34A',
  warning: '#D97706',
  danger: '#DC2626',
  border: '#E5EAF2'
} as const;

export const spacing = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 24,
  xxl: 32
} as const;

export const radius = {
  sm: 8,
  md: 12,
  lg: 16,
  xl: 22,
  pill: 999
} as const;

export const shadow = {
  card: '0 8px 24px rgba(15, 23, 42, 0.08)',
  floating: '0 16px 40px rgba(10, 132, 255, 0.18)'
} as const;
