import { useEffect, useState } from 'react'
import { createQuote, exportPdf, getIndustries } from './api'

const baseForm = {
  industry_id: '', region: 'DEFAULT', urgency: 'standard', rooms: 0, bathrooms: 0,
  selected_addons: [], scope_text: '', tier: 'FREE'
}

export default function App() {
  const [industries, setIndustries] = useState([])
  const [form, setForm] = useState(baseForm)
  const [quote, setQuote] = useState(null)

  useEffect(() => {
    getIndustries().then((items) => {
      setIndustries(items)
      if (items[0]) setForm((f) => ({ ...f, industry_id: items[0].id }))
    })
  }, [])

  const submit = async () => setQuote(await createQuote(form))

  const downloadPdf = async () => {
    if (!quote) return
    const blob = await exportPdf({ quote_result: quote, tier: form.tier, industry_name: form.industry_id, scope_text: form.scope_text })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'quote.pdf'
    a.click()
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-4">
      <h1 className="text-2xl font-bold">SnapQuote Web Blueprint</h1>
      <div className="grid grid-cols-2 gap-3">
        <select className="bg-slate-800 p-2" value={form.industry_id} onChange={(e) => setForm({ ...form, industry_id: e.target.value })}>
          {industries.map((i) => <option key={i.id} value={i.id}>{i.name}</option>)}
        </select>
        <input className="bg-slate-800 p-2" type="number" value={form.rooms} onChange={(e) => setForm({ ...form, rooms: Number(e.target.value) })} placeholder="Rooms" />
        <input className="bg-slate-800 p-2" type="number" value={form.bathrooms} onChange={(e) => setForm({ ...form, bathrooms: Number(e.target.value) })} placeholder="Bathrooms" />
        <select className="bg-slate-800 p-2" value={form.urgency} onChange={(e) => setForm({ ...form, urgency: e.target.value })}>
          <option>standard</option><option>urgent</option><option>same_day</option>
        </select>
      </div>
      <textarea className="w-full bg-slate-800 p-2" value={form.scope_text} onChange={(e) => setForm({ ...form, scope_text: e.target.value })} placeholder="Scope" />
      <div className="space-x-2">
        <button className="bg-blue-700 px-3 py-2 rounded" onClick={submit}>Generate Quote</button>
        <button className="bg-emerald-700 px-3 py-2 rounded" onClick={downloadPdf}>Download PDF</button>
      </div>
      {quote && (
        <div className="bg-slate-800 p-4 rounded">
          <div className="text-xl">Total: {quote.currency} {quote.total}</div>
          <ul>{quote.breakdown.map((b, idx) => <li key={idx}>{b.item}: {b.amount}</li>)}</ul>
        </div>
      )}
    </div>
  )
}
