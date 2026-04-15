import { useEffect, type Dispatch, type SetStateAction } from 'react'

import { getCreditBalance, listAssistantModels } from '@/lib/chat-api'
import { getErrorMessage, mapModelOption, pickActiveModelId, type ModelOption } from '@/lib/chat-ui'

type SetState<T> = Dispatch<SetStateAction<T>>
type SetErrorMessage = SetState<string | null>

export function useAssistantModelsLoader(params: {
  setAssistantModelOptions: SetState<ModelOption[]>
  setActiveModelId: SetState<string | null>
  setErrorMessage: SetErrorMessage
}) {
  const { setAssistantModelOptions, setActiveModelId, setErrorMessage } = params

  useEffect(() => {
    let cancelled = false

    const loadAssistantModels = async () => {
      try {
        const response = await listAssistantModels()
        if (cancelled) {
          return
        }

        const nextOptions = response.items.map(mapModelOption)
        setAssistantModelOptions(nextOptions)
        setActiveModelId((current) => pickActiveModelId(current, nextOptions))
      } catch (error) {
        if (!cancelled) {
          setErrorMessage(getErrorMessage(error, 'Nao foi possivel carregar os modelos disponiveis.'))
        }
      }
    }

    void loadAssistantModels()

    return () => {
      cancelled = true
    }
  }, [setActiveModelId, setAssistantModelOptions, setErrorMessage])
}

export function useCreditsLoader(params: {
  trimmedApiKey: string
  setCredits: SetState<number | null>
  setErrorMessage: SetErrorMessage
}) {
  const { trimmedApiKey, setCredits, setErrorMessage } = params

  useEffect(() => {
    if (!trimmedApiKey) {
      setCredits(null)
      return
    }

    let cancelled = false

    const loadCredits = async () => {
      try {
        const balance = await getCreditBalance(trimmedApiKey)
        if (!cancelled) {
          setCredits(balance.available)
        }
      } catch (error) {
        if (!cancelled) {
          setCredits(null)
          setErrorMessage(getErrorMessage(error, 'Nao foi possivel carregar os creditos atuais.'))
        }
      }
    }

    void loadCredits()

    return () => {
      cancelled = true
    }
  }, [setCredits, setErrorMessage, trimmedApiKey])
}
