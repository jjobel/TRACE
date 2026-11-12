import { spawn } from 'node:child_process'
import { createInterface } from 'node:readline'

/** The analysis core, running as a process of its own beside the shell. */
export interface Core {
  /** Resolves to the address of the core's local API once it is listening. */
  ready: Promise<string>
  /** Stops the core. Safe to call at any time, and more than once. */
  stop(): void
}

export interface CoreOptions {
  /** The program that runs the core, and its first arguments. */
  command: string
  args: string[]
  /** The folder the core keeps Logs in. */
  dataDir: string
  /** The secret of this launch, which every request to the API must carry. */
  secret: string
  /** The web origin of the user interface, the only one a browser lets call the API. */
  uiOrigin: string
}

/**
 * Starts the core and waits for it to say where it listens.
 *
 * The core listens on the loopback interface only, on a port it chooses, and
 * announces the port as one line of JSON on its standard output. It is given
 * the secret in its environment. It stops when its standard input closes, so
 * it cannot outlive the shell even if the shell dies.
 */
export function startCore(options: CoreOptions): Core {
  const child = spawn(
    options.command,
    [...options.args, '--data-dir', options.dataDir, '--ui-origin', options.uiOrigin],
    {
      env: { ...process.env, TRACE_API_SECRET: options.secret },
      stdio: ['pipe', 'pipe', 'inherit'],
    },
  )

  const ready = new Promise<string>((resolve, reject) => {
    child.once('error', (cause) => {
      reject(new Error(`The analysis core could not be started: ${cause.message}`))
    })
    child.once('exit', (code) => {
      reject(new Error(`The analysis core stopped before it was ready (exit code ${code}).`))
    })
    createInterface({ input: child.stdout }).once('line', (line) => {
      const { port } = JSON.parse(line) as { port: number }
      resolve(`http://127.0.0.1:${port}`)
    })
  })

  return {
    ready,
    stop() {
      child.stdin.end()
      child.kill()
    },
  }
}
