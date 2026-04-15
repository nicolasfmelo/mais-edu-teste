import type { Dispatch, KeyboardEvent, SetStateAction } from 'react'

import { createChatSession, getCreditBalance, postChatAudioMessage, postChatMessage } from '@/lib/chat-api'
import {
  appendMessageToThread,
  createLocalId,
  formatThreadTime,
  getErrorMessage,
  isCreditsDepleted,
  mapMessage,
  mapThread,
  markThreadLoaded,
  replaceThreadMessages,
  updateThreadAfterAssistantMessage,
  updateThreadAfterUserMessage,
  type Message,
  type Thread,
} from '@/lib/chat-ui'

type SetState<T> = Dispatch<SetStateAction<T>>

type SetErrorMessage = SetState<string | null>
type SetMessagesByThread = SetState<Record<string, Message[]>>
type SetThreads = SetState<Thread[]>
type SetLoadedThreadIds = SetState<Record<string, boolean>>

export async function refreshCreditsAfterSend(apiKey: string) {
  const balance = await getCreditBalance(apiKey)
  return balance.available
}

export async function sendChatMessage(params: {
  content: string
  activeThreadId: string | null
  credits: number | null
  isSending: boolean
  trimmedApiKey: string
  apiKey: string
  modelId?: string
  messagesByThread: Record<string, Message[]>
  threads: Thread[]
  setApiKeyModalOpen: SetState<boolean>
  setErrorMessage: SetErrorMessage
  setMessagesByThread: SetMessagesByThread
  setThreads: SetThreads
  setIsSending: SetState<boolean>
  setLoadedThreadIds: SetLoadedThreadIds
  setCredits: SetState<number | null>
}) {
  const {
    content,
    activeThreadId,
    credits,
    isSending,
    trimmedApiKey,
    apiKey,
    modelId,
    messagesByThread,
    threads,
    setApiKeyModalOpen,
    setErrorMessage,
    setMessagesByThread,
    setThreads,
    setIsSending,
    setLoadedThreadIds,
    setCredits,
  } = params
  const threadId = activeThreadId

  if (!content || isCreditsDepleted(credits) || !threadId || isSending) {
    return
  }

  if (!trimmedApiKey) {
    setApiKeyModalOpen(true)
    setErrorMessage('Adicione a API key antes de enviar uma mensagem.')
    return
  }

  const time = formatThreadTime()
  const userMessage: Message = {
    id: createLocalId(),
    role: 'user',
    content,
    time,
    status: 'seen',
  }
  const previousMessages = messagesByThread[threadId] ?? []
  const previousThreads = threads

  setErrorMessage(null)
  setMessagesByThread((current) => appendMessageToThread(current, threadId, userMessage))
  setThreads((current) => updateThreadAfterUserMessage(current, { threadId, content, time }))
  setIsSending(true)

  try {
    const response = await postChatMessage({
      sessionId: threadId,
      message: content,
      apiKey,
      modelId,
    })
    const assistantMessage = mapMessage(response.assistant_message)

    setMessagesByThread((current) => appendMessageToThread(current, threadId, assistantMessage))
    setThreads((current) =>
      updateThreadAfterAssistantMessage(current, {
        threadId,
        content,
        message: assistantMessage,
      }),
    )
    setLoadedThreadIds((current) => markThreadLoaded(current, threadId))
    setCredits((current) => (current === null ? current : Math.max(current - 1, 0)))

    void refreshCreditsAfterSend(trimmedApiKey)
      .then((availableCredits) => {
        setCredits(availableCredits)
      })
      .catch((error) => {
        setErrorMessage(
          getErrorMessage(error, 'A mensagem foi enviada, mas nao foi possivel atualizar os creditos.'),
        )
      })
  } catch (error) {
    setMessagesByThread((current) => replaceThreadMessages(current, threadId, previousMessages))
    setThreads(previousThreads)
    setErrorMessage(getErrorMessage(error, 'Nao foi possivel enviar a mensagem.'))
  } finally {
    setIsSending(false)
  }
}

export async function sendChatAudioMessage(params: {
  audio: File
  activeThreadId: string | null
  credits: number | null
  isSending: boolean
  trimmedApiKey: string
  apiKey: string
  modelId?: string
  threads: Thread[]
  setApiKeyModalOpen: SetState<boolean>
  setErrorMessage: SetErrorMessage
  setMessagesByThread: SetMessagesByThread
  setThreads: SetThreads
  setIsSending: SetState<boolean>
  setLoadedThreadIds: SetLoadedThreadIds
  setCredits: SetState<number | null>
}) {
  const {
    audio,
    activeThreadId,
    credits,
    isSending,
    trimmedApiKey,
    apiKey,
    modelId,
    threads,
    setApiKeyModalOpen,
    setErrorMessage,
    setMessagesByThread,
    setThreads,
    setIsSending,
    setLoadedThreadIds,
    setCredits,
  } = params
  const threadId = activeThreadId

  if (isCreditsDepleted(credits) || !threadId || isSending) {
    return
  }

  if (!trimmedApiKey) {
    setApiKeyModalOpen(true)
    setErrorMessage('Adicione a API key antes de enviar uma mensagem.')
    return
  }

  const previousThreads = threads
  setErrorMessage(null)
  setIsSending(true)

  try {
    const response = await postChatAudioMessage({
      sessionId: threadId,
      audio,
      filename: audio.name || 'audio.webm',
      apiKey,
      modelId,
      language: 'pt',
    })

    const assistantMessage = mapMessage(response.assistant_message)
    const userMessage: Message = {
      id: createLocalId(),
      role: 'user',
      content: response.transcription,
      time: assistantMessage.time,
      status: 'seen',
    }

    setMessagesByThread((current) => {
      const withUser = appendMessageToThread(current, threadId, userMessage)
      return appendMessageToThread(withUser, threadId, assistantMessage)
    })
    setThreads((current) => {
      const withUser = updateThreadAfterUserMessage(current, {
        threadId,
        content: response.transcription,
        time: userMessage.time,
      })
      return updateThreadAfterAssistantMessage(withUser, {
        threadId,
        content: response.transcription,
        message: assistantMessage,
      })
    })
    setLoadedThreadIds((current) => markThreadLoaded(current, threadId))
    setCredits((current) => (current === null ? current : Math.max(current - 1, 0)))

    void refreshCreditsAfterSend(trimmedApiKey)
      .then((availableCredits) => {
        setCredits(availableCredits)
      })
      .catch((error) => {
        setErrorMessage(
          getErrorMessage(error, 'A mensagem foi enviada, mas nao foi possivel atualizar os creditos.'),
        )
      })
  } catch (error) {
    setThreads(previousThreads)
    setErrorMessage(getErrorMessage(error, 'Nao foi possivel enviar o audio.'))
  } finally {
    setIsSending(false)
  }
}

export async function createWorkspaceThread(params: {
  isCreatingThread: boolean
  setIsCreatingThread: SetState<boolean>
  setErrorMessage: SetErrorMessage
  setThreads: SetThreads
  setMessagesByThread: SetMessagesByThread
  setLoadedThreadIds: SetLoadedThreadIds
  setActiveThreadId: SetState<string | null>
}) {
  const {
    isCreatingThread,
    setIsCreatingThread,
    setErrorMessage,
    setThreads,
    setMessagesByThread,
    setLoadedThreadIds,
    setActiveThreadId,
  } = params

  if (isCreatingThread) {
    return
  }

  setIsCreatingThread(true)
  setErrorMessage(null)

  try {
    const createdSession = await createChatSession()
    const freshThread = mapThread(createdSession)

    setThreads((current) => [freshThread, ...current])
    setMessagesByThread((current) => ({
      ...current,
      [createdSession.id]: [],
    }))
    setLoadedThreadIds((current) => markThreadLoaded(current, createdSession.id))
    setActiveThreadId(createdSession.id)
  } catch (error) {
    setErrorMessage(getErrorMessage(error, 'Nao foi possivel criar uma nova conversa.'))
  } finally {
    setIsCreatingThread(false)
  }
}

export function handleComposerEnter(
  event: KeyboardEvent<HTMLTextAreaElement>,
  sendMessage: (content: string) => Promise<void>,
  content: string,
) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    void sendMessage(content)
  }
}
