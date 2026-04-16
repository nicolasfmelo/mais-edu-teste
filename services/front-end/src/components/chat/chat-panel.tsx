import { memo, useState, type KeyboardEvent, type RefObject } from 'react'

import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { CheckCheck, CircleAlert, LoaderCircle, Mic, SendHorizontal, Trash2 } from 'lucide-react'

import { useAudioRecorder } from '@/components/chat/use-audio-recorder'
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
  isBootstrapping: boolean
  isSending: boolean
  hasActiveThread: boolean
  credits: number | null
  onSend: (content: string) => void
  onSendAudio: (audio: File) => void
}

type MessageComposerProps = {
  isBootstrapping: boolean
  isSending: boolean
  hasActiveThread: boolean
  credits: number | null
  onSend: (content: string) => void
  onSendAudio: (audio: File) => void
}

type RecordingErrorBannerProps = {
  message: string | null
}

function RecordingErrorBanner({ message }: RecordingErrorBannerProps) {
  if (!message) {
    return null
  }

  return (
    <div className="mx-auto mb-2 max-w-4xl rounded-lg border border-[#f1b8b5] bg-[#fdecea] px-3 py-2 text-xs text-[#8a1c17]">
      {message}
    </div>
  )
}

function formatRecordingDuration(totalSeconds: number) {
  const minutes = Math.floor(totalSeconds / 60)
  const seconds = totalSeconds % 60

  return `${minutes}:${seconds.toString().padStart(2, '0')}`
}

type RecordingComposerProps = {
  durationSeconds: number
  canDiscard: boolean
  onDiscard: () => void
}

function RecordingComposer({ durationSeconds, canDiscard, onDiscard }: RecordingComposerProps) {
  const bars = [10, 16, 28, 20, 12, 24, 18, 11, 22, 15, 26, 14]

  return (
    <div className="flex min-h-14 flex-1 items-center rounded-lg bg-[#0b141a] px-3 text-white shadow-[inset_0_0_0_1px_rgba(255,255,255,0.04)]">
      <button
        type="button"
        onClick={onDiscard}
        disabled={!canDiscard}
        aria-label="Descartar gravação"
        className="inline-flex size-9 items-center justify-center rounded-full text-[#aebac1] transition hover:bg-white/8 hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
      >
        <Trash2 className="size-5" />
      </button>

      <span className="ml-2 min-w-18 text-3xl font-light tabular-nums text-[#f5f8fa]">
        {formatRecordingDuration(durationSeconds)}
      </span>

      <div className="ml-4 flex flex-1 items-center justify-center gap-1.5">
        {bars.map((height, index) => (
          <span
            key={`${height}-${index}`}
            className="w-1.5 rounded-full bg-[#aebac1]/90 animate-pulse"
            style={{ height: `${height}px`, animationDelay: `${index * 120}ms` }}
          />
        ))}
      </div>

      <span className="ml-3 text-[11px] font-medium tracking-[0.2em] text-[#8ca2b0]">REC</span>
    </div>
  )
}

type MainActionButtonProps = {
  isSending: boolean
  isRecording: boolean
  hasDraft: boolean
  isFinalizingRecording: boolean
  disabled: boolean
  onClick: () => void
}

function MainActionButton({
  isSending,
  isRecording,
  hasDraft,
  isFinalizingRecording,
  disabled,
  onClick,
}: MainActionButtonProps) {
  const shouldShowLoader = isSending || isFinalizingRecording

  const ariaLabel = isRecording
    ? 'Parar gravação e enviar áudio'
    : hasDraft
      ? 'Enviar mensagem'
      : 'Iniciar gravação de áudio'

  return (
    <Button
      type="button"
      onClick={onClick}
      disabled={disabled}
      aria-label={ariaLabel}
      className="size-11 rounded-full bg-[#00a884] text-white hover:bg-[#0dc39a] disabled:bg-[#9abcb4]"
    >
      {shouldShowLoader ? (
        <LoaderCircle className="size-5 animate-spin" />
      ) : hasDraft || isRecording ? (
        <SendHorizontal className="size-5" />
      ) : (
        <Mic className="size-5" />
      )}
    </Button>
  )
}

const MessageComposer = memo(function MessageComposer({
  isBootstrapping,
  isSending,
  hasActiveThread,
  credits,
  onSend,
  onSendAudio,
}: MessageComposerProps) {
  const [draft, setDraft] = useState('')
  const [isFinalizingRecording, setIsFinalizingRecording] = useState(false)

  const {
    isRecording,
    recordingError,
    recordingDurationSeconds,
    startRecording,
    stopRecordingAndGetFile,
    discardRecording,
    clearAudioFile,
  } = useAudioRecorder()

  const isInteractionLocked = [!hasActiveThread, isBootstrapping, isSending].some(Boolean)
  const canSpendCredits = credits !== 0
  const trimmedDraft = draft.trim()
  const hasDraft = Boolean(trimmedDraft)

  const canSendText = hasDraft && !isInteractionLocked && canSpendCredits
  const canStartRecording = !isInteractionLocked && !isRecording && !hasDraft && canSpendCredits && !isFinalizingRecording
  const canStopAndSendRecording = isRecording && !isBootstrapping && hasActiveThread && canSpendCredits && !isFinalizingRecording
  const canDiscardRecording = isRecording && !isFinalizingRecording

  const isMainActionDisabled = isRecording ? !canStopAndSendRecording : hasDraft ? !canSendText : !canStartRecording

  const handleMainAction = async () => {
    if (isRecording) {
      if (!canStopAndSendRecording) {
        return
      }

      setIsFinalizingRecording(true)

      try {
        const recordedFile = await stopRecordingAndGetFile()
        if (!recordedFile) {
          return
        }

        clearAudioFile()
        setDraft('')
        onSendAudio(recordedFile)
      } finally {
        setIsFinalizingRecording(false)
      }

      return
    }

    if (hasDraft) {
      if (!canSendText) {
        return
      }

      setDraft('')
      clearAudioFile()
      onSend(trimmedDraft)
      return
    }

    if (!canStartRecording) {
      return
    }

    await startRecording()
  }

  const handleDiscardRecording = () => {
    discardRecording()
    setIsFinalizingRecording(false)
  }

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      void handleMainAction()
    }
  }

  return (
    <div className="border-t border-black/8 bg-[#f0f2f5] px-4 py-3">
      <RecordingErrorBanner message={recordingError} />

      <div className="mx-auto flex max-w-4xl items-end gap-3">
        {isRecording ? (
          <RecordingComposer
            durationSeconds={recordingDurationSeconds}
            canDiscard={canDiscardRecording}
            onDiscard={handleDiscardRecording}
          />
        ) : (
          <div className="flex min-h-14 flex-1 items-center rounded-lg bg-white px-3">
            <textarea
              id="chat-message-input"
              name="message"
              aria-label="Mensagem do chat"
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type a message"
              className="min-h-10 flex-1 resize-none bg-transparent py-3 text-sm text-[#111b21] outline-none placeholder:text-[#8696a0]"
              autoComplete="off"
              disabled={isInteractionLocked || isFinalizingRecording}
            />
          </div>
        )}

        <MainActionButton
          isSending={isSending}
          isRecording={isRecording}
          hasDraft={hasDraft}
          isFinalizingRecording={isFinalizingRecording}
          disabled={isMainActionDisabled}
          onClick={() => void handleMainAction()}
        />
      </div>
    </div>
  )
})

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
  isBootstrapping,
  isSending,
  hasActiveThread,
  credits,
  onSend,
  onSendAudio,
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

          {isSending ? (
            <div className="inline-flex items-center gap-2 rounded-full bg-white px-3 py-1 text-xs font-medium text-[#54656f] shadow-sm">
              <LoaderCircle className="size-3.5 animate-spin" />
              Clara está respondendo
            </div>
          ) : null}
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

      <MessageComposer
        isBootstrapping={isBootstrapping}
        isSending={isSending}
        hasActiveThread={hasActiveThread}
        credits={credits}
        onSend={onSend}
        onSendAudio={onSendAudio}
      />
    </div>
  )
}
