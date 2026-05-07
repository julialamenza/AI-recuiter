import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import type { Candidate } from '../types'

export function CandidatesPage() {
  const qc = useQueryClient()
  const [name, setName] = useState('')
  const list = useQuery({
    queryKey: ['candidates'],
    queryFn: () => api<Candidate[]>('/api/candidates'),
  })
  const upload = useMutation({
    mutationFn: async (file: File) => {
      const fd = new FormData()
      fd.append('file', file)
      if (name.trim()) fd.append('name', name.trim())
      return api<Candidate>('/api/candidates', { method: 'POST', body: fd })
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['candidates'] })
      setName('')
    },
  })

  return (
    <div className="stack two-col">
      <section className="card">
        <h2>Upload CV</h2>
        <p className="muted small">PDF, DOCX, or plain text. Extraction uses OpenAI.</p>
        <label className="block">
          Optional name
          <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Jane Doe" />
        </label>
        <label className="block">
          File
          <input
            type="file"
            accept=".pdf,.doc,.docx,.txt,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            onChange={(e) => {
              const f = e.target.files?.[0]
              if (f) upload.mutate(f)
              e.target.value = ''
            }}
          />
        </label>
        {upload.isPending && <p className="muted">Uploading & extracting…</p>}
        {upload.error && <p className="error">{String(upload.error.message)}</p>}
      </section>
      <section className="card">
        <h2>Candidates</h2>
        {list.isLoading && <p className="muted">Loading…</p>}
        {list.error && <p className="error">{String(list.error.message)}</p>}
        <ul className="list">
          {list.data?.map((c) => (
            <li key={c.id}>
              <Link to={`/candidates/${c.id}`}>{c.name || c.id.slice(0, 8)}</Link>
              <span className="muted small">{c.cv_mime_type}</span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  )
}
