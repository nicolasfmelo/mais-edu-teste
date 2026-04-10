# Backend

Backend do MVP **Mais A Educ**, implementado em **Python 3.12 + FastAPI** e organizado com uma estrutura inspirada em **MASA (Modular Agentic Semantic Architecture)**. O objetivo atual do serviço e oferecer uma base cognoscivel para evolucao de:

- chat com suporte a RAG
- importacao de base de universidades
- avaliacao de sessoes
- metricas operacionais simples
- registro e versionamento de prompts

Hoje o projeto privilegia **fronteiras claras entre camadas**, **injeção explicita de dependencias** e **adapters fake/in-memory** para acelerar a evolucao do dominio antes da integracao com infraestrutura real.

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

Apesar dos nomes de algumas integracoes remeterem a servicos reais, o backend ainda opera com implementacoes locais para facilitar iteracao:

| Componente | Implementacao atual |
| --- | --- |
| AI gateway | `FakeAIGatewayClient` retorna uma resposta sintetica com hint de contexto |
| Credito | `FakeCreditSystemClient` sempre retorna credito disponivel |
| Embeddings | `FakeEmbeddingClient` gera vetores deterministicos simples |
| Sessoes | `InMemorySessionRepository` |
| Metricas | `InMemoryMetricsRepository` |
| Prompt registry | `InMemoryPromptRegistryRepository` |
| Vector store | `QdrantKnowledgeRepository` em memoria |
| Object store | `MinioDocumentStore` em memoria |

Isso significa que o projeto ja demonstra o desenho dos contratos e dos fluxos de negocio, mas ainda nao deve ser tratado como backend pronto para producao.

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
4. `services/agent/agent_service.py` decide consultar credito e RAG.
5. `services/rag/rag_service.py` usa `EmbeddingClient` + `KnowledgeRepository`.
6. `integrations/...` executam os adapters concretos configurados no `AppContainer`.

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

### Subir a API

```bash
cd services/back-end
source .venv/bin/activate
uvicorn app.main:app --reload
```

Aplicacao disponivel em:

- `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Testes

```bash
cd services/back-end
pytest -q
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
curl -X POST http://127.0.0.1:8000/api/chat/messages \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "11111111-1111-1111-1111-111111111111",
    "message": "Quais faculdades tem curso de ADS em Belo Horizonte?"
  }'
```

### Importacao de universidades

```bash
curl -X POST http://127.0.0.1:8000/api/indexing/universities/import \
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
curl -X POST http://127.0.0.1:8000/api/prompt-registry/prompts \
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
