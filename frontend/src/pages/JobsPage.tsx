import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { Link } from 'react-router-dom'
import { api } from '../api'
import type { Job } from '../types'

type Form = { title: string; raw_description: string }

export function JobsPage() {
  const qc = useQueryClient()
  const jobs = useQuery({
    queryKey: ['jobs'],
    queryFn: () => api<Job[]>('/api/jobs'),
  })
  const create = useMutation({
    mutationFn: (body: Form) =>
      api<Job>('/api/jobs', { method: 'POST', body: JSON.stringify(body) }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['jobs'] }),
  })
  const form = useForm<Form>({ defaultValues: { title: '', raw_description: '' } })

  return (
    <div className="stack two-col">
      <section className="card">
        <h2>Create job</h2>
        <form
          className="form"
          onSubmit={form.handleSubmit((v) => create.mutate(v))}
        >
          <label>
            Title
            <input {...form.register('title', { required: true })} />
          </label>
          <label>
            Description
            <textarea rows={10} {...form.register('raw_description', { required: true })} />
          </label>
          <button type="submit" disabled={create.isPending}>
            {create.isPending ? 'Saving…' : 'Create & structure with AI'}
          </button>
          {create.error && <p className="error">{String(create.error.message)}</p>}
        </form>
      </section>
      <section className="card">
        <h2>Jobs</h2>
        {jobs.isLoading && <p className="muted">Loading…</p>}
        {jobs.error && <p className="error">{String(jobs.error.message)}</p>}
        <ul className="list">
          {jobs.data?.map((j) => (
            <li key={j.id}>
              <Link to={`/jobs/${j.id}`}>{j.title}</Link>
              <span className="muted small">{new Date(j.created_at).toLocaleString()}</span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  )
}
