export type Candidate = {
  id: string
  name: string | null
  cv_mime_type: string
  extracted_profile: Record<string, unknown> | null
  created_at: string
}

export type Job = {
  id: string
  title: string
  raw_description: string
  structured_requirements: Record<string, unknown> | null
  created_at: string
}

export type Screening = {
  id: string
  candidate_id: string
  job_id: string
  score: number
  reasons: unknown[]
  summary_markdown: string
  model_recommendation: string
  human_decision: string | null
  human_decision_at: string | null
  rejection_confirmed: boolean
  created_at: string
}

export type Availability = {
  id: string
  user_id: string
  weekly_rules: { weekday: number; start: string; end: string }[]
  timezone: string
  updated_at: string
}

export type InterviewProposal = {
  id: string
  screening_id: string
  proposed_slots: { start: string; duration_minutes: number }[]
  status: string
  candidate_selected_slot: string | null
  created_at: string
}
