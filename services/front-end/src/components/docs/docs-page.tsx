import { BookOpen } from 'lucide-react'

// -----------------------------------------------------------------------
// CONTEUDO DA DOCUMENTACAO
// Para editar qualquer secao, basta localizar o item correspondente neste
// array e alterar os campos title, anchor e blocks.
// -----------------------------------------------------------------------

type Block =
  | { type: 'paragraph'; text: string }
  | { type: 'heading'; text: string }
  | { type: 'list'; items: string[] }
  | { type: 'table'; headers: string[]; rows: string[][] }
  | { type: 'code'; language: string; text: string }

interface DocSection {
  anchor: string
  title: string
  blocks: Block[]
}

const SECTIONS: DocSection[] = [
  {
    anchor: 'contexto',
    title: 'Contexto e Proposta',
    blocks: [
      {
        type: 'paragraph',
        text: 'Este projeto e uma resposta tecnica a um teste pratico para a posicao de Coordenador de IA. O desafio central consistia em avaliar a qualidade das conversas conduzidas por uma IA operadora em um contexto de atendimento educacional.',
      },
      {
        type: 'paragraph',
        text: 'A IA operadora se chama Clara e atende potenciais alunos do Instituto Horizonte Digital, uma instituicao ficticia de ensino superior. Clara orienta alunos sobre cursos de graduacao, pos-graduacao e MBA, responde duvidas sobre modalidades e encaminha para atendimento humano quando necessario.',
      },
      {
        type: 'paragraph',
        text: 'O problema proposto era: dado um conjunto de conversas entre Clara e clientes reais, como medir se a IA operadora esta entregando um bom atendimento? A solucao construida aborda esse problema com uma plataforma de LLMOps que inclui um agente de avaliacao, dashboard de metricas, chat de demonstracao e registro de prompts.',
      },
      {
        type: 'heading',
        text: 'Objetivos do projeto',
      },
      {
        type: 'list',
        items: [
          'Avaliar a qualidade das conversas da IA operadora com base em metricas inspiradas em NPS',
          'Medir satisfacao do cliente, esforco, entendimento do objetivo e resolucao util',
          'Rastrear consumo de tokens por sessao e ao longo do tempo',
          'Oferecer um dashboard operacional para acompanhamento das metricas',
          'Demonstrar o fluxo completo de chat com RAG sobre catalogo de cursos',
          'Suportar versionamento e ativacao de prompts do agente',
        ],
      },
    ],
  },
  {
    anchor: 'fluxo-inicial',
    title: 'Fluxo de Trabalho Inicial',
    blocks: [
      {
        type: 'paragraph',
        text: 'O processo comecou com a leitura atenta do material do case e de 20 exemplos de conversas fornecidos. A partir dessa analise, foram levantadas hipoteses, anotacoes de padroes observados e duvidas operacionais que guiaram as decisoes de arquitetura e metodologia.',
      },
      {
        type: 'heading',
        text: 'Steps iniciais',
      },
      {
        type: 'list',
        items: [
          'Leitura e avaliacao da proposta do case',
          'Analise das 20 conversas de exemplo fornecidas',
          'Identificacao de padroes de sucesso e falha nas conversas',
          'Definicao das regras de metrificacao baseadas na perspectiva do cliente',
          'Planejamento de tecnologia, arquitetura e escopo',
        ],
      },
      {
        type: 'heading',
        text: 'Hipoteses e anotacoes iniciais',
      },
      {
        type: 'list',
        items: [
          'A proposta e essencialmente um NPS aplicado a IA operadora',
          'A leitura das conversas deve ser feita pela perspectiva do cliente, nao da IA',
          'Verificar o esforco do cliente para obter o que pediu',
          'Identificar se o objetivo da conversa foi atingido',
          'Verificar se e comum os clientes agradecerem ou reclamarem no final, como sinal de conclusao',
          'Identificar possivel prompt injection e alteracoes comportamentais',
          'Rastrear numero medio de tokens por cliente e por mensagem da IA',
          'Um usuario pode ter varias sessoes',
          'Transferencia para humano nao e necessariamente ruim, depende do contexto',
          'Cursos mais buscados como dado extra de inteligencia operacional',
        ],
      },
      {
        type: 'heading',
        text: 'Duvidas levantadas',
      },
      {
        type: 'list',
        items: [
          'Quantos clientes usam a solucao em producao?',
          'Transferencias para humano devem ser consideradas como conclusao bem-sucedida? (Assumido que sim)',
          'Qual a escala de usuarios esperada no curto e medio prazo?',
        ],
      },
    ],
  },
  {
    anchor: 'metodologia',
    title: 'Metodologia de Avaliacao',
    blocks: [
      {
        type: 'paragraph',
        text: 'A metodologia de avaliacao foi desenhada para medir a qualidade percebida pelo cliente nas conversas com a IA operadora. A unidade de analise e a sessao, identificada por um sessionId. Cada sessao gera uma classificacao principal e metricas auxiliares de diagnostico.',
      },
      {
        type: 'heading',
        text: 'Metrica principal: satisfacao do cliente',
      },
      {
        type: 'paragraph',
        text: 'A satisfacao reflete se o cliente sentiu que foi compreendido, avancou no que buscava, teve baixo atrito e recebeu resposta util ou encaminhamento coerente.',
      },
      {
        type: 'table',
        headers: ['Valor', 'Classe', 'Regra pratica'],
        rows: [
          ['3', 'Bom', 'Cliente atingiu o objetivo ou aceitou o proximo passo; conversa fluiu com baixo atrito'],
          ['2', 'Neutro', 'Houve progresso, mas com pequenas friccoes, lacunas ou conclusao parcial'],
          ['1', 'Ruim', 'Cliente precisou insistir, corrigir a IA, repetir contexto ou saiu sem resposta util'],
        ],
      },
      {
        type: 'heading',
        text: 'Indice da IA Operadora',
      },
      {
        type: 'paragraph',
        text: 'Apos classificar cada sessao, o indice consolidado e calculado como:',
      },
      {
        type: 'code',
        language: 'text',
        text: 'INDICE_IA_OPERADORA = % bom - % ruim',
      },
      {
        type: 'paragraph',
        text: 'Esse indicador resume a experiencia geral da operacao em logica inspirada em NPS, mas nao substitui as metricas auxiliares.',
      },
      {
        type: 'heading',
        text: 'Metricas auxiliares',
      },
      {
        type: 'table',
        headers: ['Metrica', 'Escala', 'Peso sugerido'],
        rows: [
          ['Satisfacao do cliente', 'Ruim / Neutro / Bom (1-3)', '40%'],
          ['Esforco do cliente', '1 a 5 (1 = baixo esforco)', '20%'],
          ['Entendimento do objetivo', '0 a 2', '20%'],
          ['Resolucao ou avanco util', '0 a 2', '20%'],
          ['Mudanca comportamental', 'Positiva / Neutra / Negativa', 'Ajuste qualitativo'],
        ],
      },
      {
        type: 'heading',
        text: 'Padroes que reduzem nota',
      },
      {
        type: 'list',
        items: [
          'Perguntar algo que o cliente ja havia respondido',
          'Duplicar resposta ou responder duas vezes no mesmo ponto',
          'Trocar o contexto do cliente por outro tema proximo mas incorreto',
          'Insistir em transferencia quando o cliente quer apenas informacao objetiva',
          'Nao reconhecer correcoes explicitas do cliente',
        ],
      },
      {
        type: 'heading',
        text: 'Padroes que elevam nota',
      },
      {
        type: 'list',
        items: [
          'Capturar rapidamente o contexto profissional do cliente',
          'Relacionar o curso ao objetivo declarado',
          'Ser transparente quando nao puder informar algo',
          'Encaminhar para proximo passo coerente com o momento da conversa',
        ],
      },
    ],
  },
  {
    anchor: 'arquitetura',
    title: 'Arquitetura do Sistema',
    blocks: [
      {
        type: 'paragraph',
        text: 'O backend foi organizado com base em MASA (Modular Agentic Semantic Architecture), uma estrutura de camadas que prioriza fronteiras claras, injecao explicita de dependencias e evolucao incremental dos adapters.',
      },
      {
        type: 'heading',
        text: 'Camadas do backend',
      },
      {
        type: 'table',
        headers: ['Camada', 'Responsabilidade'],
        rows: [
          ['domain_models', 'Entidades, IDs tipados, contratos e excecoes de dominio'],
          ['engines', 'Regras puras e deterministicas, sem I/O'],
          ['integrations', 'Adapters de infraestrutura que implementam contratos do dominio'],
          ['services', 'Orquestracao dos casos de uso, combinando engines e integracoes'],
          ['delivery', 'Handlers HTTP e schemas de entrada e saida'],
          ['bootstrap', 'Wiring explicito das dependencias via construtor'],
        ],
      },
      {
        type: 'heading',
        text: 'Estrutura de diretorios do backend',
      },
      {
        type: 'code',
        language: 'text',
        text: `src/app
├── bootstrap/
│   └── container.py
├── delivery/
│   ├── http/
│   └── schemas/
├── domain_models/
│   ├── agent/
│   ├── chat/
│   ├── common/
│   ├── evaluation/
│   ├── indexing/
│   ├── metrics/
│   ├── prompt/
│   └── rag/
├── engines/
│   ├── evaluation/
│   ├── indexing/
│   ├── metrics/
│   └── prompt/
├── integrations/
│   ├── database/
│   ├── external_apis/
│   ├── llm/
│   ├── object_store/
│   └── vector_store/
├── services/
│   ├── agent/
│   ├── chat/
│   ├── evaluation/
│   ├── indexing/
│   ├── metrics/
│   ├── prompt/
│   └── rag/
└── main.py`,
      },
      {
        type: 'heading',
        text: 'Diretrizes para evolucao',
      },
      {
        type: 'paragraph',
        text: 'Ao adicionar novas features, a ordem de implementacao por camada deve ser respeitada: domain_models, engines, integrations, services, delivery. Importar adapters de integrations diretamente em handlers, colocar regra de negocio em delivery ou esconder dependencias em globais sao antipadroes a evitar.',
      },
    ],
  },
  {
    anchor: 'stack',
    title: 'Stack Tecnologica',
    blocks: [
      {
        type: 'paragraph',
        text: 'A escolha da stack priorizou produtividade, estabilidade e facilidade de manutencao no contexto de um MVP com possibilidade de evolucao incremental.',
      },
      {
        type: 'table',
        headers: ['Componente', 'Tecnologia', 'Justificativa'],
        rows: [
          ['Backend', 'Python 3.12 + FastAPI', 'Sem necessidade de performance massiva; ecossistema de LLM mais maduro'],
          ['Agente', 'LangChain + LangGraph', 'Melhor controle de fluxo do mercado para agentes'],
          ['Frontend', 'TypeScript + React + Bun + Shadcn', 'Rapidez de desenvolvimento, tipagem forte, componentes acessiveis'],
          ['Banco de dados', 'PostgreSQL 16', 'Estabilidade, suporte a JSONB e vetores, amplamente conhecido'],
          ['ORM', 'SQLAlchemy', 'Maturidade, suporte a migracao e compatibilidade com testes via SQLite'],
          ['Vector store', 'Qdrant (em memoria no MVP)', 'Bom custo-beneficio para busca semantica'],
          ['Object store', 'MinIO', 'Compativel com S3, facil de rodar localmente e em cloud'],
          ['Conteinerizacao', 'Docker Compose com imagens Alpine', 'Leveza, reproducibilidade, facilidade de onboarding'],
          ['LLM Gateway', 'Proxy HTTP na AWS API Gateway', 'Sistema de creditos e autenticacao ja configurado'],
        ],
      },
      {
        type: 'heading',
        text: 'Modelos de linguagem suportados',
      },
      {
        type: 'list',
        items: [
          'us.anthropic.claude-sonnet-4-6',
          'us.anthropic.claude-haiku-4-5-20251001-v1:0',
          'minimax.minimax-m2.5',
          'us.amazon.nova-2-lite-v1:0',
        ],
      },
    ],
  },
  {
    anchor: 'fluxos',
    title: 'Fluxos do Sistema',
    blocks: [
      {
        type: 'paragraph',
        text: 'O backend expoe uma API HTTP que coordena cinco fluxos principais. Cada fluxo segue a ordem de camadas MASA e tem fronteiras claras entre dominio, logica pura e infraestrutura.',
      },
      {
        type: 'table',
        headers: ['Fluxo', 'O que faz'],
        rows: [
          ['Chat', 'Recebe mensagem, recupera contexto via RAG, gera resposta do agente e registra metricas'],
          ['Indexing', 'Importa dataset de cursos, gera chunks e persiste documentos e chunks'],
          ['Evaluation', 'Avalia uma sessao existente com base nas mensagens trocadas'],
          ['Metrics', 'Expoe healthcheck e resumo agregado das metricas coletadas'],
          ['Prompt Registry', 'Cadastra prompts, cria versoes e ativa a versao vigente'],
        ],
      },
      {
        type: 'heading',
        text: 'Fluxo de chat detalhado',
      },
      {
        type: 'list',
        items: [
          '1. delivery/http/chat_handler.py valida a requisicao HTTP',
          '2. delivery/schemas/chat_schemas.py transforma o payload em ChatRequest',
          '3. services/chat/chat_service.py recupera a sessao, delega ao agente e registra metricas',
          '4. services/agent/langgraph_course_agent.py executa o fluxo do agente em LangGraph',
          '5. services/rag/rag_service.py recupera contexto do catalogo de cursos',
          '6. integrations/external_apis/llm_proxy_gateway_client.py encaminha prompt e api-key para o proxy AWS',
        ],
      },
      {
        type: 'heading',
        text: 'Endpoints disponíveis',
      },
      {
        type: 'table',
        headers: ['Metodo', 'Rota', 'Descricao'],
        rows: [
          ['POST', '/api/chat/messages', 'Envia mensagem para uma sessao e retorna resposta do agente'],
          ['POST', '/api/indexing/universities/import', 'Importa registros de universidades e gera chunks'],
          ['GET', '/api/metrics/health', 'Healthcheck simples'],
          ['GET', '/api/metrics/summary', 'Resumo agregado de sessoes, mensagens e hits de RAG'],
          ['POST', '/api/evaluation/sessions/{session_id}', 'Avalia uma sessao existente'],
          ['GET', '/api/prompt-registry/prompts', 'Lista prompts cadastrados'],
          ['POST', '/api/prompt-registry/prompts', 'Cadastra um novo prompt'],
          ['POST', '/api/prompt-registry/prompts/{key}/versions', 'Cria nova versao de um prompt'],
          ['GET', '/api/prompt-registry/prompts/{key}/active', 'Recupera a versao ativa'],
          ['POST', '/api/prompt-registry/prompts/{key}/active', 'Ativa uma versao especifica'],
        ],
      },
    ],
  },
  {
    anchor: 'infra',
    title: 'Infraestrutura e Ambiente',
    blocks: [
      {
        type: 'paragraph',
        text: 'O ambiente de desenvolvimento e levantado via Docker Compose a partir da raiz do repositorio. O compose centraliza os containers compartilhados entre frontend e backend.',
      },
      {
        type: 'heading',
        text: 'Servicos do Docker Compose',
      },
      {
        type: 'table',
        headers: ['Servico', 'Imagem', 'Porta padrao'],
        rows: [
          ['PostgreSQL', 'postgres:16-alpine', '5432'],
          ['MinIO', 'minio/minio:latest', '9000 (API), 9001 (Console)'],
        ],
      },
      {
        type: 'heading',
        text: 'Variaveis de ambiente do backend',
      },
      {
        type: 'table',
        headers: ['Variavel', 'Padrao', 'Descricao'],
        rows: [
          ['DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/mais_a_educ', 'Conexao com o Postgres'],
          ['DATASETS_DIR', 'services/datasets', 'Caminho do diretorio de datasets de cursos'],
          ['INDEXING_BOOTSTRAP_ENABLED', 'true', 'Habilita a carga inicial do catalogo de cursos no startup'],
          ['LLM_PROXY_BASE_URL', 'https://kviwmiapph.execute-api.us-east-1.amazonaws.com', 'URL base do proxy de LLM'],
        ],
      },
      {
        type: 'heading',
        text: 'Bootstrap de cursos no startup',
      },
      {
        type: 'paragraph',
        text: 'No startup da API, o backend le todos os arquivos Markdown em services/datasets/, parseia cada curso e persiste via upsert por slug na tabela course_catalog_entries. Isso garante que o catalogo esteja carregado quando a API iniciar, sem necessidade de passo manual.',
      },
      {
        type: 'heading',
        text: 'Tabelas transacionais',
      },
      {
        type: 'table',
        headers: ['Tabela', 'Finalidade'],
        rows: [
          ['chat_sessions', 'Representa a sessao de conversa e seu ciclo de vida'],
          ['chat_messages', 'Cada mensagem persistida dentro de uma sessao'],
          ['conversation_metrics', 'Metricas gravadas a cada turno do fluxo de chat'],
          ['prompt_registry_entries', 'Prompts cadastrados com chave normalizada'],
          ['prompt_versions', 'Versoes de cada prompt com suporte a ativacao'],
          ['course_catalog_entries', 'Catalogo de cursos carregado via bootstrap dos datasets Markdown'],
        ],
      },
      {
        type: 'heading',
        text: 'Como executar localmente',
      },
      {
        type: 'code',
        language: 'bash',
        text: `# Subir infra
docker compose up -d postgres

# Backend
cd services/back-end
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/mais_a_educ"
python run_local.py

# Frontend
cd services/front-end
bun install
bun run dev`,
      },
    ],
  },
  {
    anchor: 'llm-proxy',
    title: 'LLM Proxy e Creditos',
    blocks: [
      {
        type: 'paragraph',
        text: 'O backend nao chama provedores de LLM diretamente. Todas as chamadas passam por um proxy HTTP hospedado na AWS API Gateway, que gerencia autenticacao por chave de API e um sistema de creditos.',
      },
      {
        type: 'heading',
        text: 'Contrato de invocacao',
      },
      {
        type: 'table',
        headers: ['Campo', 'Valor'],
        rows: [
          ['Metodo', 'POST'],
          ['Rota', '/v1/llm/invoke'],
          ['Header obrigatorio', 'x-api-key'],
          ['Header obrigatorio', 'x-idempotency-key'],
        ],
      },
      {
        type: 'heading',
        text: 'Regras de credito',
      },
      {
        type: 'list',
        items: [
          '1 invocacao = 1 credito',
          'Fluxo interno: reserve, invoke provider, confirm',
          'Se o provider falhar, o credito e estornado automaticamente',
          'Saldo disponivel consultado via GET /v1/credits/balance com header x-api-key',
        ],
      },
      {
        type: 'heading',
        text: 'Codigos de erro do proxy',
      },
      {
        type: 'table',
        headers: ['Status', 'Codigo'],
        rows: [
          ['400', 'missing_idempotency_key, missing_input, model_not_allowed'],
          ['401', 'missing_api_key, unauthorized'],
          ['402', 'insufficient_credit'],
          ['429', 'provider_throttled'],
          ['500', 'credit_service_error'],
          ['502', 'provider_error'],
        ],
      },
    ],
  },
  {
    anchor: 'dataset',
    title: 'Dataset Ficticio e Agente Clara',
    blocks: [
      {
        type: 'paragraph',
        text: 'Para o MVP, foi criado um conjunto de dados ficticio representando o Instituto Horizonte Digital, uma instituicao de ensino superior com foco em formacao profissional flexivel. O dataset simula o contexto real onde a IA operadora Clara atua.',
      },
      {
        type: 'heading',
        text: 'Portfolio academico',
      },
      {
        type: 'table',
        headers: ['Nivel', 'Quantidade', 'Exemplos'],
        rows: [
          ['Graduacao', '8 cursos', 'Analise e Desenvolvimento de Sistemas, Pedagogia, Ciencias Contabeis, Engenharia de Software'],
          ['Pos-graduacao', '6 cursos', 'Ciencia de Dados, Gestao Hospitalar, Direito Digital e Protecao de Dados'],
          ['MBA', '6 cursos', 'Gestao de Projetos, Lideranca e Gestao de Pessoas, Marketing Digital e Growth'],
        ],
      },
      {
        type: 'heading',
        text: 'Modalidades',
      },
      {
        type: 'list',
        items: [
          'EAD: formato com autonomia, trilhas digitais e acompanhamento academico online',
          'Remoto: formato com interacao ao vivo, encontros online programados e maior proximidade com docentes',
        ],
      },
      {
        type: 'heading',
        text: 'A agente Clara',
      },
      {
        type: 'paragraph',
        text: 'Clara e a agente virtual de atendimento do Instituto Horizonte Digital. Seu papel e entender o momento profissional do aluno, recomendar cursos aderentes ao objetivo declarado, explicar diferencas entre niveis e modalidades e encaminhar para atendimento humano quando necessario.',
      },
      {
        type: 'paragraph',
        text: 'O tom de voz da Clara deve ser consultivo, cordial, seguro, direto e empatico sem ser informal demais. O discurso comercial evita pressao e prioriza ajuda orientativa, relacionando sempre o curso ao objetivo declarado pelo aluno antes de sugerir matricula.',
      },
      {
        type: 'heading',
        text: 'Quando Clara deve transferir para humano',
      },
      {
        type: 'list',
        items: [
          'Pedidos de condicoes comerciais especificas',
          'Negociacao de bolsa ou condicoes de pagamento',
          'Necessidade de validacao documental',
          'Duvidas fora do escopo informativo do catalogo',
        ],
      },
    ],
  },
  {
    anchor: 'estimativas',
    title: 'Estimativas e Escala',
    blocks: [
      {
        type: 'paragraph',
        text: 'O planejamento de escala parte do calculo de tokens por requisicao de usuario para estimar o custo e a capacidade necessaria em diferentes cenarios de crescimento.',
      },
      {
        type: 'heading',
        text: 'Cenarios de escala',
      },
      {
        type: 'list',
        items: [
          'Escala inicial: ate 10.000 usuarios ativos, processamento inline (resposta sincrona)',
          'Escala media: considerar a cada 1.000 usuarios com N requisicoes, avaliar necessidade de filas',
          'Hiper-escala: arquitetura orientada a eventos, batch processing para avaliacao em massa',
        ],
      },
      {
        type: 'heading',
        text: 'Batch Process vs Inline Process',
      },
      {
        type: 'table',
        headers: ['Modo', 'Quando usar', 'Vantagem'],
        rows: [
          ['Inline', 'Demonstracao, volumes baixos', 'Resposta imediata, simples de implementar'],
          ['Batch', 'Grandes volumes, avaliacao em massa', 'Custo muito menor, uso eficiente de tokens'],
        ],
      },
      {
        type: 'heading',
        text: 'Consideracoes sobre SLM vs LLM',
      },
      {
        type: 'paragraph',
        text: 'Para avaliacao de sessoes, foi planejado comparar LLMs maiores (melhor precisao) com SLMs menores (menor custo por avaliacao). O objetivo e encontrar o melhor custo-beneficio para o volume esperado, testando modelos como claude-haiku ou nova-lite antes de fechar a escolha.',
      },
    ],
  },
  {
    anchor: 'llmops',
    title: 'Observabilidade e LLMOps',
    blocks: [
      {
        type: 'paragraph',
        text: 'A pagina de LLMOps da plataforma cobre o planejamento de observabilidade operacional. O objetivo e ter visibilidade completa sobre o comportamento da IA ao longo do tempo, incluindo metricas de consumo, latencia e qualidade.',
      },
      {
        type: 'heading',
        text: 'Metricas operacionais planejadas',
      },
      {
        type: 'list',
        items: [
          'Tokens por minuto (throughput)',
          'Latencia media e percentis por modelo',
          'Tokens por requisicao',
          'Tokens por usuario ao longo do tempo',
          'Distribuicao de consumo por sessao',
          'Taxa de sucesso e falha do proxy de LLM',
        ],
      },
      {
        type: 'heading',
        text: 'Metricas de negocio planejadas',
      },
      {
        type: 'list',
        items: [
          'Indice da IA Operadora (% bom - % ruim)',
          'Distribuicao de satisfacao por periodo',
          'Esforco medio do cliente por sessao',
          'Taxa de transferencia para humano',
          'Cursos mais buscados',
          'Sessoes sem resolucao util',
        ],
      },
      {
        type: 'heading',
        text: 'Esteiras planejadas para producao',
      },
      {
        type: 'list',
        items: [
          'Esteira de drifting: detectar degradacao da qualidade ao longo do tempo',
          'Esteira de anotacao: pipeline para rotular novas conversas',
          'Esteira de prompt engineering: versionamento e experimentos de prompt com metricas',
          'Batch process para avaliacao de grandes volumes com custo reduzido',
        ],
      },
      {
        type: 'heading',
        text: 'Ferramentas consideradas',
      },
      {
        type: 'list',
        items: [
          'OpenTelemetry (OTEL) para tracing distribuido',
          'ClickHouse ou Loki para armazenamento de logs',
          'Prometheus para metricas de sistema',
          'Grafana para visualizacao e alertas',
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
        text: 'O desenvolvimento foi conduzido com uso intensivo de coding agents via GitHub Copilot CLI, combinando diferentes modelos e skills especializadas para maximizar a qualidade e a velocidade das entregas.',
      },
      {
        type: 'heading',
        text: 'Modelos utilizados',
      },
      {
        type: 'list',
        items: [
          'Claude Sonnet 4.6 para tarefas de raciocinio e arquitetura',
          'GPT-5.4 para tarefas de geracao de codigo',
        ],
      },
      {
        type: 'heading',
        text: 'Skills e ferramentas',
      },
      {
        type: 'table',
        headers: ['Ferramenta', 'Uso'],
        rows: [
          ['MASA Framework skill', 'Garantir aderencia ao padrao de camadas no backend'],
          ['Interface Design skill', 'Construcao e revisao de interfaces no frontend'],
          ['Chrome DevTools MCP', 'Inspecao e depuracao do frontend diretamente no browser'],
          ['code-quality skill', 'Auditoria e correcao de qualidade de codigo'],
          ['code-review agent', 'Revisao de segurança e logica antes de merges'],
        ],
      },
      {
        type: 'heading',
        text: 'Cobertura de testes planejada',
      },
      {
        type: 'list',
        items: [
          'Testes unitarios: engines puras e servicos de dominio',
          'Testes integrados: happy path e wrong path para rotas HTTP',
          'Testes end-to-end: fluxo completo de chat contra o proxy real (opt-in)',
          'Testes de carga: validar comportamento nos cenarios de escala planejados',
        ],
      },
      {
        type: 'heading',
        text: 'Proximos passos naturais',
      },
      {
        type: 'list',
        items: [
          'Trocar adapters fake por clientes reais de LLM, embedding e vector store',
          'Ampliar cobertura de testes para chat, indexing, metrics e evaluation',
          'Formalizar contratos de erro HTTP para excecoes de dominio',
          'Implementar esteira de drifting e anotacao de novas conversas',
          'Adicionar autenticacao (JWT ou chave de API) no frontend',
          'Configurar pipeline de CI/CD com testes e lint automatizados',
        ],
      },
    ],
  },
]

// -----------------------------------------------------------------------
// FIM DO CONTEUDO
// -----------------------------------------------------------------------

function renderBlock(block: Block, idx: number) {
  switch (block.type) {
    case 'paragraph':
      return (
        <p key={idx} className="text-sm leading-relaxed text-[#3b4a54]">
          {block.text}
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
              {item}
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
                      {cell}
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
  }
}

export function DocsPage() {
  return (
    <div className="flex-1 overflow-y-auto">
      <div className="flex min-h-full">
        {/* Sumario lateral */}
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

        {/* Conteudo principal */}
        <main className="flex-1 p-6 lg:p-10">
          <div className="mx-auto max-w-3xl">
            {/* Cabecalho */}
            <div className="mb-10 flex items-center gap-3">
              <div className="flex size-10 items-center justify-center rounded-xl bg-[#00a884]/10">
                <BookOpen className="size-5 text-[#00a884]" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-[#111b21]">Solution Docs</h1>
                <p className="text-sm text-[#667781]">
                  Documentacao tecnica e de produto da plataforma Mais A Educ
                </p>
              </div>
            </div>

            {/* Secoes */}
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
