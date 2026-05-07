import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api'
import type { Candidate, InterviewProposal, Job, Screening } from '../types'

export function ScreeningDetailPage() {
  const { screeningId } = useParams()
  const qc = useQueryClient()
  const [rejectOpen, setRejectOpen] = useState(false)
  const [confirmReject, setConfirmReject] = useState(false)
  const [proposalState, setProposalState] = useState<InterviewProposal | null>(null)

  const screening = useQuery({
    queryKey: ['screening', screeningId],
    queryFn: () => api<Screening>(`/api/screenings/${screeningId}`),
    enabled: Boolean(screeningId),
  })

  const candidate = useQuery({
    queryKey: ['candidate', screening.data?.candidate_id],
    queryFn: () => api<Candidate>(`/api/candidates/${screening.data!.candidate_id}`),
    enabled: Boolean(screening.data?.candidate_id),
  })

  const job = useQuery({
    queryKey: ['job', screening.data?.job_id],
    queryFn: () => api<Job>(`/api/jobs/${screening.data!.job_id}`),
    enabled: Boolean(screening.data?.job_id),
  })

  const decision = useMutation({
    mutationFn: (body: { decision: string; confirm_rejection?: boolean }) =>
      api<Screening>(`/api/screenings/${screeningId}/decision`, {
        method: 'PATCH',
        body: JSON.stringify(body),
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['screening', screeningId] })
      setRejectOpen(false)
      setConfirmReject(false)
    },
  })

  const genProposal = useMutation({
    mutationFn: () =>
      api<InterviewProposal>(`/api/screenings/${screeningId}/interview-proposals`, {
        method: 'POST',
      }),
    onSuccess: (p) => setProposalState(p),
  })

  const pickSlot = useMutation({
    mutationFn: ({ proposalId, slot }: { proposalId: string; slot: string }) =>
      api<InterviewProposal>(`/api/screenings/${screeningId}/interview-proposals/${proposalId}`, {
        method: 'PATCH',
        body: JSON.stringify({
          candidate_selected_slot: slot,
          status: 'candidate_responded',
        }),
      }),
    onSuccess: (p) => setProposalState(p),
  })

  if (!screeningId) return null

  const s = screening.data

  return (
    <div className="stack">
      <Link to="/screening" className="back">
        ← New screening
      </Link>
      {screening.isLoading && <p className="muted">Loading…</p>}
      {screening.error && <p className="error">{String(screening.error.message)}</p>}
      {s && (
        <>
          <div className="two-col">
            <section className="card">
              <h2>Score</h2>
              <div className="score-ring">
                <span>{s.score}</span>
                <small>/ 100</small>
              </div>
              <p className="badge suggestion">
                AI suggestion: <strong>{s.model_recommendation.replace('_', ' ')}</strong>
              </p>
              {s.human_decision && (
                <p className="badge human">
                  Your decision: <strong>{s.human_decision}</strong>
                  {s.rejection_confirmed && ' (reject confirmed)'}
                </p>
              )}
              <h3>Reasons</h3>
              <ul className="bullets">
                {s.reasons.map((r, i) => (
                  <li key={i}>{String(r)}</li>
                ))}
              </ul>
            </section>
            <section className="card">
              <h2>Screening summary</h2>
              <div className="markdown">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{s.summary_markdown}</ReactMarkdown>
              </div>
            </section>
          </div>

          <div className="two-col">
            <section className="card">
              <h3>Candidate</h3>
              {candidate.isLoading && <p className="muted">Loading…</p>}
              {candidate.data && (
                <pre className="pre small">{JSON.stringify(candidate.data.extracted_profile, null, 2)}</pre>
              )}
            </section>
            <section className="card">
              <h3>Job</h3>
              {job.isLoading && <p className="muted">Loading…</p>}
              {job.data && (
                <>
                  <p>
                    <strong>{job.data.title}</strong>
                  </p>
                  <pre className="pre small">{JSON.stringify(job.data.structured_requirements, null, 2)}</pre>
                </>
              )}
            </section>
          </div>

          <section className="card">
            <h2>Your decision</h2>
            <p className="muted small">
              Rejecting requires an explicit confirmation. The AI never auto-rejects.
            </p>
            <div className="btn-row">
              <button
                type="button"
                className="secondary"
                disabled={decision.isPending}
                onClick={() => decision.mutate({ decision: 'shortlist' })}
              >
                Shortlist
              </button>
              <button
                type="button"
                className="secondary"
                disabled={decision.isPending}
                onClick={() => decision.mutate({ decision: 'manual_review' })}
              >
                Manual review
              </button>
              <button type="button" className="danger" onClick={() => setRejectOpen(true)}>
                Reject…
              </button>
            </div>
            {decision.error && <p className="error">{String(decision.error.message)}</p>}
          </section>

          <section className="card">
            <h2>Interview slots</h2>
            <p className="muted small">Uses your saved weekly availability (timezone-aware).</p>
            <button type="button" disabled={genProposal.isPending} onClick={() => genProposal.mutate()}>
              {genProposal.isPending ? 'Generating…' : 'Generate proposed slots'}
            </button>
            {genProposal.error && <p className="error">{String(genProposal.error.message)}</p>}
            {proposalState && proposalState.proposed_slots.length > 0 && (
              <ul className="list slots">
                {proposalState.proposed_slots.map((slot) => (
                  <li key={slot.start}>
                    <code>{slot.start}</code> ({slot.duration_minutes} min)
                    <button
                      type="button"
                      className="linkish"
                      onClick={() =>
                        pickSlot.mutate({
                          proposalId: proposalState.id,
                          slot: slot.start,
                        })
                      }
                    >
                      Select (mock candidate choice)
                    </button>
                  </li>
                ))}
              </ul>
            )}
            {proposalState?.candidate_selected_slot && (
              <p className="muted">
                Selected: <code>{proposalState.candidate_selected_slot}</code>
              </p>
            )}
          </section>

          {rejectOpen && (
            <div className="modal-backdrop" role="presentation" onClick={() => setRejectOpen(false)}>
              <div
                className="modal"
                role="dialog"
                aria-modal="true"
                onClick={(e) => e.stopPropagation()}
              >
                <h3>Confirm reject</h3>
                <p className="muted small">
                  This records a human reject decision. It is not performed automatically by the AI.
                </p>
                <label className="inline-check">
                  <input
                    type="checkbox"
                    checked={confirmReject}
                    onChange={(e) => setConfirmReject(e.target.checked)}
                  />
                  I confirm this candidate should be rejected for this role.
                </label>
                <div className="btn-row">
                  <button type="button" className="secondary" onClick={() => setRejectOpen(false)}>
                    Cancel
                  </button>
                  <button
                    type="button"
                    className="danger"
                    disabled={!confirmReject || decision.isPending}
                    onClick={() =>
                      decision.mutate({ decision: 'reject', confirm_rejection: true })
                    }
                  >
                    Confirm reject
                  </button>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
