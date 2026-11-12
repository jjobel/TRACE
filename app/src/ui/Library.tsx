import { useEffect, useState } from 'react'

import { coreApi, type CoreApi, type LogSummary } from './core-api'

let connecting: Promise<CoreApi> | undefined

/** The core's API, connected to once and shared. */
function core(): Promise<CoreApi> {
  connecting ??= window.trace.coreConnection().then(coreApi)
  return connecting
}

function messageOf(cause: unknown): string {
  return cause instanceof Error ? cause.message : String(cause)
}

/**
 * The library: the Logs that have been imported, and a way to import another.
 *
 * This is the bare first version. It is given its real look and the rest of
 * its abilities later.
 */
export function Library() {
  const [logs, setLogs] = useState<LogSummary[] | null>(null)
  const [problem, setProblem] = useState<string | null>(null)

  useEffect(() => {
    let shown = true
    core()
      .then((api) => api.listLogs())
      .then(
        (listed) => shown && setLogs(listed),
        (cause) => shown && setProblem(messageOf(cause)),
      )
    return () => {
      shown = false
    }
  }, [])

  async function importLog() {
    setProblem(null)
    try {
      const path = await window.trace.chooseLogFile()
      if (path === null) return
      const api = await core()
      await api.importLog(path)
      setLogs(await api.listLogs())
    } catch (cause) {
      setProblem(messageOf(cause))
    }
  }

  return (
    <main>
      <h1>Library</h1>
      <button type="button" onClick={importLog}>
        Import Log…
      </button>
      {problem !== null && <p role="alert">{problem}</p>}
      {logs === null ? (
        problem === null && <p>Opening the library…</p>
      ) : logs.length === 0 ? (
        <p>No Logs yet. Import a .vbo file to add the first one.</p>
      ) : (
        <ul aria-label="Logs">
          {logs.map((log) => (
            <li key={log.id}>
              {log.file_name}, imported {new Date(log.imported_at).toLocaleString()}
            </li>
          ))}
        </ul>
      )}
    </main>
  )
}
