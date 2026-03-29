import React from 'react';
import { SafeAreaView, View, Text, Pressable } from 'react-native';
import { colors, spacing } from '../../../../shared/design-tokens/tokens';

export function WasherApp() {
  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg, padding: spacing.xl, gap: spacing.lg }}>
      <Text style={{ fontSize: 30, fontWeight: '700', color: colors.textPrimary }}>Today’s Runs</Text>
      <View style={{ backgroundColor: 'white', borderRadius: 16, padding: spacing.lg, gap: spacing.sm }}>
        <Text style={{ fontWeight: '700', fontSize: 17 }}>10:30 • Bondi • Full Inside & Out</Text>
        <Text style={{ color: colors.textSecondary }}>Customer: O. Chen • ETA SLA: 12 mins</Text>
        <Text style={{ color: colors.textSecondary }}>Trust flags: none • Proof required: before + after</Text>
        <View style={{ flexDirection: 'row', gap: spacing.sm, marginTop: spacing.md }}>
          <Pressable style={{ backgroundColor: colors.accent, borderRadius: 10, padding: spacing.md, flex: 1 }}>
            <Text style={{ color: 'white', textAlign: 'center', fontWeight: '700' }}>Accept</Text>
          </Pressable>
          <Pressable style={{ backgroundColor: '#F3F4F6', borderRadius: 10, padding: spacing.md, flex: 1 }}>
            <Text style={{ color: colors.textPrimary, textAlign: 'center', fontWeight: '700' }}>Decline</Text>
          </Pressable>
        </View>
      </View>
    </SafeAreaView>
  );
}
