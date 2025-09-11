'use client';
import { useState } from 'react';

export default function SearchPage() {
  const [q, setQ] = useState('');
  const [items, setItems] = useState<any[]>([]);

  async function run() {
    const res = await fetch(process.env.NEXT_PUBLIC_API_URL + '/api/search', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ q, limit: 20 })
    });
    const js = await res.json();
    setItems(js.items || []);
  }

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-bold">Search</h1>
      <div className="flex gap-2">
        <input className="border px-3 py-2 w-full" value={q} onChange={e=>setQ(e.target.value)} placeholder="Search highlights..."/>
        <button className="px-4 py-2 bg-black text-white" onClick={run}>Search</button>
      </div>
      <ul className="space-y-3">
        {items.map((it,i)=> (
          <li key={i} className="border p-3 rounded">
            <div className="font-semibold">{it.title || '(no title)'}</div>
            <div className="text-xs text-gray-500">{it.link}</div>
          </li>
        ))}
      </ul>
    </div>
  );
}