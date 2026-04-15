import { BookOpen, ChartColumn, ChevronDown, KeyRound, MessageSquare, Plus, Sparkles, Wallet, Workflow } from 'lucide-react'

import { Button } from '@/components/ui/button'
import type { ModelOption } from '@/lib/chat-ui'

export type AppPage = 'chat' | 'metrics' | 'llmops' | 'docs'

const operationalRoutes: { label: string; icon: typeof ChartColumn; page: AppPage }[] = [
  { label: 'Chat', icon: MessageSquare, page: 'chat' },
  { label: 'Metrics', icon: ChartColumn, page: 'metrics' },
  { label: 'LLMOps', icon: Workflow, page: 'llmops' },
]

const referenceRoutes: { label: string; icon: typeof ChartColumn; page: AppPage }[] = [
  { label: 'Solution Docs', icon: BookOpen, page: 'docs' },
]

type AppToolbarProps = {
  modelMenuOpen: boolean
  modelOptions: ModelOption[]
  activeModel: ModelOption
  isBootstrapping: boolean
  isCreatingThread: boolean
  credits: number | null
  apiKey: string
  activePage: AppPage
  onToggleModelMenu: () => void
  onSelectModel: (modelId: string) => void
  onCreateThread: () => void
  onOpenApiKeyModal: () => void
  onNavigateTo: (page: AppPage) => void
}

export function AppToolbar({
  modelMenuOpen,
  modelOptions,
  activeModel,
  isBootstrapping,
  isCreatingThread,
  credits,
  apiKey,
  activePage,
  onToggleModelMenu,
  onSelectModel,
  onCreateThread,
  onOpenApiKeyModal,
  onNavigateTo,
}: AppToolbarProps) {
  return (
    <header className="border-b border-black/8 bg-[#f7f8fa] px-4 py-3 sm:px-5">
      <div className="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
        <div className="flex flex-wrap items-center gap-2">
          <div className="relative">
            <button
              type="button"
              onClick={onToggleModelMenu}
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
                    onClick={() => onSelectModel(model.id)}
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
            onClick={onCreateThread}
            disabled={isBootstrapping || isCreatingThread}
            aria-label="Nova conversa"
            className="rounded-full border-black/8 bg-white text-[#111b21] hover:bg-[#f5f6f6]"
          >
            <Plus className="size-4" />
          </Button>
        </div>

        <div className="min-w-0 flex-1 xl:px-5">
          <div className="rounded-[20px] border border-black/6 bg-white px-3 py-1.5">
            <div className="flex flex-wrap items-center gap-x-3 gap-y-1.5">
              <span className="text-[11px] font-medium uppercase tracking-[0.18em] text-[#667781]">
                active assistant
              </span>
              <span className="text-sm font-semibold text-[#111b21]">{activeModel.label}</span>
              <span className="inline-flex items-center gap-1 rounded-full bg-[#d9fdd3] px-2.5 py-1 text-xs font-medium text-[#0b5c4b]">
                <Wallet className="size-3.5" />
                {credits === null ? (apiKey ? 'Carregando...' : 'Sem chave') : `${credits} credits`}
              </span>
              <button
                type="button"
                onClick={onOpenApiKeyModal}
                className="inline-flex items-center gap-2 rounded-full border border-black/8 bg-[#f7f8fa] px-3 py-1.5 text-xs text-[#667781] transition hover:bg-[#eef1f3]"
              >
                <KeyRound className="size-3.5 text-[#00a884]" />
                <span>API key</span>
                <span className="text-[#111b21]">{apiKey ? 'Chave salva' : 'Adicionar chave'}</span>
              </button>
            </div>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <div className="flex flex-wrap items-center gap-2 rounded-full border border-[#00a884]/18 bg-[#f3f7f6] px-2 py-2">
            <span className="px-2 text-[11px] font-semibold uppercase tracking-[0.2em] text-[#667781]">
              Operate
            </span>
            {operationalRoutes.map(({ label, icon: Icon, page }) => (
              <Button
                key={label}
                type="button"
                variant="ghost"
                onClick={() => onNavigateTo(page)}
                className={`rounded-full border px-3.5 text-sm font-medium transition ${
                  activePage === page
                    ? 'border-[#00a884] bg-[#00a884] text-white hover:bg-[#009977]'
                    : 'border-[#00a884]/36 bg-white text-[#00a884] hover:bg-[#f0fdf9] hover:border-[#00a884]/70'
                }`}
              >
                <Icon className="size-4" />
                {label}
              </Button>
            ))}
          </div>

          <div className="flex flex-wrap items-center gap-2 rounded-full border border-black/8 bg-white px-2 py-2">
            <span className="px-2 text-[11px] font-semibold uppercase tracking-[0.2em] text-[#667781]">
              Reference
            </span>
            {referenceRoutes.map(({ label, icon: Icon, page }) => (
              <Button
                key={label}
                type="button"
                variant="ghost"
                onClick={() => onNavigateTo(page)}
                className={`rounded-full border px-3.5 text-sm font-medium transition ${
                  activePage === page
                    ? 'border-[#17343b] bg-[#17343b] text-white hover:bg-[#1d444d]'
                    : 'border-black/8 bg-white text-[#54656f] hover:bg-[#f5f7f7] hover:border-black/12'
                }`}
              >
                <Icon className="size-4" />
                {label}
              </Button>
            ))}
          </div>
        </div>
      </div>
    </header>
  )
}
