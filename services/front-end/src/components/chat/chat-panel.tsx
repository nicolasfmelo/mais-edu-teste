import type { KeyboardEventHandler, RefObject } from 'react'

import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { CheckCheck, CircleAlert, MoreVertical, Search, SendHorizontal } from 'lucide-react'

import { Button } from '@/components/ui/button'
import type { Message } from '@/lib/chat-ui'

type ChatPanelProps = {
  activeThreadInitials: string
  activeThreadName: string
  activeModelLabel: string
  infoBannerMessage: string
  errorMessage: string | null
  chatScrollRef: RefObject<HTMLDivElement | null>
  onChatScroll: () => void
  isLoadingThread: boolean
  activeMessages: Message[]
  draft: string
  onDraftChange: (value: string) => void
  onDraftKeyDown: KeyboardEventHandler<HTMLTextAreaElement>
  isBootstrapping: boolean
  isSending: boolean
  hasActiveThread: boolean
  onSend: () => void
  composerDisabled: boolean
}

export function ChatPanel({
  activeThreadInitials,
  activeThreadName,
  activeModelLabel,
  infoBannerMessage,
  errorMessage,
  chatScrollRef,
  onChatScroll,
  isLoadingThread,
  activeMessages,
  draft,
  onDraftChange,
  onDraftKeyDown,
  isBootstrapping,
  isSending,
  hasActiveThread,
  onSend,
  composerDisabled,
}: ChatPanelProps) {
  return (
    <div className="flex min-h-0 flex-col bg-[#efeae2]">
      <div className="border-b border-black/8 bg-[#f0f2f5] px-4 py-3">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-full bg-[#dfe5e7] text-sm font-semibold text-[#111b21]">
              {activeThreadInitials}
            </div>
            <div>
              <p className="text-sm font-semibold text-[#111b21]">{activeThreadName}</p>
              <p className="text-xs text-[#667781]">{activeModelLabel}</p>
            </div>
          </div>

          <div className="flex items-center gap-2 text-[#54656f]">
            <Button type="button" variant="ghost" size="icon-sm" className="rounded-full hover:bg-black/5">
              <Search className="size-4" />
            </Button>
            <Button type="button" variant="ghost" size="icon-sm" className="rounded-full hover:bg-black/5">
              <MoreVertical className="size-4" />
            </Button>
          </div>
        </div>
      </div>

      <div className="border-b border-black/6 bg-[#fff3c4] px-4 py-2 text-center text-[12px] text-[#54656f]">
        <div className="inline-flex animate-in items-center gap-2 fade-in duration-300">
          <CircleAlert className="size-3.5 text-[#667781]" />
          {infoBannerMessage}
        </div>
      </div>

      {errorMessage ? (
        <div className="border-b border-[#f1b8b5] bg-[#fdecea] px-4 py-2 text-center text-[12px] text-[#8a1c17]">
          {errorMessage}
        </div>
      ) : null}

      <div
        ref={chatScrollRef}
        onScroll={onChatScroll}
        className="min-h-0 flex-1 overflow-y-auto scroll-smooth bg-[#efeae2] bg-[radial-gradient(rgba(255,255,255,0.32)_1px,transparent_1px)] bg-[length:24px_24px] px-4 py-4 sm:px-8"
      >
        <div className="mx-auto flex min-h-full max-w-4xl flex-col justify-end gap-3">
          <div className="mx-auto rounded-md bg-[#e1f2fb] px-2.5 py-1 text-[11px] font-medium uppercase text-[#54656f] shadow-sm">
            Today
          </div>

          {isLoadingThread ? <div className="mx-auto text-sm text-[#667781]">Carregando mensagens...</div> : null}

          {!isLoadingThread && activeMessages.length === 0 ? (
            <div className="mx-auto rounded-2xl bg-white/80 px-4 py-3 text-sm text-[#54656f] shadow-sm">
              Nenhuma mensagem ainda. Envie a primeira para iniciar a conversa.
            </div>
          ) : null}

          {activeMessages.map((message) => {
            const isUser = message.role === 'user'

            return (
              <article key={message.id} className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
                <div
                  className={`max-w-[32rem] rounded-lg px-3 py-2 shadow-[0_1px_0_rgba(17,27,33,0.08)] ${
                    isUser ? 'bg-[#d9fdd3] text-[#111b21]' : 'bg-white text-[#111b21]'
                  }`}
                >
                  <div className="prose prose-sm max-w-none text-[14px] leading-6 text-[#111b21] [&_a]:text-[#009de2] [&_a]:underline [&_blockquote]:border-l-2 [&_blockquote]:border-[#667781] [&_blockquote]:pl-3 [&_blockquote]:text-[#54656f] [&_blockquote]:italic [&_code]:rounded [&_code]:bg-black/8 [&_code]:px-1 [&_code]:py-0.5 [&_code]:font-mono [&_code]:text-[13px] [&_hr]:border-black/10 [&_li]:my-0.5 [&_ol]:my-1.5 [&_ol]:list-decimal [&_ol]:pl-5 [&_pre]:my-2 [&_pre]:overflow-x-auto [&_pre]:rounded-md [&_pre]:bg-black/8 [&_pre]:p-3 [&_pre_code]:bg-transparent [&_pre_code]:p-0 [&_strong]:font-semibold [&_table]:w-full [&_table]:border-collapse [&_td]:border [&_td]:border-black/10 [&_td]:px-2 [&_td]:py-1 [&_th]:border [&_th]:border-black/10 [&_th]:px-2 [&_th]:py-1 [&_th]:font-semibold [&_ul]:my-1.5 [&_ul]:list-disc [&_ul]:pl-5">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
                  </div>
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
              onChange={(event) => onDraftChange(event.target.value)}
              onKeyDown={onDraftKeyDown}
              placeholder="Type a message"
              className="min-h-10 flex-1 resize-none bg-transparent py-3 text-sm text-[#111b21] outline-none placeholder:text-[#8696a0]"
              autoComplete="off"
              disabled={isBootstrapping || isSending || !hasActiveThread}
            />
          </div>

          <Button
            type="button"
            onClick={onSend}
            disabled={composerDisabled}
            className="size-11 rounded-full bg-[#00a884] text-white hover:bg-[#0dc39a]"
          >
            <SendHorizontal className="size-5" />
          </Button>
        </div>
      </div>
    </div>
  )
}
