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
  /** Rejects with an Error whose message can be shown to the user as it is. */
  async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
    let response: Response
    let answer: unknown
    try {
      response = await fetch(connection.baseUrl + path, {
        method,
        headers: {
          Authorization: `Bearer ${connection.secret}`,
          ...(body === undefined ? {} : { 'Content-Type': 'application/json' }),
        },
        body: body === undefined ? undefined : JSON.stringify(body),
      })
      answer = await response.json()
    } catch {
      throw new Error(
        'TRACE lost contact with its analysis core. Quit TRACE and open it again.',
      )
    }
    if (!response.ok) {
      const detail = (answer as { detail?: unknown } | null)?.detail
      throw new Error(
        typeof detail === 'string'
          ? detail
          : `The analysis core ran into a fault (status ${response.status}). ` +
            'Quit TRACE and open it again; if this happens again, please report it.',
      )
    }
    return answer as T
  }

  return {
    listLogs: () => request('GET', '/logs'),
    importLog: (path) => request('POST', '/logs/import', { path }),
  }
}
