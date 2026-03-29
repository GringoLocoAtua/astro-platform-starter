import React from 'react';
import { SafeAreaView, ScrollView, Text, View, Pressable } from 'react-native';
import { colors, spacing } from '../../../../shared/design-tokens/tokens';
import { useCustomerBookingStore } from '../state/bookingStore';

export function CustomerApp() {
  const { selectedPackage, setSelectedPackage } = useCustomerBookingStore();

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <ScrollView contentContainerStyle={{ padding: spacing.xl, gap: spacing.lg }}>
        <Text style={{ fontSize: 30, fontWeight: '700', color: colors.textPrimary }}>BU1ST Wash™</Text>
        <Text style={{ color: colors.textSecondary }}>Book a premium mobile wash in under 60 seconds.</Text>

        <View style={{ backgroundColor: colors.surface, borderRadius: 16, padding: spacing.lg, gap: spacing.md }}>
          <Text style={{ fontSize: 18, fontWeight: '600' }}>1. Choose package</Text>
          {['Quick Exterior', 'Exterior + Vacuum', 'Full Inside & Out', 'Premium Detail'].map((name) => {
            const active = selectedPackage === name;
            return (
              <Pressable
                key={name}
                onPress={() => setSelectedPackage(name)}
                style={{
                  padding: spacing.md,
                  borderRadius: 12,
                  borderWidth: 1,
                  borderColor: active ? colors.accent : colors.border,
                  backgroundColor: active ? '#ECF5FF' : 'white'
                }}
              >
                <Text style={{ fontWeight: '600', color: colors.textPrimary }}>{name}</Text>
              </Pressable>
            );
          })}
        </View>

        <Pressable style={{ backgroundColor: colors.accent, borderRadius: 14, padding: spacing.lg }}>
          <Text style={{ color: 'white', fontWeight: '700', textAlign: 'center' }}>Continue to vehicle + schedule</Text>
        </Pressable>
      </ScrollView>
    </SafeAreaView>
  );
}
