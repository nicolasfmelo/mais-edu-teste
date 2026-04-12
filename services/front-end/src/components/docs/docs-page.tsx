import { BookOpen, FileText, Layers, MessageSquare, Zap } from 'lucide-react'

const sections = [
  {
    icon: MessageSquare,
    title: 'Chat com Assistente',
    description:
      'Inicie conversas com o assistente de IA configurado para sua instituição. Crie novos threads, envie mensagens e receba respostas contextualizadas.',
  },
  {
    icon: Layers,
    title: 'Modelos disponíveis',
    description:
      'Escolha entre diferentes modelos de linguagem disponíveis na plataforma. Cada modelo tem características específicas de performance e custo.',
  },
  {
    icon: Zap,
    title: 'API Key',
    description:
      'Configure sua chave de API para habilitar o consumo de créditos. Sem a chave, o assistente opera em modo limitado.',
  },
  {
    icon: FileText,
    title: 'Métricas',
    description:
      'Acompanhe o uso da plataforma, consumo de créditos e desempenho dos assistentes em tempo real na página de métricas.',
  },
]

export function DocsPage() {
  return (
    <div className="flex-1 overflow-y-auto p-6 lg:p-10">
      <div className="mx-auto max-w-3xl">
        <div className="mb-8 flex items-center gap-3">
          <div className="flex size-10 items-center justify-center rounded-xl bg-[#00a884]/10">
            <BookOpen className="size-5 text-[#00a884]" />
          </div>
          <div>
            <h1 className="text-xl font-semibold text-[#111b21]">Solution Docs</h1>
            <p className="text-sm text-[#667781]">Documentação da plataforma Mais A Educ</p>
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          {sections.map(({ icon: Icon, title, description }) => (
            <div
              key={title}
              className="rounded-2xl border border-black/6 bg-white p-5 transition hover:shadow-sm"
            >
              <div className="mb-3 flex size-9 items-center justify-center rounded-xl bg-[#00a884]/10">
                <Icon className="size-4 text-[#00a884]" />
              </div>
              <h2 className="mb-1.5 text-sm font-semibold text-[#111b21]">{title}</h2>
              <p className="text-xs leading-relaxed text-[#667781]">{description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
