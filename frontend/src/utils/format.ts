const dateFmt = new Intl.DateTimeFormat('en-CA', { year: 'numeric', month: '2-digit', day: '2-digit' })
const timeFmt = new Intl.DateTimeFormat('en-GB', { hour: '2-digit', minute: '2-digit', second: '2-digit' })

/** "2026-10-30" in the viewer's local time zone. */
export function formatDate(iso: string | Date): string {
  return dateFmt.format(typeof iso === 'string' ? new Date(iso) : iso)
}

/** "14:05:09" */
export function formatTime(iso: string | Date): string {
  return timeFmt.format(typeof iso === 'string' ? new Date(iso) : iso)
}

/** "Today 14:05", "Yesterday 09:12", or "2026-10-28 09:12". */
export function formatRecent(iso: string, now = new Date()): string {
  const date = new Date(iso)
  const day = startOfDay(date).getTime()
  const today = startOfDay(now).getTime()
  const hm = timeFmt.format(date).slice(0, 5)
  if (day === today) return `Today ${hm}`
  if (day === today - 86_400_000) return `Yesterday ${hm}`
  return `${formatDate(date)} ${hm}`
}

export function startOfDay(date: Date): Date {
  const d = new Date(date)
  d.setHours(0, 0, 0, 0)
  return d
}

export function addDays(date: Date, days: number): Date {
  const d = new Date(date)
  d.setDate(d.getDate() + days)
  return d
}

export function formatCount(n: number): string {
  return n.toLocaleString('en-US')
}

export function plural(n: number, one: string, many = `${one}s`): string {
  return `${formatCount(n)} ${n === 1 ? one : many}`
}

/** Path relative to the project's destination folder, for compact display. */
export function relativePath(path: string, base: string): string {
  const b = base.replace(/[\\/]+$/, '')
  return path.startsWith(b) ? path.slice(b.length + 1) : path
}
