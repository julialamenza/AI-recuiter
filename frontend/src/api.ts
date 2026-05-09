function apiBase(): string {
  const raw = import.meta.env.VITE_API_BASE_URL
  if (raw != null && String(raw).trim() !== '') {
    return String(raw).trim().replace(/\/$/, '')
  }
  return ''
}

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const base = apiBase()
  const url = `${base}${path}`
  let res: Response
  try {
    res = await fetch(url, {
      ...init,
      headers: {
        ...(init?.body instanceof FormData ? {} : { 'Content-Type': 'application/json' }),
        ...init?.headers,
      },
    })
  } catch (e) {
    if (e instanceof TypeError) {
      throw new Error(
        `Could not reach the API (${url}). In dev, start the backend (uvicorn on port 8000) and ` +
          (base ? 'check VITE_API_BASE_URL.' : 'either leave VITE_API_BASE_URL unset to use the Vite proxy, or set it to your API URL.'),
      )
    }
    throw e
  }
  if (!res.ok) {
    let detail = res.statusText
    try {
      const j = await res.json()
      if (j?.detail) detail = typeof j.detail === 'string' ? j.detail : JSON.stringify(j.detail)
    } catch {
      /* ignore */
    }
    throw new Error(detail)
  }
  if (res.status === 204) return undefined as T
  return (await res.json()) as T
}
