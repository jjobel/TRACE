import type { CoreConnection } from '../bridge'

/** A Log as the library lists it. */
export interface LogSummary {
  id: string
  file_name: string
  imported_at: string
}

/** The core's local API, as the user interface uses it. */
export interface CoreApi {
  listLogs(): Promise<LogSummary[]>
  /** Imports the file at a path on this computer. Rejects with the cause if it cannot be read. */
  importLog(path: string): Promise<LogSummary>
}

export function coreApi(connection: CoreConnection): CoreApi {
  async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
    const response = await fetch(connection.baseUrl + path, {
      method,
      headers: {
        Authorization: `Bearer ${connection.secret}`,
        ...(body === undefined ? {} : { 'Content-Type': 'application/json' }),
      },
      body: body === undefined ? undefined : JSON.stringify(body),
    })
    const answer: unknown = await response.json()
    if (!response.ok) {
      const detail = (answer as { detail?: unknown }).detail
      throw new Error(
        typeof detail === 'string' ? detail : `The analysis core answered ${response.status}.`,
      )
    }
    return answer as T
  }

  return {
    listLogs: () => request('GET', '/logs'),
    importLog: (path) => request('POST', '/logs/import', { path }),
  }
}
