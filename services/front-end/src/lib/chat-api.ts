import { buildApiUrl } from '@/lib/api-url'
import { fetchWithTimeout, readJsonBody } from '@/lib/http-json'

export type ChatSessionSummary = {
  id: string
  status: string
  display_name: string
  preview: string
  message_count: number
  created_at: string | null
  updated_at: string | null
  last_message_at: string | null
}

export type ChatSessionMessage = {
  id: string
  role: 'assistant' | 'user' | 'system'
  content: string
  created_at: string | null
}

export type ChatSessionDetail = {
  session: ChatSessionSummary
  messages: ChatSessionMessage[]
}

export type SendChatMessageResponse = {
  session_id: string
  reply: string
  assistant_message: ChatSessionMessage
}

export type SendChatAudioMessageResponse = SendChatMessageResponse & {
  transcription: string
}

export type CreditBalance = {
  available: number
  checked_at: string
}

export type AssistantModel = {
  key: string
  label: string
  provider: string
  is_default: boolean
  status: string
}

type ApiErrorPayload = {
  error?: string
}

const TRANSCRIPTION_REQUEST_TIMEOUT_MS = 180_000

async function request<T>(path: string, init?: RequestInit, timeoutMs?: number): Promise<T> {
  const headers = new Headers(init?.headers ?? {})
  if (!(init?.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  const response = await fetchWithTimeout(
    buildApiUrl(path),
    {
      ...init,
      headers,
    },
    timeoutMs,
  )

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

export function listChatSessions() {
  return request<{ items: ChatSessionSummary[] }>('/api/chat/sessions')
}

export function listAssistantModels() {
  return request<{ items: AssistantModel[] }>('/api/assistant-models')
}

export function getCreditBalance(apiKey: string) {
  return request<CreditBalance>('/api/credits/balance', {
    headers: {
      'x-api-key': apiKey,
    },
  })
}

export function createChatSession() {
  return request<ChatSessionSummary>('/api/chat/sessions', {
    method: 'POST',
  })
}

export function getChatSession(sessionId: string) {
  return request<ChatSessionDetail>(`/api/chat/sessions/${sessionId}`)
}

export function postChatMessage(input: {
  sessionId: string
  message: string
  apiKey: string
  modelId?: string
}) {
  return request<SendChatMessageResponse>('/api/chat/messages', {
    method: 'POST',
    body: JSON.stringify({
      session_id: input.sessionId,
      message: input.message,
      api_key: input.apiKey,
      model_id: input.modelId,
    }),
  })
}

export function postChatAudioMessage(input: {
  sessionId: string
  audio: Blob
  filename: string
  apiKey: string
  modelId?: string
  language?: string
}) {
  const formData = new FormData()
  formData.append('session_id', input.sessionId)
  formData.append('api_key', input.apiKey)
  formData.append('audio', input.audio, input.filename)
  if (input.modelId) {
    formData.append('model_id', input.modelId)
  }
  if (input.language) {
    formData.append('language', input.language)
  }

  return request<SendChatAudioMessageResponse>(
    '/api/chat/audio-messages',
    {
      method: 'POST',
      body: formData,
    },
    TRANSCRIPTION_REQUEST_TIMEOUT_MS,
  )
}
