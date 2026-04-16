import { lazy, Suspense, useState } from 'react'
import { ApiKeyModal } from '@/components/chat/api-key-modal'
import { AppToolbar, type AppPage } from '@/components/chat/app-toolbar'
import { ChatPanel } from '@/components/chat/chat-panel'
import { ThreadSidebar } from '@/components/chat/thread-sidebar'
import { useChatWorkspace } from '@/hooks/use-chat-workspace'
import { cn } from '@/lib/utils'

const DocsPage = lazy(async () => {
  const module = await import('@/components/docs/docs-page')
  return { default: module.DocsPage }
})

const LLMOpsPage = lazy(async () => {
  const module = await import('@/components/llmops/llmops-page')
  return { default: module.LLMOpsPage }
})

const MetricsPage = lazy(async () => {
  const module = await import('@/components/metrics/metrics-page')
  return { default: module.MetricsPage }
})

function App() {
  const workspace = useChatWorkspace()
  const [activePage, setActivePage] = useState<AppPage>('chat')
  const isWorkspacePage = activePage === 'chat'
  const isLlMOpsPage = activePage === 'llmops'

  return (
    <main
      className={cn(
        'dark h-screen overflow-hidden px-3 py-5 text-foreground sm:px-5 lg:px-8',
        isWorkspacePage
          ? 'bg-[linear-gradient(180deg,#00a884_0,#00a884_152px,#e9edef_152px,#d1d7db_100%)]'
          : isLlMOpsPage
            ? 'bg-[linear-gradient(180deg,#dfe9e6_0,#eef3f1_32%,#f5f7f6_100%)]'
            : 'bg-[linear-gradient(180deg,#eef2f1_0,#f4f6f5_36%,#e5eaeb_100%)]',
      )}
    >
      <div
        className={cn(
          'mx-auto flex h-[calc(100svh-2.5rem)] w-full max-w-[1480px] flex-col overflow-hidden',
          isWorkspacePage
            ? 'rounded-[18px] border border-black/8 bg-[#f0f2f5] shadow-[0_8px_24px_rgba(17,27,33,0.16)]'
            : isLlMOpsPage
              ? 'rounded-[26px] border border-[#17343b]/10 bg-[#f3f6f5] shadow-[0_22px_60px_rgba(18,35,38,0.10)]'
              : 'rounded-[22px] border border-black/6 bg-[#f6f8f8] shadow-[0_12px_34px_rgba(17,27,33,0.08)]',
        )}
      >
        <AppToolbar
          modelMenuOpen={workspace.modelMenuOpen}
          modelOptions={workspace.modelOptions}
          activeModel={workspace.activeModel}
          isBootstrapping={workspace.isBootstrapping}
          isCreatingThread={workspace.isCreatingThread}
          credits={workspace.credits}
          creditsStatus={workspace.creditsStatus}
          apiKey={workspace.apiKey}
          activePage={activePage}
          onToggleModelMenu={workspace.toggleModelMenu}
          onSelectModel={workspace.selectModel}
          onCreateThread={() => {
            void workspace.createThread()
          }}
          onOpenApiKeyModal={workspace.openApiKeyModal}
          onNavigateTo={setActivePage}
        />

        {activePage === 'metrics' ? (
          <Suspense fallback={<PageLoadingState label="Carregando métricas" />}>
            <MetricsPage apiKey={workspace.apiKey} />
          </Suspense>
        ) : activePage === 'llmops' ? (
          <Suspense fallback={<PageLoadingState label="Carregando LLMOps" tone="llmops" />}>
            <LLMOpsPage />
          </Suspense>
        ) : activePage === 'docs' ? (
          <Suspense fallback={<PageLoadingState label="Carregando documentação" />}>
            <DocsPage />
          </Suspense>
        ) : (
          <section className="grid min-h-0 flex-1 grid-cols-1 lg:grid-cols-[340px_minmax(0,1fr)]">
            <ThreadSidebar
              threads={workspace.threads}
              activeThreadId={workspace.activeThreadId}
              isBootstrapping={workspace.isBootstrapping}
              onSelectThread={workspace.selectThread}
            />
            <ChatPanel
              activeThreadInitials={workspace.activeThreadInitials}
              activeThreadName={workspace.activeThreadName}
              activeModelLabel={workspace.activeModel.label}
              infoBannerMessage={workspace.infoBannerMessage}
              errorMessage={workspace.errorMessage}
              chatScrollRef={workspace.chatScrollRef}
              onChatScroll={workspace.handleChatScroll}
              isLoadingThread={workspace.isLoadingThread}
              activeMessages={workspace.activeMessages}
              isBootstrapping={workspace.isBootstrapping}
              isSending={workspace.isSending}
              hasActiveThread={Boolean(workspace.activeThreadId)}
              credits={workspace.credits}
              onSend={(content) => {
                void workspace.sendMessage(content)
              }}
              onSendAudio={(audio) => {
                void workspace.sendAudioMessage(audio)
              }}
            />
          </section>
        )}
      </div>

      {workspace.apiKeyModalOpen ? (
        <ApiKeyModal
          apiKey={workspace.apiKeyDraft}
          onChangeApiKey={workspace.setApiKeyDraft}
          onSave={workspace.saveApiKey}
          onClose={workspace.closeApiKeyModal}
        />
      ) : null}
    </main>
  )
}

function PageLoadingState({
  label,
  tone = 'default',
}: {
  label: string
  tone?: 'default' | 'llmops'
}) {
  return (
    <section
      className={cn(
        'flex min-h-0 flex-1 items-center justify-center',
        tone === 'llmops' ? 'bg-[linear-gradient(180deg,#eef3f1_0,#f6f8f7_100%)]' : 'bg-[#f0f2f5]',
      )}
    >
      <div
        className={cn(
          'rounded-2xl px-5 py-4 text-sm font-medium shadow-sm',
          tone === 'llmops'
            ? 'border border-[#17343b]/10 bg-white text-[#32525a]'
            : 'border border-black/6 bg-white text-[#667781]',
        )}
      >
        {label}...
      </div>
    </section>
  )
}

export default App
