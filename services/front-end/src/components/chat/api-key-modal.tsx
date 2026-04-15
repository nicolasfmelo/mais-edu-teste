import { Button } from '@/components/ui/button'

type ApiKeyModalProps = {
  apiKey: string
  onChangeApiKey: (value: string) => void
  onSave: () => void
  onClose: () => void
}

export function ApiKeyModal({ apiKey, onChangeApiKey, onSave, onClose }: ApiKeyModalProps) {
  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-[#111b21]/30 px-4 backdrop-blur-[2px]">
      <form
        className="w-full max-w-md rounded-[28px] border border-black/8 bg-[#f7f8fa] p-5 shadow-[0_16px_40px_rgba(17,27,33,0.22)]"
        onSubmit={(event) => {
          event.preventDefault()
          onSave()
        }}
      >
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-sm font-semibold text-[#111b21]">API key</p>
            <p className="mt-1 text-sm text-[#667781]">
              Salve a chave para montar o header de request no back sem poluir o topo do chat.
            </p>
          </div>
          <Button
            type="button"
            variant="ghost"
            size="icon-sm"
            onClick={onClose}
            aria-label="Fechar modal de chave"
            className="rounded-full text-[#667781] hover:bg-black/5 hover:text-[#111b21]"
          >
            <span aria-hidden="true" className="text-base leading-none">
              ×
            </span>
          </Button>
        </div>

        <div className="mt-5 space-y-3">
          <label
            htmlFor="api-key-input"
            className="block text-xs font-medium uppercase tracking-[0.14em] text-[#667781]"
          >
            Chave de acesso
          </label>
          <input
            id="api-key-input"
            name="api_key"
            type="password"
            value={apiKey}
            onChange={(event) => onChangeApiKey(event.target.value)}
            placeholder="Cole sua chave aqui"
            className="w-full rounded-2xl border border-black/8 bg-white px-4 py-3 text-sm text-[#111b21] outline-none placeholder:text-[#8696a0] focus:border-[#00a884]/50"
            autoComplete="off"
            spellCheck={false}
          />
          <p className="text-xs text-[#667781]">
            Ela fica escondida na interface e pronta para compor os requests do backend.
          </p>
        </div>

        <div className="mt-5 flex items-center justify-end gap-2">
          <Button
            type="button"
            variant="ghost"
            onClick={onClose}
            className="rounded-full px-4 text-[#667781] hover:bg-black/5 hover:text-[#111b21]"
          >
            Fechar
          </Button>
          <Button type="submit" className="rounded-full bg-[#00a884] px-4 text-[#06291f] hover:bg-[#0dc39a]">
            Salvar chave
          </Button>
        </div>
      </form>
    </div>
  )
}
