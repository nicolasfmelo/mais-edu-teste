# Planejamento inicial das tabelas transacionais

## Objetivo

Definir o primeiro corte das tabelas do **Postgres** para suportar o fluxo transacional de **chat**, com foco em:

- sessoes
- mensagens

Este documento nasceu para o primeiro corte transacional. Hoje ele tambem serve como referencia para a persistencia relacional implementada via **SQLAlchemy**, que ja cobre chat, metricas, prompt registry e catalogo de cursos. Documentos de RAG e chunks continuam fora deste escopo.

## Escopo deste primeiro corte

### Entra agora

| Area | Motivo |
| --- | --- |
| `chat_sessions` | representa a conversa e seu ciclo de vida |
| `chat_messages` | representa cada mensagem persistida da sessao |

### Ficava fora no primeiro corte

| Area | Motivo |
| --- | --- |
| metricas | hoje ja persistidas em `conversation_metrics` |
| prompt registry | hoje ja persistido em `prompt_registry_entries` e `prompt_versions` |
| documentos/chunks de RAG | tendem a viver em object store + vector store |
| auditoria detalhada de agente/credito | ainda nao e requisito central do corte inicial |

## Principios de modelagem

1. **IDs de dominio em UUID**: o dominio ja usa `SessionId` e `MessageId` como UUID.
2. **Sessao e mensagem separadas**: uma sessao possui muitas mensagens.
3. **Ordem da conversa explicita**: a mensagem precisa de `sequence_number` para leitura consistente.
4. **Tipos simples no primeiro corte**: preferir `text + check constraint` em vez de enum nativo do Postgres onde isso reduzir acoplamento de migration.
5. **Sem soft delete agora**: usar delecao fisica apenas se necessario; por padrao o sistema trabalha com dados ativos.

## Mapeamento dominio -> banco

| Dominio | Tabela | Observacao |
| --- | --- | --- |
| `ChatSession.id` | `chat_sessions.id` | PK em UUID |
| `ChatMessage.id` | `chat_messages.id` | PK em UUID |
| `ChatMessage.role` | `chat_messages.role` | `user`, `assistant` |
| `ChatMessage.content` | `chat_messages.content` | corpo da mensagem |
| `ChatSession.messages` | `chat_messages` | relacao 1:N por `session_id` |

## Tabelas propostas

### 1. `chat_sessions`

Representa a sessao de conversa. No dominio atual ela tem basicamente o `id`, mas no banco vale guardar metadados operacionais minimos.

| Coluna | Tipo | Regra | Observacao |
| --- | --- | --- | --- |
| `id` | `uuid` | PK | mesmo ID do dominio |
| `status` | `text` | not null, default `'active'` | permite fechar/arquivar no futuro sem remodelar a tabela |
| `created_at` | `timestamptz` | not null, default `now()` | data de criacao |
| `updated_at` | `timestamptz` | not null, default `now()` | ultima atualizacao da sessao |
| `last_message_at` | `timestamptz` | null | facilita listagens e ordenacao |

#### Regras

- `status` com `check` inicial em `('active', 'closed', 'archived')`
- sessao e criada sob demanda no primeiro envio de mensagem
- `updated_at` e `last_message_at` devem ser atualizados a cada nova mensagem

### 2. `chat_messages`

Representa cada evento de mensagem dentro de uma sessao.

| Coluna | Tipo | Regra | Observacao |
| --- | --- | --- | --- |
| `id` | `uuid` | PK | mesmo ID do dominio |
| `session_id` | `uuid` | FK not null | referencia `chat_sessions(id)` |
| `sequence_number` | `integer` | not null | ordem da mensagem dentro da sessao |
| `role` | `text` | not null | `user`, `assistant` |
| `content` | `text` | not null | conteudo integral da mensagem |
| `created_at` | `timestamptz` | not null, default `now()` | data da mensagem |

#### Regras

- `foreign key (session_id) references chat_sessions(id) on delete cascade`
- `unique (session_id, sequence_number)` para evitar ambiguidade de ordenacao
- `check (sequence_number > 0)`
- `check (role in ('user', 'assistant'))`

## Relacionamento

```text
chat_sessions (1) -----< (N) chat_messages
```

## DDL de referencia

```sql
create table chat_sessions (
    id uuid primary key,
    status text not null default 'active',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    last_message_at timestamptz null,
    constraint chat_sessions_status_check
        check (status in ('active', 'closed', 'archived'))
);

create table chat_messages (
    id uuid primary key,
    session_id uuid not null,
    sequence_number integer not null,
    role text not null,
    content text not null,
    created_at timestamptz not null default now(),
    constraint chat_messages_session_fk
        foreign key (session_id)
        references chat_sessions (id)
        on delete cascade,
    constraint chat_messages_sequence_number_check
        check (sequence_number > 0),
    constraint chat_messages_role_check
        check (role in ('user', 'assistant')),
    constraint chat_messages_session_sequence_unique
        unique (session_id, sequence_number)
);
```

## Indices recomendados

```sql
create index ix_chat_sessions_last_message_at
    on chat_sessions (last_message_at desc nulls last);

create index ix_chat_messages_session_created_at
    on chat_messages (session_id, created_at);

create index ix_chat_messages_session_sequence
    on chat_messages (session_id, sequence_number);
```

## Fluxos transacionais esperados

### 1. Criar sessao sob demanda

Quando chegar uma mensagem para uma sessao inexistente:

1. inserir `chat_sessions`
2. inserir mensagem do usuario em `chat_messages`
3. inserir resposta do assistente em `chat_messages`
4. atualizar `updated_at` e `last_message_at` da sessao

Idealmente tudo no **mesmo commit**.

### 2. Carregar historico da conversa

Consulta principal:

```sql
select
    m.id,
    m.role,
    m.content,
    m.sequence_number,
    m.created_at
from chat_messages m
where m.session_id = $1
order by m.sequence_number asc;
```

### 3. Recuperar sessao por atividade recente

Consulta util para backoffice e observabilidade simples:

```sql
select
    s.id,
    s.status,
    s.created_at,
    s.updated_at,
    s.last_message_at
from chat_sessions s
order by s.last_message_at desc nulls last
limit 50;
```

## Decisoes intencionais deste desenho

### Por que nao guardar mensagens dentro de um JSON na sessao?

Porque o modelo de acesso principal e listar mensagens em ordem, e isso fica mais simples, consistente e indexavel com uma tabela propria.

### Por que `sequence_number` alem de `created_at`?

Porque timestamps podem empatar ou variar conforme estrategia de persistencia. A ordenacao da conversa nao deve depender de granularidade de clock.

### Por que `role` em `text` com `check`?

Porque no primeiro corte isso reduz atrito de migration. Se o conjunto estabilizar, migramos depois para enum nativo do Postgres.

## Possiveis extensoes futuras

Se o escopo crescer, os proximos candidatos naturais sao:

- `agent_runs`
- `session_evaluations`
- `message_feedback`

## Tabelas transacionais adicionais implementadas

### `conversation_metrics`

Persistencia simples das metricas gravadas pelo fluxo de chat.

| Coluna | Tipo | Observacao |
| --- | --- | --- |
| `id` | `uuid` | identificador tecnico |
| `session_id` | `uuid` | referencia logica da sessao |
| `messages_count` | `integer` | quantidade de mensagens apos o turno |
| `rag_hits` | `integer` | quantidade de chunks recuperados |
| `used_credit_check` | `boolean` | se o turno consumiu verificacao de credito |
| `created_at` | `timestamptz` | momento do registro |

### `prompt_registry_entries`

Tabela raiz do prompt registry.

| Coluna | Tipo | Observacao |
| --- | --- | --- |
| `key` | `text` | chave normalizada do prompt |
| `created_at` | `timestamptz` | data de criacao |
| `updated_at` | `timestamptz` | data da ultima alteracao |

### `prompt_versions`

Tabela de versoes associadas a `prompt_registry_entries`.

| Coluna | Tipo | Observacao |
| --- | --- | --- |
| `id` | `uuid` | ID de dominio da versao |
| `prompt_key` | `text` | FK para `prompt_registry_entries.key` |
| `version_number` | `integer` | contador incremental por chave |
| `template` | `text` | template persistido |
| `description` | `text` | descricao funcional |
| `is_active` | `boolean` | indica a versao ativa |
| `created_at` | `timestamptz` | data de criacao |

## Tabela de indexacao inicial de cursos

Para o primeiro corte de busca de cursos sem embeddings, o Postgres tambem pode manter uma tabela relacional simples com uma linha por arquivo Markdown do dataset em `services/datasets/`.

### `course_catalog_entries`

| Coluna | Tipo | Regra | Observacao |
| --- | --- | --- | --- |
| `id` | `uuid` | PK | UUID estavel derivado do slug do arquivo |
| `slug` | `text` | not null unique | nome-base do arquivo `.md` |
| `title` | `text` | not null | titulo exibido do curso |
| `level` | `text` | not null | `graduacao`, `pos-graduacao`, `mba` |
| `modality` | `text` | not null | `ead`, `remoto` |
| `duration_text` | `text` | not null | ex.: `12 meses`, `4 anos` |
| `learning_summary` | `text` | not null | secao "O que voce vai aprender" |
| `market_application` | `text` | not null | secao "Onde aplicar no mercado de trabalho" |
| `curriculum_text` | `text` | not null | grade curricular consolidada |
| `search_text` | `text` | not null | texto consolidado para busca simples |
| `source_path` | `text` | not null | caminho relativo dentro de `services/datasets/` |
| `created_at` | `timestamptz` | not null default `now()` | primeira carga |
| `updated_at` | `timestamptz` | not null default `now()` | ultima atualizacao via bootstrap |

### Regras

- `check (level in ('graduacao', 'pos-graduacao', 'mba'))`
- `check (modality in ('ead', 'remoto'))`
- `unique (slug)`
- indices simples por `level` e `modality`
- carga via `insert ... on conflict (slug) do update`

### DDL de referencia

```sql
create table if not exists course_catalog_entries (
    id uuid primary key,
    slug text not null unique,
    title text not null,
    level text not null,
    modality text not null,
    duration_text text not null,
    learning_summary text not null,
    market_application text not null,
    curriculum_text text not null,
    search_text text not null,
    source_path text not null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint course_catalog_entries_level_check
        check (level in ('graduacao', 'pos-graduacao', 'mba')),
    constraint course_catalog_entries_modality_check
        check (modality in ('ead', 'remoto'))
);

create index ix_course_catalog_entries_level
    on course_catalog_entries (level);

create index ix_course_catalog_entries_modality
    on course_catalog_entries (modality);
```

### Uso planejado

- bootstrap automatico no startup da API
- leitura do dataset local em `services/datasets/*.md`
- busca inicial com filtros (`level`, `modality`) e texto simples em `search_text`

## Recomendacao de implementacao

Para o primeiro passo de persistencia real no backend, a ordem sugerida e:

1. criar modelos/repositorios Postgres para `chat_sessions` e `chat_messages`
2. manter `ChatService` como orquestrador sem mudar o dominio
3. salvar as duas mensagens do fluxo (`user` e `assistant`) na mesma transacao
4. expor leitura do historico da sessao a partir da ordenacao por `sequence_number`
