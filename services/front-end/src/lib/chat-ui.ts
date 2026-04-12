import type { AssistantModel, ChatSessionMessage, ChatSessionSummary } from '@/lib/chat-api'

export type ModelOption = {
  id: string
  label: string
  family: string
  hint: string
  isDefault?: boolean
  modelId?: string
}

export type Thread = {
  id: string
  name: string
  preview: string
  time: string
  unread: number
}

export type Message = {
  id: string
  role: 'assistant' | 'user' | 'system'
  content: string
  time: string
  status?: 'sent' | 'seen'
}

export type MessagesByThread = Record<string, Message[]>
export type LoadedThreadIds = Record<string, boolean>

export const randomModelOption: ModelOption = {
  id: 'random',
  label: 'Random',
  family: 'Orquestrador',
  hint: 'Escolhe o melhor fluxo para atender no estilo WhatsApp.',
}

export const infoBannerMessages = [
  'Caso precise de chaves de API, foi enviado um lote de 10 chaves ao RH',
  'Devido ao proxy existir em lambda com coldstart pode ocorrer alguma latência no primeiro invoke.',
]

export function formatThreadTime(value?: string | null) {
  if (!value) {
    return 'agora'
  }

  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) {
    return 'agora'
  }

  const now = new Date()
  const formatter = new Intl.DateTimeFormat(
    'pt-BR',
    parsed.toDateString() === now.toDateString()
      ? {
          hour: '2-digit',
          minute: '2-digit',
        }
      : {
          day: '2-digit',
          month: '2-digit',
        },
  )

  return formatter.format(parsed)
}

function formatMessageTime(value?: string | null) {
  if (!value) {
    return formatThreadTime()
  }

  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) {
    return formatThreadTime()
  }

  return new Intl.DateTimeFormat('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(parsed)
}

export function getErrorMessage(error: unknown, fallback: string) {
  if (error instanceof Error && error.message.trim()) {
    return error.message
  }

  return fallback
}

function toThreadName(name: string, sessionId: string) {
  const trimmed = name.trim()
  return trimmed || `Sessao ${sessionId.slice(0, 8)}`
}

export function buildThreadNameFromContent(sessionId: string, content: string) {
  const trimmed = content.trim()
  if (!trimmed) {
    return `Sessao ${sessionId.slice(0, 8)}`
  }

  const base = trimmed.slice(0, 40).trimEnd()
  return trimmed.length > 40 ? `${base}...` : base
}

export function buildThreadInitials(name: string) {
  return name
    .split(' ')
    .slice(0, 2)
    .map((part) => part[0])
    .join('')
}

export function createLocalId() {
  if (typeof globalThis.crypto?.randomUUID === 'function') {
    return globalThis.crypto.randomUUID()
  }

  return `local-${Date.now()}-${Math.random().toString(16).slice(2)}`
}

export function mapThread(summary: ChatSessionSummary): Thread {
  return {
    id: summary.id,
    name: toThreadName(summary.display_name, summary.id),
    preview: summary.preview,
    time: formatThreadTime(summary.last_message_at ?? summary.updated_at ?? summary.created_at),
    unread: 0,
  }
}

export function mapMessage(message: ChatSessionMessage): Message {
  const role = message.role === 'system' ? 'assistant' : message.role

  return {
    id: message.id,
    role,
    content: message.content,
    time: formatMessageTime(message.created_at),
    status: role === 'user' ? 'seen' : undefined,
  }
}

function buildModelHint(model: AssistantModel) {
  if (model.is_default) {
    return `Modelo padrao ativo do backend (${model.provider}).`
  }

  return `Modelo ${model.provider} disponivel via backend.`
}

export function mapModelOption(model: AssistantModel): ModelOption {
  return {
    id: model.key,
    label: model.label,
    family: 'Assistant model',
    hint: buildModelHint(model),
    isDefault: model.is_default,
    modelId: model.key,
  }
}

export function pickActiveModelId(currentId: string | null, options: ModelOption[]) {
  const availableIds = [randomModelOption.id, ...options.map((option) => option.id)]
  if (currentId && availableIds.includes(currentId)) {
    return currentId
  }

  return options.find((option) => option.isDefault)?.id ?? randomModelOption.id
}

export function isCreditsDepleted(credits: number | null) {
  return credits !== null && credits <= 0
}

function hasDraftContent(draft: string) {
  return draft.trim().length > 0
}

function hasActiveThread(activeThreadId: string | null) {
  return Boolean(activeThreadId)
}

export function isComposerDisabled(params: {
  draft: string
  credits: number | null
  isBootstrapping: boolean
  isSending: boolean
  activeThreadId: string | null
}) {
  const { draft, credits, isBootstrapping, isSending, activeThreadId } = params

  if (!hasDraftContent(draft) || !hasActiveThread(activeThreadId)) {
    return true
  }

  return isCreditsDepleted(credits) || isBootstrapping || isSending
}

export function appendMessageToThread(
  messagesByThread: MessagesByThread,
  threadId: string,
  message: Message,
) {
  return {
    ...messagesByThread,
    [threadId]: [...(messagesByThread[threadId] ?? []), message],
  }
}

export function replaceThreadMessages(
  messagesByThread: MessagesByThread,
  threadId: string,
  messages: Message[],
) {
  return {
    ...messagesByThread,
    [threadId]: messages,
  }
}

export function markThreadLoaded(loadedThreadIds: LoadedThreadIds, threadId: string) {
  return {
    ...loadedThreadIds,
    [threadId]: true,
  }
}

export function updateThreadAfterUserMessage(
  threads: Thread[],
  params: { threadId: string; content: string; time: string },
) {
  const { threadId, content, time } = params

  return threads.map((thread) =>
    thread.id === threadId
      ? {
          ...thread,
          name: buildThreadNameFromContent(threadId, content),
          preview: content,
          time,
          unread: 0,
        }
      : thread,
  )
}

export function updateThreadAfterAssistantMessage(
  threads: Thread[],
  params: { threadId: string; content: string; message: Message },
) {
  const { threadId, content, message } = params

  return threads.map((thread) =>
    thread.id === threadId
      ? {
          ...thread,
          name: buildThreadNameFromContent(threadId, content),
          preview: message.content,
          time: message.time,
          unread: 0,
        }
      : thread,
  )
}
