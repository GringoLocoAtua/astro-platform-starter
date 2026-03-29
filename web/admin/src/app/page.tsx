'use client';

const kpis = [
  { label: 'Bookings today', value: '148', delta: '+12%' },
  { label: 'Revenue (AUD)', value: '$18,420', delta: '+9.4%' },
  { label: 'Repeat customers', value: '64%', delta: '+4.1 pts' },
  { label: 'Completion rate', value: '96.8%', delta: '+1.2 pts' }
];

const liveJobs = [
  { id: 'BW-3012', suburb: 'Bondi', status: 'ON_THE_WAY', washer: 'Liam D.', eta: '8m' },
  { id: 'BW-3013', suburb: 'Surry Hills', status: 'IN_PROGRESS', washer: 'Ava N.', eta: '—' },
  { id: 'BW-3014', suburb: 'Parramatta', status: 'REQUESTED', washer: 'Unassigned', eta: '—' }
];

export default function AdminHomePage() {
  return (
    <main style={{ background: '#F6F8FB', minHeight: '100vh', padding: 32, fontFamily: 'Inter, sans-serif' }}>
      <header style={{ marginBottom: 24 }}>
        <h1 style={{ margin: 0, fontSize: 34, color: '#0E1726' }}>BU1ST Wash Ops</h1>
        <p style={{ color: '#4A5A73' }}>National command view • Sydney launch wave</p>
      </header>

      <section style={{ display: 'grid', gridTemplateColumns: 'repeat(4, minmax(0,1fr))', gap: 16, marginBottom: 24 }}>
        {kpis.map((kpi) => (
          <article key={kpi.label} style={{ background: 'white', borderRadius: 14, padding: 16, boxShadow: '0 8px 24px rgba(15,23,42,0.08)' }}>
            <div style={{ fontSize: 13, color: '#4A5A73' }}>{kpi.label}</div>
            <div style={{ marginTop: 6, fontSize: 28, fontWeight: 700, color: '#0E1726' }}>{kpi.value}</div>
            <div style={{ marginTop: 4, color: '#16A34A', fontWeight: 600 }}>{kpi.delta}</div>
          </article>
        ))}
      </section>

      <section style={{ background: 'white', borderRadius: 14, padding: 16 }}>
        <h2 style={{ marginTop: 0 }}>Live Job Board</h2>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ textAlign: 'left', color: '#4A5A73' }}>
              <th>Booking</th>
              <th>Suburb</th>
              <th>Status</th>
              <th>Washer</th>
              <th>ETA</th>
            </tr>
          </thead>
          <tbody>
            {liveJobs.map((job) => (
              <tr key={job.id} style={{ borderTop: '1px solid #E5EAF2' }}>
                <td style={{ padding: '12px 0' }}>{job.id}</td>
                <td>{job.suburb}</td>
                <td>{job.status}</td>
                <td>{job.washer}</td>
                <td>{job.eta}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </main>
  );
}
