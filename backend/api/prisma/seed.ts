import { PrismaClient, BookingStatus } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
  const zones = await Promise.all([
    prisma.serviceZone.upsert({
      where: { id: 'zone-bondi' },
      update: {},
      create: {
        id: 'zone-bondi', suburb: 'Bondi', state: 'NSW', postcode: '2026', launchEnabled: true, travelFeeCents: 500
      }
    }),
    prisma.serviceZone.upsert({
      where: { id: 'zone-surry' },
      update: {},
      create: {
        id: 'zone-surry', suburb: 'Surry Hills', state: 'NSW', postcode: '2010', launchEnabled: true, travelFeeCents: 300
      }
    }),
    prisma.serviceZone.upsert({
      where: { id: 'zone-parramatta' },
      update: {},
      create: {
        id: 'zone-parramatta', suburb: 'Parramatta', state: 'NSW', postcode: '2150', launchEnabled: true, travelFeeCents: 800
      }
    })
  ]);

  const customerUser = await prisma.user.upsert({
    where: { email: 'olivia.chen@bu1stwash.com.au' },
    update: {},
    create: {
      email: 'olivia.chen@bu1stwash.com.au',
      passwordHash: 'demo-hash',
      role: 'CUSTOMER',
      phone: '+61412345678'
    }
  });

  const customer = await prisma.customer.upsert({
    where: { userId: customerUser.id },
    update: {},
    create: { userId: customerUser.id, firstName: 'Olivia', lastName: 'Chen', creditsCents: 2500 }
  });

  const washerUser = await prisma.user.upsert({
    where: { email: 'liam.doyle@bu1stwash.com.au' },
    update: {},
    create: {
      email: 'liam.doyle@bu1stwash.com.au',
      passwordHash: 'demo-hash',
      role: 'WASHER',
      phone: '+61419876543'
    }
  });

  const washer = await prisma.washer.upsert({
    where: { userId: washerUser.id },
    update: {},
    create: {
      userId: washerUser.id,
      displayName: 'Liam D.',
      abn: '83 914 571 673',
      verified: true,
      trainingStatus: 'COMPLETED',
      completionScore: 97.5,
      latenessRate: 0.03,
      cancellationRate: 0.01,
      jobsCompleted: 684,
      ratingAverage: 4.92,
      ratingCount: 412
    }
  });

  const adminUser = await prisma.user.upsert({
    where: { email: 'ops.admin@bu1stwash.com.au' },
    update: {},
    create: {
      email: 'ops.admin@bu1stwash.com.au',
      passwordHash: 'demo-hash',
      role: 'ADMIN',
      phone: '+61411111111'
    }
  });

  await prisma.admin.upsert({
    where: { userId: adminUser.id },
    update: {},
    create: { userId: adminUser.id, fullName: 'BU1ST Launch Ops' }
  });

  const packageFull = await prisma.servicePackage.upsert({
    where: { id: 'pkg-full' },
    update: {},
    create: {
      id: 'pkg-full',
      name: 'Full Inside & Out',
      description: 'Exterior wash + full interior vacuum and wipe-down.',
      basePriceCents: 9900,
      estimatedMinutes: 75,
      availableForSubscription: true
    }
  });

  await prisma.addOn.createMany({
    skipDuplicates: true,
    data: [
      { id: 'addon-pet-hair', name: 'Pet hair removal', priceCents: 2200 },
      { id: 'addon-tyre-shine', name: 'Tyre shine', priceCents: 1200 },
      { id: 'addon-child-seat', name: 'Child seat clean', priceCents: 1800 }
    ]
  });

  const vehicle1 = await prisma.vehicle.create({
    data: {
      customerId: customer.id,
      make: 'Tesla',
      model: 'Model Y',
      bodyType: 'SUV',
      sizeTier: 'LARGE',
      condition: 'GOOD',
      notes: 'Underground parking level B2.'
    }
  });

  const booking = await prisma.booking.create({
    data: {
      customerId: customer.id,
      washerId: washer.id,
      serviceZoneId: zones[0].id,
      servicePackageId: packageFull.id,
      status: BookingStatus.ON_THE_WAY,
      scheduledAt: new Date(Date.now() + 30 * 60 * 1000),
      subtotalCents: 12400,
      discountCents: 900,
      gstCents: 1045,
      totalCents: 11500,
      notes: 'Please avoid blocking driveway gate.'
    }
  });

  await prisma.bookingVehicle.create({ data: { bookingId: booking.id, vehicleId: vehicle1.id } });
  await prisma.bookingAddOn.create({ data: { bookingId: booking.id, addOnId: 'addon-tyre-shine' } });

  await prisma.bookingStatusEvent.createMany({
    data: [
      { bookingId: booking.id, status: BookingStatus.REQUESTED },
      { bookingId: booking.id, status: BookingStatus.ACCEPTED },
      { bookingId: booking.id, status: BookingStatus.ON_THE_WAY }
    ]
  });

  await prisma.bookingPhoto.createMany({
    data: [
      { bookingId: booking.id, stage: 'BEFORE', url: 'https://images.bu1stwash.com/demo/before-1.jpg' },
      { bookingId: booking.id, stage: 'AFTER', url: 'https://images.bu1stwash.com/demo/after-1.jpg' }
    ]
  });

  await prisma.review.create({
    data: {
      customerId: customer.id,
      bookingId: booking.id,
      rating: 5,
      comment: 'On-time, meticulous, and premium finish. Rebooking next fortnight.'
    }
  });

  await prisma.fleetAccount.create({
    data: {
      legalName: 'Harbour Clinical Group',
      abn: '63 820 554 021',
      billingMode: 'MONTHLY_INVOICE',
      accountManager: 'Sophie Tran',
      notes: '12 vehicles across Bondi Junction and Zetland sites.'
    }
  });
}

main()
  .then(async () => prisma.$disconnect())
  .catch(async (e) => {
    console.error(e);
    await prisma.$disconnect();
    process.exit(1);
  });
