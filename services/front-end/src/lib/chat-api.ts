const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL ?? 'http://0.0.0.0:8000').replace(/\/$/, '')

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
