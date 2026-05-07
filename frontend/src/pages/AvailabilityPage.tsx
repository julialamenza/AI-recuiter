import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import { api } from '../api'
import type { Availability } from '../types'

const DAYS = [
  { id: 0, label: 'Mon' },
  { id: 1, label: 'Tue' },
  { id: 2, label: 'Wed' },
  { id: 3, label: 'Thu' },
  { id: 4, label: 'Fri' },
  { id: 5, label: 'Sat' },
  { id: 6, label: 'Sun' },
]

type Row = { weekday: number; enabled: boolean; start: string; end: string }

export function AvailabilityPage() {
  const qc = useQueryClient()
  const [timezone, setTimezone] = useState('UTC')
  const [rows, setRows] = useState<Row[]>(() =>
    DAYS.map((d) => ({
      weekday: d.id,
      enabled: d.id < 5,
      start: '09:00',
      end: '17:00',
    })),
  )

  const existing = useQuery({
    queryKey: ['availability'],
    queryFn: () => api<Availability>('/api/availability'),
    retry: false,
  })

  useEffect(() => {
    if (existing.data) {
      setTimezone(existing.data.timezone)
      const rules = existing.data.weekly_rules || []
      setRows(
        DAYS.map((d) => {
          const r = rules.find((x) => x.weekday === d.id)
          return {
            weekday: d.id,
            enabled: Boolean(r),
            start: r?.start || '09:00',
            end: r?.end || '17:00',
          }
        }),
      )
    }
  }, [existing.data])

  const save = useMutation({
    mutationFn: () => {
      const weekly_rules = rows
        .filter((r) => r.enabled)
        .map((r) => ({ weekday: r.weekday, start: r.start, end: r.end }))
      return api<Availability>('/api/availability', {
        method: 'PUT',
        body: JSON.stringify({ user_id: 'default', weekly_rules, timezone }),
      })
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['availability'] }),
  })

  return (
    <div className="stack card">
      <h1>Weekly availability</h1>
      <p className="muted small">
        Calendar-style recurring hours (Monday=0 … Sunday=6). Used to propose interview start times.
      </p>
      {existing.isError && <p className="muted small">No saved availability yet — defaults shown.</p>}
      <label className="block">
        Timezone (IANA)
        <input value={timezone} onChange={(e) => setTimezone(e.target.value)} placeholder="Europe/Dublin" />
      </label>
      <div className="calendar-grid">
        <div className="grid-head">Day</div>
        <div className="grid-head">Available</div>
        <div className="grid-head">Start</div>
        <div className="grid-head">End</div>
        {rows.map((row, idx) => (
          <div className="grid-row" key={row.weekday}>
            <div className="day-label">{DAYS[idx].label}</div>
            <label className="center">
              <input
                type="checkbox"
                checked={row.enabled}
                onChange={(e) => {
                  const next = [...rows]
                  next[idx] = { ...row, enabled: e.target.checked }
                  setRows(next)
                }}
              />
            </label>
            <input
              type="time"
              value={row.start}
              disabled={!row.enabled}
              onChange={(e) => {
                const next = [...rows]
                next[idx] = { ...row, start: e.target.value }
                setRows(next)
              }}
            />
            <input
              type="time"
              value={row.end}
              disabled={!row.enabled}
              onChange={(e) => {
                const next = [...rows]
                next[idx] = { ...row, end: e.target.value }
                setRows(next)
              }}
            />
          </div>
        ))}
      </div>
      <button type="button" disabled={save.isPending} onClick={() => save.mutate()}>
        {save.isPending ? 'Saving…' : 'Save availability'}
      </button>
      {save.error && <p className="error">{String(save.error.message)}</p>}
      {save.isSuccess && <p className="muted small">Saved.</p>}
    </div>
  )
}
