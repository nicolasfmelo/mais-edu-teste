import { BookOpen } from 'lucide-react'
import type { ReactNode } from 'react'

// -----------------------------------------------------------------------
// CONTEUDO DA DOCUMENTACAO (VERSAO FINAL DETALHADA)
// -----------------------------------------------------------------------

type Block =
  | { type: 'paragraph'; text: string }
  | { type: 'heading'; text: string }
  | { type: 'list'; items: string[] }
  | { type: 'table'; headers: string[]; rows: string[][] }
  | { type: 'code'; language: string; text: string }
  | { type: 'image'; src: string; alt: string; caption?: string }

interface DocSection {
  anchor: string
  title: string
  blocks: Block[]
}

const SECTIONS: DocSection[] = [
  {
    anchor: 'escopo',
    title: 'Escopo do Problema',
    blocks: [
      {
        type: 'paragraph',
        text: 'Esta entrega responde ao teste pratico para Coordenador(a) de IA e foi organizada para cobrir o que o PDF pede de forma fim a fim: entendimento do problema, metodologia de avaliacao, arquitetura, prototipo funcional, visao de operacao e registro de uso de IA.',
      },
      { type: 'heading', text: 'Contexto pratico do problema' },
      {
        type: 'list',
        items: [
          'O case trata da avaliacao da qualidade de atendimento de uma IA operadora em conversas de captacao e orientacao de alunos.',
          'O agente da instituicao ficticia se chama Clara e atende potenciais alunos do Instituto Horizonte Digital.',
          'O insumo principal do problema e um conjunto de conversas reais ou similares em chat/WhatsApp, com possibilidade futura de expansao para voz.',
          'A saida esperada e uma avaliacao estruturada por sessao, com scores, justificativas e evidencias textuais.',
        ],
      },
      { type: 'heading', text: 'Referencias do case' },
      {
        type: 'list',
        items: [
          'PDF do desafio: case/Teste Prático - Coordenador de IA (v2) 1.pdf',
          'Conversas de exemplo: case/Teste Prático - Coordenador de IA - Exemplo Conversas.json',
          'Arquitetura e notas tecnicas: docs/',
          'Rascunhos, perguntas e decisoes iniciais: docs/drafts/',
        ],
      },
      { type: 'heading', text: 'Escopo oficial do desafio (PDF)' },
      {
        type: 'list',
        items: [
          'Analisar conversas de atendimento em chat e WhatsApp com extensao futura para voz.',
          'Retornar analise estruturada com scores, justificativas e evidencias.',
          'Considerar viabilidade economica, auditabilidade, rastreabilidade e potencial de escala.',
          'Permitir evolucao dos criterios ao longo do tempo e uso inicial como apoio a avaliacao humana.',
          'Levar em conta tratamento de dados sensiveis e operacao em ambiente real.',
        ],
      },
      { type: 'heading', text: 'O que a avaliacao espera observar' },
      {
        type: 'list',
        items: [
          'Visao arquitetural fim a fim.',
          'Estrategia de IA: prompts, modelos, orquestracao e trade-offs.',
          'Comparacao de pelo menos duas abordagens arquiteturais.',
          'Prototipo funcional executavel.',
          'Visao de operacao: monitoracao, metricas e evolucao em producao.',
        ],
      },
      { type: 'heading', text: 'Entregaveis exigidos no teste' },
      {
        type: 'table',
        headers: ['Entregavel', 'Conteudo esperado'],
        rows: [
          [
            'Documento de solucao',
            'Visao geral, fluxo, decisoes tecnicas, prompts, modelos, orquestracao, comparacao arquitetural e justificativas',
          ],
          [
            'Prototipo funcional',
            'Repositorio com instrucoes, exemplo de request/response e analise estruturada em funcionamento',
          ],
          [
            'Registro de uso de IA',
            'Ferramentas usadas, finalidade e validacao tecnica das sugestoes',
          ],
        ],
      },
    ],
  },
  {
    anchor: 'formulacao',
    title: 'Formulacao Inicial',
    blocks: [
      {
        type: 'paragraph',
        text: 'Antes de implementar, o problema foi tratado como um caso de avaliacao operacional inspirado em NPS. A leitura das conversas e das notas em docs/drafts deixou claro que a pergunta central nao era apenas se a IA responde, mas se o cliente sente que avancou com clareza, pouco atrito e aderencia ao que buscava.',
      },
      { type: 'heading', text: 'Steps iniciais executados' },
      {
        type: 'list',
        items: [
          'Leitura completa da proposta.',
          'Analise das conversas de exemplo fornecidas no case.',
          'Levantamento de sinais de sucesso e falha em cada sessao.',
          'Definicao de uma regua de avaliacao pela perspectiva do cliente.',
          'Planejamento da stack, do prototipo e da arquitetura de escala.',
        ],
      },
      { type: 'heading', text: 'Hipoteses iniciais que orientaram a solucao' },
      {
        type: 'list',
        items: [
          'O problema se comporta como um NPS operacional aplicado a IA operadora.',
          'A perspectiva correta da analise e a do cliente, nao a do bot.',
          'Transferencia para humano nao e necessariamente ruim; depende do contexto e do momento.',
          'Sinal de fechamento ajuda, mas sozinho nao resolve a avaliacao.',
          'Esforco do cliente, entendimento do objetivo e resolucao precisam complementar a satisfacao.',
          'Prompt injection, tokens e mudanca comportamental sao indicadores operacionais relevantes.',
        ],
      },
      { type: 'heading', text: 'Perguntas abertas que entraram no desenho' },
      {
        type: 'list',
        items: [
          'Qual o volume esperado de clientes e sessoes?',
          'Que nivel de transferencia para humano deve contar como sucesso?',
          'Quais cursos e intencoes aparecem com maior frequencia?',
          'Como medir queda de qualidade ao longo do tempo (drifting)?',
        ],
      },
      { type: 'heading', text: 'Consequencia direta no desenho final' },
      {
        type: 'paragraph',
        text: 'Por isso a entrega foi dividida em duas trilhas: um MVP Inline Process implementado para demonstrar o fluxo completo e uma proposta Batch Process para o recorte que o teste mais valoriza em custo, escala e governanca operacional.',
      },
    ],
  },
  {
    anchor: 'metodologia',
    title: 'Metodologia de Avaliacao',
    blocks: [
      {
        type: 'paragraph',
        text: 'A metodologia consolidada veio dos rascunhos em docs/drafts/rules.md e foi mantida aderente ao shape de resposta implementado no backend. A unidade de leitura e a sessao, e o julgamento principal sempre considera a percepcao do cliente ao longo da conversa inteira.',
      },
      { type: 'heading', text: 'Regra central' },
      {
        type: 'list',
        items: [
          'Ler a sessao como experiencia do cliente.',
          'Inferir o objetivo dominante da conversa antes de pontuar.',
          'Separar satisfacao percebida de diagnosticos auxiliares.',
          'Registrar evidencias textuais curtas que justifiquem a nota.',
        ],
      },
      { type: 'heading', text: 'Classificacao principal de satisfacao' },
      {
        type: 'table',
        headers: ['Valor', 'Classe', 'Regra pratica'],
        rows: [
          ['3', 'Bom', 'Cliente avancou com baixo atrito, recebeu resposta util ou aceitou claramente o proximo passo'],
          ['2', 'Neutro', 'Houve progresso parcial, mas com lacunas, friccoes ou conclusao incompleta'],
          ['1', 'Ruim', 'Cliente precisou insistir, corrigir a IA, repetir contexto ou saiu sem resposta util'],
        ],
      },
      { type: 'heading', text: 'Indicador consolidado da operacao' },
      {
        type: 'code',
        language: 'text',
        text: 'INDICE_IA_OPERADORA = % bom - % ruim',
      },
      {
        type: 'paragraph',
        text: 'Esse indicador resume o comportamento agregado da operacao em logica inspirada em NPS. Ele nao substitui diagnosticos auxiliares e por isso o backend tambem devolve medias de esforco, entendimento, resolucao, tokens e incidencias de injection.',
      },
      { type: 'heading', text: 'Metricas auxiliares' },
      {
        type: 'table',
        headers: ['Metrica', 'Escala', 'Leitura pratica', 'Peso sugerido inicial'],
        rows: [
          ['Satisfacao', '1 a 3', 'Resultado final percebido pelo cliente', '40%'],
          ['Esforco do cliente', '1 a 5', 'Quanto o cliente precisou insistir, repetir ou corrigir', '20%'],
          ['Entendimento do objetivo', '0 a 2', 'Se a IA entendeu cedo, tarde ou nao entendeu', '20%'],
          ['Resolucao / avanco util', '0 a 2', 'Se houve progresso real ou proximo passo claro', '20%'],
          ['Mudanca comportamental', 'qualitativa', 'Positiva, neutra ou negativa ao longo da sessao', 'ajuste qualitativo'],
        ],
      },
      { type: 'heading', text: 'Heuristicas que derrubam nota' },
      {
        type: 'list',
        items: [
          'Perguntar algo ja respondido pelo cliente.',
          'Duplicar resposta ou responder duas vezes ao mesmo ponto.',
          'Trocar o contexto do cliente por tema proximo, mas incorreto.',
          'Insistir em transferencia quando o cliente quer apenas informacao objetiva.',
          'Nao reconhecer correcoes explicitas feitas pelo cliente.',
        ],
      },
      { type: 'heading', text: 'Heuristicas que elevam nota' },
      {
        type: 'list',
        items: [
          'Capturar rapido o contexto profissional do cliente.',
          'Relacionar curso, nivel e modalidade ao objetivo declarado.',
          'Ser transparente quando nao puder responder algo.',
          'Encaminhar para proximo passo coerente com o momento da conversa.',
        ],
      },
      { type: 'heading', text: 'Campos anotados por sessao' },
      {
        type: 'table',
        headers: ['Campo', 'Descricao'],
        rows: [
          ['session_id', 'Identificador da conversa'],
          ['objetivo_cliente', 'Objetivo dominante inferido para a sessao'],
          ['satisfaction', 'Classificacao principal: bom, neutro ou ruim'],
          ['effort_score', 'Esforco do cliente na escala 1 a 5'],
          ['understanding_score', 'Entendimento do objetivo na escala 0 a 2'],
          ['resolution_score', 'Resolucao ou avanco util na escala 0 a 2'],
          ['mudanca_comportamental', 'Positiva, neutra ou negativa'],
          ['sinal_fechamento', 'Positivo, neutro ou negativo'],
          ['evidences', 'Trechos curtos que justificam a avaliacao'],
          ['prompt_tokens / completion_tokens / total_tokens', 'Consumo de tokens da analise'],
          ['prompt_injection_detected / injection_snippets', 'Sinalizacao de tentativa de injection'],
        ],
      },
    ],
  },
  {
    anchor: 'introducao',
    title: 'Introducao e Propostas',
    blocks: [
      {
        type: 'paragraph',
        text: 'Foram desenvolvidas duas propostas complementares. A primeira esta implementada como MVP Inline Process, com fluxo completo de chat, audio, metricas, avaliacao e LLMOps. A segunda foi desenhada como MVP Batch Process, com foco em custo e escala para o recorte exato do desafio.',
      },
      {
        type: 'list',
        items: [
          'MVP Inline Process: emulacao de experiencia estilo WhatsApp, transcricao de audio, agente conversacional, agente avaliador, RAG, metricas e operacao de prompts.',
          'MVP Batch Process: pipeline orientado a armazenamento, filas e processamento assinado pelo provider para reduzir custo em volume.',
          'Todos os materiais do raciocinio ficaram no repositorio em formato RAW, especialmente em docs/ e docs/drafts/.',
        ],
      },
      {
        type: 'paragraph',
        text: 'A escolha da AWS na proposta batch nao e limitacao arquitetural. Ela veio do reaproveitamento do gateway de LLM e do sistema de creditos que ja estavam operacionais na minha conta pessoal para o MVP inline.',
      },
    ],
  },
  {
    anchor: 'comparacao',
    title: 'Comparacao de Abordagens',
    blocks: [
      {
        type: 'table',
        headers: ['Abordagem', 'Vantagens', 'Limitacoes', 'Quando usar'],
        rows: [
          [
            'Inline Process',
            'Resposta imediata, demonstracao forte, UX completa, validacao rapida do produto',
            'Custo unitario maior em escala e maior pressao no runtime online',
            'MVP, validacao funcional, demos, avaliacao assistida humana em menor volume',
          ],
          [
            'Batch Process',
            'Melhor custo por volume, desacoplamento ingestao/processamento, melhor governanca de operacao',
            'Menor imediatismo e setup operacional mais elaborado',
            'Escala de producao, analise massiva e operacao com previsibilidade de custo',
          ],
        ],
      },
      {
        type: 'paragraph',
        text: 'A entrega final usa Inline Process como MVP porque o objetivo era provar o fluxo completo em funcionamento. A recomendacao explicita para escala, aderente ao PDF, continua sendo Batch Process.',
      },
      { type: 'heading', text: 'Por que o batch e a solucao ideal para o desafio' },
      {
        type: 'list',
        items: [
          'A inferencia em batch reduz necessidade de infraestrutura quente para processamento continuo.',
          'A coleta de conversas pode ser feita por jobs simples e barata.',
          'A camada de LLMOps pode ficar isolada para avaliadores e prompt engineers.',
          'Front, dashboards e governanca continuam separados do pipeline pesado de analise.',
        ],
      },
      { type: 'heading', text: 'Arquitetura Batch (proposta)' },
      {
        type: 'image',
        src: '/docs/mvp-batch-process.png',
        alt: 'Arquitetura MVP Batch Process',
        caption: 'Diagrama da arquitetura proposta para processamento em batch.',
      },
    ],
  },
  {
    anchor: 'custos',
    title: 'Custos e Escala',
    blocks: [
      {
        type: 'paragraph',
        text: 'A modelagem de custo foi feita para 30.000 analises por mes em us-east-1 com margem de seguranca de 30%. O racional completo esta consolidado em estimated-infra-costs.md e foi trazido para o fluxo final.',
      },
      { type: 'heading', text: 'Premissas usadas no calculo' },
      {
        type: 'list',
        items: [
          'Janela mensal de 730 horas.',
          '1 task Fargate 24/7 com 1 vCPU e 2 GB RAM.',
          '2 buckets S3 com 20 GB totais e 120 mil operacoes mensais.',
          '2 Lambdas somando 90 mil invocacoes mensais.',
          '3 tabelas DynamoDB on-demand com 300 mil writes, 900 mil reads e 10 GB.',
          'CloudFront, WAF e CloudWatch incluidos no subtotal.',
          '30% de margem adicional aplicada ao total consolidado.',
        ],
      },
      { type: 'heading', text: 'Infraestrutura mensal estimada' },
      {
        type: 'table',
        headers: ['Componente', 'Custo (USD/mes)'],
        rows: [
          ['S3 (2 buckets)', '0,78'],
          ['EventBridge', '0,06'],
          ['Lambda', '0,77'],
          ['DynamoDB', '2,80'],
          ['Fargate', '36,04'],
          ['ALB', '17,01'],
          ['CloudFront', '4,30'],
          ['WAF', '8,03'],
          ['CloudWatch', '16,90'],
          ['Bedrock (infra fixa)', '0,00'],
          ['Subtotal Infra', '86,69'],
          ['Infra +30% margem', '112,70'],
        ],
      },
      { type: 'heading', text: 'Custos de LLM em 30 mil analises por mes' },
      {
        type: 'table',
        headers: ['Modelo', 'Custo medio por analise (USD)', 'Custo LLM em 30k (USD/mes)'],
        rows: [
          ['anthropic.claude-sonnet-4-6', '0,004644', '139,32'],
          ['anthropic.claude-haiku-4-5-20251001-v1:0', '0,001548', '46,44'],
          ['minimax.minimax-m2.5', '0,000340', '10,20'],
          ['amazon.nova-2-lite-v1:0', '0,000764', '22,92'],
        ],
      },
      { type: 'heading', text: 'Total consolidado com margem de 30%' },
      {
        type: 'table',
        headers: ['Modelo', 'Infra (USD)', 'LLM 30k (USD)', 'Total com +30% (USD)'],
        rows: [
          ['anthropic.claude-sonnet-4-6', '86,69', '139,32', '293,81'],
          ['anthropic.claude-haiku-4-5-20251001-v1:0', '86,69', '46,44', '173,07'],
          ['minimax.minimax-m2.5', '86,69', '10,20', '125,96'],
          ['amazon.nova-2-lite-v1:0', '86,69', '22,92', '142,49'],
        ],
      },
      { type: 'heading', text: 'Como audio entra nessa conta' },
      {
        type: 'paragraph',
        text: 'Para levar transcricao para producao em escala, a proposta natural e adicionar armazenamento dedicado para audio bruto e artefatos de transcricao, uma tabela especifica de metadados e uma camada de monitoracao propria para qualidade de ASR. Isso pode ser self-hosted ou via API paga, dependendo do custo por minuto e do nivel de controle desejado.',
      },
    ],
  },
  {
    anchor: 'inline',
    title: 'MVP Inline Process',
    blocks: [
      {
        type: 'paragraph',
        text: 'O MVP inline foi o recorte implementado para mostrar o ciclo completo. Ele emula uma experiencia de conversa estilo WhatsApp, aceita audio, responde com a agente Clara, exporta sessoes, roda analise NPS-like e oferece operacao minima de prompts.',
      },
      {
        type: 'list',
        items: [
          'Chat textual com sessoes persistidas.',
          'Chat por audio com transcricao local em Whisper ONNX (whisper-small).',
          'Agente conversacional para orientacao academica.',
          'Agente avaliador para satisfacao, esforco, resolucao e injection.',
          'RAG de primeiro corte sobre catalogo de cursos.',
          'Pagina de Metrics e pagina de LLMOps no front.',
        ],
      },
      { type: 'heading', text: 'Arquitetura Inline (implementada)' },
      {
        type: 'image',
        src: '/docs/mvp-inline-process.png',
        alt: 'Arquitetura MVP Inline Process',
        caption: 'Diagrama da arquitetura implementada no MVP inline.',
      },
    ],
  },
  {
    anchor: 'arquitetura',
    title: 'Arquitetura e Estrategia de IA',
    blocks: [
      {
        type: 'paragraph',
        text: 'O backend segue organizacao inspirada em MASA para manter fronteiras claras entre dominio, regra pura, integracoes e orquestracao. O [MASA Framework](https://www.masa-framework.org/) foi desenvolvido por mim (Nicolas Melo).',
      },
      {
        type: 'table',
        headers: ['Camada', 'Responsabilidade'],
        rows: [
          ['domain_models', 'Entidades, IDs de dominio, contratos e excecoes'],
          ['engines', 'Regras puras e deterministicas, sem I/O'],
          ['integrations', 'Adapters de banco, object store, proxy LLM e vector store'],
          ['services', 'Orquestracao dos casos de uso'],
          ['delivery', 'Handlers HTTP e schemas de entrada/saida'],
          ['bootstrap', 'Wiring explicito de dependencias e startup'],
        ],
      },
      { type: 'heading', text: 'Estrutura principal do backend' },
      {
        type: 'code',
        language: 'text',
        text: `src/app
├── bootstrap
├── delivery
│   ├── http
│   └── schemas
├── domain_models
│   ├── agent
│   ├── chat
│   ├── common
│   ├── evaluation
│   ├── indexing
│   ├── metrics
│   ├── prompt
│   └── rag
├── engines
│   ├── evaluation
│   ├── indexing
│   ├── metrics
│   └── prompt
├── integrations
│   ├── database
│   ├── external_apis
│   ├── llm_providers
│   ├── object_store
│   └── vector_store
├── services
│   ├── agent
│   ├── chat
│   ├── evaluation
│   ├── indexing
│   ├── metrics
│   ├── prompt
│   └── rag
└── main.py`,
      },
      { type: 'heading', text: 'Estrategia de prompts' },
      {
        type: 'list',
        items: [
          'chat-agent-system: prompt da Clara para atendimento consultivo, descoberta de objetivo e recomendacao de curso.',
          'nps-agent-system: prompt do avaliador para satisfacao, esforco, entendimento, resolucao, mudanca comportamental e injection.',
          'Os prompts ficam em registry versionado, com ativacao da versao corrente por chave.',
        ],
      },
      { type: 'heading', text: 'Estrategia de modelos' },
      {
        type: 'list',
        items: [
          'Modelos expostos hoje via allowlist e catalogo: us.anthropic.claude-sonnet-4-6, us.anthropic.claude-haiku-4-5-20251001-v1:0, minimax.minimax-m2.5 e us.amazon.nova-2-lite-v1:0.',
          'O front consulta essa lista em GET /api/assistant-models.',
          'O objetivo do MVP nao foi fixar um modelo unico, mas manter flexibilidade de runtime sob controle de custo e credito.',
        ],
      },
      { type: 'heading', text: 'Estrategia de orquestracao' },
      {
        type: 'list',
        items: [
          'Fluxo de chat: recupera contexto do catalogo, monta prompt final e chama o proxy LLM.',
          'Fluxo de analise: exporta sessoes, le objetos do MinIO e executa a avaliacao por sessao.',
          'Fluxos implementados com LangGraph para deixar a sequencia de etapas explicita e extensivel.',
          'No primeiro corte de RAG, o catalogo funciona sem embeddings reais obrigatorios; o foco foi provar o fluxo e manter acoplamento baixo para evolucao.',
        ],
      },
    ],
  },
  {
    anchor: 'fluxos',
    title: 'Fluxos e Endpoints Implementados',
    blocks: [
      {
        type: 'paragraph',
        text: 'O diff anterior da pagina de docs tinha varios detalhes de rotas e namespaces. A reconciliacao final abaixo considera o que esta realmente implementado hoje no backend e o que o front de fato consome.',
      },
      { type: 'heading', text: 'Fluxos funcionais cobertos pela codebase' },
      {
        type: 'table',
        headers: ['Fluxo', 'Descricao funcional', 'Rotas principais'],
        rows: [
          [
            'Chat e sessoes',
            'Lista, cria, consulta sessoes e envia mensagens para a Clara',
            'GET /api/chat/sessions, POST /api/chat/sessions, GET /api/chat/sessions/{session_id}, POST /api/chat/messages',
          ],
          [
            'Chat por audio',
            'Recebe audio, transcreve com Whisper local e envia a mensagem transcrita ao fluxo do chat',
            'POST /api/chat/audio-messages',
          ],
          [
            'Catalogo operacional',
            'Consulta saldo de creditos e modelos disponiveis',
            'GET /api/credits/balance, GET /api/assistant-models',
          ],
          [
            'Export e analise em lote',
            'Exporta as conversas persistidas para object store e executa a analise por sessao',
            'POST /api/conversations/export, POST /api/evaluation/agent-analysis',
          ],
          [
            'Avaliacao operacional',
            'Consulta sumario agregado, lista unitarios e abre detalhe de cada sessao avaliada',
            'GET /api/evaluation/summary, GET /api/evaluation/agent-sessions, GET /api/evaluation/agent-sessions/{session_id}',
          ],
          [
            'Metricas',
            'Healthcheck, resumo operacional, serie de tokens e ultimo job de export/analise',
            'GET /metrics, GET /api/metrics/health, GET /api/metrics/summary, GET /api/metrics/tokens-report, GET /api/metrics/jobs/export/latest, GET /api/metrics/jobs/analysis/latest',
          ],
          [
            'Prompt Registry',
            'Lista prompts, detalha, cria versoes e ativa a versao corrente',
            'GET/POST /api/prompt-registry/prompts, GET /api/prompt-registry/prompts/{prompt_key}, POST /api/prompt-registry/prompts/{prompt_key}/versions, GET/POST /api/prompt-registry/prompts/{prompt_key}/active',
          ],
        ],
      },
      { type: 'heading', text: 'Importante sobre drafts e proposta de evolucao' },
      {
        type: 'list',
        items: [
          'O arquivo services/back-end/api.md propoe uma evolucao futura para /api/metrics/overview, /api/metrics/timeseries e /api/metrics/sessions.',
          'Esse mesmo documento tambem propoe migrar /api/prompt-registry para um namespace /api/llmops.',
          'Essas ideias continuam validas como direcao arquitetural, mas nao sao o contrato implementado hoje; por isso a documentacao final manteve os endpoints reais e marcou as evolucoes apenas como referencia de design.',
        ],
      },
    ],
  },
  {
    anchor: 'infra',
    title: 'Infraestrutura e Persistencia',
    blocks: [
      {
        type: 'paragraph',
        text: 'O ambiente local foi desenhado para subir a plataforma inteira com Compose: banco, object store, backend, frontend e observabilidade. Esse ponto aparecia de forma mais rica no diff antigo e precisava voltar, porque ele explica como o MVP funciona de ponta a ponta.',
      },
      { type: 'heading', text: 'Servicos do Compose' },
      {
        type: 'table',
        headers: ['Servico', 'Tecnologia', 'Papel no MVP', 'Porta'],
        rows: [
          ['postgres', 'postgres:17-alpine', 'Persistencia transacional principal', '5432'],
          ['minio', 'minio/minio', 'Object store para export de conversas', '9000 / 9001'],
          ['back-end', 'FastAPI + Python 3.12', 'API principal, chat, avaliacao e metricas', '8000'],
          ['front-end', 'React + Vite', 'Interface de chat, metrics, llmops e docs', '8080'],
          ['prometheus', 'prom/prometheus', 'Scraping de /metrics', '9090'],
          ['loki', 'grafana/loki', 'Armazenamento de logs', '3100'],
          ['promtail', 'grafana/promtail', 'Coleta de logs dos containers', '-'],
          ['grafana', 'grafana/grafana', 'Dashboards e visualizacao operacional', '3000'],
        ],
      },
      { type: 'heading', text: 'Variaveis de ambiente relevantes' },
      {
        type: 'table',
        headers: ['Variavel', 'Uso'],
        rows: [
          ['DATABASE_URL', 'Conexao com o Postgres e bootstrap ORM'],
          ['LLM_PROXY_BASE_URL', 'URL base do gateway de LLM'],
          ['LLM_PROXY_TEST_API_KEY', 'Chave usada em fluxos de teste/local'],
          ['MINIO_ENDPOINT / MINIO_ACCESS_KEY / MINIO_SECRET_KEY', 'Conexao com o object store'],
          ['MINIO_EXPORT_BUCKET', 'Bucket das exportacoes de conversa'],
          ['DATASETS_DIR', 'Diretorio do catalogo de cursos em markdown'],
          ['INSTITUTION_PROFILE_PATH', 'Perfil institucional do Instituto Horizonte Digital e da Clara'],
          ['WHISPER_MODEL_PATH', 'Caminho do modelo whisper-small local'],
          ['LOG_LEVEL / LOG_FORMAT', 'Configuracao de logs estruturados'],
        ],
      },
      { type: 'heading', text: 'Bootstrap e startup' },
      {
        type: 'list',
        items: [
          'No startup, o backend cria o schema relacional principal via SQLAlchemy.',
          'O catalogo de cursos em services/datasets/*.md e carregado com upsert em course_catalog_entries.',
          'O perfil institucional tambem e lido de markdown para compor o comportamento da Clara.',
          'Isso elimina passos manuais para a demonstracao e garante que o catalogo esteja pronto ao subir a aplicacao.',
        ],
      },
      { type: 'heading', text: 'Persistencia e artefatos mantidos' },
      {
        type: 'table',
        headers: ['Tabela / artefato', 'Finalidade'],
        rows: [
          ['chat_sessions', 'Ciclo de vida das sessoes de chat'],
          ['chat_messages', 'Mensagens da conversa com ordenacao por sequencia'],
          ['conversation_metrics', 'Metricas operacionais por turno de chat'],
          ['agent_session_evaluations', 'Avaliacoes persistidas por sessao'],
          ['prompt_registry_entries', 'Chaves de prompts registradas'],
          ['prompt_versions', 'Versoes de prompt e indicacao da ativa'],
          ['course_catalog_entries', 'Catalogo relacional bootstrapado do dataset'],
          ['knowledge_documents', 'Documentos de conhecimento do recorte de RAG'],
          ['knowledge_chunks', 'Chunks associados aos documentos'],
          ['metrics_jobs', 'Historico de jobs de export e analise'],
          ['MinIO conversations bucket', 'Objetos JSON com exportacao de conversas para analise'],
        ],
      },
    ],
  },
  {
    anchor: 'dataset',
    title: 'Contexto Institucional e Dados Fake',
    blocks: [
      {
        type: 'paragraph',
        text: 'O MVP usa um contexto institucional ficticio, mas estruturado o suficiente para sustentar o fluxo de recomendacao e o RAG. Esse material continua presente na codebase em services/back-end/institution-profile.md.',
      },
      {
        type: 'table',
        headers: ['Elemento', 'Descricao'],
        rows: [
          ['Instituicao', 'Instituto Horizonte Digital'],
          ['Portfolio', '20 cursos ficticios entre graduacao, pos-graduacao e MBA'],
          ['Modalidades', 'EAD e Remoto'],
          ['Posicionamento', 'Formacao profissional flexivel, conectada ao mercado e orientada a empregabilidade'],
          ['Abrangencia', 'Nacional, com atendimento consultivo e foco em transicao de carreira e desenvolvimento profissional'],
        ],
      },
      { type: 'heading', text: 'Agente institucional: Clara' },
      {
        type: 'paragraph',
        text: 'Clara e a assistente virtual do Instituto Horizonte Digital. Ela atua como primeira camada de relacionamento, identifica o momento do aluno, recomenda cursos aderentes e explica diferencas entre nivel de formacao, modalidade e aplicacao no mercado.',
      },
      {
        type: 'list',
        items: [
          'Tom de voz: consultivo, cordial, seguro, direto e empatico sem excesso de informalidade.',
          'Objetivo: reduzir duvida inicial, apoiar comparacao entre cursos e indicar proximos passos coerentes.',
          'Escopo ideal: explicar portfolio, modalidades, aplicabilidade profissional e trilha academica.',
          'Encaminhamento para humano: condicoes comerciais especificas, bolsa, pagamento, documentacao e temas fora do catalogo.',
        ],
      },
    ],
  },
  {
    anchor: 'prototipo',
    title: 'Prototipo Funcional',
    blocks: [
      {
        type: 'paragraph',
        text: 'A entrega final contempla o minimo pedido pelo teste e vai alem: alem da analise estruturada, ha chat multi-sessao, audio, dashboards de metricas, registro de prompts e infraestrutura local para reproducao.',
      },
      { type: 'heading', text: 'Fluxo real de demonstracao' },
      {
        type: 'list',
        items: [
          '1. Criar ou listar uma sessao de chat.',
          '2. Enviar mensagem textual ou arquivo de audio para a Clara.',
          '3. Persistir mensagens, metricas e metadados da sessao.',
          '4. Exportar conversas para object store.',
          '5. Rodar o agente avaliador sobre os JSONs exportados.',
          '6. Consultar sumarios, tokens, jobs e avaliacoes unitarias na pagina de Metrics.',
          '7. Consultar e operar prompts ativos na pagina de LLMOps.',
        ],
      },
      { type: 'heading', text: 'Exemplo de execucao da analise estruturada' },
      {
        type: 'code',
        language: 'bash',
        text: `# 1) Exportar conversas persistidas
curl -X POST http://0.0.0.0:8000/api/conversations/export

# 2) Rodar analise do agente sobre as sessoes exportadas
curl -X POST http://0.0.0.0:8000/api/evaluation/agent-analysis \\
  -H "Content-Type: application/json" \\
  -d '{
    "api_key": "key_xxx",
    "model_id": "us.anthropic.claude-sonnet-4-6"
  }'`,
      },
      { type: 'heading', text: 'Resposta estruturada (shape implementado)' },
      {
        type: 'code',
        language: 'json',
        text: `{
  "evaluations": [
    {
      "session_id": "11111111-1111-1111-1111-111111111111",
      "satisfaction": "bom",
      "effort_score": 2,
      "understanding_score": 2,
      "resolution_score": 2,
      "evidences": ["Trecho curto da conversa"],
      "objetivo_cliente": "Migrar para area de tecnologia",
      "mudanca_comportamental": "positiva",
      "sinal_fechamento": "positivo",
      "prompt_tokens": 890,
      "completion_tokens": 210,
      "total_tokens": 1100,
      "prompt_injection_detected": false,
      "injection_snippets": []
    }
  ],
  "summary": {
    "total_evaluated": 1,
    "count_bom": 1,
    "count_neutro": 0,
    "count_ruim": 0,
    "pct_bom": 100.0,
    "pct_neutro": 0.0,
    "pct_ruim": 0.0,
    "indice_ia_operadora": 100.0,
    "avg_effort": 2.0,
    "avg_understanding": 2.0,
    "avg_resolution": 2.0,
    "total_tokens_used": 1100,
    "count_mudanca_positiva": 1,
    "count_mudanca_neutra": 0,
    "count_mudanca_negativa": 0,
    "count_injection_detected": 0,
    "pct_injection_detected": 0.0
  }
}`,
      },
    ],
  },
  {
    anchor: 'credito',
    title: 'Sistema de Credito e Proxy LLM',
    blocks: [
      {
        type: 'paragraph',
        text: 'Como o gateway de inferencia usa minha AWS pessoal, foi implementado um sistema de creditos por chave para isolar consumo e evitar impacto aberto direto na conta principal. Esse ponto aparecia no diff antigo e continua sendo central para reproduzir o MVP com seguranca operacional minima.',
      },
      {
        type: 'list',
        items: [
          'O front armazena a API key do usuario/testador.',
          'O saldo e consultado em GET /api/credits/balance com header x-api-key.',
          'Toda inferencia segue pelo proxy HTTP, nao diretamente pelo provider.',
          'A chamada de inferencia exige x-api-key e x-idempotency-key no contrato do proxy.',
          'Regra de credito: 1 invoke = 1 credito, com refund automatico se o provider falhar.',
        ],
      },
      { type: 'heading', text: 'Contrato principal do proxy' },
      {
        type: 'table',
        headers: ['Item', 'Valor atual'],
        rows: [
          ['Base URL validada', 'https://kviwmiapph.execute-api.us-east-1.amazonaws.com/v1'],
          ['Invoke', 'POST /v1/llm/invoke'],
          ['Balance', 'GET /v1/credits/balance'],
          ['Header obrigatorio', 'x-api-key'],
          ['Header obrigatorio', 'x-idempotency-key'],
          ['Modelos permitidos', 'Sonnet 4.6, Haiku 4.5, Minimax M2.5 e Nova 2 Lite'],
        ],
      },
      { type: 'heading', text: 'Erros e garantias operacionais' },
      {
        type: 'list',
        items: [
          '400: missing_idempotency_key, missing_input, model_not_allowed.',
          '401: missing_api_key ou unauthorized.',
          '402: insufficient_credit.',
          '429: provider_throttled.',
          '500: credit_service_error.',
          '502: provider_error.',
          'Se o provider falha apos reserva, o credito e estornado.',
        ],
      },
      {
        type: 'image',
        src: '/docs/credit-system.png',
        alt: 'Sistema de Credito',
        caption: 'Fluxo de credito e invocacao do proxy de LLM.',
      },
    ],
  },
  {
    anchor: 'observabilidade',
    title: 'Metricas, Observabilidade e LLMOps',
    blocks: [
      {
        type: 'paragraph',
        text: 'A pagina de Metrics e a stack de observabilidade cobrem tanto indicadores de qualidade da IA quanto sinais operacionais do sistema. Os drafts antigos ja apontavam para isso, e a versao final manteve o que esta de fato implementado hoje.',
      },
      { type: 'heading', text: 'Metricas de qualidade acompanhadas' },
      {
        type: 'list',
        items: [
          'Distribuicao de satisfacao: bom, neutro, ruim.',
          'Indice IA Operadora.',
          'Medias de esforco, entendimento e resolucao.',
          'Mudanca comportamental agregada.',
          'Incidencia de prompt injection e snippets detectados.',
        ],
      },
      { type: 'heading', text: 'Metricas operacionais acompanhadas' },
      {
        type: 'list',
        items: [
          'Total de sessoes, mensagens e hits de RAG.',
          'Tokens totais, serie temporal e distribuicao por modelo.',
          'Status do ultimo job de export.',
          'Status do ultimo job de analise.',
          'Healthcheck e scraping Prometheus via /metrics.',
        ],
      },
      { type: 'heading', text: 'Endpoints que a pagina de Metrics consome hoje' },
      {
        type: 'table',
        headers: ['Endpoint', 'Finalidade'],
        rows: [
          ['GET /api/metrics/summary', 'Cards operacionais de sessoes, mensagens e rag hits'],
          ['GET /api/metrics/tokens-report', 'Serie temporal e distribuicao de tokens por modelo'],
          ['GET /api/metrics/jobs/export/latest', 'Ultimo job de exportacao'],
          ['GET /api/metrics/jobs/analysis/latest', 'Ultimo job de analise'],
          ['GET /api/evaluation/summary', 'Resumo agregado da avaliacao'],
          ['GET /api/evaluation/agent-sessions', 'Lista de avaliacoes unitarias'],
          ['GET /api/evaluation/agent-sessions/{session_id}', 'Detalhe de uma sessao avaliada'],
        ],
      },
      { type: 'heading', text: 'LLMOps implementado no MVP' },
      {
        type: 'list',
        items: [
          'Dois prompts operacionais principais: chat-agent-system e nps-agent-system.',
          'Cadastro de prompt base.',
          'Criacao de novas versoes.',
          'Consulta da versao ativa.',
          'Ativacao explicita de versao para testes e operacao.',
        ],
      },
      { type: 'heading', text: 'Direcoes registradas nos drafts' },
      {
        type: 'list',
        items: [
          'Esteira de drifting para detectar degradacao da qualidade.',
          'Esteira de anotacao para novas conversas.',
          'Esteira de prompt engineering e validacao offline/online.',
          'Possivel ampliacao para OTEL, tracing e visao mais rica de latencia.',
        ],
      },
    ],
  },
  {
    anchor: 'stack',
    title: 'Stack Utilizada',
    blocks: [
      {
        type: 'table',
        headers: ['Componente', 'Tecnologia', 'Justificativa'],
        rows: [
          ['Backend', 'Python 3.12 + FastAPI', 'Produtividade alta e ecossistema maduro para IA e APIs'],
          ['Orquestracao de agentes', 'LangGraph', 'Fluxos explicitos e rastreaveis para chat e avaliacao'],
          ['Persistencia', 'SQLAlchemy + PostgreSQL', 'Estabilidade, relacional forte e baixo atrito para evolucao'],
          ['Frontend', 'React + TypeScript + Vite + Bun', 'Rapidez para construir dashboard, chat e docs com tipagem forte'],
          ['Object store', 'MinIO', 'Compatibilidade S3 e facilidade para execucao local'],
          ['Transcricao', 'Whisper ONNX (whisper-small)', 'Recorte local e reproduzivel para demonstrar audio sem depender de API externa'],
          ['Observabilidade', 'Prometheus + Loki + Promtail + Grafana', 'Pilha simples e suficiente para o MVP operacional'],
          ['Gateway de inferencia', 'Proxy HTTP AWS com API key e creditos', 'Controle de consumo, allowlist e isolamento da conta pessoal'],
          ['Arquitetura de codigo', 'MASA Framework', 'Separacao clara de camadas; framework desenvolvido por mim.'],
        ],
      },
    ],
  },
  {
    anchor: 'processo',
    title: 'Processo de Desenvolvimento',
    blocks: [
      {
        type: 'paragraph',
        text: 'O desenvolvimento foi conduzido com uso intensivo de coding agents via Codex CLI e GitHub Copilot CLI. O objetivo foi acelerar implementacao, documentacao, revisao e depuracao sem abrir mao de validacao manual e checks tecnicos.',
      },
      { type: 'heading', text: 'Modelos utilizados' },
      {
        type: 'list',
        items: ['GPT-5.4', 'GPT-5.3 Codex'],
      },
      { type: 'heading', text: 'Skills e ferramentas aplicadas' },
      {
        type: 'table',
        headers: ['Ferramenta', 'Uso'],
        rows: [
          ['MASA Framework skill', 'Aderencia ao padrao de camadas no backend (framework desenvolvido por mim).'],
          ['Interface Design skill', 'Construcao e revisao de interfaces do frontend com a skill [interface-design](https://github.com/Dammyjay93/interface-design).'],
          ['Chrome DevTools MCP', 'Inspecao e depuracao da UI diretamente no browser com [chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp).'],
          ['code-quality skill', 'Auditoria e correcao de qualidade de codigo com [qlty](https://github.com/qltysh/qlty).'],
          ['code-review agent', 'Revisao de seguranca e logica antes da consolidacao.'],
        ],
      },
      { type: 'heading', text: 'Sequencia executada no case' },
      {
        type: 'list',
        items: [
          'Leitura da proposta e das conversas de exemplo.',
          'Definicao da metodologia de avaliacao pela perspectiva do cliente.',
          'Rascunho de arquitetura, stack e estrategia de escala em docs/drafts.',
          'Implementacao do MVP inline com chat, audio, metricas, avaliacao e llmops.',
          'Desenho da proposta batch e consolidacao de custos.',
          'Revisao final do documento, da pagina de docs e do racional tecnico.',
        ],
      },
    ],
  },
  {
    anchor: 'uso-ia',
    title: 'Registro de Uso de IA',
    blocks: [
      { type: 'heading', text: 'Ferramentas e modelos usados' },
      {
        type: 'list',
        items: ['Codex CLI', 'GitHub Copilot CLI', 'GPT-5.4', 'GPT-5.3 Codex'],
      },
      { type: 'heading', text: 'Partes em que a IA foi utilizada' },
      {
        type: 'list',
        items: [
          'Exploracao e comparacao de alternativas arquiteturais.',
          'Implementacao de trechos de backend e frontend.',
          'Refinamento de prompts, criterios de avaliacao e documentacao.',
          'Revisao tecnica de fluxos, contratos e coerencia da entrega.',
        ],
      },
      { type: 'heading', text: 'Como as sugestoes foram validadas' },
      {
        type: 'list',
        items: [
          'Execucao de testes no projeto.',
          'Uso do qlty CLI e checks de qualidade.',
          'Confrontacao com os requisitos do PDF.',
          'Conferencia contra o comportamento real da codebase e dos endpoints implementados.',
          'Revisao manual de coerencia tecnica antes da consolidacao final.',
        ],
      },
    ],
  },
]

// -----------------------------------------------------------------------
// FIM DO CONTEUDO
// -----------------------------------------------------------------------

const INLINE_LINK_PATTERN = /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)|(https?:\/\/[^\s)]+)/g

function renderInlineText(text: string) {
  const nodes: ReactNode[] = []
  let lastIndex = 0
  let key = 0

  for (const match of text.matchAll(INLINE_LINK_PATTERN)) {
    const matchIndex = match.index ?? 0
    if (matchIndex > lastIndex) {
      nodes.push(text.slice(lastIndex, matchIndex))
    }

    const label = match[1] ?? match[3] ?? ''
    const url = match[2] ?? match[3] ?? ''
    nodes.push(
      <a
        key={`link-${key}`}
        href={url}
        target="_blank"
        rel="noreferrer"
        className="underline decoration-[#00a884]/40 decoration-2 underline-offset-2 hover:text-[#0b8469]"
      >
        {label}
      </a>,
    )
    key += 1
    lastIndex = matchIndex + match[0].length
  }

  if (lastIndex < text.length) {
    nodes.push(text.slice(lastIndex))
  }

  return nodes
}

function renderBlock(block: Block, idx: number) {
  switch (block.type) {
    case 'paragraph':
      return (
        <p key={idx} className="text-sm leading-relaxed text-[#3b4a54]">
          {renderInlineText(block.text)}
        </p>
      )
    case 'heading':
      return (
        <h3 key={idx} className="mt-5 text-sm font-semibold text-[#111b21]">
          {block.text}
        </h3>
      )
    case 'list':
      return (
        <ul key={idx} className="space-y-1.5 pl-4">
          {block.items.map((item, i) => (
            <li key={i} className="list-disc text-sm leading-relaxed text-[#3b4a54]">
              {renderInlineText(item)}
            </li>
          ))}
        </ul>
      )
    case 'table':
      return (
        <div key={idx} className="overflow-x-auto rounded-xl border border-black/6">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-[#f0f2f5]">
                {block.headers.map((h, i) => (
                  <th
                    key={i}
                    className="px-4 py-2.5 text-left text-xs font-semibold text-[#111b21]"
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {block.rows.map((row, i) => (
                <tr key={i} className="border-t border-black/6 bg-white">
                  {row.map((cell, j) => (
                    <td key={j} className="px-4 py-2.5 text-xs leading-relaxed text-[#3b4a54]">
                      {renderInlineText(cell)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )
    case 'code':
      return (
        <pre
          key={idx}
          className="overflow-x-auto rounded-xl bg-[#1e1e2e] px-4 py-3 text-xs leading-relaxed text-[#cdd6f4]"
        >
          <code>{block.text}</code>
        </pre>
      )
    case 'image':
      return (
        <figure key={idx} className="space-y-2">
          <img
            src={block.src}
            alt={block.alt}
            className="w-full rounded-xl border border-black/8 bg-white"
            loading="lazy"
          />
          {block.caption ? (
            <figcaption className="text-xs text-[#667781]">{block.caption}</figcaption>
          ) : null}
        </figure>
      )
  }
}

export function DocsPage() {
  return (
    <div className="flex-1 overflow-y-auto">
      <div className="flex min-h-full">
        <aside className="hidden w-56 shrink-0 border-r border-black/6 bg-[#f0f2f5] lg:block">
          <div className="sticky top-0 p-5">
            <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-[#667781]">
              Conteudo
            </p>
            <nav className="space-y-1">
              {SECTIONS.map((s) => (
                <a
                  key={s.anchor}
                  href={`#${s.anchor}`}
                  className="block rounded-lg px-2 py-1.5 text-xs text-[#3b4a54] transition hover:bg-white hover:text-[#111b21]"
                >
                  {s.title}
                </a>
              ))}
            </nav>
          </div>
        </aside>

        <main className="flex-1 p-6 lg:p-10">
          <div className="mx-auto max-w-3xl">
            <div className="mb-10 flex items-center gap-3">
              <div className="flex size-10 items-center justify-center rounded-xl bg-[#00a884]/10">
                <BookOpen className="size-5 text-[#00a884]" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-[#111b21]">Solution Docs</h1>
                <p className="text-sm text-[#667781]">
                  Documento final de solucao tecnica e de produto da plataforma Mais A Educ
                </p>
              </div>
            </div>

            <div className="space-y-12">
              {SECTIONS.map((section) => (
                <section key={section.anchor} id={section.anchor}>
                  <h2 className="mb-4 border-b border-black/6 pb-2 text-base font-semibold text-[#111b21]">
                    {section.title}
                  </h2>
                  <div className="space-y-4">
                    {section.blocks.map((block, idx) => renderBlock(block, idx))}
                  </div>
                </section>
              ))}
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
