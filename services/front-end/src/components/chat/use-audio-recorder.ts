import { useEffect, useRef, useState, type MutableRefObject } from 'react'

const RECORDING_NOT_SUPPORTED_MESSAGE = 'Gravação de áudio não é suportada neste navegador.'
const MICROPHONE_ACCESS_ERROR_MESSAGE = 'Não foi possível acessar o microfone.'
const RECORDING_CAPTURE_ERROR_MESSAGE = 'Não foi possível gravar áudio.'

type StopResolver = (file: File | null) => void

type RecorderRefs = {
  mediaRecorderRef: MutableRefObject<MediaRecorder | null>
  streamRef: MutableRefObject<MediaStream | null>
  chunksRef: MutableRefObject<BlobPart[]>
  stopResolversRef: MutableRefObject<StopResolver[]>
  shouldDiscardOnStopRef: MutableRefObject<boolean>
}

type RecorderSetters = {
  setAudioFile: (file: File | null) => void
  setIsRecording: (isRecording: boolean) => void
  setRecordingError: (error: string | null) => void
}

function resolveSupportedMimeType() {
  if (typeof MediaRecorder.isTypeSupported !== 'function') {
    return null
  }

  const preferredMimeTypes = ['audio/webm;codecs=opus', 'audio/webm', 'audio/mp4']
  return preferredMimeTypes.find((mimeType) => MediaRecorder.isTypeSupported(mimeType)) ?? null
}

function stopMediaStream(stream: MediaStream | null) {
  if (!stream) {
    return
  }

  stream.getTracks().forEach((track) => track.stop())
}

function cleanupRecorderResources(refs: RecorderRefs) {
  stopMediaStream(refs.streamRef.current)
  refs.streamRef.current = null
  refs.mediaRecorderRef.current = null
  refs.chunksRef.current = []
  refs.shouldDiscardOnStopRef.current = false
}

function flushStopResolvers(refs: RecorderRefs, file: File | null) {
  refs.stopResolversRef.current.forEach((resolve) => resolve(file))
  refs.stopResolversRef.current = []
}

function createRecordedFile(chunks: BlobPart[], mimeType: string) {
  const extension = mimeType.includes('mp4') ? 'mp4' : 'webm'
  const blob = new Blob(chunks, { type: mimeType })
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
  const filename = `recording-${timestamp}.${extension}`
  return new File([blob], filename, { type: mimeType })
}

function finalizeRecorderStop(params: { refs: RecorderRefs; setters: RecorderSetters; file: File | null }) {
  const { refs, setters, file } = params

  setters.setIsRecording(false)
  flushStopResolvers(refs, file)
  cleanupRecorderResources(refs)
}

function attachRecorderHandlers(params: {
  mediaRecorder: MediaRecorder
  supportedMimeType: string | null
  refs: RecorderRefs
  setters: RecorderSetters
}) {
  const { mediaRecorder, supportedMimeType, refs, setters } = params

  mediaRecorder.ondataavailable = (event) => {
    if (event.data.size > 0) {
      refs.chunksRef.current.push(event.data)
    }
  }

  mediaRecorder.onerror = () => {
    setters.setRecordingError(RECORDING_CAPTURE_ERROR_MESSAGE)
    refs.shouldDiscardOnStopRef.current = true
  }

  mediaRecorder.onstop = () => {
    const shouldDiscard = refs.shouldDiscardOnStopRef.current

    if (shouldDiscard || refs.chunksRef.current.length === 0) {
      if (!shouldDiscard && refs.chunksRef.current.length === 0) {
        setters.setRecordingError(RECORDING_CAPTURE_ERROR_MESSAGE)
      }

      setters.setAudioFile(null)
      finalizeRecorderStop({ refs, setters, file: null })
      return
    }

    const mimeType = mediaRecorder.mimeType || supportedMimeType || 'application/octet-stream'
    const audioFile = createRecordedFile(refs.chunksRef.current, mimeType)

    setters.setAudioFile(audioFile)
    finalizeRecorderStop({ refs, setters, file: audioFile })
  }
}

async function startAudioRecording(params: { refs: RecorderRefs; setters: RecorderSetters }) {
  const { refs, setters } = params

  setters.setAudioFile(null)
  setters.setRecordingError(null)

  if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === 'undefined') {
    setters.setRecordingError(RECORDING_NOT_SUPPORTED_MESSAGE)
    return
  }

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    refs.streamRef.current = stream
    refs.chunksRef.current = []
    refs.shouldDiscardOnStopRef.current = false

    const supportedMimeType = resolveSupportedMimeType()
    const mediaRecorder = supportedMimeType
      ? new MediaRecorder(stream, { mimeType: supportedMimeType })
      : new MediaRecorder(stream)

    attachRecorderHandlers({
      mediaRecorder,
      supportedMimeType,
      refs,
      setters,
    })

    mediaRecorder.start()
    refs.mediaRecorderRef.current = mediaRecorder
    setters.setIsRecording(true)
  } catch {
    setters.setRecordingError(MICROPHONE_ACCESS_ERROR_MESSAGE)
    setters.setIsRecording(false)
    cleanupRecorderResources(refs)
  }
}

function stopAudioRecording(params: {
  refs: RecorderRefs
  discard?: boolean
}): Promise<File | null> {
  const { refs, discard = false } = params
  const mediaRecorder = refs.mediaRecorderRef.current

  if (!mediaRecorder || mediaRecorder.state === 'inactive') {
    return Promise.resolve(null)
  }

  if (discard) {
    refs.shouldDiscardOnStopRef.current = true
  }

  return new Promise((resolve) => {
    refs.stopResolversRef.current.push(resolve)

    try {
      mediaRecorder.stop()
    } catch {
      refs.stopResolversRef.current = refs.stopResolversRef.current.filter((resolver) => resolver !== resolve)
      resolve(null)
    }
  })
}

export function useAudioRecorder() {
  const [audioFile, setAudioFile] = useState<File | null>(null)
  const [isRecording, setIsRecording] = useState(false)
  const [recordingError, setRecordingError] = useState<string | null>(null)
  const [recordingDurationSeconds, setRecordingDurationSeconds] = useState(0)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const chunksRef = useRef<BlobPart[]>([])
  const stopResolversRef = useRef<StopResolver[]>([])
  const shouldDiscardOnStopRef = useRef(false)

  useEffect(() => {
    if (!isRecording) {
      return
    }

    const startedAt = Date.now()

    const intervalId = window.setInterval(() => {
      setRecordingDurationSeconds(Math.floor((Date.now() - startedAt) / 1000))
    }, 250)

    return () => {
      window.clearInterval(intervalId)
    }
  }, [isRecording])

  useEffect(() => {
    const stream = streamRef.current

    return () => {
      stopMediaStream(stream)
      stopResolversRef.current.forEach((resolve) => resolve(null))
      stopResolversRef.current = []
      cleanupRecorderResources({ mediaRecorderRef, streamRef, chunksRef, stopResolversRef, shouldDiscardOnStopRef })
    }
  }, [])

  const refs = { mediaRecorderRef, streamRef, chunksRef, stopResolversRef, shouldDiscardOnStopRef }

  const startRecording = () => {
    setRecordingDurationSeconds(0)

    return startAudioRecording({
      refs,
      setters: {
        setAudioFile: (file) => setAudioFile(file),
        setIsRecording: (nextValue) => setIsRecording(nextValue),
        setRecordingError: (error) => setRecordingError(error),
      },
    })
  }

  const stopRecording = () => {
    setRecordingDurationSeconds(0)
    void stopAudioRecording({ refs })
  }

  const stopRecordingAndGetFile = () => stopAudioRecording({ refs })

  const discardRecording = () => {
    setAudioFile(null)
    setRecordingError(null)
    setRecordingDurationSeconds(0)
    if (!isRecording) {
      return
    }

    void stopAudioRecording({ refs, discard: true })
  }

  const clearAudioFile = () => {
    setAudioFile(null)
    setRecordingError(null)
    setRecordingDurationSeconds(0)
  }

  return {
    audioFile,
    isRecording,
    recordingError,
    recordingDurationSeconds,
    startRecording,
    stopRecording,
    stopRecordingAndGetFile,
    discardRecording,
    clearAudioFile,
  }
}
