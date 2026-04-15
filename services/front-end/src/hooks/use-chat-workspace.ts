import { useMemo, useRef, useState } from 'react'
import {
  buildThreadInitials,
  infoBannerMessages,
  randomModelOption,
  type Message,
  type ModelOption,
  type Thread,
} from '@/lib/chat-ui'
import {
  syncAutoScrollPreference,
  useChatAutoScroll,
  useInfoBannerRotation,
} from './use-chat-workspace-helpers'
import { createWorkspaceThread, sendChatAudioMessage, sendChatMessage } from './use-chat-workspace-actions'
import {
  useActiveThreadLoader,
  useChatBootstrap,
} from './use-chat-workspace-loaders'
import { useAssistantModelsLoader, useCreditsLoader } from './use-chat-workspace-resource-loaders'

export function useChatWorkspace() {
  const [activeModelId, setActiveModelId] = useState<string | null>(null)
  const [apiKey, setApiKey] = useState('')
  const [apiKeyDraft, setApiKeyDraft] = useState('')
  const [apiKeyModalOpen, setApiKeyModalOpen] = useState(false)
  const [credits, setCredits] = useState<number | null>(null)
  const [assistantModelOptions, setAssistantModelOptions] = useState<ModelOption[]>([])
  const [threads, setThreads] = useState<Thread[]>([])
  const [messagesByThread, setMessagesByThread] = useState<Record<string, Message[]>>({})
  const [activeThreadId, setActiveThreadId] = useState<string | null>(null)
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

  const sendMessage = (content: string) =>
    sendChatMessage({
      content,
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
      setIsSending,
      setLoadedThreadIds,
      setCredits,
    })

  const sendAudioMessage = (audio: File) =>
    sendChatAudioMessage({
      audio,
      activeThreadId,
      credits,
      isSending,
      trimmedApiKey,
      apiKey,
      modelId: activeModel.modelId,
      threads,
      setApiKeyModalOpen,
      setErrorMessage,
      setMessagesByThread,
      setThreads,
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

  return {
    activeModel,
    activeMessages,
    activeThreadId,
    activeThreadInitials,
    activeThreadName,
    apiKey,
    apiKeyDraft,
    apiKeyModalOpen,
    chatScrollRef,
    credits,
    errorMessage,
    handleChatScroll,
    infoBannerMessage: infoBannerMessages[infoBannerIndex],
    isBootstrapping,
    isCreatingThread,
    isLoadingThread,
    isSending,
    modelMenuOpen,
    modelOptions,
    createThread,
    openApiKeyModal: () => {
      setApiKeyDraft(apiKey)
      setApiKeyModalOpen(true)
    },
    closeApiKeyModal: () => {
      setApiKeyDraft(apiKey)
      setApiKeyModalOpen(false)
    },
    saveApiKey: () => {
      setApiKey(apiKeyDraft)
      setApiKeyModalOpen(false)
    },
    selectModel: (modelId: string) => {
      setActiveModelId(modelId)
      setModelMenuOpen(false)
    },
    selectThread: setActiveThreadId,
    sendMessage,
    sendAudioMessage,
    setApiKeyDraft,
    toggleModelMenu: () => setModelMenuOpen((current) => !current),
    threads,
  }
}
