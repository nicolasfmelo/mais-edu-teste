const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL ?? 'http://0.0.0.0:8000').replace(/\/$/, '')

type ApiErrorPayload = {
  error?: string
}

export type PromptVersion = {
  id: string
  version_number: number
  template: string
  description: string
  is_active: boolean
}

export type PromptRegistryEntry = {
  key: string
  active_version_id: string | null
  versions: PromptVersion[]
}

export type CreatePromptInput = {
  key: string
  template: string
  description: string
}

export type CreatePromptVersionInput = {
  template: string
  description: string
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
  })

  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as ApiErrorPayload | null
    throw new Error(payload?.error ?? 'Nao foi possivel completar a requisicao.')
  }

  return (await response.json()) as T
}

export async function getPrompt(promptKey: string): Promise<PromptRegistryEntry | null> {
  const response = await fetch(`${apiBaseUrl}/api/prompt-registry/prompts/${promptKey}`)

  if (response.status === 404) {
    return null
  }

  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as ApiErrorPayload | null
    throw new Error(payload?.error ?? 'Nao foi possivel carregar o prompt.')
  }

  return (await response.json()) as PromptRegistryEntry
}

export function createPrompt(input: CreatePromptInput) {
  return request<PromptRegistryEntry>('/api/prompt-registry/prompts', {
    method: 'POST',
    body: JSON.stringify(input),
  })
}

export function createPromptVersion(promptKey: string, input: CreatePromptVersionInput) {
  return request<PromptRegistryEntry>(`/api/prompt-registry/prompts/${promptKey}/versions`, {
    method: 'POST',
    body: JSON.stringify(input),
  })
}

export function activatePromptVersion(promptKey: string, versionId: string) {
  return request<PromptRegistryEntry>(`/api/prompt-registry/prompts/${promptKey}/active`, {
    method: 'POST',
    body: JSON.stringify({ version_id: versionId }),
  })
}
