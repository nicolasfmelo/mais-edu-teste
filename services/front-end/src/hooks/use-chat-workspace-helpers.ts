import { useEffect, type Dispatch, type KeyboardEvent, type MutableRefObject, type SetStateAction } from 'react'

import {
  createChatSession,
  getCreditBalance,
  getChatSession,
  listAssistantModels,
  listChatSessions,
  postChatMessage,
} from '@/lib/chat-api'
import {
  appendMessageToThread,
  createLocalId,
  formatThreadTime,
  getErrorMessage,
  infoBannerMessages,
  isCreditsDepleted,
  mapMessage,
  mapModelOption,
  mapThread,
  markThreadLoaded,
  pickActiveModelId,
  replaceThreadMessages,
  updateThreadAfterAssistantMessage,
  updateThreadAfterUserMessage,
  type Message,
  type ModelOption,
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

export function scrollChatToBottom(
  chatScrollRef: MutableRefObject<HTMLDivElement | null>,
  behavior: ScrollBehavior = 'smooth',
) {
  const container = chatScrollRef.current
  if (!container) {
    return
  }

  container.scrollTo({
    top: container.scrollHeight,
    behavior,
  })
}

export function syncAutoScrollPreference(
  chatScrollRef: MutableRefObject<HTMLDivElement | null>,
  shouldAutoScrollRef: MutableRefObject<boolean>,
) {
  const container = chatScrollRef.current
  if (!container) {
    return
  }

  const distanceFromBottom = container.scrollHeight - container.scrollTop - container.clientHeight
  shouldAutoScrollRef.current = distanceFromBottom < 72
}

export function useInfoBannerRotation(setInfoBannerIndex: SetState<number>) {
  useEffect(() => {
    const intervalId = window.setInterval(() => {
      setInfoBannerIndex((current) => (current + 1) % infoBannerMessages.length)
    }, 5000)

    return () => window.clearInterval(intervalId)
  }, [setInfoBannerIndex])
}

export function useAssistantModelsLoader(params: {
  setAssistantModelOptions: SetState<ModelOption[]>
  setActiveModelId: SetState<string | null>
  setErrorMessage: SetErrorMessage
}) {
  const { setAssistantModelOptions, setActiveModelId, setErrorMessage } = params

  useEffect(() => {
    let cancelled = false

    const loadAssistantModels = async () => {
      try {
        const response = await listAssistantModels()
        if (cancelled) {
          return
        }

        const nextOptions = response.items.map(mapModelOption)
        setAssistantModelOptions(nextOptions)
        setActiveModelId((current) => pickActiveModelId(current, nextOptions))
      } catch (error) {
        if (!cancelled) {
          setErrorMessage(getErrorMessage(error, 'Nao foi possivel carregar os modelos disponiveis.'))
        }
      }
    }

    void loadAssistantModels()

    return () => {
      cancelled = true
    }
  }, [setActiveModelId, setAssistantModelOptions, setErrorMessage])
}

export function useChatBootstrap(params: {
  setIsBootstrapping: SetState<boolean>
  setErrorMessage: SetErrorMessage
  setThreads: SetThreads
  setMessagesByThread: SetMessagesByThread
  setLoadedThreadIds: SetLoadedThreadIds
  setActiveThreadId: SetState<string | null>
}) {
  const {
    setIsBootstrapping,
    setErrorMessage,
    setThreads,
    setMessagesByThread,
    setLoadedThreadIds,
    setActiveThreadId,
  } = params

  useEffect(() => {
    let cancelled = false

    const bootstrapChat = async () => {
      setIsBootstrapping(true)
      setErrorMessage(null)

      try {
        const response = await listChatSessions()
        if (cancelled) {
          return
        }

        if (response.items.length === 0) {
          const createdSession = await createChatSession()
          if (cancelled) {
            return
          }

          const createdThread = mapThread(createdSession)
          setThreads([createdThread])
          setMessagesByThread({ [createdSession.id]: [] })
          setLoadedThreadIds(markThreadLoaded({}, createdSession.id))
          setActiveThreadId(createdSession.id)
          return
        }

        const nextThreads = response.items.map(mapThread)
        setThreads(nextThreads)
        setActiveThreadId(nextThreads[0]?.id ?? null)
      } catch (error) {
        if (!cancelled) {
          setErrorMessage(getErrorMessage(error, 'Nao foi possivel carregar as conversas.'))
        }
      } finally {
        if (!cancelled) {
          setIsBootstrapping(false)
        }
      }
    }

    void bootstrapChat()

    return () => {
      cancelled = true
    }
  }, [
    setActiveThreadId,
    setErrorMessage,
    setIsBootstrapping,
    setLoadedThreadIds,
    setMessagesByThread,
    setThreads,
  ])
}

export function useCreditsLoader(params: {
  trimmedApiKey: string
  setCredits: SetState<number | null>
  setErrorMessage: SetErrorMessage
}) {
  const { trimmedApiKey, setCredits, setErrorMessage } = params

  useEffect(() => {
    if (!trimmedApiKey) {
      setCredits(null)
      return
    }

    let cancelled = false

    const loadCredits = async () => {
      try {
        const balance = await getCreditBalance(trimmedApiKey)
        if (!cancelled) {
          setCredits(balance.available)
        }
      } catch (error) {
        if (!cancelled) {
          setCredits(null)
          setErrorMessage(getErrorMessage(error, 'Nao foi possivel carregar os creditos atuais.'))
        }
      }
    }

    void loadCredits()

    return () => {
      cancelled = true
    }
  }, [setCredits, setErrorMessage, trimmedApiKey])
}

export function useChatAutoScroll(params: {
  activeThreadId: string | null
  activeMessageCount: number
  chatScrollRef: MutableRefObject<HTMLDivElement | null>
  shouldAutoScrollRef: MutableRefObject<boolean>
}) {
  const { activeThreadId, activeMessageCount, chatScrollRef, shouldAutoScrollRef } = params

  useEffect(() => {
    shouldAutoScrollRef.current = true
    window.requestAnimationFrame(() => scrollChatToBottom(chatScrollRef, 'auto'))
  }, [activeThreadId, chatScrollRef, shouldAutoScrollRef])

  useEffect(() => {
    if (!shouldAutoScrollRef.current) {
      return
    }

    window.requestAnimationFrame(() => scrollChatToBottom(chatScrollRef, 'smooth'))
  }, [activeMessageCount, chatScrollRef, shouldAutoScrollRef])
}

export function useActiveThreadLoader(params: {
  activeThreadId: string | null
  loadedThreadIds: Record<string, boolean>
  setIsLoadingThread: SetState<boolean>
  setErrorMessage: SetErrorMessage
  setMessagesByThread: SetMessagesByThread
  setThreads: SetThreads
  setLoadedThreadIds: SetLoadedThreadIds
}) {
  const {
    activeThreadId,
    loadedThreadIds,
    setIsLoadingThread,
    setErrorMessage,
    setMessagesByThread,
    setThreads,
    setLoadedThreadIds,
  } = params

  useEffect(() => {
    if (!activeThreadId || loadedThreadIds[activeThreadId]) {
      return
    }

    let cancelled = false

    const loadActiveThread = async () => {
      setIsLoadingThread(true)
      setErrorMessage(null)

      try {
        const response = await getChatSession(activeThreadId)
        if (cancelled) {
          return
        }

        setMessagesByThread((current) =>
          replaceThreadMessages(current, activeThreadId, response.messages.map(mapMessage)),
        )
        setThreads((current) =>
          current.map((thread) => (thread.id === activeThreadId ? mapThread(response.session) : thread)),
        )
        setLoadedThreadIds((current) => markThreadLoaded(current, activeThreadId))
      } catch (error) {
        if (!cancelled) {
          setErrorMessage(getErrorMessage(error, 'Nao foi possivel carregar a conversa selecionada.'))
        }
      } finally {
        if (!cancelled) {
          setIsLoadingThread(false)
        }
      }
    }

    void loadActiveThread()

    return () => {
      cancelled = true
    }
  }, [
    activeThreadId,
    loadedThreadIds,
    setErrorMessage,
    setIsLoadingThread,
    setLoadedThreadIds,
    setMessagesByThread,
    setThreads,
  ])
}

export async function sendChatMessage(params: {
  draft: string
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
  setDraft: SetState<string>
  setIsSending: SetState<boolean>
  setLoadedThreadIds: SetLoadedThreadIds
  setCredits: SetState<number | null>
}) {
  const {
    draft,
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
    setDraft,
    setIsSending,
    setLoadedThreadIds,
    setCredits,
  } = params
  const content = draft.trim()
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
  setDraft('')
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
    setDraft(content)
    setErrorMessage(getErrorMessage(error, 'Nao foi possivel enviar a mensagem.'))
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
  sendMessage: () => Promise<void>,
) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    void sendMessage()
  }
}
