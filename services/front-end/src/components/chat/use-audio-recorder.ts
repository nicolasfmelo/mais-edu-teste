import { useEffect, useRef, useState, type MutableRefObject } from 'react'

const RECORDING_NOT_SUPPORTED_MESSAGE = 'Gravação de áudio não é suportada neste navegador.'
const MICROPHONE_ACCESS_ERROR_MESSAGE = 'Não foi possível acessar o microfone.'
const RECORDING_CAPTURE_ERROR_MESSAGE = 'Não foi possível gravar áudio.'

type RecorderRefs = {
  mediaRecorderRef: MutableRefObject<MediaRecorder | null>
  streamRef: MutableRefObject<MediaStream | null>
  chunksRef: MutableRefObject<BlobPart[]>
}

type RecorderSetters = {
  setAudioFile: (file: File) => void
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
}

function createRecordedFile(chunks: BlobPart[], mimeType: string) {
  const extension = mimeType.includes('mp4') ? 'mp4' : 'webm'
  const blob = new Blob(chunks, { type: mimeType })
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
  const filename = `recording-${timestamp}.${extension}`
  return new File([blob], filename, { type: mimeType })
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
  }

  mediaRecorder.onstop = () => {
    const mimeType = mediaRecorder.mimeType || supportedMimeType || 'application/octet-stream'
    const audioFile = createRecordedFile(refs.chunksRef.current, mimeType)

    setters.setAudioFile(audioFile)
    cleanupRecorderResources(refs)
    setters.setIsRecording(false)
  }
}

async function startAudioRecording(params: { refs: RecorderRefs; setters: RecorderSetters }) {
  const { refs, setters } = params
  setters.setRecordingError(null)

  if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === 'undefined') {
    setters.setRecordingError(RECORDING_NOT_SUPPORTED_MESSAGE)
    return
  }

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    refs.streamRef.current = stream
    refs.chunksRef.current = []

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

function stopAudioRecording(mediaRecorderRef: MutableRefObject<MediaRecorder | null>) {
  const mediaRecorder = mediaRecorderRef.current
  if (!mediaRecorder || mediaRecorder.state === 'inactive') {
    return
  }

  mediaRecorder.stop()
}

export function useAudioRecorder() {
  const [audioFile, setAudioFile] = useState<File | null>(null)
  const [isRecording, setIsRecording] = useState(false)
  const [recordingError, setRecordingError] = useState<string | null>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const chunksRef = useRef<BlobPart[]>([])

  useEffect(() => {
    return () => {
      stopAudioRecording(mediaRecorderRef)
      cleanupRecorderResources({ mediaRecorderRef, streamRef, chunksRef })
    }
  }, [])

  const startRecording = () =>
    startAudioRecording({
      refs: { mediaRecorderRef, streamRef, chunksRef },
      setters: {
        setAudioFile: (file) => setAudioFile(file),
        setIsRecording: (nextValue) => setIsRecording(nextValue),
        setRecordingError: (error) => setRecordingError(error),
      },
    })

  const stopRecording = () => {
    stopAudioRecording(mediaRecorderRef)
  }

  const clearAudioFile = () => {
    setAudioFile(null)
    setRecordingError(null)
  }

  return {
    audioFile,
    isRecording,
    recordingError,
    startRecording,
    stopRecording,
    clearAudioFile,
  }
}
