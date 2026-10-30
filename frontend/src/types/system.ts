export interface PickedDirectory {
  path: string | null
  method: string
}

export interface DirectoryEntry {
  name: string
  path: string
}

export interface DirectoryListing {
  path: string
  parent: string | null
  entries: DirectoryEntry[]
  shortcuts: DirectoryEntry[]
}

export interface ServerEvent<T = unknown> {
  event: string
  data: T
}
