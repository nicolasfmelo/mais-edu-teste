import { useEffect, type Dispatch, type MutableRefObject, type SetStateAction } from 'react'

import { infoBannerMessages } from '@/lib/chat-ui'

type SetState<T> = Dispatch<SetStateAction<T>>

export function scrollChatToBottom(
  chatScrollRef: MutableRefObject<HTMLDivElement | null>,
  behavior: ScrollBehavior = 'smooth',
) {
  const container = chatScrollRef.current
  if (!container) {
    return
  }

  container.scrollTo({
    top: container.scrollHeight,
    behavior,
  })
}

export function syncAutoScrollPreference(
  chatScrollRef: MutableRefObject<HTMLDivElement | null>,
  shouldAutoScrollRef: MutableRefObject<boolean>,
) {
  const container = chatScrollRef.current
  if (!container) {
    return
  }

  const distanceFromBottom = container.scrollHeight - container.scrollTop - container.clientHeight
  shouldAutoScrollRef.current = distanceFromBottom < 72
}

export function useInfoBannerRotation(setInfoBannerIndex: SetState<number>) {
  useEffect(() => {
    const intervalId = window.setInterval(() => {
      setInfoBannerIndex((current) => (current + 1) % infoBannerMessages.length)
    }, 5000)

    return () => window.clearInterval(intervalId)
  }, [setInfoBannerIndex])
}

export function useChatAutoScroll(params: {
  activeThreadId: string | null
  activeMessageCount: number
  chatScrollRef: MutableRefObject<HTMLDivElement | null>
  shouldAutoScrollRef: MutableRefObject<boolean>
}) {
  const { activeThreadId, activeMessageCount, chatScrollRef, shouldAutoScrollRef } = params

  useEffect(() => {
    shouldAutoScrollRef.current = true
    window.requestAnimationFrame(() => scrollChatToBottom(chatScrollRef, 'auto'))
  }, [activeThreadId, chatScrollRef, shouldAutoScrollRef])

  useEffect(() => {
    if (!shouldAutoScrollRef.current) {
      return
    }

    window.requestAnimationFrame(() => scrollChatToBottom(chatScrollRef, 'smooth'))
  }, [activeMessageCount, chatScrollRef, shouldAutoScrollRef])
}
