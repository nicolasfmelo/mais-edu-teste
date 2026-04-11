# Contrato de Integração - LLM Proxy

Este documento define como um serviço cliente deve chamar o proxy de LLM e interpretar a resposta.

## Endpoint principal
- Método: `POST`
- URL: `/v1/llm/invoke`
- Content-Type: `application/json`

## Base URL (importante)
- API base validada no ambiente atual:
  - `https://kviwmiapph.execute-api.us-east-1.amazonaws.com/v1`
- Obtenha `ApiEndpoint` via output do CloudFormation.
- Padrão desejado deste contrato: rotas sem prefixo duplicado (somente `/v1/...` na URL final).

## Modelos habilitados em produção
- `us.anthropic.claude-sonnet-4-6`
- `us.anthropic.claude-haiku-4-5-20251001-v1:0`
- `minimax.minimax-m2.5`
- `us.amazon.nova-2-lite-v1:0`

## Contrato de balanço
- Método: `GET`
- URL: `/v1/credits/balance`
- Content-Type: `application/json`
- Header obrigatório: `x-api-key`

### Request
```http
GET /v1/credits/balance
x-api-key: key_xxx
```

### Response de sucesso (`200`)
```json
{
  "request_id": "boZ7BgItoAMEZYA=",
  "api_key": "key_3ac77ed1",
  "remaining_credits": 19
}
```

Notas:
- `api_key` na resposta vem mascarada.
- `remaining_credits` é o saldo atual da chave informada.

### Erros possíveis
- `401 unauthorized` (sem `x-api-key`)
- `404 api_key_not_found` (chave inexistente)
- `500 internal_error`

Formato de erro:
```json
{
  "request_id": "...",
  "error": "codigo_do_erro"
}
```

## Contrato de listagem de chaves (admin)
- Método: `GET`
- URL: `/v1/admin/keys`
- Header obrigatório: `x-admin-token`

### Response de sucesso (`200`)
```json
{
  "request_id": "....",
  "keys": [
    {
      "api_key": "key_xxx",
      "status": "active",
      "allocated_credits": 20,
      "remaining_credits": 19,
      "used_credits": 1
    }
  ]
}
```

## Contrato de deleção de chave (admin)
- Método: `DELETE`
- URL: `/v1/admin/keys/{key_id}`
- Header obrigatório: `x-admin-token`

### Response de sucesso (`200`)
```json
{
  "request_id": "....",
  "deleted": true,
  "api_key": "key_xxx"
}
```

## Autenticação e headers obrigatórios
- `x-api-key`: chave da aplicação/tenant que consome créditos.
- `x-idempotency-key`: chave única da tentativa lógica de invoke.

Recomendação:
- Gere `x-idempotency-key` estável por operação de negócio (ex.: `order-123-step-llm-v1`).
- Se repetir a mesma operação, reutilize a mesma key.

## Modelos permitidos (allowlist)
Atualmente, apenas estes `model_id` são aceitos:
- `us.anthropic.claude-sonnet-4-6`
- `us.anthropic.claude-haiku-4-5-20251001-v1:0`
- `minimax.minimax-m2.5`
- `us.amazon.nova-2-lite-v1:0`

Se `model_id` não for enviado, o proxy usa o default configurado no ambiente.

## Request (contrato)
Body:
```json
{
  "model_id": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
  "input": {
    "messages": [
      {
        "role": "user",
        "content": [
          { "text": "Resuma este texto em 3 bullets." }
        ]
      }
    ],
    "inference_config": {
      "maxTokens": 300,
      "temperature": 0.2
    }
  }
}
```

### Formas aceitas em `input`
- `messages` (preferido): formato Bedrock Converse.
- `prompt` (string): proxy converte para `messages` automaticamente.
- `text` (string): proxy converte para `messages` automaticamente.
- `inference_config` opcional: enviado para `inferenceConfig` do Converse.
- Se `inference_config.maxTokens` não vier, o proxy usa `512`.

## Response de sucesso (`200`)
Exemplo:
```json
{
  "request_id": "boZ6hjftIAMEZZw=",
  "remaining_credits": 19,
  "provider_latency_ms": 723,
  "model_id": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
  "response": {
    "ResponseMetadata": {
      "RequestId": "e17d517c-b180-4222-8af5-995ad5cc5683",
      "HTTPStatusCode": 200
    },
    "output": {
      "message": {
        "role": "assistant",
        "content": [
          { "text": "ok" }
        ]
      }
    },
    "stopReason": "end_turn",
    "usage": {
      "inputTokens": 13,
      "outputTokens": 4,
      "totalTokens": 17
    },
    "metrics": {
      "latencyMs": 640
    }
  }
}
```

Notas:
- `provider_latency_ms` = latência medida pelo proxy.
- `response.metrics.latencyMs` = latência reportada pelo provider.
- A resposta do provider é repassada em `response` (payload Bedrock Converse).
- O campo `response.ResponseMetadata` também é repassado (metadados AWS SDK/Bedrock).

## Como extrair texto do output
Ler em ordem:
1. `response.output.message.content[*].text` (quando existir)
2. Se não houver `text`, tratar outros blocos (`reasoningContent`, etc.) conforme a necessidade do seu consumidor.

Exemplo prático (pseudo):
```text
for part in response.output.message.content:
  if part.text: append(part.text)
```

## Erros e status codes
- `400 missing_idempotency_key`
- `400 missing_input`
- `400 model_not_allowed` (retorna também `allowed_models`)
- `401 missing_api_key`
- `401 unauthorized` (falha na camada de crédito interna)
- `402 insufficient_credit`
- `429 provider_throttled` (throttle do modelo/provider)
- `500 credit_service_error`
- `502 provider_error`

Formato de erro:
```json
{
  "request_id": "...",
  "error": "codigo_do_erro"
}
```

## Regras de crédito
- 1 invoke = 1 crédito.
- Fluxo interno: `reserve -> invoke provider -> confirm`.
- Se o provider falhar, o crédito é estornado (`refund`).

## Exemplo de chamada
```bash
curl -X POST "$API_BASE/v1/llm/invoke" \
  -H "content-type: application/json" \
  -H "x-api-key: key_xxx" \
  -H "x-idempotency-key: op-123-v1" \
  -d '{
    "model_id": "us.amazon.nova-2-lite-v1:0",
    "input": {
      "messages": [
        {"role":"user","content":[{"text":"Responda apenas: ok"}]}
      ],
      "inference_config": {"maxTokens": 32, "temperature": 0}
    }
  }'
```
