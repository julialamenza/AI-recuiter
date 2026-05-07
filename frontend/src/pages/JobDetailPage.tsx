import { useQuery } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api'
import type { Job } from '../types'

export function JobDetailPage() {
  const { jobId } = useParams()
  const q = useQuery({
    queryKey: ['job', jobId],
    queryFn: () => api<Job>(`/api/jobs/${jobId}`),
    enabled: Boolean(jobId),
  })
  if (!jobId) return null
  return (
    <div className="stack">
      <Link to="/jobs" className="back">
        ← Jobs
      </Link>
      {q.isLoading && <p className="muted">Loading…</p>}
      {q.error && <p className="error">{String(q.error.message)}</p>}
      {q.data && (
        <div className="card">
          <h1>{q.data.title}</h1>
          <h3>Description</h3>
          <pre className="pre">{q.data.raw_description}</pre>
          {q.data.structured_requirements && (
            <>
              <h3>Structured (AI)</h3>
              <pre className="pre">{JSON.stringify(q.data.structured_requirements, null, 2)}</pre>
            </>
          )}
        </div>
      )}
    </div>
  )
}
