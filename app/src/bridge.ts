/**
 * What the desktop shell offers the user interface, as `window.trace`.
 *
 * The user interface runs in a sandbox with no access to the computer. This
 * bridge is the whole of what it can ask the shell to do.
 */
export interface TraceBridge {
  /**
   * Where the core's local API is, and the secret of this launch that every
   * request to it must carry. Resolves once the core is ready.
   */
  coreConnection(): Promise<CoreConnection>

  /**
   * Lets the user choose a file to import. Resolves to its path, or to null
   * if they cancel.
   */
  chooseLogFile(): Promise<string | null>
}

export interface CoreConnection {
  baseUrl: string
  secret: string
}

declare global {
  interface Window {
    trace: TraceBridge
  }
}
