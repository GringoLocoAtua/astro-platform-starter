const BASE = 'http://127.0.0.1:8000'

export const getIndustries = async () => fetch(`${BASE}/industries`).then((r) => r.json())

export const createQuote = async (payload) => {
  const res = await fetch(`${BASE}/quote`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!res.ok) throw new Error('Failed to create quote')
  return res.json()
}

export const exportPdf = async (payload) => {
  const res = await fetch(`${BASE}/export/pdf`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!res.ok) throw new Error('PDF export failed')
  return res.blob()
}
