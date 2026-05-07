import { useMutation, useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { api } from '../api'
import type { Candidate, Job, Screening } from '../types'

export function ScreeningNewPage() {
  const nav = useNavigate()
  const [candidateId, setCandidateId] = useState('')
  const [jobId, setJobId] = useState('')

  const candidates = useQuery({
    queryKey: ['candidates'],
    queryFn: () => api<Candidate[]>('/api/candidates'),
  })
  const jobs = useQuery({
    queryKey: ['jobs'],
    queryFn: () => api<Job[]>('/api/jobs'),
  })

  const run = useMutation({
    mutationFn: () =>
      api<Screening>('/api/screenings', {
        method: 'POST',
        body: JSON.stringify({ candidate_id: candidateId, job_id: jobId }),
      }),
    onSuccess: (s) => {
      nav(`/screenings/${s.id}`)
    },
  })

  return (
    <div className="stack card narrow">
      <h1>New screening</h1>
      <p className="muted small">Compare a candidate profile against a job. Rejections are never automatic.</p>
      <label className="block">
        Candidate
        <select value={candidateId} onChange={(e) => setCandidateId(e.target.value)} required>
          <option value="">Select…</option>
          {candidates.data?.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name || c.id.slice(0, 8)}
            </option>
          ))}
        </select>
      </label>
      <label className="block">
        Job
        <select value={jobId} onChange={(e) => setJobId(e.target.value)} required>
          <option value="">Select…</option>
          {jobs.data?.map((j) => (
            <option key={j.id} value={j.id}>
              {j.title}
            </option>
          ))}
        </select>
      </label>
      <button
        type="button"
        disabled={!candidateId || !jobId || run.isPending}
        onClick={() => run.mutate()}
      >
        {run.isPending ? 'Running AI comparison…' : 'Run screening'}
      </button>
      {run.error && <p className="error">{String(run.error.message)}</p>}
    </div>
  )
}
