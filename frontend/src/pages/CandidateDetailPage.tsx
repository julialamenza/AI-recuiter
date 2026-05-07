import { useQuery } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api'
import type { Candidate } from '../types'

export function CandidateDetailPage() {
  const { candidateId } = useParams()
  const q = useQuery({
    queryKey: ['candidate', candidateId],
    queryFn: () => api<Candidate>(`/api/candidates/${candidateId}`),
    enabled: Boolean(candidateId),
  })
  if (!candidateId) return null
  return (
    <div className="stack">
      <Link to="/candidates" className="back">
        ← Candidates
      </Link>
      {q.isLoading && <p className="muted">Loading…</p>}
      {q.error && <p className="error">{String(q.error.message)}</p>}
      {q.data && (
        <div className="card">
          <h1>{q.data.name || 'Candidate'}</h1>
          <h3>Extracted profile</h3>
          <pre className="pre">{JSON.stringify(q.data.extracted_profile, null, 2)}</pre>
        </div>
      )}
    </div>
  )
}
