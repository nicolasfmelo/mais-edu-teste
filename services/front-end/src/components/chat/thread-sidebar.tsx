import { Search } from 'lucide-react'
import { buildThreadInitials, type Thread } from '@/lib/chat-ui'

type ThreadSidebarProps = {
  threads: Thread[]
  activeThreadId: string | null
  isBootstrapping: boolean
  onSelectThread: (threadId: string) => void
}

export function ThreadSidebar({
  threads,
  activeThreadId,
  isBootstrapping,
  onSelectThread,
}: ThreadSidebarProps) {
  return (
    <aside className="flex min-h-0 flex-col border-b border-black/8 bg-white lg:border-r lg:border-b-0">
      <div className="flex items-center justify-between bg-[#f0f2f5] px-4 py-3">
        <div className="flex size-10 items-center justify-center rounded-full bg-[#dfe5e7] text-sm font-semibold text-[#111b21]">
          TE
        </div>
        <span className="text-xs font-medium uppercase tracking-[0.14em] text-[#667781]">Conversas</span>
      </div>

      <div className="border-b border-black/6 bg-[#f0f2f5] px-3 py-3">
        <div className="flex items-center gap-3 rounded-lg bg-white px-3 py-2 text-sm text-[#667781]">
          <Search className="size-4" />
          Search or start a new chat
        </div>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto bg-white">
        {isBootstrapping && threads.length === 0 ? (
          <div className="px-4 py-6 text-sm text-[#667781]">Carregando conversas...</div>
        ) : threads.length === 0 ? (
          <div className="px-4 py-6 text-sm text-[#667781]">Nenhuma conversa encontrada.</div>
        ) : (
          threads.map((thread) => {
            const selected = thread.id === activeThreadId

            return (
              <button
                key={thread.id}
                type="button"
                onClick={() => onSelectThread(thread.id)}
                className={`flex w-full items-start gap-3 border-b border-black/6 px-3 py-3 text-left transition ${
                  selected ? 'bg-[#f0f2f5]' : 'hover:bg-[#f5f6f6]'
                }`}
              >
                <div
                  className={`flex size-12 shrink-0 items-center justify-center rounded-full text-sm font-semibold ${
                    selected ? 'bg-[#d9fdd3] text-[#0b5c4b]' : 'bg-[#dfe5e7] text-[#111b21]'
                  }`}
                >
                  {buildThreadInitials(thread.name)}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-start justify-between gap-3">
                    <p className="truncate text-sm font-medium text-[#111b21]">{thread.name}</p>
                    <span className="shrink-0 text-[11px] text-[#667781]">{thread.time}</span>
                  </div>
                  <div className="mt-1 flex items-center gap-2">
                    <p className="line-clamp-1 min-w-0 flex-1 text-sm text-[#667781]">{thread.preview}</p>
                    {thread.unread > 0 ? (
                      <span className="inline-flex min-w-5 items-center justify-center rounded-full bg-[#25d366] px-1.5 py-0.5 text-[11px] font-semibold text-white">
                        {thread.unread}
                      </span>
                    ) : null}
                  </div>
                </div>
              </button>
            )
          })
        )}
      </div>
    </aside>
  )
}
