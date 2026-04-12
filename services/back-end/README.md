# Backend

Backend do MVP **Mais A Educ**, implementado em **Python 3.12 + FastAPI** e organizado com uma estrutura inspirada em **MASA (Modular Agentic Semantic Architecture)**. O objetivo atual do serviço e oferecer uma base cognoscivel para evolucao de:

- chat com suporte a RAG
- importacao de base de universidades
- avaliacao de sessoes
- metricas operacionais simples
- registro e versionamento de prompts

Hoje o projeto privilegia **fronteiras claras entre camadas**, **injeção explicita de dependencias** e evolucao incremental dos adapters, com persistencia relacional via **SQLAlchemy + Postgres** para a camada transacional principal.

## Visao geral funcional

O backend expoe uma API HTTP que coordena cinco fluxos principais:

| Area | O que faz |
| --- | --- |
| Chat | Recebe uma mensagem, recupera contexto via RAG, gera resposta do agente e registra metricas da conversa |
| Indexing | Importa um dataset de universidades, gera chunks e persiste documentos/chunks em adapters locais |
| Evaluation | Avalia uma sessao existente com base nas mensagens trocadas |
| Metrics | Expoe healthcheck e resumo agregado das metricas coletadas |
| Prompt registry | Cadastra prompts, cria novas versoes e ativa a versao vigente |

## Estado atual da infraestrutura

Apesar dos nomes de algumas integracoes remeterem a servicos reais, parte da infraestrutura ainda opera com implementacoes locais para facilitar iteracao:

| Componente | Implementacao atual |
| --- | --- |
| AI gateway | `LLMProxyGatewayClient` chama o proxy HTTP descrito em `llm-contract.md` |
| Credito | validado pelo proprio proxy via `x-api-key` |
| Embeddings | `FakeEmbeddingClient` gera vetores deterministicos simples |
| Sessoes | `SQLAlchemySessionRepository` |
| Metricas | `SQLAlchemyMetricsRepository` |
| Prompt registry | `SQLAlchemyPromptRegistryRepository` |
| Catalogo de cursos | `SQLAlchemyCourseCatalogRepository` |
| Vector store | `QdrantKnowledgeRepository` em memoria |
| Object store | `MinioDocumentStore` em memoria |

Isso significa que o projeto ja demonstra o desenho dos contratos e dos fluxos de negocio, mas ainda nao deve ser tratado como backend pronto para producao.

## Bootstrap de indexacao de cursos

O backend agora suporta um bootstrap inicial de catalogo de cursos em **Postgres**, sem embeddings, usando os arquivos Markdown em `services/datasets/`.

### Como funciona

- no startup da aplicacao, o backend verifica `DATABASE_URL`
- se a variavel estiver configurada, cria a tabela `course_catalog_entries` caso ela nao exista
- em seguida, le todos os arquivos `services/datasets/*.md`
- cada curso e persistido com `upsert` por `slug`

Esse fluxo foi desenhado para o cenario em que o repositorio e clonado e o ambiente sobe via Docker Compose, garantindo que o catalogo esteja carregado quando a API iniciar. O mesmo bootstrap de startup tambem cria o schema SQLAlchemy das tabelas transacionais principais.

### Variaveis de ambiente

- `DATABASE_URL`: conexao com o Postgres usada no bootstrap
- `DATASETS_DIR`: opcional, sobrescreve o caminho padrao `services/datasets`
- `INDEXING_BOOTSTRAP_ENABLED`: opcional, default `true`
- `LLM_PROXY_BASE_URL`: opcional, default `https://kviwmiapph.execute-api.us-east-1.amazonaws.com`

## Persistencia relacional atual

O backend agora usa SQLAlchemy como camada de persistencia para:

- `chat_sessions`
- `chat_messages`
- `conversation_metrics`
- `prompt_registry_entries`
- `prompt_versions`
- `course_catalog_entries`

No ambiente principal, a expectativa e usar **Postgres** via `DATABASE_URL`. Para testes locais automatizados, o mesmo mapping ORM pode usar SQLite temporario sem alterar services ou handlers.

## Arquitetura

O codigo fica em `src/app` e segue a separacao por camadas:

```text
src/app
├── bootstrap
│   └── container.py
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
│   │   └── repos
│   ├── external_apis
│   ├── llm
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
└── main.py
```

### Papel de cada camada

| Camada | Responsabilidade |
| --- | --- |
| `domain_models` | Entidades, IDs tipados, contratos e excecoes de dominio |
| `engines` | Regras puras e deterministicas, sem I/O |
| `integrations` | Adapters de infraestrutura que implementam os contratos do dominio |
| `services` | Orquestracao dos casos de uso, combinando engines e integracoes |
| `delivery` | Handlers HTTP e schemas de entrada/saida |
| `bootstrap` | Wiring explicito das dependencias via construtor |

### Exemplo de fluxo

O fluxo de chat ilustra bem a arquitetura:

1. `delivery/http/chat_handler.py` valida a requisicao HTTP.
2. `delivery/schemas/chat_schemas.py` transforma o payload em `ChatRequest`.
3. `services/chat/chat_service.py` recupera a sessao, delega ao agente e registra metricas.
4. `services/agent/langgraph_course_agent.py` executa o fluxo do agente em LangGraph.
5. `services/rag/rag_service.py` recupera contexto do catalogo.
6. `integrations/external_apis/llm_proxy_gateway_client.py` encaminha `prompt`, `model_id` e `x-api-key` para o proxy AWS.

## Como executar localmente

### Requisitos

- Python 3.12

### Instalacao

```bash
cd services/back-end
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Subir o Postgres local

```bash
cd <repo-root>
docker compose up -d postgres
```

Neste MVP monorepo, o `compose.yaml` fica na **raiz do repositorio** e centraliza os containers compartilhados entre front e back.

Defaults do container:

- `POSTGRES_DB=mais_a_educ`
- `POSTGRES_USER=postgres`
- `POSTGRES_PASSWORD=postgres`
- `POSTGRES_PORT=5432`

A `DATABASE_URL` correspondente para rodar o backend fora do container fica:

```bash
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/mais_a_educ"
```

### Subir a API

```bash
cd services/back-end
source .venv/bin/activate
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/mais_a_educ"
python run_local.py
```

O script `run_local.py` carrega `.env` automaticamente quando o arquivo existe e aceita overrides opcionais:

```bash
python run_local.py --host 0.0.0.0 --port 8000 --reload
```

Aplicacao disponivel em:

- `http://0.0.0.0:8000`
- Swagger UI: `http://0.0.0.0:8000/docs`
- ReDoc: `http://0.0.0.0:8000/redoc`

## Testes

```bash
cd services/back-end
pytest -q
```

Teste opt-in do chat contra o proxy real:

```bash
cd services/back-end
export LLM_PROXY_TEST_API_KEY="key_xxx"
export LLM_PROXY_BASE_URL="https://kviwmiapph.execute-api.us-east-1.amazonaws.com"
pytest -q tests/integration/test_chat_live_proxy.py
```

Suite atual:

- engines puras (`prompt`, `evaluation`, `indexing`)
- service de prompt registry
- rotas HTTP de prompt registry

## Endpoints disponiveis

| Metodo | Rota | Descricao |
| --- | --- | --- |
| `POST` | `/api/chat/messages` | Envia uma mensagem para uma sessao e retorna a resposta do agente |
| `POST` | `/api/indexing/universities/import` | Importa registros de universidades e gera chunks/documentos |
| `GET` | `/api/metrics/health` | Healthcheck simples |
| `GET` | `/api/metrics/summary` | Resumo agregado de sessoes, mensagens e hits de RAG |
| `POST` | `/api/evaluation/sessions/{session_id}` | Avalia uma sessao existente |
| `GET` | `/api/prompt-registry/prompts` | Lista prompts cadastrados |
| `GET` | `/api/prompt-registry/prompts/{prompt_key}` | Busca um prompt por chave |
| `POST` | `/api/prompt-registry/prompts` | Cadastra um novo prompt |
| `POST` | `/api/prompt-registry/prompts/{prompt_key}/versions` | Cria uma nova versao para um prompt existente |
| `GET` | `/api/prompt-registry/prompts/{prompt_key}/active` | Recupera a versao ativa |
| `POST` | `/api/prompt-registry/prompts/{prompt_key}/active` | Ativa uma versao especifica |

## Exemplos de uso

### Chat

```bash
curl -X POST http://0.0.0.0:8000/api/chat/messages \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "11111111-1111-1111-1111-111111111111",
    "message": "Quais cursos combinam com migracao para dados?",
    "api_key": "key_xxx",
    "model_id": "us.anthropic.claude-sonnet-4-6",
    "system_prompt": "Atue como consultora educacional da Clara."
  }'
```

O front-end envia `message`, `api_key`, `model_id` e `system_prompt` no body. O backend transforma isso em estado do agente e reenvia a chave para o proxy apenas no header `x-api-key` da chamada externa.

### Importacao de universidades

```bash
curl -X POST http://0.0.0.0:8000/api/indexing/universities/import \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_name": "universidades-demo",
    "records": [
      {
        "name": "Universidade Exemplo",
        "course": "Analise e Desenvolvimento de Sistemas",
        "modality": "EAD",
        "city": "Belo Horizonte",
        "summary": "Curso com foco em desenvolvimento web e dados."
      }
    ]
  }'
```

### Cadastro de prompt

```bash
curl -X POST http://0.0.0.0:8000/api/prompt-registry/prompts \
  -H "Content-Type: application/json" \
  -d '{
    "key": "agent.default.reply",
    "template": "Responda ao aluno com base no contexto recuperado.",
    "description": "Prompt principal do agente"
  }'
```

## Ponto de entrada e wiring

- `src/app/main.py` cria a aplicacao FastAPI.
- `src/app/bootstrap/container.py` monta todas as dependencias manualmente.

Essa montagem explicita ajuda a manter o projeto alinhado com MASA:

- dependencias sao visiveis no construtor de cada service
- handlers permanecem magros
- engines continuam puras
- adapters de infraestrutura ficam isolados em `integrations`

## Diretrizes para evolucao

Ao adicionar novas features, preserve a ordem de implementacao por camada:

1. `domain_models`
2. `engines`
3. `integrations`
4. `services`
5. `delivery`

Evite atalhos como:

- importar adapters de `integrations` diretamente em handlers
- colocar regra de negocio em `delivery`
- expor tipos crus de infraestrutura para `services`
- esconder dependencias em globais ou singletons

## Proximos passos naturais

Os pontos mais evidentes para evolucao sao:

- trocar adapters fake por clientes reais de LLM, credito, vector store e object store
- persistir sessoes, metricas e prompt registry fora da memoria
- ampliar cobertura de testes para `chat`, `indexing`, `metrics` e `evaluation`
- formalizar contratos de erro HTTP para excecoes de dominio
