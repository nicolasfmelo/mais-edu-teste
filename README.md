# Mais A Edu - Teste Tecnico (Coordenador de IA)

Este repositorio contem minha entrega para o teste tecnico da **Mais A Edu**.

A proposta implementa um MVP funcional de avaliacao de atendimento com IA operadora, incluindo:

- chat estilo WhatsApp (texto e audio)
- agente conversacional (Clara)
- agente de avaliacao NPS-like
- exportacao de conversas e analise estruturada
- metricas operacionais e painel de LLMOps

Tambem contem uma proposta arquitetural batch para escala e custo em:

- `docs/arquitetura/mvp-batch-process.png`

Documento principal da solucao:

- Página de docs ao subir a aplicação

## Estrutura rapida

- `services/back-end`: API FastAPI + camada de orquestracao/agentes
- `services/front-end`: aplicacao React (chat, metrics, llmops, docs)
- `services/compose.yaml`: stack local com banco, object store e observabilidade
- `docs/`: diagramas e material de arquitetura
- `docs/drafts/`: rascunhos e evolucao de decisoes

## Como rodar a aplicacao

### Opcao recomendada (Docker Compose)

Prerequisitos:

- Docker
- Docker Compose Plugin

Subir stack completa:

```bash
cd services
docker compose up -d --build
```

Acessos:

- Front-end: `http://localhost:8080`
- Back-end (Swagger): `http://localhost:8000/docs`
- Grafana: `http://localhost:3000`
- Prometheus: `http://localhost:9090`
- Loki: `http://localhost:3100`

Parar stack:

```bash
cd services
docker compose down
```

### Opcao de desenvolvimento local (sem back-end containerizado)

1. Subir infraestrutura base:

```bash
cd services
docker compose up -d postgres minio prometheus loki promtail grafana
```

2. Subir back-end:

```bash
cd services/back-end
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/mais_a_educ"
python run_local.py
```

3. Subir front-end:

```bash
cd services/front-end
bun install
bun run dev
```

Front-end local (modo dev): `http://localhost:5173`

## Observacoes de uso
- Será enviado um lote de 20 chaves para o RH da Mais A Edu
- Para inferencia real no chat/analise, e necessario usar `api_key` valida no gateway de LLM.
- Sem chave valida, a interface sobe normalmente, mas chamadas de inferencia podem falhar.

## Documentacao complementar

- Solucao consolidada: `fluxo-docs.md`
- Custos de infraestrutura: `estimated-infra-costs.md`
- Custos de modelos/tokens: `custos.md`
- Contrato do proxy LLM: `services/back-end/llm-contract.md`
