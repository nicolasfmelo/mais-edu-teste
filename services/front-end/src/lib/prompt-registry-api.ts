import { buildApiUrl } from '@/lib/api-url'
import { fetchWithTimeout, readJsonBody } from '@/lib/http-json'

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
  const response = await fetchWithTimeout(buildApiUrl(path), {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
  })

  if (!response.ok) {
    const { value: payload } = await readJsonBody<ApiErrorPayload>(response)
    throw new Error(payload?.error ?? 'Nao foi possivel completar a requisicao.')
  }

  const { parsed, value, raw } = await readJsonBody<T>(response)
  if (!parsed || value === null) {
    const contentType = response.headers.get('content-type') ?? 'desconhecido'
    const snippet = raw.slice(0, 80).replace(/\s+/g, ' ')
    throw new Error(
      `Resposta invalida da API em ${path} (content-type: ${contentType}).` +
        (snippet ? ` Trecho: ${snippet}` : ' Verifique VITE_API_BASE_URL/proxy.'),
    )
  }

  return value
}

export async function getPrompt(promptKey: string): Promise<PromptRegistryEntry | null> {
  const response = await fetchWithTimeout(buildApiUrl(`/api/prompt-registry/prompts/${promptKey}`))

  if (response.status === 404) {
    return null
  }

  if (!response.ok) {
    const { value: payload } = await readJsonBody<ApiErrorPayload>(response)
    throw new Error(payload?.error ?? 'Nao foi possivel carregar o prompt.')
  }

  const { parsed, value, raw } = await readJsonBody<PromptRegistryEntry>(response)
  if (!parsed || value === null) {
    const contentType = response.headers.get('content-type') ?? 'desconhecido'
    const snippet = raw.slice(0, 80).replace(/\s+/g, ' ')
    throw new Error(
      `Resposta invalida da API em /api/prompt-registry/prompts/${promptKey} (content-type: ${contentType}).` +
        (snippet ? ` Trecho: ${snippet}` : ' Verifique VITE_API_BASE_URL/proxy.'),
    )
  }

  return value
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
