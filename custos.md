# Estimativa de Tokens e Custos

Base analisada: `case/Teste Prático - Coordenador de IA - Exemplo Conversas.json`

## Metodologia

- Heurística usada para estimar tokens: `1 token ~= 4 caracteres`
- O cálculo considera apenas o texto após os prefixos `human:` e `ai:`
- `tokens/users` foi interpretado como tokens das mensagens `human`
- As projeções de usuários abaixo assumem `1 conversa média por usuário`
- Esta é uma estimativa agnóstica de tokenizer; os valores reais podem variar por modelo/provedor

## Resumo da Base

| Métrica | Valor |
| --- | ---: |
| Conversas | 20 |
| Mensagens totais | 238 |
| Mensagens `human` | 121 |
| Mensagens `ai` | 117 |
| Tokens estimados totais | 12.637,25 |
| Tokens estimados `human` | 1.725,00 |
| Tokens estimados `ai` | 10.912,25 |
| Média de tokens por conversa | 631,86 |
| Mediana de tokens por conversa | 438,62 |
| Mínimo por conversa | 178,00 |
| Máximo por conversa | 1.917,25 |
| Média por mensagem `human` | 14,26 |
| Média por mensagem `ai` | 93,27 |
| Média de tokens `human` por conversa | 86,25 |
| Média de tokens `ai` por conversa | 545,61 |

## Preços por Modelo

Preços on-demand padrão, em USD por 1M tokens.

| Modelo | Região | Input | Output | Observação |
| --- | --- | ---: | ---: | --- |
| `anthropic.claude-sonnet-4-6` | `us-east-1` | 3,30 | 16,50 | SKU regional |
| `anthropic.claude-sonnet-4-6` | `sa-east-1` | 3,00 | 15,00 | Catálogo expôs SKU `Global` |
| `anthropic.claude-haiku-4-5-20251001-v1:0` | `us-east-1` | 1,10 | 5,50 | SKU regional |
| `anthropic.claude-haiku-4-5-20251001-v1:0` | `sa-east-1` | 1,00 | 5,00 | Catálogo expôs SKU `Global` |
| `minimax.minimax-m2.5` | `us-east-1` | 0,30 | 1,20 | SKU padrão |
| `minimax.minimax-m2.5` | `sa-east-1` | 0,36 | 1,44 | SKU padrão |
| `amazon.nova-2-lite-v1:0` | `us-east-1` | 0,33 | 2,75 | SKU padrão |
| `amazon.nova-2-lite-v1:0` | `sa-east-1` | n/d | n/d | Não encontrado no catálogo padrão consultado |

## Preços Batch na Bedrock

Preços batch, em USD por 1M tokens.

| Modelo | Região | Input | Output | Observação |
| --- | --- | ---: | ---: | --- |
| `anthropic.claude-sonnet-4-6` | `us-east-1` | 1,65 | 8,25 | SKU batch regional |
| `anthropic.claude-sonnet-4-6` | `sa-east-1` | 1,50 | 7,50 | Catálogo expôs SKU batch `Global` |
| `anthropic.claude-haiku-4-5-20251001-v1:0` | `us-east-1` | 0,55 | 2,75 | SKU batch regional |
| `anthropic.claude-haiku-4-5-20251001-v1:0` | `sa-east-1` | 0,50 | 2,50 | Catálogo expôs SKU batch `Global` |
| `minimax.minimax-m2.5` | `us-east-1` | 0,15 | 0,60 | SKU batch padrão |
| `minimax.minimax-m2.5` | `sa-east-1` | 0,18 | 0,72 | SKU batch padrão |
| `amazon.nova-2-lite-v1:0` | `us-east-1` | 0,165 | 1,375 | SKU batch padrão |
| `amazon.nova-2-lite-v1:0` | `sa-east-1` | n/d | n/d | Não encontrado no catálogo batch padrão consultado |

## Fórmulas

- Cenário `split`: custo = `(tokens_human / 1_000_000 * preço_input) + (tokens_ai / 1_000_000 * preço_output)`
- Cenário `all input`: custo = `(tokens_totais / 1_000_000 * preço_input)`

O cenário `split` é o mais próximo do uso típico de chat, onde mensagens do usuário entram como input e respostas do modelo saem como output.

## Custo Médio por Conversa

Base do cálculo:

- `human` médio por conversa: `86,25` tokens
- `ai` médio por conversa: `545,61` tokens
- total médio por conversa: `631,86` tokens

| Modelo | Região | Custo médio `split` | Custo médio `all input` |
| --- | --- | ---: | ---: |
| `anthropic.claude-sonnet-4-6` | `us-east-1` | US$ 0,009287 | US$ 0,002085 |
| `anthropic.claude-sonnet-4-6` | `sa-east-1` | US$ 0,008443 | US$ 0,001896 |
| `anthropic.claude-haiku-4-5-20251001-v1:0` | `us-east-1` | US$ 0,003096 | US$ 0,000695 |
| `anthropic.claude-haiku-4-5-20251001-v1:0` | `sa-east-1` | US$ 0,002814 | US$ 0,000632 |
| `minimax.minimax-m2.5` | `us-east-1` | US$ 0,000681 | US$ 0,000190 |
| `minimax.minimax-m2.5` | `sa-east-1` | US$ 0,000817 | US$ 0,000227 |
| `amazon.nova-2-lite-v1:0` | `us-east-1` | US$ 0,001529 | US$ 0,000209 |

## Custo Médio por Conversa em Batch

| Modelo | Região | Custo médio `split` | Custo médio `all input` |
| --- | --- | ---: | ---: |
| `anthropic.claude-sonnet-4-6` | `us-east-1` | US$ 0,004644 | US$ 0,001043 |
| `anthropic.claude-sonnet-4-6` | `sa-east-1` | US$ 0,004221 | US$ 0,000948 |
| `anthropic.claude-haiku-4-5-20251001-v1:0` | `us-east-1` | US$ 0,001548 | US$ 0,000348 |
| `anthropic.claude-haiku-4-5-20251001-v1:0` | `sa-east-1` | US$ 0,001407 | US$ 0,000316 |
| `minimax.minimax-m2.5` | `us-east-1` | US$ 0,000340 | US$ 0,000095 |
| `minimax.minimax-m2.5` | `sa-east-1` | US$ 0,000408 | US$ 0,000114 |
| `amazon.nova-2-lite-v1:0` | `us-east-1` | US$ 0,000764 | US$ 0,000104 |

## Custo do Dataset Inteiro

Base do cálculo:

- `human` total: `1.725,00` tokens
- `ai` total: `10.912,25` tokens
- total geral: `12.637,25` tokens

| Modelo | Região | Custo total `split` |
| --- | --- | ---: |
| `anthropic.claude-sonnet-4-6` | `us-east-1` | US$ 0,185745 |
| `anthropic.claude-sonnet-4-6` | `sa-east-1` | US$ 0,168859 |
| `anthropic.claude-haiku-4-5-20251001-v1:0` | `us-east-1` | US$ 0,061915 |
| `anthropic.claude-haiku-4-5-20251001-v1:0` | `sa-east-1` | US$ 0,056286 |
| `minimax.minimax-m2.5` | `us-east-1` | US$ 0,013612 |
| `minimax.minimax-m2.5` | `sa-east-1` | US$ 0,016335 |
| `amazon.nova-2-lite-v1:0` | `us-east-1` | US$ 0,030578 |

## Custo do Dataset Inteiro em Batch

| Modelo | Região | Custo total `split` |
| --- | --- | ---: |
| `anthropic.claude-sonnet-4-6` | `us-east-1` | US$ 0,092872 |
| `anthropic.claude-sonnet-4-6` | `sa-east-1` | US$ 0,084429 |
| `anthropic.claude-haiku-4-5-20251001-v1:0` | `us-east-1` | US$ 0,030957 |
| `anthropic.claude-haiku-4-5-20251001-v1:0` | `sa-east-1` | US$ 0,028143 |
| `minimax.minimax-m2.5` | `us-east-1` | US$ 0,006806 |
| `minimax.minimax-m2.5` | `sa-east-1` | US$ 0,008167 |
| `amazon.nova-2-lite-v1:0` | `us-east-1` | US$ 0,015289 |

## Projeção para 10.000 Usuários

Assumindo `1 conversa média por usuário`:

- tokens `human`: `862.500,00`
- tokens `ai`: `5.456.100,00`
- tokens totais: `6.318.600,00`

| Modelo | Região | Custo projetado `split` | Custo projetado `all input` |
| --- | --- | ---: | ---: |
| `anthropic.claude-sonnet-4-6` | `us-east-1` | US$ 92,87 | US$ 20,85 |
| `anthropic.claude-sonnet-4-6` | `sa-east-1` | US$ 84,43 | US$ 18,96 |
| `anthropic.claude-haiku-4-5-20251001-v1:0` | `us-east-1` | US$ 30,96 | US$ 6,95 |
| `anthropic.claude-haiku-4-5-20251001-v1:0` | `sa-east-1` | US$ 28,14 | US$ 6,32 |
| `minimax.minimax-m2.5` | `us-east-1` | US$ 6,81 | US$ 1,90 |
| `minimax.minimax-m2.5` | `sa-east-1` | US$ 8,17 | US$ 2,27 |
| `amazon.nova-2-lite-v1:0` | `us-east-1` | US$ 15,29 | US$ 2,09 |

## Projeção Batch para 10.000 Usuários

Assumindo `1 conversa média por usuário`:

- tokens `human`: `862.500,00`
- tokens `ai`: `5.456.100,00`
- tokens totais: `6.318.600,00`

| Modelo | Região | Custo projetado `split` | Custo projetado `all input` |
| --- | --- | ---: | ---: |
| `anthropic.claude-sonnet-4-6` | `us-east-1` | US$ 46,44 | US$ 10,43 |
| `anthropic.claude-sonnet-4-6` | `sa-east-1` | US$ 42,21 | US$ 9,48 |
| `anthropic.claude-haiku-4-5-20251001-v1:0` | `us-east-1` | US$ 15,48 | US$ 3,48 |
| `anthropic.claude-haiku-4-5-20251001-v1:0` | `sa-east-1` | US$ 14,07 | US$ 3,16 |
| `minimax.minimax-m2.5` | `us-east-1` | US$ 3,40 | US$ 0,95 |
| `minimax.minimax-m2.5` | `sa-east-1` | US$ 4,08 | US$ 1,14 |
| `amazon.nova-2-lite-v1:0` | `us-east-1` | US$ 7,64 | US$ 1,04 |

## Projeção para 100.000 Usuários

Assumindo `1 conversa média por usuário`:

- tokens `human`: `8.625.000,00`
- tokens `ai`: `54.561.000,00`
- tokens totais: `63.186.000,00`

| Modelo | Região | Custo projetado `split` | Custo projetado `all input` |
| --- | --- | ---: | ---: |
| `anthropic.claude-sonnet-4-6` | `us-east-1` | US$ 928,72 | US$ 208,51 |
| `anthropic.claude-sonnet-4-6` | `sa-east-1` | US$ 844,29 | US$ 189,56 |
| `anthropic.claude-haiku-4-5-20251001-v1:0` | `us-east-1` | US$ 309,57 | US$ 69,50 |
| `anthropic.claude-haiku-4-5-20251001-v1:0` | `sa-east-1` | US$ 281,43 | US$ 63,19 |
| `minimax.minimax-m2.5` | `us-east-1` | US$ 68,06 | US$ 18,96 |
| `minimax.minimax-m2.5` | `sa-east-1` | US$ 81,67 | US$ 22,75 |
| `amazon.nova-2-lite-v1:0` | `us-east-1` | US$ 152,89 | US$ 20,85 |

## Projeção Batch para 100.000 Usuários

Assumindo `1 conversa média por usuário`:

- tokens `human`: `8.625.000,00`
- tokens `ai`: `54.561.000,00`
- tokens totais: `63.186.000,00`

| Modelo | Região | Custo projetado `split` | Custo projetado `all input` |
| --- | --- | ---: | ---: |
| `anthropic.claude-sonnet-4-6` | `us-east-1` | US$ 464,36 | US$ 104,26 |
| `anthropic.claude-sonnet-4-6` | `sa-east-1` | US$ 422,15 | US$ 94,78 |
| `anthropic.claude-haiku-4-5-20251001-v1:0` | `us-east-1` | US$ 154,79 | US$ 34,75 |
| `anthropic.claude-haiku-4-5-20251001-v1:0` | `sa-east-1` | US$ 140,72 | US$ 31,59 |
| `minimax.minimax-m2.5` | `us-east-1` | US$ 34,03 | US$ 9,48 |
| `minimax.minimax-m2.5` | `sa-east-1` | US$ 40,84 | US$ 11,37 |
| `amazon.nova-2-lite-v1:0` | `us-east-1` | US$ 76,44 | US$ 10,43 |

## Fontes

- AWS Price List API, `AmazonBedrockFoundationModels`:
  - `us-east-1`: `https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonBedrockFoundationModels/20260313193424/us-east-1/index.json`
  - `sa-east-1`: `https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonBedrockFoundationModels/20260313193424/sa-east-1/index.json`
- AWS Price List API, `AmazonBedrock`:
  - `us-east-1`: `https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonBedrock/20260326230352/us-east-1/index.json`
  - `sa-east-1`: `https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonBedrock/20260326230352/sa-east-1/index.json`
