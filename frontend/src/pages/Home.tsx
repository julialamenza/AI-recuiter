import { Link } from 'react-router-dom'

export function Home() {
  return (
    <div className="stack">
      <h1>Recruiting lifecycle assistant</h1>
      <p className="muted">
        Upload CVs, define jobs, run AI screening with human-gated rejections, and propose interview slots from
        your weekly availability.
      </p>
      <ul className="link-grid">
        <li>
          <Link to="/candidates">Upload candidates</Link>
        </li>
        <li>
          <Link to="/jobs">Create job descriptions</Link>
        </li>
        <li>
          <Link to="/screening">Run screening</Link>
        </li>
        <li>
          <Link to="/availability">Set availability</Link>
        </li>
      </ul>
    </div>
  )
}
