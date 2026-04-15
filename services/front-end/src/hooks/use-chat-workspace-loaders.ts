import { useEffect, type Dispatch, type SetStateAction } from 'react'

import {
  createChatSession,
  getChatSession,
  listChatSessions,
} from '@/lib/chat-api'
import {
  getErrorMessage,
  mapMessage,
  mapThread,
  markThreadLoaded,
  replaceThreadMessages,
  type Message,
  type Thread,
} from '@/lib/chat-ui'

type SetState<T> = Dispatch<SetStateAction<T>>

type SetErrorMessage = SetState<string | null>
type SetMessagesByThread = SetState<Record<string, Message[]>>
type SetThreads = SetState<Thread[]>
type SetLoadedThreadIds = SetState<Record<string, boolean>>

function applyCreatedSessionToWorkspace(params: {
  createdSession: Awaited<ReturnType<typeof createChatSession>>
  setThreads: SetThreads
  setMessagesByThread: SetMessagesByThread
  setLoadedThreadIds: SetLoadedThreadIds
  setActiveThreadId: SetState<string | null>
}) {
  const { createdSession, setThreads, setMessagesByThread, setLoadedThreadIds, setActiveThreadId } = params
  const createdThread = mapThread(createdSession)

  setThreads([createdThread])
  setMessagesByThread({ [createdSession.id]: [] })
  setLoadedThreadIds(markThreadLoaded({}, createdSession.id))
  setActiveThreadId(createdSession.id)
}

function applyListedSessionsToWorkspace(params: {
  sessions: Awaited<ReturnType<typeof listChatSessions>>['items']
  setThreads: SetThreads
  setActiveThreadId: SetState<string | null>
}) {
  const { sessions, setThreads, setActiveThreadId } = params
  const nextThreads = sessions.map(mapThread)

  setThreads(nextThreads)
  setActiveThreadId(nextThreads[0]?.id ?? null)
}

async function bootstrapWorkspace(params: {
  isCancelled: () => boolean
  setThreads: SetThreads
  setMessagesByThread: SetMessagesByThread
  setLoadedThreadIds: SetLoadedThreadIds
  setActiveThreadId: SetState<string | null>
}) {
  const { isCancelled, setThreads, setMessagesByThread, setLoadedThreadIds, setActiveThreadId } = params
  const response = await listChatSessions()
  if (isCancelled()) {
    return
  }

  if (response.items.length > 0) {
    applyListedSessionsToWorkspace({
      sessions: response.items,
      setThreads,
      setActiveThreadId,
    })
    return
  }

  const createdSession = await createChatSession()
  if (isCancelled()) {
    return
  }

  applyCreatedSessionToWorkspace({
    createdSession,
    setThreads,
    setMessagesByThread,
    setLoadedThreadIds,
    setActiveThreadId,
  })
}

function applyActiveThreadSession(params: {
  threadId: string
  response: Awaited<ReturnType<typeof getChatSession>>
  setMessagesByThread: SetMessagesByThread
  setThreads: SetThreads
  setLoadedThreadIds: SetLoadedThreadIds
}) {
  const { threadId, response, setMessagesByThread, setThreads, setLoadedThreadIds } = params
  setMessagesByThread((current) =>
    replaceThreadMessages(current, threadId, response.messages.map(mapMessage)),
  )
  setThreads((current) =>
    current.map((thread) => (thread.id === threadId ? mapThread(response.session) : thread)),
  )
  setLoadedThreadIds((current) => markThreadLoaded(current, threadId))
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
    const isCancelled = () => cancelled

    const bootstrapChat = async () => {
      setIsBootstrapping(true)
      setErrorMessage(null)

      try {
        await bootstrapWorkspace({
          isCancelled,
          setThreads,
          setMessagesByThread,
          setLoadedThreadIds,
          setActiveThreadId,
        })
      } catch (error) {
        if (!isCancelled()) {
          setErrorMessage(getErrorMessage(error, 'Nao foi possivel carregar as conversas.'))
        }
      } finally {
        if (!isCancelled()) {
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
    const isCancelled = () => cancelled

    const loadActiveThread = async () => {
      setIsLoadingThread(true)
      setErrorMessage(null)

      try {
        const response = await getChatSession(activeThreadId)
        if (isCancelled()) {
          return
        }

        applyActiveThreadSession({
          threadId: activeThreadId,
          response,
          setMessagesByThread,
          setThreads,
          setLoadedThreadIds,
        })
      } catch (error) {
        if (!isCancelled()) {
          setErrorMessage(getErrorMessage(error, 'Nao foi possivel carregar a conversa selecionada.'))
        }
      } finally {
        if (!isCancelled()) {
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
