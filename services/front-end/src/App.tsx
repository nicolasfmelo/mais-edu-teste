import { useState } from 'react'
import { ApiKeyModal } from '@/components/chat/api-key-modal'
import { AppToolbar, type AppPage } from '@/components/chat/app-toolbar'
import { ChatPanel } from '@/components/chat/chat-panel'
import { ThreadSidebar } from '@/components/chat/thread-sidebar'
import { DocsPage } from '@/components/docs/docs-page'
import { LLMOpsPage } from '@/components/llmops/llmops-page'
import { MetricsPage } from '@/components/metrics/metrics-page'
import { useChatWorkspace } from '@/hooks/use-chat-workspace'

function App() {
  const workspace = useChatWorkspace()
  const [activePage, setActivePage] = useState<AppPage>('chat')

  return (
    <main className="dark h-screen overflow-hidden bg-[linear-gradient(180deg,#00a884_0,#00a884_152px,#e9edef_152px,#d1d7db_100%)] px-3 py-5 text-foreground sm:px-5 lg:px-8">
      <div className="mx-auto flex h-[calc(100svh-2.5rem)] w-full max-w-[1480px] flex-col overflow-hidden rounded-[18px] border border-black/8 bg-[#f0f2f5] shadow-[0_8px_24px_rgba(17,27,33,0.16)]">
        <AppToolbar
          modelMenuOpen={workspace.modelMenuOpen}
          modelOptions={workspace.modelOptions}
          activeModel={workspace.activeModel}
          isBootstrapping={workspace.isBootstrapping}
          isCreatingThread={workspace.isCreatingThread}
          credits={workspace.credits}
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
          <MetricsPage apiKey={workspace.apiKey} />
        ) : activePage === 'llmops' ? (
          <LLMOpsPage />
        ) : activePage === 'docs' ? (
          <DocsPage />
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
            />
          </section>
        )}
      </div>

      {workspace.apiKeyModalOpen ? (
        <ApiKeyModal
          apiKey={workspace.apiKey}
          onChangeApiKey={workspace.setApiKey}
          onClose={workspace.closeApiKeyModal}
        />
      ) : null}
    </main>
  )
}

export default App
