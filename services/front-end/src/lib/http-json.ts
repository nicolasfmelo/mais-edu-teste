type JsonReadResult<T> = {
  parsed: boolean
  value: T | null
  raw: string
}

const DEFAULT_REQUEST_TIMEOUT_MS = 20_000

async function readResponseText(response: Response): Promise<string> {
  return (await response.text()).trim()
}

export async function readJsonBody<T>(response: Response): Promise<JsonReadResult<T>> {
  const raw = (await readResponseText(response)).replace(/^\uFEFF/, '')

  if (!raw) {
    return {
      parsed: false,
      value: null,
      raw,
    }
  }

  try {
    return {
      parsed: true,
      value: JSON.parse(raw) as T,
      raw,
    }
  } catch {
    return {
      parsed: false,
      value: null,
      raw,
    }
  }
}

function isAbortError(error: unknown): boolean {
  if (error instanceof DOMException) {
    return error.name === 'AbortError'
  }

  return error instanceof Error && error.name === 'AbortError'
}

export async function fetchWithTimeout(
  input: RequestInfo | URL,
  init?: RequestInit,
  timeoutMs: number = DEFAULT_REQUEST_TIMEOUT_MS,
): Promise<Response> {
  const controller = new AbortController()
  let timedOut = false

  const onCallerAbort = () => {
    controller.abort()
  }

  if (init?.signal) {
    if (init.signal.aborted) {
      controller.abort()
    } else {
      init.signal.addEventListener('abort', onCallerAbort, { once: true })
    }
  }

  const timeoutId = globalThis.setTimeout(() => {
    timedOut = true
    controller.abort()
  }, timeoutMs)

  try {
    return await fetch(input, {
      ...init,
      signal: controller.signal,
    })
  } catch (error) {
    if (timedOut && isAbortError(error)) {
      throw new Error(`Tempo limite excedido (${Math.round(timeoutMs / 1000)}s).`)
    }
    throw error
  } finally {
    globalThis.clearTimeout(timeoutId)
    init?.signal?.removeEventListener('abort', onCallerAbort)
  }
}
