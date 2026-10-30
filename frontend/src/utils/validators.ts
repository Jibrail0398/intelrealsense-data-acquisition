// Same rules as backend app/utils/naming.py, so mistakes show before the request.
const ILLEGAL = /[\\/:*?"<>|\x00-\x1f]/

export function classNameProblem(raw: string, existing: string[] = []): string | null {
  const name = raw.trim().replace(/\s+/g, ' ')
  if (!name) return 'Class name cannot be empty'
  if (ILLEGAL.test(name)) return 'Class name cannot contain \\ / : * ? " < > |'
  if (name.startsWith('.')) return 'Class name cannot start with a dot'
  if (name.length > 120) return 'Class name is too long (max 120 characters)'
  if (existing.some((e) => e.toLowerCase() === name.toLowerCase())) return `"${name}" is already in the list`
  return null
}
