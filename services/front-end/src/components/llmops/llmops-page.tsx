import { useEffect, useState } from 'react'
import {
  Bot,
  CircleAlert,
  GitBranchPlus,
  History,
  PencilLine,
  RefreshCw,
  ShieldCheck,
  Sparkles,
  Workflow,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  activatePromptVersion,
  createPrompt,
  createPromptVersion,
  getPrompt,
  type PromptRegistryEntry,
  type PromptVersion,
} from '@/lib/prompt-registry-api'

type AgentPromptConfig = {
  id: 'chat' | 'nps'
  label: string
  shortLabel: string
  promptKey: string
  accentClass: string
  accentSolidClass: string
  accentSoftClass: string
  accentBorderClass: string
  accentMutedClass: string
  surfaceClass: string
  borderClass: string
  icon: typeof Bot
  eyebrow: string
  summary: string
}

type ComposerMode = 'create' | 'version'

type ComposerState = {
  mode: ComposerMode
  sourceVersionId: string | null
  sourceVersionNumber: number | null
  description: string
  template: string
}

const agentConfigs: AgentPromptConfig[] = [
  {
    id: 'chat',
    label: 'Agente de Chat',
    shortLabel: 'Chat',
    promptKey: 'chat-agent-system',
    accentClass: 'text-[#0b5c4b]',
    accentSolidClass: 'bg-[#00a884]',
    accentSoftClass: 'bg-[#d9fdd3] text-[#0b5c4b]',
    accentBorderClass: 'border-[#00a884]/45',
    accentMutedClass: 'bg-[#eef7f4] text-[#32525a]',
    surfaceClass: 'bg-[linear-gradient(135deg,#d9fdd3_0%,#f7ffed_100%)]',
    borderClass: 'border-[#00a884]/30',
    icon: Bot,
    eyebrow: 'Conversa comercial',
    summary: 'Prompt-base da Clara para atendimento consultivo, descoberta de objetivo e recomendacao de curso.',
  },
  {
    id: 'nps',
    label: 'Agente de NPS',
    shortLabel: 'NPS',
    promptKey: 'nps-agent-system',
    accentClass: 'text-[#8a5a00]',
    accentSolidClass: 'bg-[#d89b1d]',
    accentSoftClass: 'bg-[#fff1cc] text-[#8a5a00]',
    accentBorderClass: 'border-[#d89b1d]/45',
    accentMutedClass: 'bg-[#fff7e5] text-[#8a5a00]',
    surfaceClass: 'bg-[linear-gradient(135deg,#fff5d8_0%,#fffaf0_100%)]',
    borderClass: 'border-[#f0b429]/40',
    icon: ShieldCheck,
    eyebrow: 'Avaliacao operacional',
    summary: 'Prompt ativo do avaliador de satisfacao, esforco, resolucao e tentativa de prompt injection.',
  },
]

const emptyComposerState: ComposerState = {
  mode: 'create',
  sourceVersionId: null,
  sourceVersionNumber: null,
  description: '',
  template: '',
}

function toErrorMessage(error: unknown, fallback: string) {
  return error instanceof Error ? error.message : fallback
}

function formatUpdatedAt(version: PromptVersion | null) {
  if (!version) return 'Sem versao ativa'
  return `Versao ${version.version_number} ativa`
}

function activeVersionOf(entry: PromptRegistryEntry | null) {
  return entry?.versions.find((version) => version.is_active) ?? null
}

function timelineLabel(version: PromptVersion, totalVersions: number) {
  if (version.version_number === 1) {
    return totalVersions === 1 ? 'baseline ativa' : 'baseline'
  }
  return `versao ${version.version_number}`
}

function useAgentPromptRegistry(promptKey: string) {
  const [entry, setEntry] = useState<PromptRegistryEntry | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  const load = async ({ silent }: { silent?: boolean } = {}) => {
    if (!silent) {
      setIsLoading(true)
    }
    setErrorMessage(null)

    try {
      const nextEntry = await getPrompt(promptKey)
      setEntry(nextEntry)
    } catch (error) {
      setErrorMessage(toErrorMessage(error, 'Nao foi possivel carregar o prompt do agente.'))
    } finally {
      if (!silent) {
        setIsLoading(false)
      }
    }
  }

  useEffect(() => {
    setIsLoading(true)
    setErrorMessage(null)

    void getPrompt(promptKey)
      .then((nextEntry) => {
        setEntry(nextEntry)
      })
      .catch((error: unknown) => {
        setErrorMessage(toErrorMessage(error, 'Nao foi possivel carregar o prompt do agente.'))
      })
      .finally(() => {
        setIsLoading(false)
      })
  }, [promptKey])

  const clearSuccess = () => {
    setSuccessMessage(null)
  }

  const submitPrompt = async (
    input: ComposerState,
    keyForCreation: string,
  ) => {
    setErrorMessage(null)
    setSuccessMessage(null)

    try {
      const nextEntry =
        input.mode === 'create'
          ? await createPrompt({
              key: keyForCreation,
              description: input.description,
              template: input.template,
            })
          : await createPromptVersion(keyForCreation, {
              description: input.description,
              template: input.template,
            })

      setEntry(nextEntry)
      setSuccessMessage(
        input.mode === 'create'
          ? 'Prompt base criado com sucesso.'
          : `Nova versao criada a partir da V${input.sourceVersionNumber ?? 'atual'}.`,
      )
      return nextEntry
    } catch (error) {
      setErrorMessage(toErrorMessage(error, 'Nao foi possivel salvar esta versao do prompt.'))
      return null
    }
  }

  const activateVersion = async (versionId: string) => {
    setErrorMessage(null)
    setSuccessMessage(null)

    try {
      const nextEntry = await activatePromptVersion(promptKey, versionId)
      setEntry(nextEntry)
      setSuccessMessage('Versao ativa atualizada com sucesso.')
      return true
    } catch (error) {
      setErrorMessage(toErrorMessage(error, 'Nao foi possivel ativar esta versao.'))
      return false
    }
  }

  return {
    entry,
    isLoading,
    errorMessage,
    successMessage,
    clearSuccess,
    load,
    submitPrompt,
    activateVersion,
  }
}

function AgentPromptPanel({ config }: { config: AgentPromptConfig }) {
  const { entry, isLoading, errorMessage, successMessage, clearSuccess, load, submitPrompt, activateVersion } =
    useAgentPromptRegistry(config.promptKey)
  const [selectedVersionId, setSelectedVersionId] = useState<string | null>(null)
  const [composerOpen, setComposerOpen] = useState(false)
  const [composerState, setComposerState] = useState<ComposerState>(emptyComposerState)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isActivatingId, setIsActivatingId] = useState<string | null>(null)

  const activeVersion = activeVersionOf(entry)
  const selectedVersion =
    entry?.versions.find((version) => version.id === selectedVersionId) ??
    activeVersion ??
    entry?.versions[entry.versions.length - 1] ??
    null

  const openCreatePrompt = () => {
    clearSuccess()
    setComposerState(emptyComposerState)
    setComposerOpen(true)
  }

  const openCreateVersion = (version: PromptVersion | null) => {
    clearSuccess()
    setComposerState({
      mode: entry ? 'version' : 'create',
      sourceVersionId: version?.id ?? null,
      sourceVersionNumber: version?.version_number ?? null,
      description: version?.description ?? '',
      template: version?.template ?? '',
    })
    setComposerOpen(true)
  }

  const handleSubmit = async () => {
    setIsSubmitting(true)
    const nextEntry = await submitPrompt(composerState, config.promptKey)
    setIsSubmitting(false)

    if (!nextEntry) return

    const newestVersion = nextEntry.versions[nextEntry.versions.length - 1] ?? null
    if (newestVersion) {
      setSelectedVersionId(newestVersion.id)
    }

    setComposerOpen(false)
  }

  const handleActivate = async (version: PromptVersion) => {
    const confirmed = window.confirm(`Ativar a versao ${version.version_number} para ${config.label}?`)
    if (!confirmed) return

    setIsActivatingId(version.id)
    const success = await activateVersion(version.id)
    setIsActivatingId(null)

    if (success) {
      setSelectedVersionId(version.id)
    }
  }

  return (
    <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_320px]">
      <section className="flex min-h-[640px] flex-col overflow-hidden rounded-[28px] border border-black/8 bg-white shadow-[0_20px_50px_rgba(17,27,33,0.08)]">
        <div className={`border-b border-black/6 p-6 ${config.surfaceClass}`}>
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div className="min-w-0">
              <div className="flex items-center gap-3">
                <div className={`flex size-12 items-center justify-center rounded-2xl border bg-white/75 ${config.borderClass}`}>
                  <config.icon className={`size-5 ${config.accentClass}`} />
                </div>
                <div>
                  <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-[#54656f]">
                    {config.eyebrow}
                  </p>
                  <h2 className="text-2xl font-semibold tracking-tight text-[#111b21]">{config.label}</h2>
                </div>
              </div>
              <p className="mt-4 max-w-3xl text-sm leading-6 text-[#3b4a54]">{config.summary}</p>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  void load()
                }}
                className="rounded-full border-black/10 bg-white/85 px-4 text-[#111b21] hover:bg-white"
              >
                <RefreshCw className="size-4" />
                Atualizar
              </Button>
              <Button
                type="button"
                onClick={() => {
                  if (!entry) {
                    openCreatePrompt()
                    return
                  }
                  openCreateVersion(selectedVersion ?? activeVersion)
                }}
                className="rounded-full bg-[#111b21] px-4 text-white hover:bg-[#1f2c33]"
              >
                <GitBranchPlus className="size-4" />
                {entry ? 'Nova versao' : 'Criar prompt base'}
              </Button>
            </div>
          </div>
        </div>

        <div className="grid flex-1 gap-0 lg:grid-cols-[280px_minmax(0,1fr)]">
          <aside className="border-b border-black/6 bg-[#f7f8f9] p-4 lg:border-r lg:border-b-0">
            <div className="mb-4 flex items-center gap-2">
              <History className="size-4 text-[#00a884]" />
              <h3 className="text-sm font-semibold text-[#111b21]">Historico de versoes</h3>
            </div>

            {entry?.versions.length ? (
              <div className="relative pl-3">
                <div className="absolute bottom-3 left-[15px] top-3 w-px bg-[linear-gradient(180deg,#d7dfdd_0,#bccbc7_100%)]" />
                {[...entry.versions].reverse().map((version) => {
                  const isSelected = version.id === selectedVersion?.id
                  const isBaseline = version.version_number === 1
                  return (
                    <div key={version.id} className="relative pb-3 pl-6 last:pb-0">
                      <div
                        className={`absolute left-0 top-5 size-3 rounded-full border-2 ${
                          isSelected
                            ? `${config.accentBorderClass.replace('/45', '')} ${config.accentSolidClass}`
                            : version.is_active
                              ? `${config.accentBorderClass.replace('/45', '')} ${config.accentSoftClass.split(' ')[0]}`
                              : 'border-[#c3cfcc] bg-white'
                        }`}
                      />
                      <button
                        type="button"
                        onClick={() => setSelectedVersionId(version.id)}
                        className={`w-full rounded-[22px] border px-4 py-3 text-left transition ${
                          isSelected
                            ? `${config.accentBorderClass} bg-white shadow-[0_10px_24px_rgba(17,27,33,0.06)]`
                            : 'border-black/5 bg-white/75 hover:border-black/10 hover:bg-white'
                        }`}
                      >
                        <div className="flex items-start justify-between gap-3">
                          <div>
                            <div className="flex flex-wrap items-center gap-2">
                              <span className="text-sm font-semibold text-[#111b21]">V{version.version_number}</span>
                              <span className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[#7a8e8a]">
                                {timelineLabel(version, entry.versions.length)}
                              </span>
                            </div>
                            <p className="mt-2 text-xs leading-5 text-[#54656f]">{version.description}</p>
                          </div>
                          <div className="flex shrink-0 flex-col items-end gap-1">
                            {version.is_active ? (
                              <span className={`rounded-full px-2 py-0.5 text-[11px] font-semibold ${config.accentSoftClass}`}>
                                ativa
                              </span>
                            ) : null}
                            {isSelected ? (
                              <span className={`rounded-full px-2 py-0.5 text-[11px] font-semibold ${config.accentMutedClass}`}>
                                selecionada
                              </span>
                            ) : null}
                            {isBaseline ? (
                              <span className="rounded-full bg-[#f3f0e6] px-2 py-0.5 text-[11px] font-semibold text-[#7b6230]">
                                baseline
                              </span>
                            ) : null}
                          </div>
                        </div>
                      </button>
                    </div>
                  )
                })}
              </div>
            ) : isLoading ? (
              <p className="text-sm text-[#667781]">Carregando versoes...</p>
            ) : (
              <div className="rounded-2xl border border-dashed border-black/10 bg-white/70 p-4">
                <p className="text-sm font-medium text-[#111b21]">Nenhuma versao registrada.</p>
                <p className="mt-1 text-xs leading-5 text-[#667781]">
                  Crie o prompt base deste agente para liberar versionamento e ativacao.
                </p>
              </div>
            )}
          </aside>

          <div className="flex flex-1 flex-col bg-[linear-gradient(180deg,#fcfdfd_0,#f8faf9_100%)]">
            <div className="border-b border-black/6 px-5 py-4">
              <div className="grid gap-3 lg:grid-cols-[minmax(0,1fr)_280px]">
                <div className="rounded-[24px] border border-black/8 bg-white px-5 py-4 shadow-[0_8px_24px_rgba(17,27,33,0.04)]">
                  <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-[#667781]">
                    Runtime atual
                  </p>
                  <h3 className="mt-2 text-2xl font-semibold tracking-tight text-[#111b21]">
                    {activeVersion ? `V${activeVersion.version_number} em producao` : 'Prompt nao configurado'}
                  </h3>
                  <p className="mt-2 text-sm text-[#667781]">{formatUpdatedAt(activeVersion)}</p>
                </div>

                <div className={`rounded-[24px] border px-4 py-4 ${config.borderClass} ${config.surfaceClass}`}>
                  <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-[#667781]">
                    Estado operacional
                  </p>
                  <div className="mt-3 space-y-2">
                    <StatRow label="Prompt key" value={config.promptKey} />
                    <StatRow label="Versoes" value={String(entry?.versions.length ?? 0)} />
                    <StatRow label="Ativa" value={activeVersion ? `V${activeVersion.version_number}` : 'Nao definida'} />
                  </div>
                </div>
              </div>

              {activeVersion ? (
                <div className="mt-3 rounded-[22px] border border-black/8 bg-[#f7f8fa] px-4 py-3 text-sm text-[#3b4a54]">
                  <span className="font-semibold text-[#111b21]">Descricao ativa:</span> {activeVersion.description}
                </div>
              ) : null}
            </div>

            <div className="flex-1 p-5">
              {errorMessage ? (
                <Banner tone="error" icon={CircleAlert} message={errorMessage} />
              ) : null}
              {successMessage ? (
                <Banner tone="success" icon={Sparkles} message={successMessage} />
              ) : null}

              {isLoading ? (
                <div className="flex h-full min-h-[280px] items-center justify-center rounded-[24px] border border-dashed border-black/10 bg-[#fafbfb]">
                  <div className="flex items-center gap-3 text-sm text-[#667781]">
                    <RefreshCw className="size-4 animate-spin" />
                    Carregando configuracao do agente...
                  </div>
                </div>
              ) : selectedVersion ? (
                <div className="space-y-5">
                  <div className="flex flex-wrap items-center gap-3">
                    <span className="rounded-full border border-black/8 bg-white px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-[#667781]">
                      chave {entry?.key ?? config.promptKey}
                    </span>
                    <span className="rounded-full bg-[#111b21] px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-white">
                      V{selectedVersion.version_number}
                    </span>
                    {selectedVersion.is_active ? (
                      <span className={`rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] ${config.accentSoftClass}`}>
                        ativa no runtime
                      </span>
                    ) : null}
                  </div>

                  <div className="rounded-[24px] border border-black/8 bg-[#fbfcfc] p-5">
                    <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                      <div className="min-w-0">
                        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#667781]">
                          Contexto da versao
                        </p>
                        <p className="mt-2 text-sm leading-6 text-[#111b21]">{selectedVersion.description}</p>
                      </div>
                      <div className="flex flex-wrap items-center gap-2">
                        <Button
                          type="button"
                          variant="outline"
                          onClick={() => openCreateVersion(selectedVersion)}
                          className="rounded-full border-black/10 bg-white px-4 text-[#111b21] hover:bg-[#f7f8fa]"
                        >
                          <PencilLine className="size-4" />
                          Editar como nova versao
                        </Button>
                        {!selectedVersion.is_active ? (
                          <Button
                            type="button"
                            onClick={() => {
                              void handleActivate(selectedVersion)
                            }}
                            disabled={isActivatingId === selectedVersion.id}
                            className={`rounded-full px-4 text-white ${config.accentSolidClass} hover:opacity-90`}
                          >
                            <Workflow className="size-4" />
                            {isActivatingId === selectedVersion.id ? 'Ativando...' : 'Ativar versao'}
                          </Button>
                        ) : null}
                      </div>
                    </div>
                  </div>

                  <div className="rounded-[24px] border border-black/8 bg-[#111b21] p-1 shadow-[0_14px_40px_rgba(17,27,33,0.12)]">
                    <div className="rounded-[20px] bg-[linear-gradient(180deg,#16252d_0%,#0f171c_100%)] p-5">
                      <div className="mb-3 flex items-center justify-between gap-3">
                        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8fa6b2]">
                          Prompt template
                        </p>
                        <span className="text-xs text-[#8fa6b2]">
                          {selectedVersion.template.length.toLocaleString()} chars
                        </span>
                      </div>
                      <pre className="max-h-[420px] overflow-auto whitespace-pre-wrap break-words font-mono text-[13px] leading-6 text-[#e7f0f4]">
                        {selectedVersion.template}
                      </pre>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="flex h-full min-h-[280px] items-center justify-center rounded-[24px] border border-dashed border-black/10 bg-[#fafbfb] p-8 text-center">
                  <div className="max-w-md">
                    <p className="text-base font-semibold text-[#111b21]">Linha base ainda nao configurada</p>
                    <p className="mt-2 text-sm leading-6 text-[#667781]">
                      Este agente precisa de um prompt inicial para ativar o fluxo de versionamento. O baseline
                      default sera semeado no startup; se ele nao aparecer aqui, a criacao manual continua disponivel.
                    </p>
                    <Button
                      type="button"
                      onClick={openCreatePrompt}
                      className="mt-4 rounded-full bg-[#111b21] px-4 text-white hover:bg-[#1f2c33]"
                    >
                      Criar prompt base
                    </Button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      <section className="flex flex-col gap-5 xl:sticky xl:top-5 xl:self-start">
        <div className="rounded-[28px] border border-black/8 bg-white p-5 shadow-[0_20px_50px_rgba(17,27,33,0.06)]">
          <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-[#667781]">Acoes e regras</p>
          <ul className="mt-4 space-y-3 text-sm leading-6 text-[#3b4a54]">
            <li>Editar nunca sobrescreve a versao anterior; sempre gera uma nova versao a partir da selecionada.</li>
            <li>A ativacao muda o prompt usado no runtime do agente correspondente.</li>
            <li>Os prompts default funcionam como linha base operacional e podem ser substituidos por versoes novas.</li>
          </ul>
        </div>

        <div className="rounded-[28px] border border-black/8 bg-white p-5 shadow-[0_20px_50px_rgba(17,27,33,0.06)]">
          <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-[#667781]">Composer</p>
          <h3 className="mt-2 text-lg font-semibold text-[#111b21]">Abrir editor focado</h3>
          <p className="mt-3 text-sm leading-6 text-[#667781]">
            Use o editor em sobreposicao para criar baseline ou publicar uma nova versao sem disputar espaco com a leitura do runtime.
          </p>
          <Button
            type="button"
            onClick={() => {
              if (!entry) {
                openCreatePrompt()
                return
              }
              openCreateVersion(selectedVersion ?? activeVersion)
            }}
            className={`mt-4 w-full rounded-full px-4 text-white ${config.accentSolidClass} hover:opacity-90`}
          >
            {entry ? 'Abrir editor de versao' : 'Criar prompt base'}
          </Button>
        </div>
      </section>

      {composerOpen ? (
        <ComposerOverlay
          config={config}
          state={composerState}
          isSubmitting={isSubmitting}
          onClose={() => setComposerOpen(false)}
          onChange={setComposerState}
          onSubmit={() => {
            void handleSubmit()
          }}
        />
      ) : null}
    </div>
  )
}

function Banner({
  tone,
  icon: Icon,
  message,
}: {
  tone: 'error' | 'success'
  icon: typeof CircleAlert
  message: string
}) {
  const style =
    tone === 'error'
      ? 'border-red-200 bg-red-50 text-red-700'
      : 'border-[#bde5d8] bg-[#f1fff8] text-[#0b5c4b]'

  return (
    <div className={`mb-4 flex items-start gap-3 rounded-2xl border px-4 py-3 text-sm ${style}`}>
      <Icon className="mt-0.5 size-4 shrink-0" />
      <span>{message}</span>
    </div>
  )
}

function StatRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-baseline justify-between gap-3 border-b border-black/6 pb-2 last:border-b-0 last:pb-0">
      <span className="text-xs font-medium uppercase tracking-[0.16em] text-[#667781]">{label}</span>
      <span className="text-sm font-semibold text-[#111b21]">{value}</span>
    </div>
  )
}

function ComposerOverlay({
  config,
  state,
  isSubmitting,
  onClose,
  onChange,
  onSubmit,
}: {
  config: AgentPromptConfig
  state: ComposerState
  isSubmitting: boolean
  onClose: () => void
  onChange: (next: ComposerState) => void
  onSubmit: () => void
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-end bg-[#0f171c]/38 p-3 sm:p-5" onClick={onClose}>
      <div
        className="flex h-full w-full max-w-[860px] flex-col overflow-hidden rounded-[32px] border border-[#17343b]/10 bg-white shadow-[0_28px_80px_rgba(17,27,33,0.22)]"
        onClick={(event) => event.stopPropagation()}
      >
        <div className={`border-b border-black/6 px-6 py-5 ${config.surfaceClass}`}>
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-[#667781]">
                {state.mode === 'create' ? 'Prompt base' : 'Nova versao'}
              </p>
              <h3 className="mt-1 text-2xl font-semibold text-[#111b21]">
                {state.mode === 'create'
                  ? `Criar baseline de ${config.shortLabel}`
                  : `Versionar prompt de ${config.shortLabel}`}
              </h3>
            </div>
            <Button
              type="button"
              variant="ghost"
              onClick={onClose}
              className="rounded-full border border-black/8 px-4 text-[#667781] hover:bg-white/75"
            >
              Fechar
            </Button>
          </div>
        </div>

        <div className="flex-1 overflow-auto px-6 py-5">
          {state.mode === 'version' && state.sourceVersionNumber ? (
            <div className={`rounded-2xl border px-4 py-3 text-sm ${config.accentBorderClass} ${config.accentSoftClass}`}>
              Nova versao baseada na V{state.sourceVersionNumber}. A versao anterior continua preservada.
            </div>
          ) : null}

          <div className="mt-5 grid gap-5 lg:grid-cols-[280px_minmax(0,1fr)]">
              <div className={`rounded-[24px] border p-4 ${config.borderClass} ${config.surfaceClass}`}>
              <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-[#667781]">Modo do editor</p>
              <div className="mt-4 space-y-3 text-sm leading-6 text-[#3b4a54]">
                <p>
                  {state.mode === 'create'
                    ? 'Crie a linha base inicial deste agente diretamente a partir do registry.'
                    : 'Revise a versao selecionada, ajuste o texto e publique uma nova iteracao versionada.'}
                </p>
                <p>Nenhuma versao historica sera sobrescrita.</p>
              </div>
            </div>

            <div className="space-y-4">
              <label className="block">
                <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.18em] text-[#667781]">
                  Descricao da versao
                </span>
                <input
                  value={state.description}
                  onChange={(event) => onChange({ ...state, description: event.target.value })}
                  placeholder="Ex: reforca discovery antes de recomendar inscricao"
                  className={`h-12 w-full rounded-2xl border border-black/10 bg-[#f7f8fa] px-4 text-sm text-[#111b21] outline-none transition focus:bg-white ${config.accentBorderClass}`}
                />
              </label>

              <label className="block">
                <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.18em] text-[#667781]">
                  Template do prompt
                </span>
                <textarea
                  value={state.template}
                  onChange={(event) => onChange({ ...state, template: event.target.value })}
                  placeholder="Escreva o prompt completo desta versao."
                  className={`min-h-[420px] w-full rounded-[24px] border border-black/10 bg-[#111b21] px-4 py-4 font-mono text-[13px] leading-6 text-[#ecf4f7] outline-none transition ${config.accentBorderClass}`}
                />
              </label>
            </div>
          </div>
        </div>

        <div className="flex flex-wrap items-center justify-between gap-3 border-t border-black/6 px-6 py-4">
          <p className="text-xs text-[#667781]">
            A submissao salva uma nova linha de base versionada e nao altera textos historicos.
          </p>
          <Button
            type="button"
            onClick={onSubmit}
            disabled={isSubmitting || !state.description.trim() || !state.template.trim()}
            className={`rounded-full px-4 text-white ${config.accentSolidClass} hover:opacity-90`}
          >
            {isSubmitting ? 'Salvando...' : state.mode === 'create' ? 'Criar prompt' : 'Salvar nova versao'}
          </Button>
        </div>
      </div>
    </div>
  )
}

export function LLMOpsPage() {
  const [activeAgentId, setActiveAgentId] = useState<AgentPromptConfig['id']>('chat')
  const activeConfig = agentConfigs.find((config) => config.id === activeAgentId) ?? agentConfigs[0]

  return (
    <section className="min-h-0 flex-1 overflow-auto bg-[radial-gradient(circle_at_top_left,#f6fffb_0,#eef3f2_42%,#e7ecef_100%)] px-4 py-5 sm:px-5 lg:px-6">
      <div className="mx-auto flex w-full max-w-[1520px] flex-col gap-5">
        <div className="flex flex-wrap gap-3">
          {agentConfigs.map((config) => {
            const Icon = config.icon
            const isActive = config.id === activeAgentId
            return (
              <button
                key={config.id}
                type="button"
                onClick={() => setActiveAgentId(config.id)}
                className={`group rounded-[24px] border px-5 py-4 text-left transition ${
                  isActive
                    ? `${config.borderClass} ${config.surfaceClass} shadow-[0_16px_40px_rgba(17,27,33,0.08)]`
                    : 'border-black/8 bg-white hover:border-black/12 hover:bg-[#f9fbfb]'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className={`flex size-11 items-center justify-center rounded-2xl border bg-white ${isActive ? config.borderClass : 'border-black/8'}`}>
                    <Icon className={`size-5 ${isActive ? config.accentClass : 'text-[#667781]'}`} />
                  </div>
                  <div>
                    <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-[#667781]">
                      {config.eyebrow}
                    </p>
                    <p className="text-base font-semibold text-[#111b21]">{config.label}</p>
                  </div>
                </div>
              </button>
            )
          })}
        </div>

        <AgentPromptPanel config={activeConfig} />
      </div>
    </section>
  )
}
