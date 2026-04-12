import { useMemo, useRef, useState, type KeyboardEvent } from 'react'
import {
  buildThreadInitials,
  infoBannerMessages,
  isComposerDisabled,
  randomModelOption,
  type Message,
  type ModelOption,
  type Thread,
} from '@/lib/chat-ui'
import {
  createWorkspaceThread,
  handleComposerEnter,
  sendChatMessage,
  syncAutoScrollPreference,
  useActiveThreadLoader,
  useAssistantModelsLoader,
  useChatAutoScroll,
  useChatBootstrap,
  useCreditsLoader,
  useInfoBannerRotation,
} from './use-chat-workspace-helpers'

export function useChatWorkspace() {
  const [activeModelId, setActiveModelId] = useState<string | null>(null)
  const [apiKey, setApiKey] = useState('')
  const [apiKeyModalOpen, setApiKeyModalOpen] = useState(false)
  const [credits, setCredits] = useState<number | null>(null)
  const [assistantModelOptions, setAssistantModelOptions] = useState<ModelOption[]>([])
  const [threads, setThreads] = useState<Thread[]>([])
  const [messagesByThread, setMessagesByThread] = useState<Record<string, Message[]>>({})
  const [activeThreadId, setActiveThreadId] = useState<string | null>(null)
  const [draft, setDraft] = useState('')
  const [modelMenuOpen, setModelMenuOpen] = useState(false)
  const [infoBannerIndex, setInfoBannerIndex] = useState(0)
  const [loadedThreadIds, setLoadedThreadIds] = useState<Record<string, boolean>>({})
  const [isBootstrapping, setIsBootstrapping] = useState(true)
  const [isLoadingThread, setIsLoadingThread] = useState(false)
  const [isCreatingThread, setIsCreatingThread] = useState(false)
  const [isSending, setIsSending] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const chatScrollRef = useRef<HTMLDivElement | null>(null)
  const shouldAutoScrollRef = useRef(true)
  const trimmedApiKey = apiKey.trim()
  const modelOptions = useMemo(() => [randomModelOption, ...assistantModelOptions], [assistantModelOptions])

  const activeModel = useMemo(
    () =>
      modelOptions.find((model) => model.id === activeModelId) ??
      assistantModelOptions.find((model) => model.isDefault) ??
      assistantModelOptions[0] ??
      randomModelOption,
    [activeModelId, assistantModelOptions, modelOptions],
  )

  const activeThread = useMemo(
    () => threads.find((thread) => thread.id === activeThreadId) ?? null,
    [activeThreadId, threads],
  )

  const activeMessages = activeThreadId ? (messagesByThread[activeThreadId] ?? []) : []
  const activeThreadName = activeThread?.name ?? 'Carregando conversa'
  const activeThreadInitials = buildThreadInitials(activeThreadName)
  const composerDisabled = isComposerDisabled({
    draft,
    credits,
    isBootstrapping,
    isSending,
    activeThreadId,
  })

  const handleChatScroll = () => syncAutoScrollPreference(chatScrollRef, shouldAutoScrollRef)

  useInfoBannerRotation(setInfoBannerIndex)
  useAssistantModelsLoader({
    setAssistantModelOptions,
    setActiveModelId,
    setErrorMessage,
  })
  useChatBootstrap({
    setIsBootstrapping,
    setErrorMessage,
    setThreads,
    setMessagesByThread,
    setLoadedThreadIds,
    setActiveThreadId,
  })
  useCreditsLoader({
    trimmedApiKey,
    setCredits,
    setErrorMessage,
  })
  useChatAutoScroll({
    activeThreadId,
    activeMessageCount: activeMessages.length,
    chatScrollRef,
    shouldAutoScrollRef,
  })
  useActiveThreadLoader({
    activeThreadId,
    loadedThreadIds,
    setIsLoadingThread,
    setErrorMessage,
    setMessagesByThread,
    setThreads,
    setLoadedThreadIds,
  })

  const sendMessage = () =>
    sendChatMessage({
      draft,
      activeThreadId,
      credits,
      isSending,
      trimmedApiKey,
      apiKey,
      modelId: activeModel.modelId,
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
    })

  const createThread = () =>
    createWorkspaceThread({
      isCreatingThread,
      setIsCreatingThread,
      setErrorMessage,
      setThreads,
      setMessagesByThread,
      setLoadedThreadIds,
      setActiveThreadId,
    })

  const handleComposerKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) =>
    handleComposerEnter(event, sendMessage)

  return {
    activeModel,
    activeMessages,
    activeThreadId,
    activeThreadInitials,
    activeThreadName,
    apiKey,
    apiKeyModalOpen,
    chatScrollRef,
    composerDisabled,
    credits,
    draft,
    errorMessage,
    handleChatScroll,
    handleComposerKeyDown,
    infoBannerMessage: infoBannerMessages[infoBannerIndex],
    isBootstrapping,
    isCreatingThread,
    isLoadingThread,
    isSending,
    modelMenuOpen,
    modelOptions,
    createThread,
    openApiKeyModal: () => setApiKeyModalOpen(true),
    closeApiKeyModal: () => setApiKeyModalOpen(false),
    selectModel: (modelId: string) => {
      setActiveModelId(modelId)
      setModelMenuOpen(false)
    },
    selectThread: setActiveThreadId,
    sendMessage,
    setApiKey,
    setDraft,
    toggleModelMenu: () => setModelMenuOpen((current) => !current),
    threads,
  }
}
