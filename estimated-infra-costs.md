# Estimated Infra Costs (AWS) - 30.000 analises/mes

## Objetivo

Consolidar uma estimativa mensal de custo para o agente de NPS (infra + LLM), com base em:

- arquitetura MVP batch informada (2 S3, 2 EventBridge, 2 Lambda, 3 DynamoDB, Bedrock, 1 Fargate, 1 ALB, 1 CloudFront, 1 WAF, CloudWatch);
- volume de `30.000` analises/mes;
- margem de seguranca de `+30%`.

## Premissas adotadas

- Regiao: `us-east-1`.
- Janela mensal: `730 horas`.
- Trafego web/API: `50.000 requests/mes` (baixo).
- Bedrock em batch gerenciado (sem custo fixo de infraestrutura do Bedrock alem dos tokens).
- Fargate: `1 task 24/7` com `1 vCPU` e `2 GB RAM`.
- Lambda (2 funcoes somadas): `90.000 invocations/mes`, `512 MB`, `1s` medio por execucao.
- EventBridge: `60.000 eventos custom/mes`.
- S3 (2 buckets): `20 GB` armazenados, `60.000 PUT/COPY/POST/LIST`, `60.000 GET/outros`.
- DynamoDB (3 tabelas, on-demand): `300.000 writes`, `900.000 reads`, `10 GB` armazenados.
- CloudFront: `50 GB` de data transfer out + `50.000` HTTPS requests.
- WAF: `1 Web ACL` + `3 regras` + `50.000 requests`.
- CloudWatch: `30 GB` de logs ingeridos, `30 GB` armazenados, `10` alarmes.
- Sem Free Tier, sem impostos e sem descontos contratuais.

## Precos unitarios usados (AWS Price List API)

| Servico | Unidade de preco | Valor (USD) |
| --- | --- | ---: |
| Fargate (Linux x86) | vCPU-hora | 0,04048 |
| Fargate (Linux x86) | GB-hora memoria | 0,004445 |
| ALB | hora | 0,0225 |
| ALB | LCU-hora | 0,008 |
| S3 Standard | GB-mes armazenamento (primeiros 50 TB) | 0,023 |
| S3 Standard | 1.000 PUT/COPY/POST/LIST | 0,005 |
| S3 Standard | 10.000 GET/outros | 0,004 |
| EventBridge custom | 1 milhao de eventos | 1,00 |
| Lambda | 1 milhao de requests | 0,20 |
| Lambda | GB-second | 0,0000166667 |
| DynamoDB on-demand | 1 milhao de writes | 0,625 |
| DynamoDB on-demand | 1 milhao de reads | 0,125 |
| DynamoDB | GB-mes armazenamento | 0,25 |
| CloudFront (US) | GB data transfer out (primeiros 10 TB) | 0,085 |
| CloudFront (US) | 10.000 HTTPS requests | 0,01 |
| WAF | Web ACL / mes | 5,00 |
| WAF | regra / mes | 1,00 |
| WAF | 1 milhao de requests | 0,60 |
| CloudWatch Logs | GB ingerido | 0,50 |
| CloudWatch Logs | GB-mes armazenado | 0,03 |
| CloudWatch Alarms | alarme / mes | 0,10 |

## Estimativa mensal de infraestrutura

| Servico | Formula resumida | Custo (USD/mes) |
| --- | --- | ---: |
| S3 (2 buckets) | `(20*0,023) + (60*0,005) + (6*0,004)` | 0,78 |
| EventBridge (2 buses) | `(60.000/1.000.000)*1,00` | 0,06 |
| Lambda (2 funcoes) | `(90.000/1.000.000*0,20) + (90.000*1s*0,5GB*0,0000166667)` | 0,77 |
| DynamoDB (3 tabelas) | `(300k*0,625/1M) + (900k*0,125/1M) + (10*0,25)` | 2,80 |
| Fargate (1 task 24/7) | `(1*730*0,04048) + (2*730*0,004445)` | 36,04 |
| ALB | `(730*0,0225) + (730*0,1*0,008)` | 17,01 |
| CloudFront | `(50*0,085) + (50.000/10.000*0,01)` | 4,30 |
| WAF | `5 + (3*1) + (50.000/1.000.000*0,60)` | 8,03 |
| CloudWatch | `(30*0,50) + (30*0,03) + (10*0,10)` | 16,90 |
| Bedrock (infra fixa) | `sem custo fixo de capacidade` | 0,00 |
| **Subtotal Infra** |  | **86,69** |
| **Infra +30% margem** | `86,69*1,30` | **112,70** |

## Custos de LLM para 30.000 analises/mes

Fonte: `custos.md` (cenario `batch split`, `us-east-1`).

| Modelo | Custo medio por analise (USD) | Custo LLM em 30k (USD/mes) |
| --- | ---: | ---: |
| `anthropic.claude-sonnet-4-6` | 0,004644 | 139,32 |
| `anthropic.claude-haiku-4-5-20251001-v1:0` | 0,001548 | 46,44 |
| `minimax.minimax-m2.5` | 0,000340 | 10,20 |
| `amazon.nova-2-lite-v1:0` | 0,000764 | 22,92 |

## Total consolidado (Infra + LLM + margem de 30%)

| Modelo | Infra (USD) | LLM 30k (USD) | Total sem margem (USD) | Total com +30% (USD) |
| --- | ---: | ---: | ---: | ---: |
| `anthropic.claude-sonnet-4-6` | 86,69 | 139,32 | 226,01 | 293,81 |
| `anthropic.claude-haiku-4-5-20251001-v1:0` | 86,69 | 46,44 | 133,13 | 173,07 |
| `minimax.minimax-m2.5` | 86,69 | 10,20 | 96,89 | 125,96 |
| `amazon.nova-2-lite-v1:0` | 86,69 | 22,92 | 109,61 | 142,49 |

## Fontes

- `custos.md` (custos de LLM ja calculados no repositorio).
- AWS Price List API (consulta em `2026-04-16`):
  - `https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonECS/current/index.json`
  - `https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSELB/current/index.json`
  - `https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/index.json`
  - `https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSEvents/current/index.json`
  - `https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSLambda/current/index.json`
  - `https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonDynamoDB/current/index.json`
  - `https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/awswaf/current/index.json`
  - `https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonCloudFront/current/index.json`
  - `https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonCloudWatch/current/index.json`
