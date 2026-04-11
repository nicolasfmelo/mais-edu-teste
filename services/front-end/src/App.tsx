import { useEffect, useMemo, useRef, useState } from 'react'
import {
  ChartColumn,
  ChevronDown,
  CheckCheck,
  CircleAlert,
  KeyRound,
  MessageSquareText,
  MoreVertical,
  Plus,
  Search,
  SendHorizontal,
  Sparkles,
  Wallet,
  Workflow,
} from 'lucide-react'

import { Button } from '@/components/ui/button'

type ModelOption = {
  id: string
  label: string
  family: string
  hint: string
}

type Thread = {
  id: string
  name: string
  preview: string
  time: string
  unread: number
}

type Message = {
  id: string
  role: 'assistant' | 'user'
  content: string
  time: string
  status?: 'sent' | 'seen'
}

const modelOptions: ModelOption[] = [
  {
    id: 'random',
    label: 'Random',
    family: 'Orquestrador',
    hint: 'Escolhe o melhor fluxo para atender no estilo WhatsApp.',
  },
  {
    id: 'sonnet',
    label: 'Claude Sonnet 4.6',
    family: 'Assistant model',
    hint: 'Mais equilibrado para conversas longas e contexto operacional.',
  },
  {
    id: 'gpt',
    label: 'GPT-5.4',
    family: 'Assistant model',
    hint: 'Bom para respostas mais estruturadas e resumos rápidos.',
  },
]

const initialThreads: Thread[] = [
  {
    id: 'random-funnel',
    name: 'Random',
    preview: 'Quero testar um payload curto e continuar a conversa por aqui.',
    time: '19:40',
    unread: 2,
  },
  {
    id: 'root-user',
    name: 'Root user',
    preview: 'Deixa o saldo visível e mantém a sessão pronta para atendimento.',
    time: '18:05',
    unread: 0,
  },
  {
    id: 'model-selector',
    name: 'Model select',
    preview: 'Quero alternar de modelo sem sair do fluxo principal da conversa.',
    time: 'Ontem',
    unread: 0,
  },
]

const initialMessages: Record<string, Message[]> = {
  'random-funnel': [
    {
      id: 'm-1',
      role: 'assistant',
      content:
        'Root user autenticado. Posso emular a conversa e guardar o apontamento para storage.',
      time: '19:32',
    },
    {
      id: 'm-2',
      role: 'user',
      content:
        'Perfeito. Quero deixar o front com cara de WhatsApp e o modelo visível no topo.',
      time: '19:36',
      status: 'seen',
    },
    {
      id: 'm-3',
      role: 'assistant',
      content:
        'Fechado. Vou priorizar thread, histórico, composer e atalhos de Metrics/LLMOps como ações secundárias.',
      time: '19:40',
    },
  ],
  'root-user': [
    {
      id: 'm-4',
      role: 'assistant',
      content: 'Usuário root conectado com JWT válido para abrir a shell do chat.',
      time: '18:00',
    },
    {
      id: 'm-5',
      role: 'user',
      content: 'Mantém visível o saldo de créditos no cabeçalho.',
      time: '18:05',
      status: 'seen',
    },
  ],
  'model-selector': [
    {
      id: 'm-6',
      role: 'assistant',
      content: 'O seletor precisa parecer parte da conversa, não um filtro de dashboard.',
      time: 'Ontem',
    },
  ],
}

const quickRoutes = [
  { label: 'Metrics Page', icon: ChartColumn },
  { label: 'LLMOps Page', icon: Workflow },
]

const assistantReplies: Record<string, string> = {
  random:
    'Recebi a nova mensagem. Posso encaminhar esse JSON pequeno para a rota livre e manter a experiência no chat.',
  sonnet:
    'Com Sonnet ativo, eu consigo manter contexto mais longo e devolver a próxima ação já no formato da thread.',
  gpt:
    'Com GPT-5.4 ativo, eu resumo o payload, valido o fluxo e respondo pronto para o próximo passo da UI.',
}

const infoBannerMessages = [
  'Caso precise de chaves de API, foi enviado um lote de 10 chaves ao RH',
  'Devido ao proxy existir em lambda com coldstart pode ocorrer alguma latência no primeiro invoke.',
]

function formatThreadTime() {
  return new Intl.DateTimeFormat('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date())
}

function App() {
  const [activeModelId, setActiveModelId] = useState('sonnet')
  const [apiKey, setApiKey] = useState('')
  const [apiKeyModalOpen, setApiKeyModalOpen] = useState(false)
  const [credits, setCredits] = useState(20)
  const [threads, setThreads] = useState(initialThreads)
  const [messagesByThread, setMessagesByThread] = useState(initialMessages)
  const [activeThreadId, setActiveThreadId] = useState(initialThreads[0].id)
  const [draft, setDraft] = useState('')
  const [modelMenuOpen, setModelMenuOpen] = useState(false)
  const [infoBannerIndex, setInfoBannerIndex] = useState(0)
  const chatScrollRef = useRef<HTMLDivElement | null>(null)
  const shouldAutoScrollRef = useRef(true)

  const activeModel = useMemo(
    () => modelOptions.find((model) => model.id === activeModelId) ?? modelOptions[1],
    [activeModelId],
  )

  const activeThread = useMemo(
    () => threads.find((thread) => thread.id === activeThreadId) ?? threads[0],
    [activeThreadId, threads],
  )

  const activeMessages = messagesByThread[activeThreadId] ?? []

  const scrollChatToBottom = (behavior: ScrollBehavior = 'smooth') => {
    const container = chatScrollRef.current
    if (!container) {
      return
    }

    container.scrollTo({
      top: container.scrollHeight,
      behavior,
    })
  }

  const handleChatScroll = () => {
    const container = chatScrollRef.current
    if (!container) {
      return
    }

    const distanceFromBottom =
      container.scrollHeight - container.scrollTop - container.clientHeight

    shouldAutoScrollRef.current = distanceFromBottom < 72
  }

  useEffect(() => {
    const intervalId = window.setInterval(() => {
      setInfoBannerIndex((current) => (current + 1) % infoBannerMessages.length)
    }, 5000)

    return () => window.clearInterval(intervalId)
  }, [])

  useEffect(() => {
    shouldAutoScrollRef.current = true
    window.requestAnimationFrame(() => scrollChatToBottom('auto'))
  }, [activeThreadId])

  useEffect(() => {
    if (!shouldAutoScrollRef.current) {
      return
    }

    window.requestAnimationFrame(() => scrollChatToBottom('smooth'))
  }, [activeMessages.length])

  const sendMessage = () => {
    const content = draft.trim()
    if (!content || credits <= 0) {
      return
    }

    const time = formatThreadTime()
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content,
      time,
      status: 'seen',
    }

    setMessagesByThread((current) => ({
      ...current,
      [activeThreadId]: [...(current[activeThreadId] ?? []), userMessage],
    }))

    setThreads((current) =>
      current.map((thread) =>
        thread.id === activeThreadId
          ? {
              ...thread,
              preview: content,
              time,
              unread: 0,
            }
          : thread,
      ),
    )

    setDraft('')
    setCredits((current) => Math.max(current - 1, 0))

    window.setTimeout(() => {
      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: assistantReplies[activeModel.id],
        time: formatThreadTime(),
      }

      setMessagesByThread((current) => ({
        ...current,
        [activeThreadId]: [...(current[activeThreadId] ?? []), assistantMessage],
      }))

      setThreads((current) =>
        current.map((thread) =>
          thread.id === activeThreadId
            ? {
                ...thread,
                preview: assistantMessage.content,
                time: assistantMessage.time,
              }
            : thread,
        ),
      )
    }, 900)
  }

  const createThread = () => {
    const id = crypto.randomUUID()
    const freshThread: Thread = {
      id,
      name: `Usuário ${threads.length + 1}`,
      preview: 'Nova conversa iniciada. Pode mandar a primeira mensagem.',
      time: 'agora',
      unread: 0,
    }

    setThreads((current) => [freshThread, ...current])
    setMessagesByThread((current) => ({
      ...current,
      [id]: [
        {
          id: crypto.randomUUID(),
          role: 'assistant',
          content:
            'Nova thread criada. Pode mandar a primeira mensagem que eu já respondo com o modelo ativo.',
          time: formatThreadTime(),
        },
      ],
    }))
    setActiveThreadId(id)
  }

  return (
    <main className="dark h-screen overflow-hidden bg-[linear-gradient(180deg,#00a884_0,#00a884_152px,#e9edef_152px,#d1d7db_100%)] px-3 py-5 text-foreground sm:px-5 lg:px-8">
      <div className="mx-auto flex h-[calc(100svh-2.5rem)] w-full max-w-[1480px] flex-col overflow-hidden rounded-[18px] border border-black/8 bg-[#f0f2f5] shadow-[0_8px_24px_rgba(17,27,33,0.16)]">
        <header className="border-b border-black/8 bg-[#f7f8fa] px-4 py-3 sm:px-5">
          <div className="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
            <div className="flex flex-wrap items-center gap-2">
              <div className="relative">
                <button
                  type="button"
                  onClick={() => setModelMenuOpen((current) => !current)}
                  className="inline-flex h-10 items-center gap-2 rounded-full border border-black/8 bg-white px-4 text-sm font-medium text-[#111b21] transition hover:bg-[#f5f6f6]"
                >
                  <Sparkles className="size-4 text-[#00a884]" />
                  {activeModel.id === 'random' ? 'Random' : 'Assistant model'}
                  <ChevronDown className="size-4 text-[#667781]" />
                </button>

                {modelMenuOpen ? (
                  <div className="absolute left-0 top-12 z-20 w-80 rounded-3xl border border-black/8 bg-white p-2 shadow-xl">
                    {modelOptions.map((model) => (
                      <button
                        key={model.id}
                        type="button"
                        onClick={() => {
                          setActiveModelId(model.id)
                          setModelMenuOpen(false)
                        }}
                        className="flex w-full flex-col rounded-2xl px-4 py-3 text-left transition hover:bg-[#f5f6f6]"
                      >
                        <span className="text-sm font-semibold text-[#111b21]">{model.label}</span>
                        <span className="text-xs text-[#667781]">{model.family}</span>
                        <span className="mt-1 text-xs text-[#54656f]">{model.hint}</span>
                      </button>
                    ))}
                  </div>
                ) : null}
              </div>

              <Button
                type="button"
                variant="outline"
                size="icon"
                onClick={createThread}
                className="rounded-full border-black/8 bg-white text-[#111b21] hover:bg-[#f5f6f6]"
              >
                <Plus className="size-4" />
              </Button>
            </div>

            <div className="min-w-0 flex-1 xl:px-5">
              <div className="rounded-[20px] border border-black/6 bg-white px-4 py-3">
                <div className="flex flex-wrap items-center gap-x-3 gap-y-2">
                  <span className="text-[11px] font-medium uppercase tracking-[0.18em] text-[#667781]">
                    active assistant
                  </span>
                  <span className="text-sm font-semibold text-[#111b21]">{activeModel.label}</span>
                  <span className="inline-flex items-center gap-1 rounded-full bg-[#d9fdd3] px-2.5 py-1 text-xs font-medium text-[#0b5c4b]">
                    <Wallet className="size-3.5" />
                    {credits} credits
                  </span>
                  <button
                    type="button"
                    onClick={() => setApiKeyModalOpen(true)}
                    className="inline-flex items-center gap-2 rounded-full border border-black/8 bg-[#f7f8fa] px-3 py-1.5 text-xs text-[#667781] transition hover:bg-[#eef1f3]"
                  >
                    <KeyRound className="size-3.5 text-[#00a884]" />
                    <span>API key</span>
                    <span className="text-[#111b21]">{apiKey ? 'Chave salva' : 'Adicionar chave'}</span>
                  </button>
                </div>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              {quickRoutes.map(({ label, icon: Icon }) => (
                <Button
                  key={label}
                  type="button"
                  variant="ghost"
                  className="rounded-full border border-black/6 bg-white px-3.5 text-[#667781] hover:bg-[#f5f6f6] hover:text-[#111b21]"
                >
                  <Icon className="size-4" />
                  {label}
                </Button>
              ))}
            </div>
          </div>
        </header>

        <section className="grid min-h-0 flex-1 grid-cols-1 lg:grid-cols-[340px_minmax(0,1fr)]">
          <aside className="flex min-h-0 flex-col border-b border-black/8 bg-white lg:border-r lg:border-b-0">
            <div className="flex items-center justify-between bg-[#f0f2f5] px-4 py-3">
              <div className="flex size-10 items-center justify-center rounded-full bg-[#dfe5e7] text-sm font-semibold text-[#111b21]">
                TE
              </div>
              <div className="flex items-center gap-2 text-[#54656f]">
                <Button
                  type="button"
                  variant="ghost"
                  size="icon-sm"
                  className="rounded-full hover:bg-black/5"
                >
                  <MessageSquareText className="size-4" />
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon-sm"
                  className="rounded-full hover:bg-black/5"
                >
                  <MoreVertical className="size-4" />
                </Button>
              </div>
            </div>

            <div className="border-b border-black/6 bg-[#f0f2f5] px-3 py-3">
              <div className="flex items-center gap-3 rounded-lg bg-white px-3 py-2 text-sm text-[#667781]">
                <Search className="size-4" />
                Search or start a new chat
              </div>
            </div>

            <div className="min-h-0 flex-1 overflow-y-auto bg-white">
              {threads.map((thread) => {
                const selected = thread.id === activeThreadId

                return (
                  <button
                    key={thread.id}
                    type="button"
                    onClick={() => setActiveThreadId(thread.id)}
                    className={`flex w-full items-start gap-3 border-b border-black/6 px-3 py-3 text-left transition ${
                      selected ? 'bg-[#f0f2f5]' : 'hover:bg-[#f5f6f6]'
                    }`}
                  >
                    <div
                      className={`flex size-12 shrink-0 items-center justify-center rounded-full text-sm font-semibold ${
                        selected
                          ? 'bg-[#d9fdd3] text-[#0b5c4b]'
                          : 'bg-[#dfe5e7] text-[#111b21]'
                      }`}
                    >
                      {thread.name
                        .split(' ')
                        .slice(0, 2)
                        .map((part) => part[0])
                        .join('')}
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-start justify-between gap-3">
                        <p className="truncate text-sm font-medium text-[#111b21]">
                          {thread.name}
                        </p>
                        <span className="shrink-0 text-[11px] text-[#667781]">{thread.time}</span>
                      </div>
                      <div className="mt-1 flex items-center gap-2">
                        <p className="line-clamp-1 min-w-0 flex-1 text-sm text-[#667781]">
                          {thread.preview}
                        </p>
                        {thread.unread > 0 ? (
                          <span className="inline-flex min-w-5 items-center justify-center rounded-full bg-[#25d366] px-1.5 py-0.5 text-[11px] font-semibold text-white">
                            {thread.unread}
                          </span>
                        ) : null}
                      </div>
                    </div>
                  </button>
                )
              })}
            </div>
          </aside>

          <div className="flex min-h-0 flex-col bg-[#efeae2]">
            <div className="border-b border-black/8 bg-[#f0f2f5] px-4 py-3">
              <div className="flex items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <div className="flex size-10 items-center justify-center rounded-full bg-[#dfe5e7] text-sm font-semibold text-[#111b21]">
                    {activeThread.name
                      .split(' ')
                      .slice(0, 2)
                      .map((part) => part[0])
                      .join('')}
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-[#111b21]">{activeThread.name}</p>
                    <p className="text-xs text-[#667781]">{activeModel.label}</p>
                  </div>
                </div>

                <div className="flex items-center gap-2 text-[#54656f]">
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon-sm"
                    className="rounded-full hover:bg-black/5"
                  >
                    <Search className="size-4" />
                  </Button>
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon-sm"
                    className="rounded-full hover:bg-black/5"
                  >
                    <MoreVertical className="size-4" />
                  </Button>
                </div>
              </div>
            </div>

            <div className="border-b border-black/6 bg-[#fff3c4] px-4 py-2 text-center text-[12px] text-[#54656f]">
              <div
                key={infoBannerIndex}
                className="inline-flex items-center gap-2 animate-in fade-in duration-300"
              >
                <CircleAlert className="size-3.5 text-[#667781]" />
                {infoBannerMessages[infoBannerIndex]}
              </div>
            </div>

            <div
              ref={chatScrollRef}
              onScroll={handleChatScroll}
              className="min-h-0 flex-1 overflow-y-auto scroll-smooth bg-[#efeae2] bg-[radial-gradient(rgba(255,255,255,0.32)_1px,transparent_1px)] bg-[length:24px_24px] px-4 py-4 sm:px-8"
            >
              <div className="mx-auto flex min-h-full max-w-4xl flex-col justify-end gap-3">
                <div className="mx-auto rounded-md bg-[#e1f2fb] px-2.5 py-1 text-[11px] font-medium uppercase text-[#54656f] shadow-sm">
                  Today
                </div>

                {activeMessages.map((message) => {
                  const isUser = message.role === 'user'

                  return (
                    <article
                      key={message.id}
                      className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[32rem] rounded-lg px-3 py-2 shadow-[0_1px_0_rgba(17,27,33,0.08)] ${
                          isUser
                            ? 'bg-[#d9fdd3] text-[#111b21]'
                            : 'bg-white text-[#111b21]'
                        }`}
                      >
                        <p className="whitespace-pre-wrap text-[14px] leading-6">
                          {message.content}
                        </p>
                        <div className="mt-1 flex items-center justify-end gap-1 text-[11px] text-[#667781]">
                          <span>{message.time}</span>
                          {isUser ? <CheckCheck className="size-3.5 text-[#53bdeb]" /> : null}
                        </div>
                      </div>
                    </article>
                  )
                })}
              </div>
            </div>

            <div className="border-t border-black/8 bg-[#f0f2f5] px-4 py-3">
              <div className="mx-auto flex max-w-4xl items-end gap-3">
                <div className="flex min-h-14 flex-1 items-center rounded-lg bg-white px-3">
                  <textarea
                    value={draft}
                    onChange={(event) => setDraft(event.target.value)}
                    onKeyDown={(event) => {
                      if (event.key === 'Enter' && !event.shiftKey) {
                        event.preventDefault()
                        sendMessage()
                      }
                    }}
                    placeholder="Type a message"
                    className="min-h-10 flex-1 resize-none bg-transparent py-3 text-sm text-[#111b21] outline-none placeholder:text-[#8696a0]"
                    autoComplete="off"
                  />
                </div>

                <Button
                  type="button"
                  onClick={sendMessage}
                  disabled={!draft.trim() || credits <= 0}
                  className="size-11 rounded-full bg-[#00a884] text-white hover:bg-[#0dc39a]"
                >
                  <SendHorizontal className="size-5" />
                </Button>
              </div>
            </div>
          </div>
        </section>
      </div>

      {apiKeyModalOpen ? (
        <div className="fixed inset-0 z-40 flex items-center justify-center bg-[#111b21]/30 px-4 backdrop-blur-[2px]">
          <div className="w-full max-w-md rounded-[28px] border border-black/8 bg-[#f7f8fa] p-5 shadow-[0_16px_40px_rgba(17,27,33,0.22)]">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-sm font-semibold text-[#111b21]">API key</p>
                <p className="mt-1 text-sm text-[#667781]">
                  Salve a chave para montar o header de request no back sem poluir o topo do chat.
                </p>
              </div>
              <Button
                type="button"
                variant="ghost"
                size="icon-sm"
                onClick={() => setApiKeyModalOpen(false)}
                className="rounded-full text-[#667781] hover:bg-black/5 hover:text-[#111b21]"
              >
                <span aria-hidden="true" className="text-base leading-none">
                  ×
                </span>
              </Button>
            </div>

            <div className="mt-5 space-y-3">
              <label className="block text-xs font-medium uppercase tracking-[0.14em] text-[#667781]">
                Chave de acesso
              </label>
              <input
                type="password"
                value={apiKey}
                onChange={(event) => setApiKey(event.target.value)}
                placeholder="Cole sua chave aqui"
                className="w-full rounded-2xl border border-black/8 bg-white px-4 py-3 text-sm text-[#111b21] outline-none placeholder:text-[#8696a0] focus:border-[#00a884]/50"
                autoComplete="off"
                spellCheck={false}
              />
              <p className="text-xs text-[#667781]">
                Ela fica escondida na interface e pronta para compor os requests do backend.
              </p>
            </div>

            <div className="mt-5 flex items-center justify-end gap-2">
              <Button
                type="button"
                variant="ghost"
                onClick={() => setApiKeyModalOpen(false)}
                className="rounded-full px-4 text-[#667781] hover:bg-black/5 hover:text-[#111b21]"
              >
                Fechar
              </Button>
              <Button
                type="button"
                onClick={() => setApiKeyModalOpen(false)}
                className="rounded-full bg-[#00a884] px-4 text-[#06291f] hover:bg-[#0dc39a]"
              >
                Salvar chave
              </Button>
            </div>
          </div>
        </div>
      ) : null}
    </main>
  )
}

export default App
