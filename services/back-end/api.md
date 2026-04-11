# Planejamento do contrato de API

## Objetivo

Definir o contrato de API do MVP a partir de tres insumos:

1. a arquitetura proposta do sistema
2. as rotas que ja existem no backend
3. o desenho do front, com foco em:
   - tela principal de conversa estilo WhatsApp
   - pagina de Metrics
   - pagina de LLMOps

Este documento nao descreve implementacao detalhada. Ele organiza o **contrato-alvo** da API para que front e backend evoluam na mesma direcao.

## Leitura do produto

O produto se comporta como um **assistente conversacional com avaliacao de satisfacao estilo NPS**, observabilidade simples e uma area operacional para gerenciar prompts/modelos.

### O que o front indica

Pelo wireframe, a experiencia principal precisa de:

- lista lateral de conversas/sessoes
- area central de mensagens
- envio de mensagem
- seletor de modelo do assistente
- exibicao do saldo de creditos
- navegacao para `Metrics` e `LLMOps`

### O que a arquitetura indica

Pela arquitetura do MVP:

- o front conversa com um backend via HTTP
- o backend fala com Postgres para dados transacionais
- o backend usa Qdrant para busca vetorial
- o backend usa MinIO para arquivos JSON
- o backend integra com `Credit System` e `AI Gateway`
- observabilidade fica fora do contrato transacional da API

## Estado atual das rotas

Hoje o backend ja expoe:

| Metodo | Rota | Status no plano |
| --- | --- | --- |
| `POST` | `/api/chat/messages` | insuficiente para o front final |
| `POST` | `/api/indexing/universities/import` | endpoint operacional, manter fora do fluxo principal do usuario |
| `GET` | `/api/metrics/health` | util, manter |
| `GET` | `/api/metrics/summary` | util, mas simplista para a pagina de Metrics |
| `POST` | `/api/evaluation/sessions/{session_id}` | boa base para avaliacao |
| `GET/POST` | `/api/prompt-registry/...` | boa base para LLMOps, mas nome e estrutura podem melhorar |

## Gaps do contrato atual

As rotas existentes ainda nao cobrem bem o front desenhado porque faltam:

- criar/listar sessoes
- carregar historico de uma sessao
- enviar mensagem vinculada a uma sessao por rota REST mais clara
- listar modelos disponiveis para o seletor
- expor saldo de creditos do usuario
- expor dados de Metrics em formato mais util para dashboard
- consolidar LLMOps em um namespace mais coerente

## Diretrizes do contrato

### 1. Separar API por contexto de uso

O contrato fica mais claro se a API for organizada em quatro grupos:

- `app`: bootstrap da interface e dados necessarios na entrada
- `chat`: experiencia conversacional
- `metrics`: observabilidade de produto e de conversa
- `llmops`: configuracao operacional de prompts/modelos

### 2. Manter endpoints operacionais fora do fluxo principal

Indexacao e importacao de dataset devem continuar existindo, mas como API interna/admin, nao como parte da experiencia do usuario final.

### 3. Priorizar recursos que o front realmente consome

Em vez de desenhar uma API abstrata, o contrato deve atender primeiro:

- hidratacao inicial da UI
- navegacao entre sessoes
- renderizacao do historico
- envio de mensagem
- leitura de creditos
- pagina de metrics
- pagina de llmops

## Contrato proposto v1

## Convencoes gerais

### Base path

```text
/api
```

### Autenticacao

Como a arquitetura mostra token vindo de um sistema externo, o contrato deve assumir:

```http
Authorization: Bearer <rh_token>
```

### Erro padrao

```json
{
  "error": {
    "code": "session_not_found",
    "message": "Session 8d8a... not found",
    "details": {}
  }
}
```

### Campos comuns

- IDs em `uuid`
- datas em `ISO 8601`
- nomes em `snake_case`

## 1. App bootstrap

Esses endpoints existem para a tela abrir pronta, sem o front precisar disparar cinco chamadas desconectadas.

### `GET /api/app/bootstrap`

Retorna o contexto inicial da interface.

```json
{
  "viewer": {
    "id": "8ad3d067-8f56-4ec6-a21e-27b6ec25b5a1",
    "name": "Nicolas"
  },
  "credits": {
    "available": 20,
    "checked_at": "2026-04-10T23:40:00Z"
  },
  "assistant_models": [
    {
      "key": "claude-sonnet-4.6",
      "label": "Sonnet 4.6",
      "is_default": true
    },
    {
      "key": "gpt-5.4-mini",
      "label": "GPT-5.4 mini",
      "is_default": false
    }
  ],
  "navigation": {
    "default_page": "chat",
    "pages": ["chat", "metrics", "llmops"]
  },
  "recent_sessions": [
    {
      "id": "9ae7d6a2-2cb3-46fd-b982-7bb16fa1fb5f",
      "title": "ADS em Belo Horizonte",
      "last_message_preview": "Quais faculdades...",
      "last_message_at": "2026-04-10T23:38:00Z"
    }
  ]
}
```

### Observacao

Esse endpoint reduz round trips e conversa diretamente com o layout do front.

## 2. Chat

Este e o nucleo do produto.

### `GET /api/chat/sessions`

Lista sessoes do usuario.

#### Query params

- `limit` (opcional, default `20`)
- `cursor` (opcional)

#### Response

```json
{
  "items": [
    {
      "id": "9ae7d6a2-2cb3-46fd-b982-7bb16fa1fb5f",
      "title": "ADS em Belo Horizonte",
      "status": "active",
      "assistant_model": "claude-sonnet-4.6",
      "last_message_preview": "Resposta inicial para...",
      "message_count": 6,
      "created_at": "2026-04-10T23:20:00Z",
      "updated_at": "2026-04-10T23:38:00Z"
    }
  ],
  "next_cursor": null
}
```

### `POST /api/chat/sessions`

Cria uma nova sessao.

#### Request

```json
{
  "assistant_model": "claude-sonnet-4.6",
  "title": "Nova conversa"
}
```

#### Response

```json
{
  "id": "9ae7d6a2-2cb3-46fd-b982-7bb16fa1fb5f",
  "status": "active",
  "assistant_model": "claude-sonnet-4.6",
  "title": "Nova conversa",
  "created_at": "2026-04-10T23:20:00Z",
  "updated_at": "2026-04-10T23:20:00Z"
}
```

### `GET /api/chat/sessions/{session_id}`

Carrega uma sessao com seu historico.

#### Response

```json
{
  "session": {
    "id": "9ae7d6a2-2cb3-46fd-b982-7bb16fa1fb5f",
    "title": "ADS em Belo Horizonte",
    "status": "active",
    "assistant_model": "claude-sonnet-4.6",
    "created_at": "2026-04-10T23:20:00Z",
    "updated_at": "2026-04-10T23:38:00Z"
  },
  "messages": [
    {
      "id": "f4fe8f5f-f1a0-4dd0-9717-15a8b5ad5f2b",
      "role": "user",
      "content": "Quais faculdades tem ADS em Belo Horizonte?",
      "created_at": "2026-04-10T23:20:02Z"
    },
    {
      "id": "7c3914a6-9c37-4642-8d0f-43dc4d4d4522",
      "role": "assistant",
      "content": "Encontrei opcoes com base no contexto recuperado...",
      "created_at": "2026-04-10T23:20:05Z"
    }
  ]
}
```

### `POST /api/chat/sessions/{session_id}/messages`

Envia mensagem do usuario e devolve a resposta do assistente.

#### Request

```json
{
  "content": "Quais faculdades tem ADS em Belo Horizonte?",
  "assistant_model": "claude-sonnet-4.6"
}
```

#### Response

```json
{
  "session_id": "9ae7d6a2-2cb3-46fd-b982-7bb16fa1fb5f",
  "user_message": {
    "id": "f4fe8f5f-f1a0-4dd0-9717-15a8b5ad5f2b",
    "role": "user",
    "content": "Quais faculdades tem ADS em Belo Horizonte?",
    "created_at": "2026-04-10T23:20:02Z"
  },
  "assistant_message": {
    "id": "7c3914a6-9c37-4642-8d0f-43dc4d4d4522",
    "role": "assistant",
    "content": "Encontrei opcoes com base no contexto recuperado...",
    "created_at": "2026-04-10T23:20:05Z"
  },
  "retrieval": {
    "chunks_used": 3
  },
  "credits": {
    "available": 19
  }
}
```

### `PATCH /api/chat/sessions/{session_id}`

Atualiza metadados simples da sessao.

#### Request

```json
{
  "title": "ADS em BH",
  "status": "archived"
}
```

## 3. Evaluation / NPS-like

Como a proposta fala em avaliacao tipo NPS, faz sentido aproximar esse modulo da jornada da sessao.

### `POST /api/chat/sessions/{session_id}/evaluation`

Executa a avaliacao automatica da sessao.

#### Response

```json
{
  "session_id": "9ae7d6a2-2cb3-46fd-b982-7bb16fa1fb5f",
  "satisfaction": "high",
  "effort_score": 2,
  "understanding_score": 4,
  "resolution_score": 4,
  "evidences": [
    "Usuario confirmou que encontrou uma opcao valida"
  ]
}
```

### `GET /api/chat/sessions/{session_id}/evaluation`

Le a ultima avaliacao persistida da sessao.

### Observacao

O endpoint atual `POST /api/evaluation/sessions/{session_id}` pode continuar existindo temporariamente, mas a API final fica mais coerente se a avaliacao viver sob `chat/sessions`.

## 4. Credits

O wireframe mostra credito no topo da tela. Isso precisa de um contrato explicito.

### `GET /api/credits/balance`

```json
{
  "available": 20,
  "source": "credit-system",
  "checked_at": "2026-04-10T23:40:00Z"
}
```

## 5. Assistant models

O seletor de modelo tambem merece um endpoint proprio.

### `GET /api/assistant-models`

```json
{
  "items": [
    {
      "key": "claude-sonnet-4.6",
      "label": "Sonnet 4.6",
      "provider": "anthropic",
      "is_default": true,
      "status": "active"
    },
    {
      "key": "gpt-5.4-mini",
      "label": "GPT-5.4 mini",
      "provider": "openai",
      "is_default": false,
      "status": "active"
    }
  ]
}
```

## 6. Metrics

A pagina de Metrics pede mais do que o `summary` atual.

### `GET /api/metrics/overview`

Cards principais da pagina.

```json
{
  "total_sessions": 120,
  "total_messages": 840,
  "total_rag_hits": 510,
  "avg_resolution_score": 3.8,
  "avg_understanding_score": 4.1,
  "credit_checks": 97
}
```

### `GET /api/metrics/timeseries`

#### Query params

- `from`
- `to`
- `interval` (`hour`, `day`)

#### Response

```json
{
  "items": [
    {
      "bucket_start": "2026-04-10T00:00:00Z",
      "sessions": 25,
      "messages": 180,
      "rag_hits": 98
    }
  ]
}
```

### `GET /api/metrics/sessions`

Lista sessoes para analise operacional.

#### Response

```json
{
  "items": [
    {
      "session_id": "9ae7d6a2-2cb3-46fd-b982-7bb16fa1fb5f",
      "messages": 6,
      "rag_hits": 3,
      "resolution_score": 4,
      "updated_at": "2026-04-10T23:38:00Z"
    }
  ]
}
```

### Compatibilidade

O endpoint atual `GET /api/metrics/summary` pode virar um alias simplificado de `overview`.

## 7. LLMOps

A area de LLMOps parece ser o painel operacional para prompt registry e configuracao do comportamento do agente.

### Recomendacao de namespace

Trocar de:

```text
/api/prompt-registry
```

para:

```text
/api/llmops
```

### `GET /api/llmops/prompts`

Lista prompts e sua versao ativa.

### `GET /api/llmops/prompts/{prompt_key}`

Detalha um prompt e suas versoes.

### `POST /api/llmops/prompts`

Cria um novo prompt.

#### Request

```json
{
  "key": "agent.default.reply",
  "template": "Responda ao aluno com base no contexto recuperado.",
  "description": "Prompt principal do agente"
}
```

### `POST /api/llmops/prompts/{prompt_key}/versions`

Cria nova versao.

### `POST /api/llmops/prompts/{prompt_key}/versions/{version_id}/activate`

Ativa uma versao de forma mais RESTful do que enviar o `version_id` no corpo para `/active`.

### `GET /api/llmops/active-config`

Retorna a configuracao ativa do assistente para renderizar a pagina de LLMOps.

```json
{
  "default_model": "claude-sonnet-4.6",
  "prompts": [
    {
      "key": "agent.default.reply",
      "active_version_id": "d3908b4e-267f-4208-a2cc-6ccbf18b8757"
    }
  ]
}
```

## 8. Indexing interno

Esse fluxo existe para suporte ao RAG e nao precisa aparecer como capability do usuario final.

### `POST /api/admin/indexing/universities/import`

Mantem a mesma ideia do endpoint atual, mas em namespace administrativo.

## Contrato minimo para o front atual

Se o objetivo for colocar o wireframe de pe com o menor numero de rotas necessarias, o corte minimo e:

1. `GET /api/app/bootstrap`
2. `GET /api/chat/sessions`
3. `POST /api/chat/sessions`
4. `GET /api/chat/sessions/{session_id}`
5. `POST /api/chat/sessions/{session_id}/messages`
6. `GET /api/credits/balance`
7. `GET /api/assistant-models`
8. `GET /api/metrics/overview`
9. `GET /api/llmops/prompts`

## Migracao das rotas atuais

| Atual | Proposto |
| --- | --- |
| `POST /api/chat/messages` | `POST /api/chat/sessions/{session_id}/messages` |
| `POST /api/evaluation/sessions/{session_id}` | `POST /api/chat/sessions/{session_id}/evaluation` |
| `GET /api/metrics/summary` | `GET /api/metrics/overview` |
| `/api/prompt-registry/*` | `/api/llmops/prompts/*` |
| `POST /api/indexing/universities/import` | `POST /api/admin/indexing/universities/import` |

## Recomendacao de ordem de implementacao

1. fechar o contrato do fluxo principal de chat
2. persistir sessoes e mensagens no Postgres
3. adicionar bootstrap, credits e assistant-models
4. expandir metrics para dashboard real
5. renomear prompt-registry para llmops sem quebrar compatibilidade
