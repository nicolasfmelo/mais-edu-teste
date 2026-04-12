import { Workflow } from 'lucide-react'

export function LLMOpsPage() {
  return (
    <div className="flex flex-1 items-center justify-center p-10">
      <div className="flex flex-col items-center gap-3 text-center">
        <div className="flex size-12 items-center justify-center rounded-2xl bg-[#00a884]/10">
          <Workflow className="size-6 text-[#00a884]" />
        </div>
        <h1 className="text-lg font-semibold text-[#111b21]">LLMOps</h1>
        <p className="max-w-xs text-sm text-[#667781]">
          Monitoramento e operações de modelos de linguagem. Em construção.
        </p>
      </div>
    </div>
  )
}
