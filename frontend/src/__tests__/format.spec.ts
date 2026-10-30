import { describe, expect, it } from 'vitest'

import { formatRecent, plural, relativePath } from '@/utils/format'
import { classNameProblem } from '@/utils/validators'

describe('format', () => {
  it('pluralises with separators', () => {
    expect(plural(1, 'image')).toBe('1 image')
    expect(plural(1284, 'image')).toBe('1,284 images')
  })

  it('shortens paths under the destination folder', () => {
    expect(relativePath('/data/set/png/stunting/stunting-0001.png', '/data/set/')).toBe('png/stunting/stunting-0001.png')
    expect(relativePath('/elsewhere/a.png', '/data/set')).toBe('/elsewhere/a.png')
  })

  it('names recent days', () => {
    const now = new Date('2026-10-30T15:00:00')
    expect(formatRecent(new Date('2026-10-30T09:05:00').toISOString(), now)).toBe('Today 09:05')
    expect(formatRecent(new Date('2026-10-29T23:59:00').toISOString(), now)).toBe('Yesterday 23:59')
  })
})

describe('class names', () => {
  it('follows the backend rules', () => {
    expect(classNameProblem('tidak stunting')).toBeNull()
    expect(classNameProblem('a/b')).toMatch(/cannot contain/)
    expect(classNameProblem('Stunting', ['stunting'])).toMatch(/already/)
  })
})
